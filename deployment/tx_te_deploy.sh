
DEFAULT_PCI_ADDRESS="30d5:00:02.0"
PCI_ADDRESS=${1:-$DEFAULT_PCI_ADDRESS}

echo $PCI_ADDRESS

mkdir -p /mnt/huge
mount -t hugetlbfs nodev /mnt/huge
echo 1536 > /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages
cat  /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages



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
