locals {
	AgentVmSize = var.AgentVmSize
	Agent1InstanceId = "agent1"
	Agent1Eth1IpAddresses = [ "10.0.2.12", "10.0.2.13" ]
	Agent2Eth0IpAddress = "10.0.10.12"
	Agent2Eth1IpAddresses = [ "10.0.2.22", "10.0.2.23" ]
	Agent2InstanceId = "agent2"
	AppTag = "ubuntu"
	AppVersion = "2204-lts"
	ClientId = var.ClientId
	ClientSecret = var.ClientSecret
	DockerComposeServices = yamldecode(file("../docker-compose.yaml"))["services"]
	GitRepoConfigPath = "${local.GitRepoExecPath}/configs"
	GitRepoExecPath = "cloud/ixia-c-netvsc-azure"
	GitRepoDeployPath = "${local.GitRepoExecPath}/deployment/"
	GitRepoName = var.GitRepoName
	GitRepoUrl = var.GitRepoUrl
	KengControllerImage = local.KengControllerService["image"]
	KengControllerService = local.DockerComposeServices["controller"]
	KengTrafficEngineImage = local.KengTrafficEngineService["image"]
	KengTrafficEngineService = local.DockerComposeServices["TE1-5551"]
	Preamble = "${local.UserLoginTag}-${local.AppTag}-${local.AppVersion}"
	PublicSecurityRuleSourceIpPrefixes = var.PublicSecurityRuleSourceIpPrefixes
	ResourceGroupLocation = var.ResourceGroupLocation
	ResourceGroupName = var.ResourceGroupName
	SshKeyAlgorithm = "RSA"
	SshKeyName = "${local.Preamble}-ssh-key"
	SshKeyRsaBits = "4096"
	SubscriptionId = var.SubscriptionId
	TenantId = var.TenantId
	UserEmailTag = var.UserEmailTag
	UserLoginTag = var.UserLoginTag
	UserProjectTag = var.UserProjectTag
}