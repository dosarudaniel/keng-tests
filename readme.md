Requirements:
- docker `sudo apt install docker.io`    
- pip3   `sudo apt install python3-pip`    
- jq     `sudo apt install jq`
- python requirements: `python3 -m pip install -r py/requirements.txt`
` 

The ixia-c-tests directory containes 6 scripts that runs different tests:
- `unidirectional_test.sh` - runs single flow unidirectional traffic
- `unidirectional_test_multiple_flows.sh`
- `bidirectional_test.sh`
- `bidirectional_test_multiple_flows.sh`
Computes the maximum throughput for 0 packet loss using the RFC2544 procedure.
- `rfc2544_test_multiple_flows.sh`
- `rfc2544_test.sh`

## Deployment steps     

Before running the above tests we need to deploy the Keysight Elastic Network Generator and the associated traffic engines, here is the topology we want to deploy:
![Topology](/configs/Hyper-V%20topology.png "Text to show on mouseover")

On the first VM we should deploy the traffic engines and the controller. To do that execute as a root the following:
```
cd /home/ixia/ixia-c-test/deployment
./te_deploy.sh
./controller_deploy.sh
```

On the second VM you should deploy the (RX) traffic engines
```
cd /home/ixia/ixia-c-test/deployment
./te_deploy.sh
```

To start testing on the first VM:
`/home/ixia/ixia-c-test/unidirectional_test.sh`
To change the frame size, edit this file `/home/ixia/ixia-c-test/config/ipv4_unidirectional.json`

`/home/ixia/ixia-c-test/bidirectional_test.sh`
To change the frame size, edit this file `/home/ixia/ixia-c-test/config/ipv4_bidirectional.json`

`/home/ixia/ixia-c-test/rfc2544_test.sh`
To change the PACKET_LOSS_TOLERANCE or the tested frame sizes (the `packet_sizes` array) edit the python test: `/home/ixia/ixia-c-test/py/test_throughput_rfc2544.py`


Higher performance and lower loss can be further achieved if the Hyper-V is fully optimized:
- CPU affinity (isolate the used CPU cores)
- Having the NIC card in the same NUMA node as the CPU cores used by the VM
- Disable hyperthreading
- BIOS settings, Hypervisor settings, Guest OS optimizations, NIC settings mentioned in this document:
https://fast.dpdk.org/doc/perf/DPDK_22_07_NVIDIA_Mellanox_NIC_performance_report.pdf 



