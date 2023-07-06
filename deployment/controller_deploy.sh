#!/bin/bash

# Remove an old docker container with the same name if existing
docker rm Ixia-c-Controller

# Deploy the KENG controller
sudo docker run -d --name Ixia-c-Controller --network=host \
ghcr.io/open-traffic-generator/licensed/ixia-c-controller:latest --accept-eula
