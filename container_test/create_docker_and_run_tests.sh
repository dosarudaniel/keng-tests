#!/bin/bash

name1=TE1-5551
name2=TE2-5552

keng_name=KENG-controller
keng_license_server_name=keng-license-server

# Default values for frame_size, duration, line_rate_per_flow and direction

duration=''
frame_size=''
line_rate_per_flow=''
direction=''

all_value=0

arguments=""

frame_sizes=(64 128 256 512 1024 1518 4096 9000)

pci1="0000:86:00.0"
pci2="0000:86:00.1"

help() {
	echo "-s <frame_size> -- int - seconds"
	echo "-t <duration> -- int - bytes"
	echo "-l <line_rate_per_flow> -- float - percentage"
	echo "-d <direction> -- upstream/downstream"
}

while getopts "hs:t:l:d:a:" option; do
    case $option in
        h) # display Help
            help
            exit;;
        s) #frame size
            echo "Frame size: $OPTARG"
            frame_size=$OPTARG
            ;;
        t) #duration
            echo "Duration: $OPTARG"
            duration=$OPTARG
            ;;
        l) #line_rate_per_flow
            echo "Line rate per flow: $OPTARG"
            line_rate_per_flow=$OPTARG 
            ;;
        d) #direction
            echo "Direction: $OPTARG"
            direction=$OPTARG 
            ;;
		a) #all frame sizes
			echo "All frame sizes $OPTARG"
			all_value=1
			;;
    esac
done


build_arguments() {
	arguments=""
	if [ ! -z "$frame_size" ]
	then
		arguments+=" -s $frame_size" 
	fi

	if [ ! -z "$duration" ]
	then
		arguments+=" -t $duration"
	fi

	if [ ! -z "$line_rate_per_flow" ]
	then
		arguments+=" -l $line_rate_per_flow"
	fi

	if [ ! -z "$direction" ]
	then
		arguments+=" -d $direction"
	fi
}

setup()
{
	keng_controller_path=ghcr.io/open-traffic-generator/keng-controller:1.6.2-1
	keng_license_server_path=ghcr.io/open-traffic-generator/keng-license-server
	te_path=ghcr.io/open-traffic-generator/ixia-c-traffic-engine:1.8.0.12 

	echo "Stopping old instances"
	docker stop $name1 $name2 $keng_name $keng_license_server_name

	echo "Removing old instances"
	docker rm $name1 $name2 $keng_name $keng_license_server_name

	echo "Creating KENG license server"
	docker run -d --name keng-license-server --restart always -p 7443:7443 -p 9443:9443 $keng_license_server_path --accept-eula

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
		-e ARG_IFACE_LIST=pci@$pci1 \
		-e ARG_CORE_LIST="0 1 2" \
		$te_path # sleep infinity

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
		-e ARG_IFACE_LIST=pci@$pci2 \
		-e ARG_CORE_LIST="3 4 5" \
		$te_path # sleep infinity

  	# echo "Creating TE3"
	# # Create TE3 with port 5553
  	# docker run -d \
	#	--name TE3-5553 \
	#	--network host \
	#	--privileged \
	#	-v /mnt/huge:/mnt/huge \
	#	-v /sys/kernel/mm/hugepages:/sys/kernel/mm/hugepages \
	#	-v /sys/bus/pci/drivers:/sys/bus/pci/drivers \
	#	-v /sys/devices/system/node:/sys/devices/system/node \
	#	-v /dev:/dev \
	#	-e OPT_LISTEN_PORT=5553 \
	#	-e ARG_IFACE_LIST=pci@$pci2 \
	#	-e ARG_CORE_LIST="6 7 8" \
	#	$te_path # sleep infinity

  	# echo "Creating TE4"
	# # Create TE4 with port 5554
  	# docker run -d \
	#	--name TE4-5554 \
	#	--network host \
	#	--privileged \
	#	-v /mnt/huge:/mnt/huge \
	#	-v /sys/kernel/mm/hugepages:/sys/kernel/mm/hugepages \
	#	-v /sys/bus/pci/drivers:/sys/bus/pci/drivers \
	#	-v /sys/devices/system/node:/sys/devices/system/node \
	#	-v /dev:/dev \
	#	-e OPT_LISTEN_PORT=5554 \
	#	-e ARG_IFACE_LIST=pci@$pci2 \
	#	-e ARG_CORE_LIST="9 10 11" \
	#	$te_path # sleep infinity
}

clean_files() {
	rm temp/*
	rmdir temp
}

unidirectional_run() {
	build_arguments
	echo "unidirectional.sh $arguments"
	bash unidirectional.sh $arguments > temp/unidirectional.out

	average_uni_tx=$(cat temp/unidirectional.out | grep "Average total TX L2 rate" | grep -o -E '[-+]?[0-9]*\.[0-9]+|[0-9]+' | cut -d' ' -f1)
	average_uni_tx=( $average_uni_tx)
	average_uni_tx=${average_uni_tx[1]}

	average_uni_rx=$(cat temp/unidirectional.out | grep "Average total RX L2 rate" | grep -o -E '[-+]?[0-9]*\.[0-9]+|[0-9]+' | cut -d' ' -f1)
	average_uni_rx=( $average_uni_rx)
	average_uni_rx=${average_uni_rx[1]}


	echo "$frame_size,$average_uni_tx,$average_uni_rx" >> ./container_test/uni.csv
	
	echo "$frame_size,$average_uni_tx,$average_uni_rx"
}

bidirectional_run() {
	build_arguments
	echo "bidirectional.sh $arguments"
	bash bidirectional.sh $arguments > temp/bidirectional.out
	
	average_bi_tx=$(cat temp/bidirectional.out | grep "Average total TX L2 rate" | grep -o -E '[-+]?[0-9]*\.[0-9]+|[0-9]+' | cut -d' ' -f1)
	average_bi_tx=( $average_bi_tx)
	average_bi_tx=${average_bi_tx[1]}

	average_bi_rx=$(cat temp/bidirectional.out | grep "Average total RX L2 rate" | grep -o -E '[-+]?[0-9]*\.[0-9]+|[0-9]+' | cut -d' ' -f1)
	average_bi_rx=( $average_bi_rx)
	average_bi_rx=${average_bi_rx[1]}

	echo "$frame_size,$average_bi_tx,$average_bi_rx" >> ./container_test/bi.csv

	echo "$frame_size,$average_bi_tx,$average_bi_rx"
}

main() {
	sudo ../deployment/setup.sh

	cpu_model=$(lscpu | grep "Model name")
	cpu_model="${cpu_model:20}"

	nic=$(lspci | grep ${pci1:5})
	nic=${nic:8}

	os=$(lsb_release -a | grep "Description")
	os="${os:13}"

	if [ ! "$(docker ps | grep $name1)" ] || [ ! "$(docker ps | grep $name2)" ] || [ ! "$(docker ps | grep $keng_name)" ] || [ ! "$(docker ps | grep $keng_license_server_name)" ]; then
		echo "Creating instances"
		setup
	fi

	if ! test -f ./uni.csv; then
		touch uni.csv
		echo $cpu_model > uni.csv
		echo $os >> uni.csv
		echo $nic >> uni.csv
		echo "FrameSize,TX,RX" >> uni.csv
	fi

	if ! test -f ./bi.csv; then
		touch bi.csv
		echo $cpu_model > bi.csv
		echo $os >> bi.csv
		echo $nic >> bi.csv
		echo "FrameSize,TX,RX" >> bi.csv
	fi

	cd ..
	mkdir temp

	if [ $all_value -eq 1 ]; then
		for val in ${frame_sizes[@]}; do
			frame_size=$val
			unidirectional_run
		done
	else
		unidirectional_run
	fi

	echo "Sleep"
	sleep 1

	if [ $all_value -eq 1 ]; then
		for val in ${frame_sizes[@]}; do
			frame_size=$val
			bidirectional_run
		done
	else
		bidirectional_run
	fi
	
	clean_files
}

main "${@}"

