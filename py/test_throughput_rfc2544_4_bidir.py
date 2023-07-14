
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
RESULTS_FILE_PATH          = "./throughput_results_rfc2544_1_bidir.json"



@pytest.mark.performance
def test_throughput_rfc2544_multiple_flows(api):
    """
    RFC-2544 Throughput determination test for bidirectional traffic
    """
    cfg = utils.load_test_config(api, 'throughtput_rfc2544_bidir.json', apply_settings=True)

    packet_sizes = [64, 512, 1518, 9000]
    #packet_sizes = [64, 128, 256, 512, 768, 1024, 1280, 1518, 9000]
    # packet_sizes = [64, 512, 1518, 9000]
    # packet_sizes = [1518]

    results = {}
    
    NUMBER_OF_FLOWS            = len(cfg.flows)   # should be an even number
    expected_runtime = len(packet_sizes) * ((NO_STEPS-1) * TEST_GAP_TIME + FINAL_RUN_TIME + 2 * TEST_GAP_TIME)
    print("\n" + "-" * 50)
    print("This is a throughput test (based on RFC-2544 procedure). The expected runtime is minimum {}s.".format(expected_runtime))
    print("Frame sizes in the test: " + str(packet_sizes))
    print("Packet loss tolerance: " + str(PACKET_LOSS_TOLERANCE))
    print("Number of flows: " + str(len(cfg.flows)))
    print("-" * 50)
    print("")

    for size in packet_sizes:
        print("\n\n--- Determining throughput for {} B packets --- ".format(size))

        for flow in cfg.flows:
            flow.size.fixed = size

        packet_loss_p = []
        left_pps    = []
        right_pps   = []
        rate_pps    = []
        max_pps_for_low_loss = []
        rcv_pkts = []
        sent_pkts = []

        packet_loss_p = [0.0 for i in range(NUMBER_OF_FLOWS)]
        left_pps = [1 for i in range(NUMBER_OF_FLOWS)]
        right_pps = [int(THEORETICAL_MAX_LINK_SPEED * 1000000000 / 8 / (size + 20) / len(cfg.flows) * 2) for i in range(NUMBER_OF_FLOWS)]
        rate_pps = [right_pps[i] for i in range(NUMBER_OF_FLOWS)]

        max_pps_for_low_loss = [0 for i in range(NUMBER_OF_FLOWS)]
        rcv_pkts = [0 for i in range(NUMBER_OF_FLOWS)]
        sent_pkts = [0 for i in range(NUMBER_OF_FLOWS)]

        step = 1

        # Trial tests
        while step < NO_STEPS:
            print("")
            print("Step [{}B]: {}".format(size, step))


            for i in range(NUMBER_OF_FLOWS):
                rate_pps[i] = int((right_pps[i] + left_pps[i]) / 2)
                print("Flow {}: Current search interval: [{} Gbps; {} Gbps]. Trial run with {} Gbps. "
                    .format(i, round(left_pps[i] * 8 * size / 1000000000, 3), 
                        round(right_pps[i] * 8 * size / 1000000000, 3), 
                        round(rate_pps[i] * 8 * size / 1000000000, 3)))

            # print("Totals: Current search interval: [{} Gbps; {} Gbps]. Trial run with {} Gbps. "
            #         .format(i, round(sum(left_pps) * 8 * size / 1000000000, 3), 
            #             round(sum(right_pps) * 8 * size / 1000000000, 3), 
            #             round(sum(rate_pps) * 8 * size / 1000000000, 3)))

            for i in range(NUMBER_OF_FLOWS):
                cfg.flows[i].rate.pps = rate_pps[i]

            utils.start_traffic(api, cfg)
            time.sleep(TRIAL_RUN_TIME)
            utils.stop_traffic(api, cfg)

            _, flow_results = utils.get_all_stats(api, None, None, False)
            
            for i in range(NUMBER_OF_FLOWS):
                rcv_pkts[i] = flow_results[i].frames_rx
                sent_pkts[i] = flow_results[i].frames_tx

                print("f{} - rcv_pkts {}; sent_pkts {}, Lost packets = {} ".format(i, rcv_pkts[i], sent_pkts[i], sent_pkts[i] - rcv_pkts[i]))
                packet_loss_p[i] = (sent_pkts[i] - rcv_pkts[i]) * 100 / sent_pkts[i]
                print("Current pkt loss % for flow {} = {}%".format(i, round(packet_loss_p[i], 6)))

                # Binary search approach to determine packet loss
                if packet_loss_p[i] > PACKET_LOSS_TOLERANCE:
                    # exceeded packet loss limit
                    right_pps[i] = rate_pps[i] - 1
                elif packet_loss_p[i] <= PACKET_LOSS_TOLERANCE:
                    # minimal loss
                    left_pps[i] = rate_pps[i] + 1
                    if rate_pps[i] > max_pps_for_low_loss[i]:
                        max_pps_for_low_loss[i] = rate_pps[i]

            step += 1
            time.sleep(TEST_GAP_TIME)


        max_mpps = [round(max_pps_for_low_loss[i] / 1000000, 3) for i in range(NUMBER_OF_FLOWS)] 
        max_mbps = [round(max_pps_for_low_loss[i] * size * 8 / 1000000, 0) for i in range(NUMBER_OF_FLOWS)]

        max_mpps_str = [str(max_mpps[i]) + " Mpps"  for i in range(NUMBER_OF_FLOWS)]
        max_mbps_str = [str(max_mbps[i]) + " Mbps"  for i in range(NUMBER_OF_FLOWS)]

        for i in range(NUMBER_OF_FLOWS):
            print("- Flow {}: Determined max RX rate for {}B packets is {} Mpps. Equivalent to {} Mbps."
              .format(i, size, max_mpps[i], max_mbps[i]))

        print("\nDetermined TOTAL max RX rate for {}B packets is {} Mpps. Equivalent to {} Mbps.\n"
              .format(size, sum(max_mpps), sum(max_mbps)))

        time.sleep(TEST_GAP_TIME)
            
        # Actual test: to confirm the result determined during trial tests
        # We are running a FINAL_RUN_TIMEs test again, and check the packet loss percentage
        print("\nTo confirm the results determined during trial tests we are running " + str(FINAL_RUN_TIME) +"s tests again, and check the packet loss percentage")

        while True: # packet_loss_percentage > PACKET_LOSS_TOLERANCE:

            for i in range(NUMBER_OF_FLOWS):
                print("Flow {}: Running with {} Mpps ...".format(i, max_pps_for_low_loss[i]/1000000))
                cfg.flows[i].rate.pps = max_pps_for_low_loss[i]

            utils.start_traffic(api, cfg)
            time.sleep(FINAL_RUN_TIME)
            utils.stop_traffic(api, cfg)

            _, flow_results = utils.get_all_stats(api, None, None, False)

            test_passed = [False for i in range(NUMBER_OF_FLOWS)]
            for i in range(NUMBER_OF_FLOWS):
                rcv_pkts[i] = flow_results[i].frames_rx
                sent_pkts[i] = flow_results[i].frames_tx

                print("f{} - rcv_pkts {}; sent_pkts {}, lost packets = {} ".format(i, rcv_pkts[i], sent_pkts[i], sent_pkts[i] - rcv_pkts[i]))
                packet_loss_p[i] = (sent_pkts[i] - rcv_pkts[i]) * 100 / sent_pkts[i]

                print("### Flow{}: {}s test result for {}B packet: rcv_pkts {}; sent_pkts {}, packet_loss_percentage = {} "
                .format(i, FINAL_RUN_TIME, size, rcv_pkts[i], sent_pkts[i], round(packet_loss_p[i], 5)))

                if packet_loss_p[i] <= PACKET_LOSS_TOLERANCE:
                    test_passed[i] = True
                    print("Flow {}: The {}s test with {}pps PASSED".format(i, FINAL_RUN_TIME, max_pps_for_low_loss[i]))
                else: 
                    max_pps_for_low_loss[i] = (int) (0.95 * max_pps_for_low_loss[i])
                    print("Flow {}: The {}s test with {}pps per flow did NOT pass, trying again with {} pps PER FLOW."
                          .format(i, FINAL_RUN_TIME, max_pps_for_low_loss[i], (int) (0.95 * max_pps_for_low_loss[i])))
                    
            all_test_passed = True
            for i in range(NUMBER_OF_FLOWS):
                if test_passed[i] == False:
                    all_test_passed = False

            if all_test_passed == True:
                break
            
            time.sleep(TEST_GAP_TIME)

        max_mpps = [round(max_pps_for_low_loss[i] / 1000000 / len(cfg.flows) / 2, 3) for i in range(NUMBER_OF_FLOWS)] 
        max_mbps = [round(max_pps_for_low_loss[i] * size * 8 / 1000000, 0) for i in range(NUMBER_OF_FLOWS)]

        max_mpps_str = [str(max_mpps[i]) + " Mpps"  for i in range(NUMBER_OF_FLOWS)]
        max_mbps_str = [str(max_mbps[i]) + " Mbps"  for i in range(NUMBER_OF_FLOWS)]

        test_pkt_loss_p_str = [str(round(packet_loss_p[i], 5)) + " % loss" for i in range(NUMBER_OF_FLOWS)]
        nr_packets_lost_str = [str(sent_pkts[i] - rcv_pkts[i]) + " packets lost" for i in range(NUMBER_OF_FLOWS)]

        result_flows = {}
        for i in range(NUMBER_OF_FLOWS):
            result_flows[str(i)] = [max_mpps_str[i], max_mbps_str[i], nr_packets_lost_str[i], test_pkt_loss_p_str[i]]
    
        results[str(size)] = result_flows
        print(results)

        time.sleep(TEST_GAP_TIME)

    with open(RESULTS_FILE_PATH, "w") as file:
        json.dump(results, file)
