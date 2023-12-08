data "azurerm_subscription" "current" {}

data "azurerm_subscriptions" "available" {}

data "cloudinit_config" "init_cli" {
	gzip = false
	base64_encode = false
	part {
		content_type = "text/cloud-config"
		content = templatefile("cloud-init.yml", {
			GitRepoDeployPath: local.GitRepoDeployPath
			GitRepoExecPath: local.GitRepoExecPath
			GitRepoName: local.GitRepoName
			GitRepoUrl: local.GitRepoUrl
			KengContainerRegistry: local.KengContainerRegistry
			KengContainerRegistryToken: local.KengContainerRegistryToken
			KengContainerRegistryUser: local.KengContainerRegistryUser
			KengControllerImage: local.KengControllerImage
			KengLicenseImage: local.KengLicenseImage
			KengTrafficEngineImage: local.KengTrafficEngineImage
			UserName: local.AppTag
		})
	}
	part {
		filename = "script-001"
		content_type = "text/cloud-config"
		content = templatefile("cloud-init.azure.yml", {
			Agent1Eth1PrivateIpAddresses: local.Agent1Eth1IpAddresses
			Agent2Eth1PrivateIpAddresses: local.Agent2Eth1IpAddresses
			ClientId: local.ClientId
			ClientSecret: local.ClientSecret
			GitRepoConfigPath: local.GitRepoConfigPath
			GitRepoExecPath: local.GitRepoExecPath
			GitRepoName: local.GitRepoName
			TenantId: local.TenantId
			UserName: local.AppTag
		})
	}	
}