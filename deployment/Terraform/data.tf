data "aws_region" "current" {}

data "aws_availability_zones" "available" {
	state = "available"
}

data "cloudinit_config" "init_cli" {
	gzip = true
	base64_encode = true
	part {
		content_type = "text/cloud-config"
		content = templatefile("cloud_init.yml", {
			GitRepoName: local.GitRepoName
			GitRepoUrl: local.GitRepoUrl
			KengContainerRegistry: local.KengContainerRegistry
			KengContainerRegistryToken: local.KengContainerRegistryToken
			KengContainerRegistryUser: local.KengContainerRegistryUser
			KengControllerImage: local.KengControllerImage
			KengTrafficEngineImage: local.KengTrafficEngineImage
			UserName: local.AppTag
		})
	}	
	part {
		content_type = "text/x-shellscript"
		content = templatefile("cloud-init.sh", {
			Agent1Eth1PrivateIpAddresses: local.Agent1Eth1PrivateIpAddresses
			Agent1Eth2PrivateIpAddresses: local.Agent1Eth2PrivateIpAddresses
			Agent1Eth3PrivateIpAddresses: local.Agent1Eth3PrivateIpAddresses
			Agent2Eth1PrivateIpAddresses: local.Agent2Eth1PrivateIpAddresses
			Agent2Eth2PrivateIpAddresses: local.Agent2Eth2PrivateIpAddresses
			Agent2Eth3PrivateIpAddresses: local.Agent2Eth3PrivateIpAddresses
			AwsMetadataServerUrl: local.AwsMetadataServerUrl
			GitRepoName: local.GitRepoName
			GitRepoUrl: local.GitRepoUrl
			UserName: local.AppTag
		})
	}	
}