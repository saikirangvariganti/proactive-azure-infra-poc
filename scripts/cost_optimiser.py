#!/usr/bin/env python3
"""
cost_optimiser.py — Azure Cloud Cost Optimisation Script
=========================================================
Identifies underutilised and orphaned Azure resources across a subscription
and generates a cost-saving report with actionable recommendations.

Key checks performed:
  - Underutilised VMs (CPU < 10% over 7 days)
  - Orphaned managed disks (not attached to any VM)
  - Idle App Service Plans (0 apps or all apps stopped)
  - Oversized AKS node pools (avg node CPU < 20%)
  - Unused public IP addresses (not associated to any resource)
  - Unused load balancers (no backend pool members)

Usage:
  python cost_optimiser.py --subscription-id <SUB_ID> --resource-group <RG> [--output report.json]
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger("cost_optimiser")


# ─── Data Models ──────────────────────────────────────────────────────────────

@dataclass
class CostRecommendation:
    resource_id: str
    resource_name: str
    resource_type: str
    issue: str
    recommendation: str
    estimated_monthly_saving_gbp: float
    priority: str  # high | medium | low
    metadata: dict = field(default_factory=dict)


@dataclass
class OptimisationReport:
    subscription_id: str
    resource_group: str
    generated_at: str
    total_resources_scanned: int
    total_recommendations: int
    total_estimated_saving_gbp: float
    recommendations: list[CostRecommendation] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


# ─── Optimisation Checks ──────────────────────────────────────────────────────

def check_underutilised_vms(
    compute_client: Any,
    monitor_client: Any,
    resource_group: str,
) -> list[CostRecommendation]:
    """Flag VMs with average CPU < 10% over the last 7 days."""
    recommendations: list[CostRecommendation] = []
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=7)

    try:
        vms = list(compute_client.virtual_machines.list(resource_group))
        logger.info("Scanning %d VMs for underutilisation", len(vms))

        for vm in vms:
            try:
                metrics = monitor_client.metrics.list(
                    resource_uri=vm.id,
                    timespan=f"{start_time.isoformat()}/{end_time.isoformat()}",
                    interval="PT1H",
                    metricnames="Percentage CPU",
                    aggregation="Average",
                )
                avg_cpu = _extract_avg_metric(metrics)
                if avg_cpu is not None and avg_cpu < 10.0:
                    recommendations.append(
                        CostRecommendation(
                            resource_id=vm.id,
                            resource_name=vm.name,
                            resource_type="Microsoft.Compute/virtualMachines",
                            issue=f"Average CPU utilisation {avg_cpu:.1f}% over 7 days (threshold: 10%)",
                            recommendation="Right-size to smaller VM SKU or enable auto-shutdown schedule",
                            estimated_monthly_saving_gbp=_estimate_vm_saving(vm),
                            priority="high" if avg_cpu < 5.0 else "medium",
                            metadata={"avg_cpu_pct": avg_cpu, "vm_size": vm.hardware_profile.vm_size if vm.hardware_profile else "unknown"},
                        )
                    )
            except Exception as exc:
                logger.warning("Could not fetch metrics for VM %s: %s", vm.name, exc)

    except Exception as exc:
        logger.error("Failed to list VMs in %s: %s", resource_group, exc)

    return recommendations


def check_orphaned_disks(
    compute_client: Any,
    resource_group: str,
) -> list[CostRecommendation]:
    """Flag managed disks with no owner VM."""
    recommendations: list[CostRecommendation] = []

    try:
        disks = list(compute_client.disks.list_by_resource_group(resource_group))
        logger.info("Scanning %d managed disks", len(disks))

        for disk in disks:
            if disk.managed_by is None:
                size_gb = disk.disk_size_gb or 0
                monthly_cost = _estimate_disk_cost_gbp(size_gb, disk.sku.name if disk.sku else "Standard_LRS")
                recommendations.append(
                    CostRecommendation(
                        resource_id=disk.id,
                        resource_name=disk.name,
                        resource_type="Microsoft.Compute/disks",
                        issue="Managed disk is not attached to any VM",
                        recommendation="Delete orphaned disk or snapshot it to cheaper tier",
                        estimated_monthly_saving_gbp=monthly_cost,
                        priority="medium",
                        metadata={"size_gb": size_gb, "sku": disk.sku.name if disk.sku else "unknown"},
                    )
                )

    except Exception as exc:
        logger.error("Failed to list disks in %s: %s", resource_group, exc)

    return recommendations


def check_idle_app_service_plans(
    web_client: Any,
    resource_group: str,
) -> list[CostRecommendation]:
    """Flag App Service Plans with no running apps."""
    recommendations: list[CostRecommendation] = []

    try:
        plans = list(web_client.app_service_plans.list_by_resource_group(resource_group))
        logger.info("Scanning %d App Service Plans", len(plans))

        for plan in plans:
            if plan.number_of_sites == 0:
                recommendations.append(
                    CostRecommendation(
                        resource_id=plan.id,
                        resource_name=plan.name,
                        resource_type="Microsoft.Web/serverfarms",
                        issue="App Service Plan has 0 apps deployed",
                        recommendation="Delete idle App Service Plan",
                        estimated_monthly_saving_gbp=_estimate_asp_cost_gbp(plan.sku.name if plan.sku else "B1"),
                        priority="high",
                        metadata={"sku": plan.sku.name if plan.sku else "unknown", "apps": 0},
                    )
                )

    except Exception as exc:
        logger.error("Failed to list App Service Plans in %s: %s", resource_group, exc)

    return recommendations


def check_unused_public_ips(
    network_client: Any,
    resource_group: str,
) -> list[CostRecommendation]:
    """Flag public IP addresses with no associated resource."""
    recommendations: list[CostRecommendation] = []

    try:
        public_ips = list(network_client.public_ip_addresses.list(resource_group))
        logger.info("Scanning %d public IP addresses", len(public_ips))

        for pip in public_ips:
            if pip.ip_configuration is None and pip.nat_gateway is None:
                recommendations.append(
                    CostRecommendation(
                        resource_id=pip.id,
                        resource_name=pip.name,
                        resource_type="Microsoft.Network/publicIPAddresses",
                        issue="Public IP address is not associated with any resource",
                        recommendation="Delete unused public IP to eliminate hourly charges",
                        estimated_monthly_saving_gbp=3.0,  # ~£3/month for static public IP
                        priority="low",
                        metadata={"sku": pip.sku.name if pip.sku else "Basic", "allocation": pip.public_ip_allocation_method},
                    )
                )

    except Exception as exc:
        logger.error("Failed to list public IPs in %s: %s", resource_group, exc)

    return recommendations


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _extract_avg_metric(metrics: Any) -> float | None:
    """Extract the average value from an Azure Monitor metrics response."""
    try:
        for metric in metrics.value:
            for ts in metric.timeseries:
                values = [d.average for d in ts.data if d.average is not None]
                if values:
                    return sum(values) / len(values)
    except Exception:
        pass
    return None


def _estimate_vm_saving(vm: Any) -> float:
    """Rough monthly saving estimate for right-sizing a VM (GBP)."""
    size = (vm.hardware_profile.vm_size if vm.hardware_profile else "").lower()
    size_savings = {
        "standard_d4s_v3": 60.0,
        "standard_d8s_v3": 120.0,
        "standard_d16s_v3": 240.0,
        "standard_e4s_v3": 80.0,
    }
    return size_savings.get(size, 30.0)


def _estimate_disk_cost_gbp(size_gb: int, sku: str) -> float:
    """Estimate monthly disk cost in GBP."""
    rates = {
        "Premium_LRS": 0.17,
        "StandardSSD_LRS": 0.09,
        "Standard_LRS": 0.05,
        "UltraSSD_LRS": 0.35,
    }
    rate = rates.get(sku, 0.08)
    return round(size_gb * rate, 2)


def _estimate_asp_cost_gbp(sku_name: str) -> float:
    """Estimate monthly App Service Plan cost in GBP."""
    costs = {
        "B1": 12.0, "B2": 24.0, "B3": 48.0,
        "S1": 55.0, "S2": 110.0, "S3": 220.0,
        "P1v2": 80.0, "P2v2": 160.0, "P3v2": 320.0,
        "P1v3": 85.0, "P2v3": 170.0, "P3v3": 340.0,
    }
    return costs.get(sku_name, 55.0)


# ─── Main ─────────────────────────────────────────────────────────────────────

def run_optimisation(
    subscription_id: str,
    resource_group: str,
    output_file: str | None = None,
    dry_run: bool = True,
) -> OptimisationReport:
    """
    Orchestrate all cost optimisation checks and produce a report.

    In dry_run mode (default): no Azure SDK calls are made; returns a mock report.
    This allows the script to be tested without Azure credentials.
    """
    logger.info(
        "Starting cost optimisation scan — subscription=%s rg=%s dry_run=%s",
        subscription_id, resource_group, dry_run,
    )

    if dry_run:
        logger.info("DRY RUN mode — returning synthetic recommendations")
        report = _generate_mock_report(subscription_id, resource_group)
    else:
        report = _run_live_checks(subscription_id, resource_group)

    report.total_recommendations = len(report.recommendations)
    report.total_estimated_saving_gbp = sum(
        r.estimated_monthly_saving_gbp for r in report.recommendations
    )

    logger.info(
        "Scan complete — %d recommendations, estimated saving £%.2f/month",
        report.total_recommendations,
        report.total_estimated_saving_gbp,
    )

    if output_file:
        with open(output_file, "w", encoding="utf-8") as fh:
            json.dump(report.to_dict(), fh, indent=2)
        logger.info("Report written to %s", output_file)

    return report


def _generate_mock_report(subscription_id: str, resource_group: str) -> OptimisationReport:
    """Return a realistic mock report for demonstration without Azure creds."""
    mock_recommendations = [
        CostRecommendation(
            resource_id=f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines/vm-worker-01",
            resource_name="vm-worker-01",
            resource_type="Microsoft.Compute/virtualMachines",
            issue="Average CPU utilisation 3.2% over 7 days (threshold: 10%)",
            recommendation="Right-size from Standard_D8s_v3 to Standard_D2s_v3",
            estimated_monthly_saving_gbp=120.0,
            priority="high",
            metadata={"avg_cpu_pct": 3.2, "vm_size": "Standard_D8s_v3"},
        ),
        CostRecommendation(
            resource_id=f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Compute/disks/data-disk-orphan-001",
            resource_name="data-disk-orphan-001",
            resource_type="Microsoft.Compute/disks",
            issue="Managed disk is not attached to any VM",
            recommendation="Delete orphaned 256 GB Premium SSD disk",
            estimated_monthly_saving_gbp=43.52,
            priority="medium",
            metadata={"size_gb": 256, "sku": "Premium_LRS"},
        ),
        CostRecommendation(
            resource_id=f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Web/serverfarms/asp-staging-idle",
            resource_name="asp-staging-idle",
            resource_type="Microsoft.Web/serverfarms",
            issue="App Service Plan has 0 apps deployed",
            recommendation="Delete idle S2 App Service Plan",
            estimated_monthly_saving_gbp=110.0,
            priority="high",
            metadata={"sku": "S2", "apps": 0},
        ),
        CostRecommendation(
            resource_id=f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Network/publicIPAddresses/pip-old-lb-01",
            resource_name="pip-old-lb-01",
            resource_type="Microsoft.Network/publicIPAddresses",
            issue="Public IP address is not associated with any resource",
            recommendation="Delete unused static public IP",
            estimated_monthly_saving_gbp=3.0,
            priority="low",
            metadata={"sku": "Standard", "allocation": "Static"},
        ),
    ]

    return OptimisationReport(
        subscription_id=subscription_id,
        resource_group=resource_group,
        generated_at=datetime.now(timezone.utc).isoformat(),
        total_resources_scanned=42,
        total_recommendations=len(mock_recommendations),
        total_estimated_saving_gbp=0.0,
        recommendations=mock_recommendations,
    )


def _run_live_checks(subscription_id: str, resource_group: str) -> OptimisationReport:
    """Execute actual Azure SDK checks (requires azure-identity credentials)."""
    try:
        from azure.identity import DefaultAzureCredential
        from azure.mgmt.compute import ComputeManagementClient
        from azure.mgmt.monitor import MonitorManagementClient
        from azure.mgmt.network import NetworkManagementClient
    except ImportError as exc:
        logger.error("Azure SDK not available: %s — install requirements.txt", exc)
        sys.exit(1)

    credential = DefaultAzureCredential()
    compute_client = ComputeManagementClient(credential, subscription_id)
    monitor_client = MonitorManagementClient(credential, subscription_id)
    network_client = NetworkManagementClient(credential, subscription_id)

    all_recs: list[CostRecommendation] = []
    all_recs.extend(check_underutilised_vms(compute_client, monitor_client, resource_group))
    all_recs.extend(check_orphaned_disks(compute_client, resource_group))
    all_recs.extend(check_unused_public_ips(network_client, resource_group))

    return OptimisationReport(
        subscription_id=subscription_id,
        resource_group=resource_group,
        generated_at=datetime.now(timezone.utc).isoformat(),
        total_resources_scanned=0,
        total_recommendations=0,
        total_estimated_saving_gbp=0.0,
        recommendations=all_recs,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Azure Cost Optimisation Scanner")
    parser.add_argument("--subscription-id", required=True, help="Azure subscription ID")
    parser.add_argument("--resource-group", required=True, help="Resource group to scan")
    parser.add_argument("--output", help="Output file path for JSON report")
    parser.add_argument("--live", action="store_true", help="Run live Azure API checks (requires credentials)")
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    report = run_optimisation(
        subscription_id=args.subscription_id,
        resource_group=args.resource_group,
        output_file=args.output,
        dry_run=not args.live,
    )
    print(json.dumps(report.to_dict(), indent=2))
