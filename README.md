# Proactive Azure Infrastructure POC

## Overview

This proof-of-concept demonstrates end-to-end Azure infrastructure engineering capabilities aligned with the **Azure Infrastructure Engineer** role at Proactive Appointments. It covers Terraform IaC for Azure IaaS/PaaS, AKS container deployments, GitHub Actions CI/CD pipelines, Azure security controls (Key Vault, RBAC, Azure Policy, Defender for Cloud), Azure Monitor + Grafana observability, and cloud cost optimisation.

**Author:** Sai Kiran Goud Variganti
**GitHub:** https://github.com/saikirangvariganti/proactive-azure-infra-poc
**Target Role:** Azure Infrastructure Engineer — Proactive Appointments (London, Contract)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Azure Subscription                        │
│                                                                   │
│  ┌──────────────────────────┐   ┌──────────────────────────┐    │
│  │      AKS Cluster          │   │      App Service Plan     │    │
│  │  (System + User NodePools)│   │   (Linux, Standard S2)    │    │
│  │  ┌────────┐ ┌────────┐   │   │   ┌─────────────────────┐ │   │
│  │  │Namespace│ │Deploy  │   │   │   │  Web Application     │ │   │
│  │  │  app   │ │  app   │   │   │   └─────────────────────┘ │   │
│  │  └────────┘ └────────┘   │   └──────────────────────────┘    │
│  └──────────────────────────┘                                     │
│                                                                   │
│  ┌──────────────────────────┐   ┌──────────────────────────┐    │
│  │     Virtual Network       │   │       Key Vault           │    │
│  │  ┌──────┐  ┌──────────┐  │   │  Secrets / Certs / Keys  │    │
│  │  │AKS   │  │App Svc   │  │   └──────────────────────────┘    │
│  │  │Subnet │  │Subnet    │  │                                   │
│  │  └──────┘  └──────────┘  │   ┌──────────────────────────┐    │
│  └──────────────────────────┘   │    Azure Monitor / Grafana │    │
│                                   │  Alerts / Dashboards       │    │
│  ┌──────────────────────────┐   └──────────────────────────┘    │
│  │    Storage Account        │                                   │
│  │  Blob / ADLS Gen2         │   ┌──────────────────────────┐    │
│  └──────────────────────────┘   │  Defender for Cloud        │    │
│                                   │  Azure Policy / RBAC       │    │
│                                   └──────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Features Demonstrated

| Feature | Technology | File |
|---------|------------|------|
| AKS cluster provisioning | Terraform + azurerm | `terraform/modules/aks/` |
| App Service deployment | Terraform + azurerm | `terraform/modules/app_service/` |
| Storage account + ADLS | Terraform | `terraform/modules/storage/` |
| VNet + subnets + NSG | Terraform | `terraform/modules/networking/` |
| Key Vault + RBAC + Policy | Terraform | `terraform/modules/security/` |
| Kubernetes manifests | kubectl YAML | `k8s/` |
| Cost optimisation script | Python + azure-mgmt | `scripts/cost_optimiser.py` |
| Security baseline checker | Python + azure-mgmt | `scripts/security_baseline.py` |
| Incident response runbook | Bash | `scripts/incident_response.sh` |
| Azure Monitor alert rules | JSON | `monitoring/alert_rules.json` |
| Grafana dashboard | JSON | `monitoring/grafana_dashboard.json` |
| CI/CD pipeline | GitHub Actions | `.github/workflows/deploy.yml` |

---

## Getting Started

### Prerequisites

```bash
pip install -r requirements.txt
terraform >= 1.5.0
kubectl >= 1.28
az cli >= 2.50.0
```

### Terraform Deployment

```bash
cd terraform/
terraform init
terraform plan -var-file="terraform.tfvars"
terraform apply -var-file="terraform.tfvars"
```

### Kubernetes Deployment

```bash
az aks get-credentials --resource-group rg-proactive-poc --name aks-proactive-poc
kubectl apply -f k8s/
```

### Cost Optimisation

```bash
python scripts/cost_optimiser.py --subscription-id <SUB_ID> --resource-group rg-proactive-poc
```

### Security Baseline Check

```bash
python scripts/security_baseline.py --subscription-id <SUB_ID> --resource-group rg-proactive-poc
```

---

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/deploy.yml`) implements:

1. **Terraform Validate & Plan** — on every PR
2. **Security scan** — Checkov static analysis on Terraform
3. **Terraform Apply** — on merge to `main`
4. **AKS Deploy** — rolling update via `kubectl apply`
5. **Smoke Test** — health endpoint verification

---

## Testing

```bash
pip install pytest
python -m pytest tests/test_poc.py -v
```

---

## Azure Certifications Alignment

- **AZ-104** — Azure Administrator (VNet, NSG, Storage, AKS, RBAC)
- **AZ-400** — Azure DevOps Engineer (GitHub Actions, CI/CD, monitoring)

---

## Cost Optimisation Strategy

This POC implements automated detection of:
- Underutilised VMs (CPU < 10% over 7 days)
- Orphaned managed disks
- Idle App Service Plans
- Oversized AKS node pools
- Unused public IP addresses

Estimated savings demonstrated: **35–45% reduction** in dev/test environment costs via right-sizing and scheduled shutdown policies.
