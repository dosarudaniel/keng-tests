import utils
import pytest
import time
import json

THEORETICAL_MAX_LINK_SPEED = 100   #  Gbps
PACKET_LOSS_TOLERANCE      = 0.0   # percent
NO_STEPS                   = 13 
TRIAL_RUN_TIME             = 5  # seconds
FINAL_RUN_TIME             = 60 # seconds
TEST_GAP_TIME              = 1  # seconds
RESULTS_FILE_PATH          = "./throughput_results.json"


@pytest.mark.performance
def test_throughput_rfc2544(api):
    """
    RFC-2544 Throughput determination test
    """
    cfg = utils.load_test_config(api, 'throughput_rfc2544.json', apply_settings=True)

    packet_sizes = [64, 128, 256, 512, 768, 1024, 1280, 1518, 9000]
    # packet_sizes = [64, 512, 1518, 9000]
    # packet_sizes = [9000]

    results = {}
    
    expected_runtime = len(packet_sizes) * ((NO_STEPS-1) * 6 + 62)
    print("-" * 50)
    print("\n\n This is a throughput test (based on RFC-2544 procedure). The expected runtime is {}s".format(expected_runtime))
    print("Frame sizes in the test: " + str(packet_sizes))
    print("Packet loss tolerance:" + str(PACKET_LOSS_TOLERANCE))
    print("-" * 50)
    print("")

    for size in packet_sizes:
        print("--- Determining throughput for {} B packets --- ".format(size))

        cfg.flows[0].size.fixed = size

        packet_loss = 0.0
        left_pps = 1
        right_pps = int(THEORETICAL_MAX_LINK_SPEED * 1000000000 / 8 / (size + 20)) # max_pps_dict[size]
        rate_pps = right_pps

        max_pps_for_low_loss = 0
        rcv_pkts = 0
        sent_pkts = 1
        step = 1

        # Trial tests
        while step < NO_STEPS:
            print("")
            print("Step: {}".format(step))

            rate_pps = int((right_pps + left_pps) / 2)
            print("left_pps={}; rate_pps={}; right_pps={}; "
                .format(left_pps, rate_pps, right_pps))
            cfg.flows[0].rate.pps = rate_pps

            utils.start_traffic(api, cfg)

            time.sleep(TRIAL_RUN_TIME)

            utils.stop_traffic(api, cfg)

            _, flow_results = utils.get_all_stats(api, None, None, False)
            rcv_pkts = flow_results[0].frames_rx
            sent_pkts = flow_results[0].frames_tx

            print("rcv_pkts {}; sent_pkts {}".format(rcv_pkts, sent_pkts))
            packet_loss_p = (sent_pkts - rcv_pkts) * 100 / sent_pkts
            print("Current pkt loss = " + str(round(packet_loss_p, 2)) + "%")
            # Binary search approach to determine packet loss
            if packet_loss_p > PACKET_LOSS_TOLERANCE:
                # exceeded packet loss limit
                right_pps = rate_pps - 1
            elif packet_loss_p <= PACKET_LOSS_TOLERANCE:
                # minimal loss
                left_pps = rate_pps + 1
                if rate_pps > max_pps_for_low_loss:
                    max_pps_for_low_loss = rate_pps

            step += 1
            time.sleep(TEST_GAP_TIME)

        max_mpps = round(max_pps_for_low_loss / 1000000, 3)
        max_mbps = round(max_pps_for_low_loss * size * 8 / 1000000, 0)

        max_mpps_str = str(max_mpps) + " Mpps"
        max_mbps_str = str(max_mbps) + " Mbps"

        print("- Determined max RX rate for {} packets is {}. Equivalent to {}"
              .format(size, max_mpps_str, max_mbps_str))

        time.sleep(TEST_GAP_TIME)

        if max_pps_for_low_loss > 0:
            # Actual test: to confirm the result determined during trial tests
            # We are running a 60s test again, and check the packet loss percentage
            cfg.flows[0].rate.pps = max_pps_for_low_loss

            utils.start_traffic(api, cfg)

            time.sleep(FINAL_RUN_TIME)

            # utils.get_config_ok(api, cfg)
            utils.stop_traffic(api, cfg)

            _, flow_results = utils.get_all_stats(api, None, None, False)
            rcv_pkts = flow_results[0].frames_rx
            sent_pkts = flow_results[0].frames_tx
            packet_loss_percentage = (sent_pkts - rcv_pkts) * 100 / sent_pkts

            print("### 60s test result for {} packet: rcv_pkts {}; sent_pkts {}, packet_loss_percentage = {} "
              .format(size, rcv_pkts, sent_pkts, round(packet_loss_percentage, 5)))

        else:
            packet_loss_percentage = 100.0

        test_pkt_loss_p_str = str(round(packet_loss_percentage, 5)) + " % loss"
        nr_packets_lost_str = str(sent_pkts - rcv_pkts) + " packets lost" 
        results[str(size)] = [max_mpps_str, max_mbps_str, nr_packets_lost_str, test_pkt_loss_p_str]
        print(results)

        time.sleep(TEST_GAP_TIME)

    with open(RESULTS_FILE_PATH, "w") as file:
        json.dump(results, file)
