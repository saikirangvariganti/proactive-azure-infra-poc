resource "azurerm_key_vault" "main" {
  name                        = "kv-${var.project_name}-${var.environment}"
  location                    = var.location
  resource_group_name         = var.resource_group_name
  enabled_for_disk_encryption = true
  tenant_id                   = var.tenant_id
  soft_delete_retention_days  = 90
  purge_protection_enabled    = var.environment == "prod" ? true : false
  sku_name                    = "standard"

  network_acls {
    default_action = "Deny"
    bypass         = "AzureServices"
    ip_rules       = []
  }

  # Terraform deployer access policy
  access_policy {
    tenant_id = var.tenant_id
    object_id = var.object_id

    key_permissions = [
      "Get", "List", "Create", "Delete", "Update", "Recover", "Backup", "Restore"
    ]
    secret_permissions = [
      "Get", "List", "Set", "Delete", "Recover", "Backup", "Restore"
    ]
    certificate_permissions = [
      "Get", "List", "Create", "Delete", "Update", "Import"
    ]
  }

  tags = var.common_tags
}

# Enable Defender for Key Vault
resource "azurerm_security_center_subscription_pricing" "key_vault" {
  tier          = "Standard"
  resource_type = "KeyVaults"
}

resource "azurerm_security_center_subscription_pricing" "aks" {
  tier          = "Standard"
  resource_type = "KubernetesService"
}

resource "azurerm_security_center_subscription_pricing" "storage" {
  tier          = "Standard"
  resource_type = "StorageAccounts"
}

# Azure Policy — enforce HTTPS only
resource "azurerm_subscription_policy_assignment" "require_https_storage" {
  name                 = "require-https-storage-${var.environment}"
  subscription_id      = "/subscriptions/${var.subscription_id}"
  policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/404c3081-a854-4457-ae30-26a93ef643f9"
  description          = "Ensure storage accounts enforce HTTPS traffic"
  display_name         = "Require HTTPS for Storage Accounts (${var.environment})"
}

# Azure Policy — deny public IP on VMs
resource "azurerm_subscription_policy_assignment" "deny_public_ip_vms" {
  name                 = "deny-public-ip-vms-${var.environment}"
  subscription_id      = "/subscriptions/${var.subscription_id}"
  policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/83a86a26-fd1f-447c-b59d-e51f44264114"
  description          = "Prevent VMs from being created with public IP addresses"
  display_name         = "Deny Public IP on VMs (${var.environment})"
}

# Diagnostic settings for Key Vault
resource "azurerm_monitor_diagnostic_setting" "key_vault" {
  name                       = "diag-kv-${var.project_name}-${var.environment}"
  target_resource_id         = azurerm_key_vault.main.id
  log_analytics_workspace_id = var.log_analytics_id

  enabled_log {
    category = "AuditEvent"
  }
  enabled_log {
    category = "AzurePolicyEvaluationDetails"
  }

  metric {
    category = "AllMetrics"
    enabled  = true
  }
}

output "key_vault_id"  { value = azurerm_key_vault.main.id }
output "key_vault_uri" { value = azurerm_key_vault.main.vault_uri }
output "key_vault_name" { value = azurerm_key_vault.main.name }

variable "resource_group_name" { type = string }
variable "location"             { type = string }
variable "project_name"         { type = string }
variable "environment"          { type = string }
variable "tenant_id"            { type = string }
variable "object_id"            { type = string }
variable "subscription_id"      { type = string }
variable "log_analytics_id"     { type = string }
variable "common_tags"          { type = map(string); default = {} }
