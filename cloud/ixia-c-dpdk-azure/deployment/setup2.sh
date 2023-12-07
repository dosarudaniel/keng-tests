# Enable 2MB hugepages.
echo 1024 | tee /sys/devices/system/node/node*/hugepages/hugepages-2048kB/nr_hugepages

# Assuming use of eth1 for DPDK in this demo
PRIMARY="eth1"

# $ ip -br link show master eth1 
# > enP30832p0s0     UP             f0:0d:3a:ec:b4:0a <... # truncated
# grab interface name for device bound to primary
SECONDARY="`ip -br link show master $PRIMARY | awk '{ print $1 }'`"
# Get mac address for MANA interface (should match primary)
MANA_MAC="`ip -br link show master $PRIMARY | awk '{ print $3 }'`"


# $ ethtool -i enP30832p0s0 | grep bus-info
# > bus-info: 7870:00:00.0
# get MANA device bus info to pass to DPDK
BUS_INFO="`ethtool -i $SECONDARY | grep bus-info | awk '{ print $2 }'`"

# Set MANA interfaces DOWN before starting DPDK
ip link set $PRIMARY down
ip link set $SECONDARY down


## Move synthetic channel to user mode and allow it to be used by NETVSC PMD in DPDK
DEV_UUID=$(basename $(readlink /sys/class/net/$PRIMARY/device))
NET_UUID="f8615163-df3e-46c5-913f-f2d2f965ed0e"
modprobe uio_hv_generic
echo $NET_UUID > /sys/bus/vmbus/drivers/uio_hv_generic/new_id
echo $DEV_UUID > /sys/bus/vmbus/drivers/hv_netvsc/unbind
echo $DEV_UUID > /sys/bus/vmbus/drivers/uio_hv_generic/bind

# MANA single queue test
#dpdk-testpmd -l 1-3 --vdev="$BUS_INFO,mac=$MANA_MAC" -- --forward-mode=txonly --auto-start --txd=128 --rxd=128 --stats 2

# MANA multiple queue test (example assumes > 9 cores)
#dpdk-testpmd -l 1-9 --vdev="$BUS_INFO,mac=$MANA_MAC" -- --forward-mode=txonly --auto-start --nb-cores=8  --txd=128 --rxd=128 --txq=8 --rxq=8 --stats 2
