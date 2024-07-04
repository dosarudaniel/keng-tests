#!/bin/bash

name1=TE1-5551
name2=TE2-5552

keng_name=KENG-controller

setup()
{
	keng_controller_path=ghcr.io/open-traffic-generator/keng-controller:1.6.2-1

	te_path=ghcr.io/open-traffic-generator/ixia-c-traffic-engine:1.8.0.12 

	echo "Stopping old instances"
	docker stop $name1 $name2 $keng_name

	echo "Removing old instances"
	docker rm $name1 $name2 $keng_name

	echo "Creating KENG controller"
	# Start the KENG controller 
	docker run -d --name KENG-controller --network=host $keng_controller_path --accept-eula --license-servers=localhost

	echo "Creating TE1"
	# Create TE1 with port 5551

	docker run -d \
		--name TE1-5551 \
		--network host \
		--privileged \
		-v /mnt/huge:/mnt/huge \
		-v /sys/kernel/mm/hugepages:/sys/kernel/mm/hugepages \
		-v /sys/bus/pci/drivers:/sys/bus/pci/drivers \
		-v /sys/devices/system/node:/sys/devices/system/node \
		-v /dev:/dev \
		-e OPT_LISTEN_PORT=5551 \
		-e ARG_IFACE_LIST=pci@0000:86:00.0 \
		-e ARG_CORE_LIST="0 1 2" \
		$te_path #sleep infinity

	echo "Creating TE2"
	# Create TE2 with port 5552
  	docker run -d \
		--name TE2-5552 \
		--network host \
		--privileged \
		-v /mnt/huge:/mnt/huge \
		-v /sys/kernel/mm/hugepages:/sys/kernel/mm/hugepages \
		-v /sys/bus/pci/drivers:/sys/bus/pci/drivers \
		-v /sys/devices/system/node:/sys/devices/system/node \
		-v /dev:/dev \
		-e OPT_LISTEN_PORT=5552 \
		-e ARG_IFACE_LIST=pci@0000:86:00.1 \
		-e ARG_CORE_LIST="3 4 5" \
		$te_path #sleep infinity
}

clean_files() {
	rm temp/*
	rmdir temp
}

main() {
	if [ ! "$(docker ps -a | grep $name1)" ] | [ ! "$(docker ps -a | grep $name2)" ] | [ ! "$(docker ps -a | grep $keng_name)" ]; then
		setup
	fi
	
	cd ..
	mkdir temp
	./unidirectional.sh > temp/unidirectional.out
	./bidirectional.sh > temp/bidirectional.out

	average_uni_tx=$(cat temp/unidirectional.out | grep "Average total TX L2 rate" | grep -o -E '[-+]?[0-9]*\.[0-9]+|[0-9]+' | cut -d' ' -f1)
	average_uni_tx=( $average_uni_tx)
	average_uni_tx=${average_uni_tx[1]}
	echo $average_uni_tx

	average_uni_rx=$(cat temp/unidirectional.out | grep "Average total RX L2 rate" | grep -o -E '[-+]?[0-9]*\.[0-9]+|[0-9]+' | cut -d' ' -f1)
	average_uni_rx=( $average_uni_rx)
	average_uni_rx=${average_uni_rx[1]}
	echo $average_uni_rx

	average_bi_tx=$(cat temp/bidirectional.out | grep "Average total TX L2 rate" | grep -o -E '[-+]?[0-9]*\.[0-9]+|[0-9]+' | cut -d' ' -f1)
	average_bi_tx=( $average_bi_tx)
	average_bi_tx=${average_bi_tx[1]}
	echo $average_bi_tx

	average_bi_rx=$(cat temp/bidirectional.out | grep "Average total RX L2 rate" | grep -o -E '[-+]?[0-9]*\.[0-9]+|[0-9]+' | cut -d' ' -f1)
	average_bi_rx=( $average_bi_rx)
	average_bi_rx=${average_bi_rx[1]}
	echo $average_bi_rx

	clean_files
}

main "${@}"