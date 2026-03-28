terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.90"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.47"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }

  backend "azurerm" {
    resource_group_name  = "rg-tfstate"
    storage_account_name = "stproactivetfstate"
    container_name       = "tfstate"
    key                  = "proactive-poc.terraform.tfstate"
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy    = true
      recover_soft_deleted_key_vaults = true
    }
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

provider "azuread" {}

# ─── Data Sources ─────────────────────────────────────────────────────────────

data "azurerm_client_config" "current" {}

data "azurerm_subscription" "current" {}

# ─── Resource Group ───────────────────────────────────────────────────────────

resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location

  tags = local.common_tags
}

# ─── Log Analytics Workspace ──────────────────────────────────────────────────

resource "azurerm_log_analytics_workspace" "main" {
  name                = "law-${var.project_name}-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "PerGB2018"
  retention_in_days   = var.log_retention_days

  tags = local.common_tags
}

# ─── Modules ──────────────────────────────────────────────────────────────────

module "networking" {
  source = "./modules/networking"

  resource_group_name  = azurerm_resource_group.main.name
  location             = azurerm_resource_group.main.location
  project_name         = var.project_name
  environment          = var.environment
  vnet_address_space   = var.vnet_address_space
  aks_subnet_prefix    = var.aks_subnet_prefix
  app_subnet_prefix    = var.app_subnet_prefix
  common_tags          = local.common_tags
}

module "security" {
  source = "./modules/security"

  resource_group_name    = azurerm_resource_group.main.name
  location               = azurerm_resource_group.main.location
  project_name           = var.project_name
  environment            = var.environment
  tenant_id              = data.azurerm_client_config.current.tenant_id
  object_id              = data.azurerm_client_config.current.object_id
  subscription_id        = data.azurerm_subscription.current.subscription_id
  log_analytics_id       = azurerm_log_analytics_workspace.main.id
  common_tags            = local.common_tags
}

module "storage" {
  source = "./modules/storage"

  resource_group_name  = azurerm_resource_group.main.name
  location             = azurerm_resource_group.main.location
  project_name         = var.project_name
  environment          = var.environment
  log_analytics_id     = azurerm_log_analytics_workspace.main.id
  common_tags          = local.common_tags
}

module "aks" {
  source = "./modules/aks"

  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  project_name             = var.project_name
  environment              = var.environment
  kubernetes_version       = var.kubernetes_version
  aks_subnet_id            = module.networking.aks_subnet_id
  node_count               = var.aks_node_count
  node_vm_size             = var.aks_node_vm_size
  key_vault_id             = module.security.key_vault_id
  log_analytics_id         = azurerm_log_analytics_workspace.main.id
  common_tags              = local.common_tags

  depends_on = [module.networking, module.security]
}

module "app_service" {
  source = "./modules/app_service"

  resource_group_name  = azurerm_resource_group.main.name
  location             = azurerm_resource_group.main.location
  project_name         = var.project_name
  environment          = var.environment
  app_subnet_id        = module.networking.app_subnet_id
  key_vault_id         = module.security.key_vault_id
  log_analytics_id     = azurerm_log_analytics_workspace.main.id
  common_tags          = local.common_tags

  depends_on = [module.networking, module.security]
}

# ─── Azure Monitor Action Group ───────────────────────────────────────────────

resource "azurerm_monitor_action_group" "critical" {
  name                = "ag-${var.project_name}-critical"
  resource_group_name = azurerm_resource_group.main.name
  short_name          = "critical"

  email_receiver {
    name          = "ops-team"
    email_address = var.alert_email
  }

  tags = local.common_tags
}

# ─── Locals ───────────────────────────────────────────────────────────────────

locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    Owner       = "platform-team"
    CostCenter  = "engineering"
  }
}
