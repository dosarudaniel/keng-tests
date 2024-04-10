#!/bin/bash

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <interface1> [interface2 interface3 interface4]"
  exit
fi

default_controller_ip="10.38.163.161"
interfaces=()

if [ -n "$CONTROLLER_IP" ]; then
  controller_ip="$CONTROLLER_IP"
  echo "Controller IP (from environment variable): $controller_ip"
else
  controller_ip="$default_controller_ip"
  echo "Controller IP (default): $controller_ip"
fi

interfaces+=("$1")
echo "Interface 1: ${interfaces[0]}"

# Extract additional interfaces (if provided) and store them in the array
echo "Using the following PRIMARY interface names:"

for ((i = 2; i <= $#; i++)); do
  interfaces+=("${!i}")
  echo "Interface $i: ${interfaces[$((i-1))]}"
done

# Print all interfaces in the array
echo "All interfaces provided: ${interfaces[@]}"

# Clean up .env and .port_macs files
truncate -s 0 .env
truncate -s 0 .port_macs 


# Allocate 2MB hugepages: 
NR_OF_HUGEPAGES=$((1024 * $#)) 
echo $NR_OF_HUGEPAGES | tee /sys/devices/system/node/node*/hugepages/hugepages-2048kB/nr_hugepages 

echo "Using the following controller IP: $CONTROLLER_IP" 
 
for index in "${!interfaces[@]}"; do 
    PRIMARY="${interfaces[index]}" 
    SECONDARY="`ip -br link show master $PRIMARY | awk '{ print $1 }'`" 
    BUS_INFO="`ethtool -i $SECONDARY | grep bus-info | awk '{ print $2 }'`" 
    MANA_MAC="`ip -br link show master $PRIMARY | awk '{ print $3 }'`" 
 
    # Set MANA interfaces DOWN before starting DPDK 
    ip link set $PRIMARY down 
    ip link set $SECONDARY down 

    ## Move synthetic channel to user mode and allow it to be used by NETVSC PMD in DPDK 
    DEV_UUID=$(basename $(readlink /sys/class/net/$PRIMARY/device)) 
    echo $DEV_UUID 
    NET_UUID=${NET_UUIDS[${index}]} #"f8615163-df3e-46c5-913f-f2d2f965ed0e" 
    modprobe uio_hv_generic 
    echo $NET_UUID > /sys/bus/vmbus/drivers/uio_hv_generic/new_id 
    echo $DEV_UUID > /sys/bus/vmbus/drivers/hv_netvsc/unbind 
    echo $DEV_UUID > /sys/bus/vmbus/drivers/uio_hv_generic/bind 

    echo "BUS_INFO$((index+1))=$BUS_INFO" >> .env 
    echo "MANA_MAC$((index+1))=$MANA_MAC" >> .env 
    echo "$MANA_MAC" >> .port_macs 
done 

echo "Content of .env file:" 
cat .env 
echo "Content of .port_macs file:" 
cat .port_macs 