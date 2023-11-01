data "azurerm_subscription" "current" {}

data "azurerm_subscriptions" "available" {}

data "cloudinit_config" "init_cli" {
	gzip = false
	base64_encode = false
	part {
		content_type = "text/cloud-config"
		content = templatefile("cloud-init.yml", {
			GitRepoName: local.GitRepoName
			GitRepoUrl: local.GitRepoUrl
			KengControllerImage: local.KengControllerImage
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
			GitRepoName: local.GitRepoName
			TenantId: local.TenantId
			UserName: local.AppTag
		})
	}	
}