#!/usr/bin/env bash
# =============================================================================
# incident_response.sh — Azure Platform Incident Response Runbook
# =============================================================================
# Automated first-responder runbook for common Azure infrastructure incidents.
# Implements structured runbooks for:
#   - AKS pod crash loops and OOMKill events
#   - App Service 5xx error spikes
#   - Storage account throttling
#   - Key Vault access failures
#   - Network connectivity issues (NSG / peering)
#   - Cost anomaly alerts
#
# Usage:
#   ./incident_response.sh --incident <INCIDENT_TYPE> \
#                          --resource-group <RG> \
#                          --subscription-id <SUB_ID> \
#                          [--dry-run]
#
# Incident types: aks-crashloop | app-5xx | storage-throttle | kv-access | network | cost-spike
# =============================================================================

set -euo pipefail
IFS=$'\n\t'

# ─── Constants ────────────────────────────────────────────────────────────────

readonly SCRIPT_NAME="$(basename "$0")"
readonly SCRIPT_VERSION="1.2.0"
readonly TIMESTAMP="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
readonly LOG_FILE="/tmp/incident_response_${TIMESTAMP//[:T]/-}.log"

# ─── Colours ──────────────────────────────────────────────────────────────────

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Colour

# ─── Logging ──────────────────────────────────────────────────────────────────

log_info()    { echo -e "${GREEN}[INFO]${NC}  $(date -u '+%H:%M:%S') $*" | tee -a "$LOG_FILE"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC}  $(date -u '+%H:%M:%S') $*" | tee -a "$LOG_FILE"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $(date -u '+%H:%M:%S') $*" | tee -a "$LOG_FILE"; }
log_section() { echo -e "\n${BLUE}══════════════════════════════════════════════${NC}" | tee -a "$LOG_FILE"
                echo -e "${BLUE}  $*${NC}" | tee -a "$LOG_FILE"
                echo -e "${BLUE}══════════════════════════════════════════════${NC}\n" | tee -a "$LOG_FILE"; }

# ─── Defaults ─────────────────────────────────────────────────────────────────

INCIDENT_TYPE=""
RESOURCE_GROUP=""
SUBSCRIPTION_ID=""
DRY_RUN=false
AKS_CLUSTER=""
NAMESPACE="app"

# ─── Argument Parsing ─────────────────────────────────────────────────────────

usage() {
  cat <<EOF
Usage: $SCRIPT_NAME [OPTIONS]

Options:
  --incident       <type>   Incident type (aks-crashloop|app-5xx|storage-throttle|kv-access|network|cost-spike)
  --resource-group <name>   Azure resource group
  --subscription-id <id>    Azure subscription ID
  --aks-cluster    <name>   AKS cluster name (required for aks-crashloop)
  --namespace      <ns>     Kubernetes namespace (default: app)
  --dry-run                 Print commands without executing
  --help                    Show this help

Examples:
  $SCRIPT_NAME --incident aks-crashloop --resource-group rg-proactive-poc --subscription-id abc-123 --aks-cluster aks-proactive-poc
  $SCRIPT_NAME --incident app-5xx --resource-group rg-proactive-poc --subscription-id abc-123 --dry-run
EOF
  exit 0
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case $1 in
      --incident)        INCIDENT_TYPE="$2";    shift 2 ;;
      --resource-group)  RESOURCE_GROUP="$2";   shift 2 ;;
      --subscription-id) SUBSCRIPTION_ID="$2";  shift 2 ;;
      --aks-cluster)     AKS_CLUSTER="$2";      shift 2 ;;
      --namespace)       NAMESPACE="$2";        shift 2 ;;
      --dry-run)         DRY_RUN=true;           shift   ;;
      --help|-h)         usage ;;
      *) log_error "Unknown argument: $1"; usage ;;
    esac
  done
}

# ─── Pre-flight Checks ────────────────────────────────────────────────────────

preflight_checks() {
  log_section "Pre-flight Checks"

  if [[ -z "$INCIDENT_TYPE" ]]; then
    log_error "--incident is required"
    exit 1
  fi

  if [[ -z "$RESOURCE_GROUP" ]]; then
    log_error "--resource-group is required"
    exit 1
  fi

  if [[ "$DRY_RUN" == "true" ]]; then
    log_warn "DRY RUN mode enabled — no changes will be made"
  fi

  # Check az CLI is available
  if ! command -v az &>/dev/null; then
    log_error "Azure CLI (az) is not installed or not in PATH"
    exit 1
  fi

  log_info "Incident type     : $INCIDENT_TYPE"
  log_info "Resource group    : $RESOURCE_GROUP"
  log_info "Subscription ID   : ${SUBSCRIPTION_ID:-<not set>}"
  log_info "Dry run           : $DRY_RUN"
  log_info "Log file          : $LOG_FILE"
}

# ─── Runbook: AKS CrashLoop ───────────────────────────────────────────────────

runbook_aks_crashloop() {
  log_section "Runbook: AKS Pod CrashLoopBackOff / OOMKill"

  local cluster="${AKS_CLUSTER:-$(az aks list -g "$RESOURCE_GROUP" --query '[0].name' -o tsv 2>/dev/null || echo 'unknown')}"

  log_info "Step 1 — Get AKS credentials"
  run_cmd az aks get-credentials \
    --resource-group "$RESOURCE_GROUP" \
    --name "$cluster" \
    --overwrite-existing

  log_info "Step 2 — List pods in CrashLoopBackOff state"
  run_cmd kubectl get pods -n "$NAMESPACE" \
    --field-selector="status.phase!=Running" \
    -o wide

  log_info "Step 3 — Capture logs from failing pods"
  run_cmd kubectl get pods -n "$NAMESPACE" \
    --field-selector="status.phase!=Running" \
    -o jsonpath='{.items[*].metadata.name}' \
    | tr ' ' '\n' \
    | while read -r pod; do
        log_info "  Fetching logs for pod: $pod"
        run_cmd kubectl logs -n "$NAMESPACE" "$pod" --previous --tail=100 || true
      done

  log_info "Step 4 — Check node resource pressure"
  run_cmd kubectl describe nodes | grep -A5 "Conditions:"

  log_info "Step 5 — Check recent events"
  run_cmd kubectl get events -n "$NAMESPACE" \
    --sort-by='.lastTimestamp' \
    | tail -20

  log_info "Step 6 — Check HPA status"
  run_cmd kubectl get hpa -n "$NAMESPACE"

  log_info "Step 7 — Restart failing deployment (if OOMKill)"
  run_cmd kubectl rollout restart deployment/proactive-api -n "$NAMESPACE"

  log_info "Step 8 — Monitor rollout"
  run_cmd kubectl rollout status deployment/proactive-api -n "$NAMESPACE" --timeout=300s

  log_info "Runbook complete — AKS CrashLoop"
}

# ─── Runbook: App Service 5xx ─────────────────────────────────────────────────

runbook_app_5xx() {
  log_section "Runbook: App Service 5xx Error Spike"

  log_info "Step 1 — Query recent HTTP 5xx errors via Azure Monitor"
  run_cmd az monitor metrics list \
    --resource-group "$RESOURCE_GROUP" \
    --resource-type "Microsoft.Web/sites" \
    --metric "Http5xx" \
    --interval PT5M \
    --start-time "$(date -u -d '-1 hour' '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date -u '+%Y-%m-%dT%H:%M:%SZ')" \
    --end-time "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" \
    -o table

  log_info "Step 2 — Check App Service logs"
  run_cmd az webapp log tail \
    --resource-group "$RESOURCE_GROUP" \
    --name "app-proactive-poc-dev" \
    --provider application \
    --filter Error

  log_info "Step 3 — Check App Service health status"
  run_cmd az webapp show \
    --resource-group "$RESOURCE_GROUP" \
    --name "app-proactive-poc-dev" \
    --query "state" -o tsv

  log_info "Step 4 — Check Key Vault connectivity (if secrets-related)"
  run_cmd az keyvault show \
    --name "kv-proactive-poc-dev" \
    --query "properties.provisioningState" -o tsv

  log_info "Step 5 — Restart App Service (if no config change needed)"
  run_cmd az webapp restart \
    --resource-group "$RESOURCE_GROUP" \
    --name "app-proactive-poc-dev"

  log_info "Runbook complete — App Service 5xx"
}

# ─── Runbook: Storage Throttling ──────────────────────────────────────────────

runbook_storage_throttle() {
  log_section "Runbook: Storage Account Throttling"

  log_info "Step 1 — List storage accounts in resource group"
  run_cmd az storage account list \
    --resource-group "$RESOURCE_GROUP" \
    --query "[].{name:name, sku:sku.name}" \
    -o table

  log_info "Step 2 — Check storage transactions metric"
  run_cmd az monitor metrics list \
    --resource-group "$RESOURCE_GROUP" \
    --resource-type "Microsoft.Storage/storageAccounts" \
    --metric "Transactions" \
    --interval PT1M \
    -o table

  log_info "Step 3 — Enable storage account logging (if not already)"
  log_warn "Manual action required: Check blob service diagnostic settings"

  log_info "Step 4 — Review storage account network rules"
  run_cmd az storage account show \
    --resource-group "$RESOURCE_GROUP" \
    --name "stproactivepocdev" \
    --query "networkRuleSet" -o json

  log_info "Runbook complete — Storage Throttling"
}

# ─── Runbook: Key Vault Access Failure ────────────────────────────────────────

runbook_kv_access() {
  log_section "Runbook: Key Vault Access Failure"

  log_info "Step 1 — Check Key Vault access policies"
  run_cmd az keyvault show \
    --name "kv-proactive-poc-dev" \
    --resource-group "$RESOURCE_GROUP" \
    --query "properties.accessPolicies" -o table

  log_info "Step 2 — Query Key Vault audit logs"
  run_cmd az monitor activity-log list \
    --resource-group "$RESOURCE_GROUP" \
    --start-time "$(date -u -d '-1 hour' '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date -u '+%Y-%m-%dT%H:%M:%SZ')" \
    --query "[?resourceType=='Microsoft.KeyVault/vaults']" \
    -o table

  log_info "Step 3 — Verify Key Vault network rules"
  run_cmd az keyvault network-rule list \
    --name "kv-proactive-poc-dev" \
    --resource-group "$RESOURCE_GROUP" \
    -o json

  log_info "Runbook complete — Key Vault Access"
}

# ─── Runbook: Network Connectivity ────────────────────────────────────────────

runbook_network() {
  log_section "Runbook: Network Connectivity Issue"

  log_info "Step 1 — List NSG effective rules for AKS subnet"
  run_cmd az network nsg show \
    --resource-group "$RESOURCE_GROUP" \
    --name "nsg-aks-proactive-poc-dev" \
    --query "securityRules[*].{name:name,priority:priority,access:access,direction:direction,port:destinationPortRange}" \
    -o table

  log_info "Step 2 — Check VNet peerings"
  run_cmd az network vnet peering list \
    --resource-group "$RESOURCE_GROUP" \
    --vnet-name "vnet-proactive-poc-dev" \
    -o table

  log_info "Step 3 — Run VNet connectivity check"
  run_cmd az network watcher test-connectivity \
    --resource-group "$RESOURCE_GROUP" \
    --source-resource "aks-proactive-poc-dev" \
    --dest-address "10.10.2.4" \
    --dest-port 443

  log_info "Runbook complete — Network Connectivity"
}

# ─── Runbook: Cost Spike ──────────────────────────────────────────────────────

runbook_cost_spike() {
  log_section "Runbook: Cost Anomaly / Spike"

  log_info "Step 1 — Query cost by resource group for current month"
  run_cmd az costmanagement query \
    --type "Usage" \
    --scope "subscriptions/$SUBSCRIPTION_ID" \
    --time-period "MonthToDate" \
    --dataset-granularity "Daily" \
    --dataset-grouping "ResourceGroup" \
    -o table

  log_info "Step 2 — Check for new or unexpected resources"
  run_cmd az resource list \
    --resource-group "$RESOURCE_GROUP" \
    --query "[*].{name:name, type:type, created:createdTime}" \
    -o table

  log_info "Step 3 — Run cost optimiser script"
  run_cmd python scripts/cost_optimiser.py \
    --subscription-id "$SUBSCRIPTION_ID" \
    --resource-group "$RESOURCE_GROUP"

  log_info "Runbook complete — Cost Spike"
}

# ─── Command Executor ─────────────────────────────────────────────────────────

run_cmd() {
  if [[ "$DRY_RUN" == "true" ]]; then
    log_warn "[DRY RUN] Would execute: $*"
  else
    log_info "Executing: $*"
    "$@" 2>&1 | tee -a "$LOG_FILE" || {
      log_warn "Command failed (continuing runbook): $*"
    }
  fi
}

# ─── Main Dispatcher ──────────────────────────────────────────────────────────

main() {
  log_section "Azure Incident Response Runbook v${SCRIPT_VERSION}"
  log_info "Timestamp: $TIMESTAMP"

  parse_args "$@"
  preflight_checks

  case "$INCIDENT_TYPE" in
    aks-crashloop)     runbook_aks_crashloop ;;
    app-5xx)           runbook_app_5xx ;;
    storage-throttle)  runbook_storage_throttle ;;
    kv-access)         runbook_kv_access ;;
    network)           runbook_network ;;
    cost-spike)        runbook_cost_spike ;;
    *)
      log_error "Unknown incident type: $INCIDENT_TYPE"
      log_error "Valid types: aks-crashloop | app-5xx | storage-throttle | kv-access | network | cost-spike"
      exit 1
      ;;
  esac

  log_section "Incident Response Complete"
  log_info "Log saved to: $LOG_FILE"
}

main "$@"
