#!/bin/bash
docker rm Ixia-c-Controller

sudo docker run -d --name Ixia-c-Controller --network=host \
ghcr.io/open-traffic-generator/licensed/ixia-c-controller:latest --accept-eula
