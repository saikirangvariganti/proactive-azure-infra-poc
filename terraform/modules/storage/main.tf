resource "random_string" "storage_suffix" {
  length  = 6
  special = false
  upper   = false
}

resource "azurerm_storage_account" "main" {
  name                = "st${replace(var.project_name, "-", "")}${var.environment}${random_string.storage_suffix.result}"
  resource_group_name = var.resource_group_name
  location            = var.location
  account_tier        = "Standard"
  account_replication_type = var.environment == "prod" ? "GRS" : "LRS"
  account_kind        = "StorageV2"

  # Security hardening
  enable_https_traffic_only = true
  min_tls_version           = "TLS1_2"
  allow_nested_items_to_be_public = false
  shared_access_key_enabled = false

  # ADLS Gen2 hierarchical namespace
  is_hns_enabled = true

  blob_properties {
    versioning_enabled  = true
    change_feed_enabled = true
    delete_retention_policy {
      days = 14
    }
    container_delete_retention_policy {
      days = 7
    }
  }

  network_rules {
    default_action             = "Deny"
    bypass                     = ["AzureServices"]
    ip_rules                   = []
    virtual_network_subnet_ids = []
  }

  identity {
    type = "SystemAssigned"
  }

  tags = var.common_tags
}

resource "azurerm_storage_container" "app_data" {
  name                  = "app-data"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "tf_state" {
  name                  = "tfstate"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "logs" {
  name                  = "platform-logs"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

resource "azurerm_monitor_diagnostic_setting" "storage" {
  name                       = "diag-storage-${var.project_name}-${var.environment}"
  target_resource_id         = "${azurerm_storage_account.main.id}/blobServices/default"
  log_analytics_workspace_id = var.log_analytics_id

  enabled_log {
    category = "StorageRead"
  }
  enabled_log {
    category = "StorageWrite"
  }
  enabled_log {
    category = "StorageDelete"
  }

  metric {
    category = "Transaction"
    enabled  = true
  }
}

output "storage_account_name" {
  value = azurerm_storage_account.main.name
}

output "storage_account_id" {
  value = azurerm_storage_account.main.id
}

output "primary_blob_endpoint" {
  value = azurerm_storage_account.main.primary_blob_endpoint
}

variable "resource_group_name" { type = string }
variable "location"             { type = string }
variable "project_name"         { type = string }
variable "environment"          { type = string }
variable "log_analytics_id"     { type = string }
variable "common_tags"          { type = map(string); default = {} }
