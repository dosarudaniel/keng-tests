#!/bin/bash
#Enable 2MB hugepages.
echo 1024 | tee /sys/devices/system/node/node*/hugepages/hugepages-2048kB/nr_hugepages

# Assuming use of eth1,eth2,eth3,eth4 for DPDK in this demo
PRIMARY1="${1:-eth1}"

# controller VM management IP:
CONTROLLER_IP="${5:-10.3.147.211}"

echo $CONTROLLER_IP

echo "Using the following PRIMARY interface names: $PRIMARY1 $PRIMARY2 $PRIMARY3 $PRIMARY4"

####################################################################################
SECONDARY1="`ip -br link show master $PRIMARY1 | awk '{ print $1 }'`"
BUS_INFO1="`ethtool -i $SECONDARY1 | grep bus-info | awk '{ print $2 }'`"
MANA_MAC1="`ip -br link show master $PRIMARY1 | awk '{ print $3 }'`"

# Set MANA interfaces DOWN before starting DPDK
ip link set $PRIMARY1 down
ip link set $SECONDARY1 down

## Move synthetic channel to user mode and allow it to be used by NETVSC PMD in DPDK
DEV_UUID1=$(basename $(readlink /sys/class/net/$PRIMARY1/device))
NET_UUID1="f7615163-df3e-46c5-913f-f2d2f965ed0e"
modprobe uio_hv_generic
echo $NET_UUID1 > /sys/bus/vmbus/drivers/uio_hv_generic/new_id
echo $DEV_UUID1 > /sys/bus/vmbus/drivers/hv_netvsc/unbind
echo $DEV_UUID1 > /sys/bus/vmbus/drivers/uio_hv_generic/bind

truncate -s 0 .env
echo "BUS_INFO1=$BUS_INFO1" >> .env
echo "MANA_MAC1=$MANA_MAC1" >> .env

echo ""
echo "Content of .env file:"
cat .env

####################################################################################
# Send port MAC addresses to controller VM
truncate -s 0 .port_macs
echo "$MANA_MAC1" >> .port_macs

VM_NAME="ixia2" #"`hostname -I | awk '{print $1}'`"

# Populate the config file from controller VM
# scp .port_macs ixia@$CONTROLLER_IP:"/home/ixia/ixia-c-tests/${VM_NAME}_port_macs"
