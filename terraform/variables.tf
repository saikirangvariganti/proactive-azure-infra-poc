variable "resource_group_name" {
  description = "Name of the Azure resource group"
  type        = string
  default     = "rg-proactive-poc"
}

variable "location" {
  description = "Azure region for all resources"
  type        = string
  default     = "uksouth"

  validation {
    condition     = contains(["uksouth", "ukwest", "westeurope", "northeurope", "eastus", "eastus2"], var.location)
    error_message = "Location must be one of the approved Azure regions."
  }
}

variable "project_name" {
  description = "Short project identifier used in resource names"
  type        = string
  default     = "proactive-poc"

  validation {
    condition     = length(var.project_name) <= 20 && can(regex("^[a-z0-9-]+$", var.project_name))
    error_message = "project_name must be lowercase alphanumeric with hyphens, max 20 chars."
  }
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be one of: dev, staging, prod."
  }
}

variable "kubernetes_version" {
  description = "Kubernetes version for AKS cluster"
  type        = string
  default     = "1.28.5"
}

variable "aks_node_count" {
  description = "Initial node count for the AKS default node pool"
  type        = number
  default     = 2

  validation {
    condition     = var.aks_node_count >= 1 && var.aks_node_count <= 10
    error_message = "aks_node_count must be between 1 and 10."
  }
}

variable "aks_node_vm_size" {
  description = "VM size for AKS nodes"
  type        = string
  default     = "Standard_D2s_v3"
}

variable "vnet_address_space" {
  description = "CIDR block for the Virtual Network"
  type        = string
  default     = "10.10.0.0/16"
}

variable "aks_subnet_prefix" {
  description = "CIDR prefix for AKS subnet"
  type        = string
  default     = "10.10.1.0/24"
}

variable "app_subnet_prefix" {
  description = "CIDR prefix for App Service subnet"
  type        = string
  default     = "10.10.2.0/24"
}

variable "log_retention_days" {
  description = "Log Analytics workspace retention in days"
  type        = number
  default     = 30

  validation {
    condition     = contains([7, 14, 30, 60, 90, 180, 365], var.log_retention_days)
    error_message = "log_retention_days must be one of: 7, 14, 30, 60, 90, 180, 365."
  }
}

variable "alert_email" {
  description = "Email address for Azure Monitor alert notifications"
  type        = string
  default     = "ops-team@proactive-poc.com"
}
