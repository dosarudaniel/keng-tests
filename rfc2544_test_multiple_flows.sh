#!/bin/bash

cd /home/ixia/ixia-c-tests

echo "" > throughput_results_rfc2544_4_flows.json  # clean old results

python3 -m pytest ./py/test_throughput_rfc2544_multiple_flows.py

cat throughput_results_rfc2544_4_flows.json  | jq
cat throughput_results_rfc2544_4_flows.json  | jq > tmp.json
cat tmp.json > throughput_results_rfc2544_4_flows.json
rm tmp.json

