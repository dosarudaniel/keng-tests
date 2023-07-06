#!/bin/bash

cd /home/ixia/ixia-c-tests

echo "" > throughput_results_rfc2544_1_flow.json
python3 -m pytest ./py/test_throughput_rfc2544.py

cat throughput_results_rfc2544_1_flow.json  | jq
cat throughput_results_rfc2544_1_flow.json  | jq > tmp.json
cat tmp.json > throughput_results_rfc2544_1_flow.json
rm tmp.json

