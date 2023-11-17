# Ixia-c traffic engine single test subnet setup on Amazon Web Services with DPDK

## Overview
This is a public cloud lab where [Ixia-c](https://github.com/open-traffic-generator/ixia-c) has two traffic ports connected within a single subnet of an AWS VPC.
The environment is deployed using [Terraform](https://www.terraform.io/) and [Cloud-Init](https://cloud-init.io/) is used to configure the application and traffic engines.
Performance improvements are enabled through [DPDK](https://www.dpdk.org/) support.
Once the lab is up, a Python script is used to request Ixia-c to generate traffic and report statistics.

![Diagram](./diagram.png)

## Prerequisites

* [Terraform](https://www.terraform.io/)


## Deploy Ixia-c lab using Terraform

1. Uncomment all lines in the required variables file and replace values to match your particular environment.

```
cd ./deployment/Terraform
nano terraform.required.auto.tfvars
```

2. Initialize Terraform environment and apply the execution plan.
 
```
terraform init
terraform apply -auto-approve
```

3. Make note of the 'public_dns' value for 'Agent1Eth0ElasticIp' in the 'Outputs:' section upon successful apply.

```
Apply complete! Resources: 42 added, 0 changed, 0 destroyed.

Outputs:

Agent1Eth0ElasticIp = {
  "public_dns" = "1-1-1-1-1.compute-1.amazonaws.com"
  "public_ip" = "1.1.1.1"
}
```

4. Output the SSH key pair associated with the AWS instances and save the private_key_pem material for connecting with your ssh client.

```
terraform output SshKey
nano ~/.ssh/SshKey.pem
ssh -i ~/.ssh/SshKey.pem ec2-1-1-1-1.compute-1.amazonaws.com
```

3. Make sure you have application and traffic containers running:

```
docker ps
```

## Execute Python test case to generate traffic between AWS instances

1. Initialize Python virtual environment

```
source ./venv/bin/activate
```

2. Run flows via snappi script, reporting flow metrics

```Shell
./rfc2544_test_n_flows.sh -s 9000
```


## Destroy the lab

To destroy the lab, exit the ssh session and destroy the Terraform deployment

```
terraform destroy -auto-approve
```