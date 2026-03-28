"""
test_poc.py — Comprehensive test suite for proactive-azure-infra-poc
=====================================================================
Covers all artefacts:
  - Terraform root + modules (HCL content validation)
  - Kubernetes manifests (namespace, deployment, service)
  - Python scripts (cost_optimiser, security_baseline)
  - Monitoring JSON (alert_rules, grafana_dashboard)
  - GitHub Actions workflow YAML
  - Project structure, README, requirements.txt

90+ test functions.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest
import yaml

# ─── Repo Root ────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).parent.parent

# ─── Helpers ──────────────────────────────────────────────────────────────────


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_yaml(path: Path) -> dict | list:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def read_yaml_all(path: Path) -> list:
    return list(yaml.safe_load_all(path.read_text(encoding="utf-8")))


# ─── 1. Project Structure ─────────────────────────────────────────────────────


def test_repo_root_exists():
    assert REPO_ROOT.is_dir(), f"REPO_ROOT {REPO_ROOT} does not exist"


def test_readme_exists():
    assert (REPO_ROOT / "README.md").is_file()


def test_requirements_txt_exists():
    assert (REPO_ROOT / "requirements.txt").is_file()


def test_terraform_dir_exists():
    assert (REPO_ROOT / "terraform").is_dir()


def test_k8s_dir_exists():
    assert (REPO_ROOT / "k8s").is_dir()


def test_scripts_dir_exists():
    assert (REPO_ROOT / "scripts").is_dir()


def test_monitoring_dir_exists():
    assert (REPO_ROOT / "monitoring").is_dir()


def test_github_workflows_dir_exists():
    assert (REPO_ROOT / ".github" / "workflows").is_dir()


def test_tests_dir_exists():
    assert (REPO_ROOT / "tests").is_dir()


def test_terraform_modules_dir_exists():
    assert (REPO_ROOT / "terraform" / "modules").is_dir()


# ─── 2. README ────────────────────────────────────────────────────────────────


def test_readme_contains_overview():
    content = read(REPO_ROOT / "README.md")
    assert "Overview" in content or "overview" in content.lower()


def test_readme_mentions_aks():
    content = read(REPO_ROOT / "README.md")
    assert "AKS" in content


def test_readme_mentions_terraform():
    content = read(REPO_ROOT / "README.md")
    assert "Terraform" in content or "terraform" in content


def test_readme_mentions_keyvault():
    content = read(REPO_ROOT / "README.md")
    assert "Key Vault" in content or "KeyVault" in content


def test_readme_mentions_github_actions():
    content = read(REPO_ROOT / "README.md")
    assert "GitHub Actions" in content or "GitHub" in content


def test_readme_mentions_grafana():
    content = read(REPO_ROOT / "README.md")
    assert "Grafana" in content or "grafana" in content


def test_readme_mentions_cost():
    content = read(REPO_ROOT / "README.md")
    assert "cost" in content.lower()


def test_readme_mentions_author():
    content = read(REPO_ROOT / "README.md")
    assert "Sai Kiran" in content or "saikirangvariganti" in content


# ─── 3. requirements.txt ──────────────────────────────────────────────────────


def test_requirements_has_azure_identity():
    content = read(REPO_ROOT / "requirements.txt")
    assert "azure-identity" in content


def test_requirements_has_azure_mgmt_compute():
    content = read(REPO_ROOT / "requirements.txt")
    assert "azure-mgmt-compute" in content


def test_requirements_has_pyyaml():
    content = read(REPO_ROOT / "requirements.txt")
    assert "pyyaml" in content or "PyYAML" in content.lower()


def test_requirements_has_pytest():
    content = read(REPO_ROOT / "requirements.txt")
    assert "pytest" in content


def test_requirements_has_azure_mgmt_network():
    content = read(REPO_ROOT / "requirements.txt")
    assert "azure-mgmt-network" in content


# ─── 4. Terraform — Root main.tf ──────────────────────────────────────────────


def test_terraform_main_tf_exists():
    assert (REPO_ROOT / "terraform" / "main.tf").is_file()


def test_terraform_main_required_providers():
    content = read(REPO_ROOT / "terraform" / "main.tf")
    assert "required_providers" in content


def test_terraform_main_azurerm_provider():
    content = read(REPO_ROOT / "terraform" / "main.tf")
    assert "azurerm" in content


def test_terraform_main_backend_azurerm():
    content = read(REPO_ROOT / "terraform" / "main.tf")
    assert 'backend "azurerm"' in content


def test_terraform_main_resource_group():
    content = read(REPO_ROOT / "terraform" / "main.tf")
    assert "azurerm_resource_group" in content


def test_terraform_main_log_analytics():
    content = read(REPO_ROOT / "terraform" / "main.tf")
    assert "azurerm_log_analytics_workspace" in content


def test_terraform_main_module_networking():
    content = read(REPO_ROOT / "terraform" / "main.tf")
    assert 'module "networking"' in content


def test_terraform_main_module_security():
    content = read(REPO_ROOT / "terraform" / "main.tf")
    assert 'module "security"' in content


def test_terraform_main_module_storage():
    content = read(REPO_ROOT / "terraform" / "main.tf")
    assert 'module "storage"' in content


def test_terraform_main_module_aks():
    content = read(REPO_ROOT / "terraform" / "main.tf")
    assert 'module "aks"' in content


def test_terraform_main_module_app_service():
    content = read(REPO_ROOT / "terraform" / "main.tf")
    assert 'module "app_service"' in content


def test_terraform_main_action_group():
    content = read(REPO_ROOT / "terraform" / "main.tf")
    assert "azurerm_monitor_action_group" in content


def test_terraform_main_common_tags():
    content = read(REPO_ROOT / "terraform" / "main.tf")
    assert "common_tags" in content


def test_terraform_main_keyvault_provider_features():
    content = read(REPO_ROOT / "terraform" / "main.tf")
    assert "key_vault" in content


# ─── 5. Terraform — variables.tf ──────────────────────────────────────────────


def test_terraform_variables_tf_exists():
    assert (REPO_ROOT / "terraform" / "variables.tf").is_file()


def test_terraform_variables_location():
    content = read(REPO_ROOT / "terraform" / "variables.tf")
    assert '"location"' in content


def test_terraform_variables_environment():
    content = read(REPO_ROOT / "terraform" / "variables.tf")
    assert '"environment"' in content


def test_terraform_variables_kubernetes_version():
    content = read(REPO_ROOT / "terraform" / "variables.tf")
    assert "kubernetes_version" in content


def test_terraform_variables_aks_node_count():
    content = read(REPO_ROOT / "terraform" / "variables.tf")
    assert "aks_node_count" in content


def test_terraform_variables_environment_validation():
    content = read(REPO_ROOT / "terraform" / "variables.tf")
    assert "dev" in content and "staging" in content and "prod" in content


def test_terraform_variables_vnet_address_space():
    content = read(REPO_ROOT / "terraform" / "variables.tf")
    assert "vnet_address_space" in content


def test_terraform_variables_log_retention():
    content = read(REPO_ROOT / "terraform" / "variables.tf")
    assert "log_retention_days" in content


# ─── 6. Terraform — outputs.tf ────────────────────────────────────────────────


def test_terraform_outputs_tf_exists():
    assert (REPO_ROOT / "terraform" / "outputs.tf").is_file()


def test_terraform_outputs_aks_cluster_name():
    content = read(REPO_ROOT / "terraform" / "outputs.tf")
    assert "aks_cluster_name" in content


def test_terraform_outputs_key_vault_uri():
    content = read(REPO_ROOT / "terraform" / "outputs.tf")
    assert "key_vault_uri" in content


def test_terraform_outputs_storage_account_name():
    content = read(REPO_ROOT / "terraform" / "outputs.tf")
    assert "storage_account_name" in content


def test_terraform_outputs_vnet_id():
    content = read(REPO_ROOT / "terraform" / "outputs.tf")
    assert "vnet_id" in content


def test_terraform_outputs_app_service_url():
    content = read(REPO_ROOT / "terraform" / "outputs.tf")
    assert "app_service_url" in content


def test_terraform_outputs_log_analytics():
    content = read(REPO_ROOT / "terraform" / "outputs.tf")
    assert "log_analytics" in content


# ─── 7. Terraform — AKS Module ────────────────────────────────────────────────


def test_aks_module_main_tf_exists():
    assert (REPO_ROOT / "terraform" / "modules" / "aks" / "main.tf").is_file()


def test_aks_module_variables_tf_exists():
    assert (REPO_ROOT / "terraform" / "modules" / "aks" / "variables.tf").is_file()


def test_aks_module_kubernetes_cluster():
    content = read(REPO_ROOT / "terraform" / "modules" / "aks" / "main.tf")
    assert "azurerm_kubernetes_cluster" in content


def test_aks_module_node_pool():
    content = read(REPO_ROOT / "terraform" / "modules" / "aks" / "main.tf")
    assert "default_node_pool" in content


def test_aks_module_user_node_pool():
    content = read(REPO_ROOT / "terraform" / "modules" / "aks" / "main.tf")
    assert "azurerm_kubernetes_cluster_node_pool" in content


def test_aks_module_rbac_enabled():
    content = read(REPO_ROOT / "terraform" / "modules" / "aks" / "main.tf")
    assert "role_based_access_control_enabled" in content


def test_aks_module_azure_policy():
    content = read(REPO_ROOT / "terraform" / "modules" / "aks" / "main.tf")
    assert "azure_policy_enabled" in content


def test_aks_module_workload_identity():
    content = read(REPO_ROOT / "terraform" / "modules" / "aks" / "main.tf")
    assert "workload_identity_enabled" in content


def test_aks_module_oms_agent():
    content = read(REPO_ROOT / "terraform" / "modules" / "aks" / "main.tf")
    assert "oms_agent" in content


def test_aks_module_key_vault_secrets_provider():
    content = read(REPO_ROOT / "terraform" / "modules" / "aks" / "main.tf")
    assert "key_vault_secrets_provider" in content


def test_aks_module_network_profile():
    content = read(REPO_ROOT / "terraform" / "modules" / "aks" / "main.tf")
    assert "network_profile" in content


def test_aks_module_autoscaling():
    content = read(REPO_ROOT / "terraform" / "modules" / "aks" / "main.tf")
    assert "enable_auto_scaling" in content


# ─── 8. Terraform — Security Module ──────────────────────────────────────────


def test_security_module_exists():
    assert (REPO_ROOT / "terraform" / "modules" / "security" / "main.tf").is_file()


def test_security_module_key_vault():
    content = read(REPO_ROOT / "terraform" / "modules" / "security" / "main.tf")
    assert "azurerm_key_vault" in content


def test_security_module_soft_delete():
    content = read(REPO_ROOT / "terraform" / "modules" / "security" / "main.tf")
    assert "soft_delete_retention_days" in content


def test_security_module_purge_protection():
    content = read(REPO_ROOT / "terraform" / "modules" / "security" / "main.tf")
    assert "purge_protection_enabled" in content


def test_security_module_network_acls():
    content = read(REPO_ROOT / "terraform" / "modules" / "security" / "main.tf")
    assert "network_acls" in content


def test_security_module_defender_keyvault():
    content = read(REPO_ROOT / "terraform" / "modules" / "security" / "main.tf")
    assert "KeyVaults" in content


def test_security_module_defender_aks():
    content = read(REPO_ROOT / "terraform" / "modules" / "security" / "main.tf")
    assert "KubernetesService" in content


def test_security_module_azure_policy_assignment():
    content = read(REPO_ROOT / "terraform" / "modules" / "security" / "main.tf")
    assert "azurerm_subscription_policy_assignment" in content


def test_security_module_diagnostic_setting():
    content = read(REPO_ROOT / "terraform" / "modules" / "security" / "main.tf")
    assert "azurerm_monitor_diagnostic_setting" in content


# ─── 9. Terraform — Networking Module ────────────────────────────────────────


def test_networking_module_exists():
    assert (REPO_ROOT / "terraform" / "modules" / "networking" / "main.tf").is_file()


def test_networking_module_vnet():
    content = read(REPO_ROOT / "terraform" / "modules" / "networking" / "main.tf")
    assert "azurerm_virtual_network" in content


def test_networking_module_aks_subnet():
    content = read(REPO_ROOT / "terraform" / "modules" / "networking" / "main.tf")
    assert "snet-aks" in content


def test_networking_module_app_subnet():
    content = read(REPO_ROOT / "terraform" / "modules" / "networking" / "main.tf")
    assert "snet-app" in content


def test_networking_module_nsg():
    content = read(REPO_ROOT / "terraform" / "modules" / "networking" / "main.tf")
    assert "azurerm_network_security_group" in content


def test_networking_module_deny_all_rule():
    content = read(REPO_ROOT / "terraform" / "modules" / "networking" / "main.tf")
    assert "DenyAllInbound" in content


def test_networking_module_nsg_association():
    content = read(REPO_ROOT / "terraform" / "modules" / "networking" / "main.tf")
    assert "azurerm_subnet_network_security_group_association" in content


# ─── 10. Terraform — Storage Module ──────────────────────────────────────────


def test_storage_module_exists():
    assert (REPO_ROOT / "terraform" / "modules" / "storage" / "main.tf").is_file()


def test_storage_module_storage_account():
    content = read(REPO_ROOT / "terraform" / "modules" / "storage" / "main.tf")
    assert "azurerm_storage_account" in content


def test_storage_module_https_only():
    content = read(REPO_ROOT / "terraform" / "modules" / "storage" / "main.tf")
    assert "enable_https_traffic_only" in content


def test_storage_module_tls12():
    content = read(REPO_ROOT / "terraform" / "modules" / "storage" / "main.tf")
    assert "TLS1_2" in content


def test_storage_module_no_public_blob():
    content = read(REPO_ROOT / "terraform" / "modules" / "storage" / "main.tf")
    assert "allow_nested_items_to_be_public" in content


def test_storage_module_adls_hns():
    content = read(REPO_ROOT / "terraform" / "modules" / "storage" / "main.tf")
    assert "is_hns_enabled" in content


def test_storage_module_containers():
    content = read(REPO_ROOT / "terraform" / "modules" / "storage" / "main.tf")
    assert "azurerm_storage_container" in content


def test_storage_module_network_rules_deny():
    content = read(REPO_ROOT / "terraform" / "modules" / "storage" / "main.tf")
    assert 'default_action' in content


# ─── 11. Kubernetes — namespace.yaml ─────────────────────────────────────────


def test_k8s_namespace_yaml_exists():
    assert (REPO_ROOT / "k8s" / "namespace.yaml").is_file()


def test_k8s_namespace_has_namespace_resource():
    docs = read_yaml_all(REPO_ROOT / "k8s" / "namespace.yaml")
    kinds = [d.get("kind") for d in docs if d]
    assert "Namespace" in kinds


def test_k8s_namespace_name_is_app():
    docs = read_yaml_all(REPO_ROOT / "k8s" / "namespace.yaml")
    ns = next(d for d in docs if d and d.get("kind") == "Namespace")
    assert ns["metadata"]["name"] == "app"


def test_k8s_namespace_has_resource_quota():
    docs = read_yaml_all(REPO_ROOT / "k8s" / "namespace.yaml")
    kinds = [d.get("kind") for d in docs if d]
    assert "ResourceQuota" in kinds


def test_k8s_namespace_has_limit_range():
    docs = read_yaml_all(REPO_ROOT / "k8s" / "namespace.yaml")
    kinds = [d.get("kind") for d in docs if d]
    assert "LimitRange" in kinds


def test_k8s_namespace_has_network_policy():
    docs = read_yaml_all(REPO_ROOT / "k8s" / "namespace.yaml")
    kinds = [d.get("kind") for d in docs if d]
    assert "NetworkPolicy" in kinds


# ─── 12. Kubernetes — deployment.yaml ────────────────────────────────────────


def test_k8s_deployment_yaml_exists():
    assert (REPO_ROOT / "k8s" / "deployment.yaml").is_file()


def test_k8s_deployment_has_deployment():
    docs = read_yaml_all(REPO_ROOT / "k8s" / "deployment.yaml")
    kinds = [d.get("kind") for d in docs if d]
    assert "Deployment" in kinds


def test_k8s_deployment_name():
    docs = read_yaml_all(REPO_ROOT / "k8s" / "deployment.yaml")
    dep = next(d for d in docs if d and d.get("kind") == "Deployment")
    assert dep["metadata"]["name"] == "proactive-api"


def test_k8s_deployment_namespace():
    docs = read_yaml_all(REPO_ROOT / "k8s" / "deployment.yaml")
    dep = next(d for d in docs if d and d.get("kind") == "Deployment")
    assert dep["metadata"]["namespace"] == "app"


def test_k8s_deployment_replicas():
    docs = read_yaml_all(REPO_ROOT / "k8s" / "deployment.yaml")
    dep = next(d for d in docs if d and d.get("kind") == "Deployment")
    assert dep["spec"]["replicas"] >= 2


def test_k8s_deployment_rolling_update():
    docs = read_yaml_all(REPO_ROOT / "k8s" / "deployment.yaml")
    dep = next(d for d in docs if d and d.get("kind") == "Deployment")
    assert dep["spec"]["strategy"]["type"] == "RollingUpdate"


def test_k8s_deployment_resource_limits():
    docs = read_yaml_all(REPO_ROOT / "k8s" / "deployment.yaml")
    dep = next(d for d in docs if d and d.get("kind") == "Deployment")
    containers = dep["spec"]["template"]["spec"]["containers"]
    assert len(containers) > 0
    for c in containers:
        assert "limits" in c.get("resources", {})


def test_k8s_deployment_resource_requests():
    docs = read_yaml_all(REPO_ROOT / "k8s" / "deployment.yaml")
    dep = next(d for d in docs if d and d.get("kind") == "Deployment")
    containers = dep["spec"]["template"]["spec"]["containers"]
    for c in containers:
        assert "requests" in c.get("resources", {})


def test_k8s_deployment_liveness_probe():
    docs = read_yaml_all(REPO_ROOT / "k8s" / "deployment.yaml")
    dep = next(d for d in docs if d and d.get("kind") == "Deployment")
    containers = dep["spec"]["template"]["spec"]["containers"]
    assert any("livenessProbe" in c for c in containers)


def test_k8s_deployment_readiness_probe():
    docs = read_yaml_all(REPO_ROOT / "k8s" / "deployment.yaml")
    dep = next(d for d in docs if d and d.get("kind") == "Deployment")
    containers = dep["spec"]["template"]["spec"]["containers"]
    assert any("readinessProbe" in c for c in containers)


def test_k8s_deployment_non_root():
    docs = read_yaml_all(REPO_ROOT / "k8s" / "deployment.yaml")
    dep = next(d for d in docs if d and d.get("kind") == "Deployment")
    security_ctx = dep["spec"]["template"]["spec"].get("securityContext", {})
    assert security_ctx.get("runAsNonRoot") is True


def test_k8s_deployment_no_privilege_escalation():
    docs = read_yaml_all(REPO_ROOT / "k8s" / "deployment.yaml")
    dep = next(d for d in docs if d and d.get("kind") == "Deployment")
    containers = dep["spec"]["template"]["spec"]["containers"]
    for c in containers:
        sc = c.get("securityContext", {})
        assert sc.get("allowPrivilegeEscalation") is False


def test_k8s_deployment_has_hpa():
    docs = read_yaml_all(REPO_ROOT / "k8s" / "deployment.yaml")
    kinds = [d.get("kind") for d in docs if d]
    assert "HorizontalPodAutoscaler" in kinds


def test_k8s_deployment_has_pdb():
    docs = read_yaml_all(REPO_ROOT / "k8s" / "deployment.yaml")
    kinds = [d.get("kind") for d in docs if d]
    assert "PodDisruptionBudget" in kinds


def test_k8s_deployment_image_pull_policy_always():
    docs = read_yaml_all(REPO_ROOT / "k8s" / "deployment.yaml")
    dep = next(d for d in docs if d and d.get("kind") == "Deployment")
    containers = dep["spec"]["template"]["spec"]["containers"]
    for c in containers:
        assert c.get("imagePullPolicy") == "Always"


# ─── 13. Kubernetes — service.yaml ───────────────────────────────────────────


def test_k8s_service_yaml_exists():
    assert (REPO_ROOT / "k8s" / "service.yaml").is_file()


def test_k8s_service_has_service():
    docs = read_yaml_all(REPO_ROOT / "k8s" / "service.yaml")
    kinds = [d.get("kind") for d in docs if d]
    assert "Service" in kinds


def test_k8s_service_has_ingress():
    docs = read_yaml_all(REPO_ROOT / "k8s" / "service.yaml")
    kinds = [d.get("kind") for d in docs if d]
    assert "Ingress" in kinds


def test_k8s_service_targets_app_namespace():
    docs = read_yaml_all(REPO_ROOT / "k8s" / "service.yaml")
    svc = next(d for d in docs if d and d.get("kind") == "Service")
    assert svc["metadata"]["namespace"] == "app"


def test_k8s_service_selector_matches_deployment():
    docs = read_yaml_all(REPO_ROOT / "k8s" / "service.yaml")
    svc = next(d for d in docs if d and d.get("kind") == "Service")
    assert svc["spec"]["selector"].get("app") == "proactive-api"


def test_k8s_ingress_ssl_redirect():
    content = read(REPO_ROOT / "k8s" / "service.yaml")
    assert "ssl-redirect" in content


def test_k8s_ingress_tls_configured():
    docs = read_yaml_all(REPO_ROOT / "k8s" / "service.yaml")
    ingress = next(d for d in docs if d and d.get("kind") == "Ingress")
    assert "tls" in ingress["spec"]


# ─── 14. cost_optimiser.py ────────────────────────────────────────────────────


def test_cost_optimiser_script_exists():
    assert (REPO_ROOT / "scripts" / "cost_optimiser.py").is_file()


def test_cost_optimiser_importable():
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import cost_optimiser  # noqa: F401
    sys.path.pop(0)


def test_cost_optimiser_dry_run_returns_report():
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from cost_optimiser import run_optimisation
    report = run_optimisation(
        subscription_id="test-sub-id",
        resource_group="rg-test",
        dry_run=True,
    )
    assert report.subscription_id == "test-sub-id"
    assert report.resource_group == "rg-test"
    sys.path.pop(0)


def test_cost_optimiser_has_recommendations():
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from cost_optimiser import run_optimisation
    report = run_optimisation("sub-id", "rg-test", dry_run=True)
    assert len(report.recommendations) > 0
    sys.path.pop(0)


def test_cost_optimiser_recommendation_fields():
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from cost_optimiser import run_optimisation
    report = run_optimisation("sub-id", "rg-test", dry_run=True)
    for rec in report.recommendations:
        assert rec.resource_id
        assert rec.resource_name
        assert rec.resource_type
        assert rec.issue
        assert rec.recommendation
        assert rec.estimated_monthly_saving_gbp >= 0
        assert rec.priority in ("high", "medium", "low")
    sys.path.pop(0)


def test_cost_optimiser_total_saving_computed():
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from cost_optimiser import run_optimisation
    report = run_optimisation("sub-id", "rg-test", dry_run=True)
    expected = sum(r.estimated_monthly_saving_gbp for r in report.recommendations)
    assert abs(report.total_estimated_saving_gbp - expected) < 0.01
    sys.path.pop(0)


def test_cost_optimiser_to_dict_serialisable():
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from cost_optimiser import run_optimisation
    report = run_optimisation("sub-id", "rg-test", dry_run=True)
    d = report.to_dict()
    # Must be JSON-serialisable
    assert json.dumps(d)
    sys.path.pop(0)


def test_cost_optimiser_parse_args():
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from cost_optimiser import parse_args
    args = parse_args(["--subscription-id", "abc", "--resource-group", "rg-test"])
    assert args.subscription_id == "abc"
    assert args.resource_group == "rg-test"
    sys.path.pop(0)


def test_cost_optimiser_estimate_disk_cost():
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from cost_optimiser import _estimate_disk_cost_gbp
    cost = _estimate_disk_cost_gbp(128, "Premium_LRS")
    assert cost > 0
    sys.path.pop(0)


def test_cost_optimiser_estimate_asp_cost():
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from cost_optimiser import _estimate_asp_cost_gbp
    assert _estimate_asp_cost_gbp("S2") == 110.0
    assert _estimate_asp_cost_gbp("B1") == 12.0
    sys.path.pop(0)


def test_cost_optimiser_generated_at_is_iso():
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from cost_optimiser import run_optimisation
    report = run_optimisation("sub-id", "rg-test", dry_run=True)
    # Should be parseable as ISO datetime
    from datetime import datetime
    datetime.fromisoformat(report.generated_at)
    sys.path.pop(0)


# ─── 15. security_baseline.py ────────────────────────────────────────────────


def test_security_baseline_script_exists():
    assert (REPO_ROOT / "scripts" / "security_baseline.py").is_file()


def test_security_baseline_importable():
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import security_baseline  # noqa: F401
    sys.path.pop(0)


def test_security_baseline_analyse_terraform():
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from security_baseline import analyse_terraform_configs
    report = analyse_terraform_configs(str(REPO_ROOT / "terraform"))
    assert report.total_controls_checked > 0
    sys.path.pop(0)


def test_security_baseline_findings_have_control_id():
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from security_baseline import analyse_terraform_configs
    report = analyse_terraform_configs(str(REPO_ROOT / "terraform"))
    for finding in report.findings:
        assert finding.control_id
        assert finding.severity in ("critical", "high", "medium", "low", "info")
    sys.path.pop(0)


def test_security_baseline_compliance_pct_in_range():
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from security_baseline import analyse_terraform_configs
    report = analyse_terraform_configs(str(REPO_ROOT / "terraform"))
    assert 0 <= report.compliance_pct <= 100
    sys.path.pop(0)


def test_security_baseline_kv_soft_delete_compliant():
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from security_baseline import analyse_terraform_configs
    report = analyse_terraform_configs(str(REPO_ROOT / "terraform"))
    kv001 = next((f for f in report.findings if f.control_id == "KV-001"), None)
    assert kv001 is not None
    assert kv001.compliant is True
    sys.path.pop(0)


def test_security_baseline_storage_https_compliant():
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from security_baseline import analyse_terraform_configs
    report = analyse_terraform_configs(str(REPO_ROOT / "terraform"))
    st001 = next((f for f in report.findings if f.control_id == "ST-001"), None)
    assert st001 is not None
    assert st001.compliant is True
    sys.path.pop(0)


def test_security_baseline_aks_rbac_compliant():
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from security_baseline import analyse_terraform_configs
    report = analyse_terraform_configs(str(REPO_ROOT / "terraform"))
    aks001 = next((f for f in report.findings if f.control_id == "AKS-001"), None)
    assert aks001 is not None
    assert aks001.compliant is True
    sys.path.pop(0)


def test_security_baseline_to_dict_serialisable():
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from security_baseline import analyse_terraform_configs
    report = analyse_terraform_configs(str(REPO_ROOT / "terraform"))
    d = report.to_dict()
    assert json.dumps(d)
    sys.path.pop(0)


def test_security_baseline_controls_dict_populated():
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from security_baseline import SECURITY_CONTROLS
    assert len(SECURITY_CONTROLS) >= 10
    for cid, ctrl in SECURITY_CONTROLS.items():
        assert "title" in ctrl
        assert "severity" in ctrl
        assert "remediation" in ctrl
    sys.path.pop(0)


def test_security_baseline_nsg_no_ssh_compliant():
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from security_baseline import analyse_terraform_configs
    report = analyse_terraform_configs(str(REPO_ROOT / "terraform"))
    net001 = next((f for f in report.findings if f.control_id == "NET-001"), None)
    assert net001 is not None
    assert net001.compliant is True
    sys.path.pop(0)


# ─── 16. monitoring/alert_rules.json ─────────────────────────────────────────


def test_alert_rules_json_exists():
    assert (REPO_ROOT / "monitoring" / "alert_rules.json").is_file()


def test_alert_rules_valid_json():
    data = read_json(REPO_ROOT / "monitoring" / "alert_rules.json")
    assert isinstance(data, dict)


def test_alert_rules_has_alert_rules_key():
    data = read_json(REPO_ROOT / "monitoring" / "alert_rules.json")
    assert "alert_rules" in data


def test_alert_rules_has_aks_cpu_rule():
    data = read_json(REPO_ROOT / "monitoring" / "alert_rules.json")
    names = [r["name"] for r in data["alert_rules"]]
    assert any("aks" in n and "cpu" in n for n in names)


def test_alert_rules_has_keyvault_rule():
    data = read_json(REPO_ROOT / "monitoring" / "alert_rules.json")
    names = [r["name"] for r in data["alert_rules"]]
    assert any("keyvault" in n or "kv" in n for n in names)


def test_alert_rules_has_storage_rule():
    data = read_json(REPO_ROOT / "monitoring" / "alert_rules.json")
    names = [r["name"] for r in data["alert_rules"]]
    assert any("storage" in n for n in names)


def test_alert_rules_has_app_service_rule():
    data = read_json(REPO_ROOT / "monitoring" / "alert_rules.json")
    names = [r["name"] for r in data["alert_rules"]]
    assert any("app" in n for n in names)


def test_alert_rules_severity_values_valid():
    data = read_json(REPO_ROOT / "monitoring" / "alert_rules.json")
    valid_severities = {0, 1, 2, 3, 4}
    for rule in data["alert_rules"]:
        assert rule["severity"] in valid_severities, f"Invalid severity in rule {rule['name']}"


def test_alert_rules_enabled_field_present():
    data = read_json(REPO_ROOT / "monitoring" / "alert_rules.json")
    for rule in data["alert_rules"]:
        assert "enabled" in rule


def test_alert_rules_minimum_count():
    data = read_json(REPO_ROOT / "monitoring" / "alert_rules.json")
    assert len(data["alert_rules"]) >= 5


def test_alert_rules_action_groups_present():
    data = read_json(REPO_ROOT / "monitoring" / "alert_rules.json")
    assert "action_groups" in data


# ─── 17. monitoring/grafana_dashboard.json ────────────────────────────────────


def test_grafana_dashboard_json_exists():
    assert (REPO_ROOT / "monitoring" / "grafana_dashboard.json").is_file()


def test_grafana_dashboard_valid_json():
    data = read_json(REPO_ROOT / "monitoring" / "grafana_dashboard.json")
    assert isinstance(data, dict)


def test_grafana_dashboard_has_title():
    data = read_json(REPO_ROOT / "monitoring" / "grafana_dashboard.json")
    assert "title" in data


def test_grafana_dashboard_has_panels():
    data = read_json(REPO_ROOT / "monitoring" / "grafana_dashboard.json")
    assert "panels" in data
    assert len(data["panels"]) > 0


def test_grafana_dashboard_has_uid():
    data = read_json(REPO_ROOT / "monitoring" / "grafana_dashboard.json")
    assert "uid" in data


def test_grafana_dashboard_has_azure_datasource():
    data = read_json(REPO_ROOT / "monitoring" / "grafana_dashboard.json")
    content = json.dumps(data)
    assert "azure" in content.lower()


def test_grafana_dashboard_has_aks_panel():
    data = read_json(REPO_ROOT / "monitoring" / "grafana_dashboard.json")
    panel_titles = [p.get("title", "") for p in data["panels"]]
    assert any("AKS" in t or "aks" in t.lower() for t in panel_titles)


def test_grafana_dashboard_refresh_set():
    data = read_json(REPO_ROOT / "monitoring" / "grafana_dashboard.json")
    assert "refresh" in data


def test_grafana_dashboard_tags_present():
    data = read_json(REPO_ROOT / "monitoring" / "grafana_dashboard.json")
    assert "tags" in data
    assert len(data["tags"]) > 0


# ─── 18. GitHub Actions — deploy.yml ──────────────────────────────────────────


def test_github_workflow_exists():
    assert (REPO_ROOT / ".github" / "workflows" / "deploy.yml").is_file()


def test_github_workflow_valid_yaml():
    data = read_yaml(REPO_ROOT / ".github" / "workflows" / "deploy.yml")
    assert isinstance(data, dict)


def test_github_workflow_has_on_trigger():
    data = read_yaml(REPO_ROOT / ".github" / "workflows" / "deploy.yml")
    trigger = data.get("on", data.get(True, {}))
    assert trigger is not None and trigger != {}


def test_github_workflow_triggers_on_push_main():
    data = read_yaml(REPO_ROOT / ".github" / "workflows" / "deploy.yml")
    trigger = data.get("on", data.get(True, {}))
    assert "push" in trigger
    branches = trigger["push"].get("branches", [])
    assert "main" in branches


def test_github_workflow_has_pull_request_trigger():
    data = read_yaml(REPO_ROOT / ".github" / "workflows" / "deploy.yml")
    trigger = data.get("on", data.get(True, {}))
    assert "pull_request" in trigger


def test_github_workflow_has_jobs():
    data = read_yaml(REPO_ROOT / ".github" / "workflows" / "deploy.yml")
    assert "jobs" in data
    assert len(data["jobs"]) > 0


def test_github_workflow_has_validate_job():
    data = read_yaml(REPO_ROOT / ".github" / "workflows" / "deploy.yml")
    assert any("validate" in job_id for job_id in data["jobs"])


def test_github_workflow_has_terraform_apply_job():
    data = read_yaml(REPO_ROOT / ".github" / "workflows" / "deploy.yml")
    job_ids = list(data["jobs"].keys())
    assert any("apply" in j or "terraform" in j for j in job_ids)


def test_github_workflow_has_aks_deploy_job():
    data = read_yaml(REPO_ROOT / ".github" / "workflows" / "deploy.yml")
    job_ids = list(data["jobs"].keys())
    assert any("aks" in j or "deploy" in j for j in job_ids)


def test_github_workflow_uses_azure_secrets():
    content = read(REPO_ROOT / ".github" / "workflows" / "deploy.yml")
    assert "AZURE_CLIENT_ID" in content or "AZURE_CREDENTIALS" in content


def test_github_workflow_has_terraform_version():
    content = read(REPO_ROOT / ".github" / "workflows" / "deploy.yml")
    assert "TF_VERSION" in content or "terraform_version" in content


def test_github_workflow_has_checkov():
    content = read(REPO_ROOT / ".github" / "workflows" / "deploy.yml")
    assert "checkov" in content.lower()


def test_github_workflow_has_cost_report_job():
    data = read_yaml(REPO_ROOT / ".github" / "workflows" / "deploy.yml")
    job_ids = list(data["jobs"].keys())
    assert any("cost" in j for j in job_ids)


# ─── 19. Incident Response Shell Script ──────────────────────────────────────


def test_incident_response_script_exists():
    assert (REPO_ROOT / "scripts" / "incident_response.sh").is_file()


def test_incident_response_has_shebang():
    content = read(REPO_ROOT / "scripts" / "incident_response.sh")
    assert content.startswith("#!/usr/bin/env bash") or content.startswith("#!/bin/bash")


def test_incident_response_handles_aks_crashloop():
    content = read(REPO_ROOT / "scripts" / "incident_response.sh")
    assert "aks-crashloop" in content


def test_incident_response_handles_app_5xx():
    content = read(REPO_ROOT / "scripts" / "incident_response.sh")
    assert "app-5xx" in content


def test_incident_response_handles_kv_access():
    content = read(REPO_ROOT / "scripts" / "incident_response.sh")
    assert "kv-access" in content


def test_incident_response_handles_cost_spike():
    content = read(REPO_ROOT / "scripts" / "incident_response.sh")
    assert "cost-spike" in content


def test_incident_response_has_dry_run():
    content = read(REPO_ROOT / "scripts" / "incident_response.sh")
    assert "dry-run" in content or "DRY_RUN" in content


def test_incident_response_has_set_e():
    content = read(REPO_ROOT / "scripts" / "incident_response.sh")
    assert "set -e" in content or "set -euo pipefail" in content


def test_incident_response_logs_to_file():
    content = read(REPO_ROOT / "scripts" / "incident_response.sh")
    assert "LOG_FILE" in content


def test_incident_response_has_usage_function():
    content = read(REPO_ROOT / "scripts" / "incident_response.sh")
    assert "usage" in content


# ─── 20. End-to-End Integration Checks ───────────────────────────────────────


def test_all_required_files_present():
    required = [
        "README.md",
        "requirements.txt",
        "terraform/main.tf",
        "terraform/variables.tf",
        "terraform/outputs.tf",
        "terraform/modules/aks/main.tf",
        "terraform/modules/aks/variables.tf",
        "terraform/modules/app_service/main.tf",
        "terraform/modules/storage/main.tf",
        "terraform/modules/networking/main.tf",
        "terraform/modules/security/main.tf",
        "k8s/namespace.yaml",
        "k8s/deployment.yaml",
        "k8s/service.yaml",
        "scripts/cost_optimiser.py",
        "scripts/security_baseline.py",
        "scripts/incident_response.sh",
        "monitoring/alert_rules.json",
        "monitoring/grafana_dashboard.json",
        ".github/workflows/deploy.yml",
        "tests/test_poc.py",
    ]
    missing = [f for f in required if not (REPO_ROOT / f).exists()]
    assert not missing, f"Missing files: {missing}"


def test_terraform_no_hardcoded_subscription_id():
    # Subscription IDs should come from variables, not be hardcoded
    tf_main = read(REPO_ROOT / "terraform" / "main.tf")
    # Check that real subscription IDs (UUID format) aren't present
    uuid_pattern = re.compile(
        r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
        re.IGNORECASE,
    )
    # There should be no hardcoded UUIDs in main.tf (they use var.* or data.*)
    matches = uuid_pattern.findall(tf_main)
    assert len(matches) == 0, f"Possible hardcoded UUIDs found in main.tf: {matches}"


def test_cost_optimiser_high_priority_recommendations_exist():
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from cost_optimiser import run_optimisation
    report = run_optimisation("sub-id", "rg-test", dry_run=True)
    high = [r for r in report.recommendations if r.priority == "high"]
    assert len(high) > 0
    sys.path.pop(0)


def test_security_baseline_defender_coverage():
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from security_baseline import analyse_terraform_configs
    report = analyse_terraform_configs(str(REPO_ROOT / "terraform"))
    defender_controls = [f for f in report.findings if f.control_id.startswith("DEF-")]
    assert len(defender_controls) >= 3
    sys.path.pop(0)


def test_k8s_manifests_all_in_app_namespace():
    for fname in ["deployment.yaml", "service.yaml"]:
        docs = read_yaml_all(REPO_ROOT / "k8s" / fname)
        for doc in docs:
            if doc and doc.get("kind") not in ("Namespace", None):
                ns = doc.get("metadata", {}).get("namespace")
                assert ns == "app", f"{fname}: {doc.get('kind')} not in 'app' namespace (found: {ns})"


def test_alert_rules_cover_all_components():
    data = read_json(REPO_ROOT / "monitoring" / "alert_rules.json")
    content = json.dumps(data).lower()
    for component in ("aks", "keyvault", "storage", "app"):
        assert component in content, f"No alert rule covers component: {component}"


def test_grafana_dashboard_panels_have_titles():
    data = read_json(REPO_ROOT / "monitoring" / "grafana_dashboard.json")
    for panel in data["panels"]:
        assert "title" in panel, f"Panel missing title: {panel.get('id')}"
