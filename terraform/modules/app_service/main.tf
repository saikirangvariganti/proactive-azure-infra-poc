resource "azurerm_service_plan" "main" {
  name                = "asp-${var.project_name}-${var.environment}"
  resource_group_name = var.resource_group_name
  location            = var.location
  os_type             = "Linux"
  sku_name            = var.environment == "prod" ? "P2v3" : "S2"

  tags = var.common_tags
}

resource "azurerm_linux_web_app" "main" {
  name                      = "app-${var.project_name}-${var.environment}"
  resource_group_name       = var.resource_group_name
  location                  = var.location
  service_plan_id           = azurerm_service_plan.main.id
  virtual_network_subnet_id = var.app_subnet_id

  https_only = true

  site_config {
    always_on        = var.environment == "prod" ? true : false
    ftps_state       = "Disabled"
    http2_enabled    = true
    minimum_tls_version = "1.2"

    application_stack {
      python_version = "3.11"
    }

    health_check_path                 = "/health"
    health_check_eviction_time_in_min = 2
  }

  app_settings = {
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
    "ENVIRONMENT"                          = var.environment
    "KEY_VAULT_URI"                        = "https://kv-${var.project_name}-${var.environment}.vault.azure.net/"
    "APPLICATIONINSIGHTS_CONNECTION_STRING" = "@Microsoft.KeyVault(SecretUri=https://kv-${var.project_name}-${var.environment}.vault.azure.net/secrets/appinsights-connection-string/)"
  }

  identity {
    type = "SystemAssigned"
  }

  logs {
    application_logs {
      file_system_level = "Information"
    }
    http_logs {
      retention_in_days {
        retention_in_days = 7
      }
    }
  }

  tags = var.common_tags
}

# RBAC: App Service identity reads Key Vault secrets
resource "azurerm_role_assignment" "app_keyvault" {
  scope                = var.key_vault_id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_linux_web_app.main.identity[0].principal_id
}

# Diagnostic settings → Log Analytics
resource "azurerm_monitor_diagnostic_setting" "app_service" {
  name                       = "diag-app-${var.project_name}-${var.environment}"
  target_resource_id         = azurerm_linux_web_app.main.id
  log_analytics_workspace_id = var.log_analytics_id

  enabled_log {
    category = "AppServiceAppLogs"
  }
  enabled_log {
    category = "AppServiceHTTPLogs"
  }

  metric {
    category = "AllMetrics"
    enabled  = true
  }
}

output "app_service_url" {
  value = "https://${azurerm_linux_web_app.main.default_hostname}"
}

output "app_service_id" {
  value = azurerm_linux_web_app.main.id
}

output "app_service_principal_id" {
  value = azurerm_linux_web_app.main.identity[0].principal_id
}

variable "resource_group_name" { type = string }
variable "location"             { type = string }
variable "project_name"         { type = string }
variable "environment"          { type = string }
variable "app_subnet_id"        { type = string }
variable "key_vault_id"         { type = string }
variable "log_analytics_id"     { type = string }
variable "common_tags"          { type = map(string); default = {} }
