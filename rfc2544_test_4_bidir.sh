#!/bin/bash

cd /home/ixia/ixia-c-tests

echo "" > throughput_results_rfc2544_4_bidir.json
python3 -m pytest ./py/test_throughput_rfc2544_4_bidir.py

cat throughput_results_rfc2544_4_bidir.json  | jq
cat throughput_results_rfc2544_4_bidir.json  | jq > tmp.json
cat tmp.json > throughput_results_rfc2544_4_bidir.json
rm tmp.json
