## Deployment steps   


Get NIC type and the PCI address using `lshw -c network -businfo`
Bus info          Device      Class          Description
========================================================     
pci@30d5:00:02.0  enP12501s2  network        MT28800 Family [ConnectX-5 Ex Virtual Function]     
pci@662a:00:02.0  enP16266s3  network        MT28800 Family [ConnectX-5 Ex Virtual Function]

## Deployment
First we will allocate hugepages on each agent
```
mkdir -p /mnt/huge
mount -t hugetlbfs nodev /mnt/huge
echo 1536 > /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages
cat  /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages
```

# TX traffic engine deployment command (On TX agent)
```
sudo docker run --rm -d --net=host --privileged --cpuset-cpus "0,1,2" \
--name ixia-TE-5551-TX \
-e OPT_LISTEN_PORT=5551 \
-e ARG_IFACE_LIST="pci@30d5:00:02.0" \
-v /mnt/huge:/mnt/huge \
-v /sys/kernel/mm/hugepages:/sys/kernel/mm/hugepages \
-v /sys/bus/pci/drivers:/sys/bus/pci/drivers \
-v /sys/devices/system/node:/sys/devices/system/node \
-v /dev:/dev \
ghcr.io/open-traffic-generator/ixia-c-traffic-engine:1.6.0.35
```

# RX traffic engine deployment command (On RX agent)
```
sudo docker run --rm -d --net=host --privileged --cpuset-cpus "0,1,2" \
--name ixia-TE-5552-RX \
-e OPT_LISTEN_PORT=5552 \
-e ARG_IFACE_LIST="pci@662a:00:02.0" \
-v /mnt/huge:/mnt/huge \
-v /sys/kernel/mm/hugepages:/sys/kernel/mm/hugepages \
-v /sys/bus/pci/drivers:/sys/bus/pci/drivers \
-v /sys/devices/system/node:/sys/devices/system/node \
-v /dev:/dev \
ghcr.io/open-traffic-generator/ixia-c-traffic-engine:1.6.0.35
```

# Deployment command for KENG controller
```
sudo docker run -d --name Ixia-c-Controller --network=host \
ghcr.io/open-traffic-generator/licensed/ixia-c-controller:latest --accept-eula
```
