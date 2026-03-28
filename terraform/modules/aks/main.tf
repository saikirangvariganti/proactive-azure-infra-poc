resource "azurerm_kubernetes_cluster" "main" {
  name                = "aks-${var.project_name}-${var.environment}"
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = "${var.project_name}-${var.environment}"
  kubernetes_version  = var.kubernetes_version

  sku_tier = var.environment == "prod" ? "Standard" : "Free"

  # System node pool
  default_node_pool {
    name                 = "system"
    node_count           = var.node_count
    vm_size              = var.node_vm_size
    vnet_subnet_id       = var.aks_subnet_id
    os_disk_size_gb      = 100
    os_disk_type         = "Managed"
    type                 = "VirtualMachineScaleSets"
    enable_auto_scaling  = true
    min_count            = 1
    max_count            = 5
    node_labels = {
      "nodepool-type" = "system"
      "environment"   = var.environment
    }
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin    = "azure"
    network_policy    = "calico"
    load_balancer_sku = "standard"
    outbound_type     = "loadBalancer"
    service_cidr      = "10.96.0.0/16"
    dns_service_ip    = "10.96.0.10"
  }

  oms_agent {
    log_analytics_workspace_id = var.log_analytics_id
  }

  key_vault_secrets_provider {
    secret_rotation_enabled  = true
    secret_rotation_interval = "2m"
  }

  azure_policy_enabled             = true
  local_account_disabled           = false
  role_based_access_control_enabled = true

  oidc_issuer_enabled       = true
  workload_identity_enabled = true

  maintenance_window {
    allowed {
      day   = "Sunday"
      hours = [2, 3, 4]
    }
  }

  tags = var.common_tags
}

# User node pool for application workloads
resource "azurerm_kubernetes_cluster_node_pool" "user" {
  name                  = "user"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.main.id
  vm_size               = var.node_vm_size
  node_count            = var.node_count
  vnet_subnet_id        = var.aks_subnet_id
  os_disk_size_gb       = 128
  mode                  = "User"
  enable_auto_scaling   = true
  min_count             = 1
  max_count             = 10

  node_labels = {
    "nodepool-type" = "user"
    "environment"   = var.environment
    "workload"      = "application"
  }

  node_taints = []

  tags = var.common_tags
}

# RBAC: grant AKS managed identity access to Key Vault
resource "azurerm_role_assignment" "aks_keyvault" {
  scope                = var.key_vault_id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_kubernetes_cluster.main.kubelet_identity[0].object_id
}
