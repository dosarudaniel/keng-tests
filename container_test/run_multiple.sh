#!/bin/bash

for i in 1 .. 10
do 
    ./create_docker.sh -a yes
    sleep 1
done
