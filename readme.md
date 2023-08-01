## Document version  
Make sure you have the latest version of this readme file by executing:
```
cd /home/ixia/ixia-c-tests
git pull
```

## VM settings
Before starting make sure that your VM has the following settings: 4 SR-IOV Mellanox Network adapters, 1 management interface, at least 16 CPU cores, 16GB of memory as it can be seen in the below image:    
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
root@keng-agent:/home/ixia/ixia-c-tests# ethtool -i eth1
driver: hv_netvsc  
```
and the actual interface used by the Keng Agent traffic engine should have mlx5_core driver:
```
root@keng-agent:/home/ixia/ixia-c-tests# ethtool -i enP12501s2
driver: mlx5_core
version: 5.15.0-76-generic
```
To double check SR-IOV, we can execute:
`lspci | grep -i Ethernet` and observe the [ConnectX-5 Ex Virtual Function] 
```
root@keng-agent:/home/ixia/ixia-c-tests# lspci | grep -i Ethernet
30d5:00:02.0 Ethernet controller: Mellanox Technologies MT28800 Family [ConnectX-5 Ex Virtual Function] (rev 80)
5850:00:02.0 Ethernet controller: Mellanox Technologies MT28800 Family [ConnectX-5 Ex Virtual Function] (rev 80)
aeca:00:02.0 Ethernet controller: Mellanox Technologies MT28800 Family [ConnectX-5 Ex Virtual Function] (rev 80)
ea49:00:02.0 Ethernet controller: Mellanox Technologies MT28800 Family [ConnectX-5 Ex Virtual Function] (rev 80)
```


## Deployment steps     
Before running the above tests we need to deploy the Keysight Elastic Network Generator and the associated traffic engines, here is the topology we want to deploy:

<img src="https://github.com/dosarudaniel/ixia-c-tests/blob/main/configs/Hyper-V%20topology.png" width="400">

On the first VM we should deploy the traffic engines and the controller. To do that execute as a root the following:
```
sudo su
cd /home/ixia/ixia-c-test/deployment
./te_deploy.sh
./controller_deploy.sh
```

On the second VM you should deploy the (RX) traffic engines, run as a root:
```
sudo su
cd /home/ixia/ixia-c-test/deployment
./te_deploy.sh
```

To validate that the deployment was succesful, run on VM1 :
```
root@keng-agent:/home/ixia/ixia-c-tests/deployment# docker ps
CONTAINER ID   IMAGE                                                              COMMAND                  CREATED         STATUS         PORTS     NAMES
5ac4e8831d8e   ghcr.io/open-traffic-generator/licensed/ixia-c-controller:latest   "./bin/controller --…"   4 seconds ago   Up 3 seconds             Ixia-c-Controller
659bedecaefa   ghcr.io/open-traffic-generator/ixia-c-traffic-engine:1.6.0.35      "./entrypoint.sh"        4 hours ago     Up 4 hours               TE1-5551
bbfa1015f3f7   ghcr.io/open-traffic-generator/ixia-c-traffic-engine:1.6.0.35      "./entrypoint.sh"        46 hours ago    Up 46 hours              TE4-5554
6117dd317906   ghcr.io/open-traffic-generator/ixia-c-traffic-engine:1.6.0.35      "./entrypoint.sh"        46 hours ago    Up 46 hours              TE3-5553
296e75f75bea   ghcr.io/open-traffic-generator/ixia-c-traffic-engine:1.6.0.35      "./entrypoint.sh"        46 hours ago    Up 46 hours              TE2-5552
```
You should see 4 Traffic Engines and 1 controller.

On VM1, edit the `/home/ixia/ixia-c-tests/settings.json` to match the Ip address of the second VM in the ports array - here is an example (snippet from `/home/ixia/ixia-c-tests/settings.json`). We have 4 ports per VM:
```
  "ports": [
    "localhost:5551",
    "localhost:5552",
    "localhost:5553",
    "localhost:5554",
    "192.168.0.56:5551",
    "192.168.0.56:5552",
    "192.168.0.56:5553",
    "192.168.0.56:5554"
  ],
```

For each test, we need to also edit the config files associated with it:
```
cd /home/ixia/ixia-c-tests/config
```
For the unidirectional test, edit the `/home/ixia/ixia-c-tests/config/ipv4_unidirectional.json` file:
- Port location: edit the "VM2-TE*" ports locations to match the IP address written in settings.json (as mentioned above).
- MAC addresses: edit the source and destination MAC addresses of the packets.
To get the source MAC address run `ifconfig` on VM1 and look at the first `enP*` interface:
```
enP12501s2: flags=6979<UP,BROADCAST,RUNNING,PROMISC,ALLMULTI,SLAVE,MULTICAST>  mtu 9000
        ether 00:15:5d:a4:08:25  txqueuelen 1000  (Ethernet)
```
The source MAC address is 00:15:5d:a4:08:25.

To get the destination MAC address run `ifconfig` on VM2 and look at the first `enP*` interface:
```
enP22413s4: flags=6979<UP,BROADCAST,RUNNING,PROMISC,ALLMULTI,SLAVE,MULTICAST>  mtu 9000
        ether 00:15:5d:a4:08:3b  txqueuelen 1000  (Ethernet)
```
The source MAC address is 00:15:5d:a4:08:3b.

Optional: Change the number of packets to be sent in the `/home/ixia/ixia-c-tests/config/ipv4_unidirectional.json` config file:
```
            "duration": {
                "choice": "fixed_packets",
                "fixed_packets": {
                    "packets": 1000000
                }
            },
```

For multiple flows tests you can easily change the frame size, number of packet to be sent for all the flow from the `./py/test_ipv4_unidirectional_4_flows.py` file by changing these variables:
``` 
FRAME_SIZE = 9000
PACKETS = 1000000
```

## Running tests
The ixia-c-tests repository contains 6 scripts:
- `unidirectional_test.sh` - runs single flow unidirectional traffic
- `unidirectional_test_multiple_flows.sh`
Computes the maximum throughput for 0 packet loss using the RFC2544 procedure.
- `rfc2544_test_multiple_flows.sh`
- `rfc2544_test.sh`

### Single flow tests:
To start testing on the first VM:
`/home/ixia/ixia-c-test/unidirectional_test.sh`
To change the frame size, edit this file `/home/ixia/ixia-c-test/config/ipv4_unidirectional.json`

`/home/ixia/ixia-c-test/rfc2544_test.sh`
To change the PACKET_LOSS_TOLERANCE or the tested frame sizes (the `packet_sizes` array) edit the python test: `/home/ixia/ixia-c-test/py/test_throughput_rfc2544.py`

### Multiple flows tests:
To start testing on the first VM:
`/home/ixia/ixia-c-testunidirectional_test_multiple_flows.sh`
To change the frame size, edit this file `/home/ixia/ixia-c-test/py/test_ipv4_unidirectional_4_flows.py``

`/home/ixia/ixia-c-test/rfc2544_test_multiple_flows.sh`
To change the PACKET_LOSS_TOLERANCE or the tested frame sizes (the `packet_sizes` array) edit the python test: `/home/ixia/ixia-c-test/py/test_throughput_rfc2544_multiple_flows.py`


## Further optimizations
Higher performance and lower loss can be further achieved if the Hyper-V is fully optimized:
- CPU affinity (isolate the used CPU cores)
- Having the NIC card in the same NUMA node as the CPU cores used by the VM
- Disable hyperthreading
- BIOS settings, Hypervisor settings, Guest OS optimizations, NIC settings mentioned in this document:
https://fast.dpdk.org/doc/perf/DPDK_22_07_NVIDIA_Mellanox_NIC_performance_report.pdf 



