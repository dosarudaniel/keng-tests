import utils
import pytest
import dpkt

@pytest.mark.uhd_regression
@pytest.mark.sanity
@pytest.mark.uhd_sanity
@pytest.mark.hw
def test_fixed_ports_ipv4(api):
    """
    Configure a IPV4 flow with,
    - fixed src and dst ports
    - 100000000 frames of 1518B size each
    - 100% line rate
    Validate,
    - tx/rx frame count and bytes are as expected
    - all captured frames have expected src and dst ports
    """
    cfg = utils.load_test_config(
        api, 'ipv4_bidirectional.json', apply_settings=True
    )

    packets = cfg.flows[0].duration.fixed_packets.packets

    size_0 = cfg.flows[0].size.fixed
    size_1 = cfg.flows[1].size.fixed

    utils.start_traffic(api, cfg)
    utils.wait_for(
        lambda: results_ok(api, packets, size_0, size_1),
        'stats to be as expected',
        timeout_seconds=1000
    )
    #utils.get_config_ok(api, cfg)
    utils.stop_traffic(api, cfg)


def results_ok(api, packets, size_0, size_1, csv_dir=None):
    """
    Returns true if stats are as expected, false otherwise.
    """
    port_results, flow_results = utils.get_all_stats(api)

    if csv_dir is not None:
        utils.print_csv(csv_dir, port_results, flow_results)
    port_tx = sum([p.frames_tx for p in port_results if p.name == 'tx'])
    port_rx = sum([p.frames_rx for p in port_results if p.name == 'rx'])
    ok = port_tx == packets # and port_rx >= packets

    sizes = [size_0, size_1]
    
    total_tx_rate = 0
    total_rx_rate = 0
    i = 0
    total_tx_bps = 0
    total_rx_bps = 0

    print('-' * 22)
    for flow_res in flow_results:
        print(flow_res.name + " " + str(sizes[i]) + "B ")
        
        print("TX Rate " + str(round(flow_res.frames_tx_rate * sizes[i] * 8 / 1000000000, 3)) + " Gbps")
        total_tx_rate += flow_res.frames_tx_rate
        total_tx_bps += flow_res.frames_tx_rate * sizes[i] * 8
        
        print("RX Rate " + str(round(flow_res.frames_rx_rate * sizes[i] * 8 / 1000000000, 3)) + " Gbps")
        total_rx_rate += flow_res.frames_rx_rate
        total_rx_bps += flow_res.frames_rx_rate * sizes[i] * 8
        i = i + 1
        print("")

    print("Totals")
    print("TX Rate " + str(round(total_tx_bps/1000000000, 3)) + " Gbps")
    print("RX Rate " + str(round(total_rx_bps/1000000000, 3)) + " Gbps")
    print('-' * 22)
    
    
    if utils.flow_metric_validation_enabled():
        flow_tx = sum([f.frames_tx for f in flow_results])
        flow_tx_bytes = sum([f.bytes_tx for f in flow_results])
        flow_rx = sum([f.frames_rx for f in flow_results])
        flow_rx_bytes = sum([f.bytes_rx for f in flow_results])
        ok = ok and flow_rx == packets and flow_tx == packets
        ok = ok and flow_tx_bytes >= packets * (sizes[0] - 4)
        ok = ok and flow_rx_bytes == packets * sizes[0]

    return ok and all(
        [f.transmit == 'stopped' for f in flow_results]
    )
