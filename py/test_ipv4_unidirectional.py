import utils
import pytest
import dpkt

def test_ipv4_unidirectional(api):
    """
    Configure a single unidirectional IPV4 flow with,
    - 100,000,000 frames of 1518B size each
    - 100% line rate
    Validate,
    - tx/rx frame count and bytes are as expected
    """
    cfg = utils.load_test_config(
        api, 'ipv4_unidirectional.json', apply_settings=True
    )

    # FRAME_SIZE = 9000
    # PACKETS = 1000000
    # LINE_RATE_PERCENTAGE = 100

    # for flow in cfg.flows:
    #     flow.duration.fixed_packets.packets = PACKETS
    #     flow.size.fixed = FRAME_SIZE
    #     flow.rate.percentage = LINE_RATE_PERCENTAGE

    print(cfg.ports)

    packets = 1000000 #cfg.flows[0].duration.fixed_packets.packets
    
    size = cfg.flows[0].size.fixed

    utils.start_traffic(api, cfg)
    utils.wait_for(
        lambda: results_ok(api, packets, size),
        'stats to be as expected',
        timeout_seconds=1000
    )
    utils.stop_traffic(api, cfg)

    duration = cfg.flows[0].duration.fixed_seconds.seconds
    port_results, flow_results = utils.get_all_stats(api)
    flows_total_tx = sum([flow_res.frames_tx for flow_res in flow_results])
    flows_total_rx = sum([flow_res.frames_rx for flow_res in flow_results])
    print("\n\nAverage total TX rate {} Gbps".format(flows_total_tx * size * 8 / duration / 1000000000))
    print("Average total RX rate {} Gbps".format(flows_total_rx * size * 8 / duration / 1000000000))


def results_ok(api, packets, size, csv_dir=None):
    """
    Returns true if stats are as expected, false otherwise.
    """
    port_results, flow_results = utils.get_all_stats(api)
    if csv_dir is not None:
        utils.print_csv(csv_dir, port_results, flow_results)
    port_tx = sum([p.frames_tx for p in port_results])
    port_rx = sum([p.frames_rx for p in port_results if p.name == 'rx'])
    ok = True# ok = port_tx == packets # and port_rx >= packets
    print('-' * 22)
    for flow_res in flow_results:
        print(flow_res.name + " " + str(size) + "B:")
        print("TX Rate " + str(round(flow_res.frames_tx_rate * size * 8 / 1000000000, 3)) + " Gbps")
        print("RX Rate " + str(round(flow_res.frames_rx_rate * size * 8 / 1000000000, 3)) + " Gbps")
    print('-' * 22)
    print('\n\n\n\n\n')
    
    if utils.flow_metric_validation_enabled():
        flow_tx = sum([f.frames_tx for f in flow_results])
        flow_tx_bytes = sum([f.bytes_tx for f in flow_results])
        flow_rx = sum([f.frames_rx for f in flow_results])
        flow_rx_bytes = sum([f.bytes_rx for f in flow_results])
        ok = ok and flow_rx == packets and flow_tx == packets
        ok = ok and flow_tx_bytes >= packets * (size - 4)
        ok = ok and flow_rx_bytes == packets * size

    return ok and all(
        [f.transmit == 'stopped' for f in flow_results]
    )
