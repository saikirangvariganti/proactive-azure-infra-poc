output "resource_group_name" {
  description = "Name of the deployed resource group"
  value       = azurerm_resource_group.main.name
}

output "resource_group_id" {
  description = "Resource ID of the deployed resource group"
  value       = azurerm_resource_group.main.id
}

output "aks_cluster_name" {
  description = "Name of the AKS cluster"
  value       = module.aks.cluster_name
}

output "aks_cluster_fqdn" {
  description = "FQDN of the AKS API server"
  value       = module.aks.cluster_fqdn
  sensitive   = true
}

output "aks_oidc_issuer_url" {
  description = "OIDC issuer URL for workload identity federation"
  value       = module.aks.oidc_issuer_url
}

output "key_vault_uri" {
  description = "URI of the deployed Key Vault"
  value       = module.security.key_vault_uri
}

output "key_vault_id" {
  description = "Resource ID of the deployed Key Vault"
  value       = module.security.key_vault_id
}

output "storage_account_name" {
  description = "Name of the deployed storage account"
  value       = module.storage.storage_account_name
}

output "storage_account_id" {
  description = "Resource ID of the storage account"
  value       = module.storage.storage_account_id
}

output "vnet_id" {
  description = "Resource ID of the Virtual Network"
  value       = module.networking.vnet_id
}

output "vnet_name" {
  description = "Name of the Virtual Network"
  value       = module.networking.vnet_name
}

output "aks_subnet_id" {
  description = "Resource ID of the AKS subnet"
  value       = module.networking.aks_subnet_id
}

output "app_service_url" {
  description = "Default hostname of the App Service"
  value       = module.app_service.app_service_url
}

output "log_analytics_workspace_id" {
  description = "Resource ID of the Log Analytics workspace"
  value       = azurerm_log_analytics_workspace.main.id
}

output "action_group_id" {
  description = "Resource ID of the critical alert action group"
  value       = azurerm_monitor_action_group.critical.id
}
