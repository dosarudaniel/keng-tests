## Document version  
Make sure you have the latest version of this readme file by executing:
```
cd /home/ixia/ixia-c-tests
git pull
```

## VM settings
Before starting make sure that your VM has the following settings: 4 SR-IOV MANA Network adapters, 1 management interface, at least 16 CPU cores, 16GB of memory as it can be seen in the below image:    
![Topology](/configs/Keng-Agent%20VM%20settings.png "")    
    
Optional: Change the hostname of the VM on the second server executing:
```
sudo vi /etc/hostname
reboot
```

Check your management IP address by executing `ip a sh` and looking at the management interface.

### Requirements: 
On Ubuntu 22.04.02 Server VM we should already have docker, net-tools, pip3, jq and python requirements
- docker `sudo apt install docker.io`  
- ifconfig `sudo apt install net-tools`  
- pip3   `sudo apt install python3-pip`    
- jq     `sudo apt install jq`
- python requirements: `python3 -m pip install -r /home/ixia/ixia-x-tests/py/requirements.txt`

Check if SR-IOV is enabled on the VM by running: `ip a sh` to get the interface name and `ethtool -i <interface name>` to get information about interface driver.     
For example:    
```
ixia@ixia1:~/ixia-c-tests$ ethtool -i eth1
driver: hv_netvsc
version: 6.2.0-35-generic 
```
and the actual interface used by the Keng Agent traffic engine should have mana driver:
```
ixia@ixia1:~/ixia-c-tests$ ethtool -i enP11940s2
driver: mana
version: 6.2.0-35-generic
```
To double check SR-IOV, we can execute:
`lspci | grep -i Ethernet` and observe the [Microsoft Corporation Device 00ba] 
```
ixia@ixia1:~/ixia-c-tests$ lspci | grep -i Ethernet
2ea4:00:02.0 Ethernet controller: Microsoft Corporation Device 00ba
5f07:00:02.0 Ethernet controller: Microsoft Corporation Device 00ba
71f3:00:02.0 Ethernet controller: Microsoft Corporation Device 00ba
be51:00:02.0 Ethernet controller: Microsoft Corporation Device 00ba
```

## Deployment steps     
Before running the above tests we need to deploy the Keysight Elastic Network Generator and the associated traffic engines, here is the topology we want to deploy:

<img src="https://github.com/dosarudaniel/ixia-c-tests/blob/main/configs/Hyper-V%20topology.png" width="400">

On the first VM we should deploy the traffic engines and the controller. To do that execute as a root the following:
```
ssh ixia@10.3.147.212
cd ixia-c-tests/deployment/
ip a sh    # check the interface names - usually we bind eth1, eth2, eth3 and eth4
sudo bash -x setup4.sh eth1 eth2 eth3 eth4 10.3.147.211  
sudo docker-compose -f docker-compose_4TE.yaml up -d
```

On the second VM you should deploy the (TX) traffic engines, controller and license server:
```
ssh ixia@10.3.147.211
cd ixia-c-tests/deployment/
ip a sh # check the interface names - usually we bind eth1, eth2, eth3 and eth4
sudo bash -x setup4.sh eth1 eth2 eth3 eth4 10.3.147.211  
sudo docker-compose -f docker-compose_4TE.yaml up -d
cd ..
./fill_config.sh
./unidirectional_test.sh -s 1500
```

To validate that the deployment was succesful, run on VM1 :
```
CONTAINER ID   IMAGE                                                                                              COMMAND                  CREATED             STATUS             PORTS                                                                                  NAMES
03a120e73861   ghcr.io/open-traffic-generator/keng-controller:0.1.0-3                                             "./bin/controller --…"   About an hour ago   Up About an hour                                                                                          deployment_controller_1
26154ca8599a   docker-local-ixvm-lbj.artifactorylbj.it.keysight.com/athena-traffic-engine:1.6.0.101-msft-mana11   "bash -c 'sleep 3 &&…"   About an hour ago   Up About an hour                                                                                          deployment_TE2-5552_1
55ac37fe9c0a   docker-local-ixvm-lbj.artifactorylbj.it.keysight.com/athena-traffic-engine:1.6.0.101-msft-mana11   "./entrypoint.sh"        About an hour ago   Up About an hour                                                                                          deployment_TE1-5551_1
11f348a452a3   docker-local-ixvm-lbj.artifactorylbj.it.keysight.com/athena-traffic-engine:1.6.0.101-msft-mana11   "bash -c 'sleep 9 &&…"   About an hour ago   Up About an hour                                                                                          deployment_TE4-5554_1
b87aa23c567d   docker-local-ixvm-lbj.artifactorylbj.it.keysight.com/athena-traffic-engine:1.6.0.101-msft-mana11   "bash -c 'sleep 6 &&…"   About an hour ago   Up About an hour                                                                                          deployment_TE3-5553_1
fe2fa8a19c23   docker-local-athena.artifactory.it.keysight.com/keng-license-server:latest                         "./bin/licenseserver…"   About an hour ago   Up About an hour   0.0.0.0:7443->7443/tcp, :::7443->7443/tcp, 0.0.0.0:9443->9443/tcp, :::9443->9443/tcp   keng-license-server
```
You should see 4 Traffic Engines and 1 controller.

On VM1, edit the `/home/ixia/ixia-c-tests/settings.json` to match the Ip address of the second VM in the ports array - here is an example (snippet from `/home/ixia/ixia-c-tests/settings.json`). We have 4 ports per VM:
```
  "ports": [
    "10.3.147.211:5551",
    "10.3.147.211:5552",
    "10.3.147.211:5553",
    "10.3.147.211:5554",
    "10.3.147.212:5551",
    "10.3.147.212:5552",
    "10.3.147.212:5553",
    "10.3.147.212:5554"
  ],
```

## Running tests

### 4 flows tests:
To start testing on the controller VM check the help menu:
`./unidirectional_test_4_flows.sh -h` 


## Further optimizations
Higher performance and lower loss can be further achieved if the Hyper-V is fully optimized:
- CPU affinity (isolate the used CPU cores)
- Having the NIC card in the same NUMA node as the CPU cores used by the VM
- Disable hyperthreading
- BIOS settings, Hypervisor settings, Guest OS optimizations, NIC settings mentioned in this document:



