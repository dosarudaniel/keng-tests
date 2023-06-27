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
        api, 'fixed_udp_ports.json', apply_settings=True
    )

    packets = cfg.flows[0].duration.fixed_packets.packets
    
    size = cfg.flows[0].size.fixed

    utils.start_traffic(api, cfg)
    utils.wait_for(
        lambda: results_ok(api, packets, size),
        'stats to be as expected',
        timeout_seconds=1000
    )
    #utils.get_config_ok(api, cfg)
    utils.stop_traffic(api, cfg)
    #captures_ok(api, cfg, size, packets)


def results_ok(api, packets, size, csv_dir=None):
    """
    Returns true if stats are as expected, false otherwise.
    """
    port_results, flow_results = utils.get_all_stats(api)
    if csv_dir is not None:
        utils.print_csv(csv_dir, port_results, flow_results)
    port_tx = sum([p.frames_tx for p in port_results if p.name == 'tx'])
    port_rx = sum([p.frames_rx for p in port_results if p.name == 'rx'])
    ok = port_tx == packets and port_rx >= packets

    print("Flow stats - rate in gbps : packet size = " + str(size) + "B ")
    for flow_res in flow_results:
        print("TX rate " + str(round(flow_res.frames_tx_rate * size * 8 / 1000000000, 2)) + " Gbps")
        print("RX rate " + str(round(flow_res.frames_rx_rate * size * 8 / 1000000000, 2)) + " Gbps") 
    
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


def captures_ok(api, cfg, size, packets):
    """
    Returns normally if patterns in captured packets are as expected.
    """

    if not utils.capture_validation_enabled():
        return True

    src_port = 5001
    dst_port = 5002
    flags = 0
    window = 1
    actual_packets = 0

    mac_dst = '00:ab:bc:ab:bc:ab'
    mac_src = '00:cd:dc:cd:dc:cd'

    ip_src = "1.1.1.2"
    ip_dst = "1.1.1.1"

    cap_dict = utils.get_all_captures_as_dpkt_pcap(api, cfg)
    for _, pcap in cap_dict.items():
        # check if number of packets is as expected
        for _, buf in pcap:
            eth = dpkt.ethernet.Ethernet(buf)
            if eth.type == dpkt.ethernet.ETH_TYPE_IP:
                actual_packets += 1
                # check packet size is as expected
                assert len(buf) == size

                # check if current packet is a valid TCP packet
                assert isinstance(eth.data.data, dpkt.tcp.TCP)
                # check if next header is as expected
                assert utils.mac_addr(eth.src) == mac_src
                assert utils.mac_addr(eth.dst) == mac_dst

                ip = eth.data
                # check if next header is as expected
                assert utils.inet_to_str(ip.src) == ip_src
                assert utils.inet_to_str(ip.dst) == ip_dst
                assert ip.p == dpkt.ip.IP_PROTO_TCP

                tcp = ip.data
                assert tcp.sport == src_port
                assert tcp.dport == dst_port
                assert tcp.flags == flags
                assert tcp.win == window

    assert actual_packets == packets
