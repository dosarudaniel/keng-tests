## Deployment steps     

Get NIC type and the PCI address using `lspci`
```
root@ixia-c-ubuntu:/home/ixia/ixia-c-tests# lspci
0000:00:00.0 Host bridge: Intel Corporation 440BX/ZX/DX - 82443BX/ZX/DX Host bridge (AGP disabled) (rev 03)
0000:00:07.0 ISA bridge: Intel Corporation 82371AB/EB/MB PIIX4 ISA (rev 01)
0000:00:07.1 IDE interface: Intel Corporation 82371AB/EB/MB PIIX4 IDE (rev 01)
0000:00:07.3 Bridge: Intel Corporation 82371AB/EB/MB PIIX4 ACPI (rev 02)
0000:00:08.0 VGA compatible controller: Microsoft Corporation Hyper-V virtual VGA
30d5:00:02.0 Ethernet controller: Mellanox Technologies MT28800 Family [ConnectX-5 Ex Virtual Function] (rev 80)
```

The pci address from the above should be passed to the traffic engine deployment scripts.
For e.g.:
```
cd /home/ixia/ixia-c-test/deployment
./tx_te_deploy.sh 30d5:00:02.0   # for the TX VM
```

On the first VM you should deploy the TX traffic engine and the controller:
```
cd /home/ixia/ixia-c-test/deployment
./tx_te_deploy.sh 30d5:00:02.0   # for the TX VM
./controller_deploy.sh
```

On the second VM you should deploy the RX traffic engine
```
cd /home/ixia/ixia-c-test/deployment
./rx_te_deploy.sh 662a:00:02.0   # for the RX VM
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



