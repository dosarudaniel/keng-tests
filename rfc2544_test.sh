#!/bin/bash

cd /home/ixia/ixia-c-tests

python3 -m pytest ./py/test_throughput_rfc2544.py

cat throughput_results.json  | jq
