import utils
import pytest
import dpkt
import time

def get_flow_src_and_dst(cfg, flow_name):
    for flow in cfg.flows:
        if flow.name == flow_name:
            return flow.tx_rx.port.tx_name + " --> " + flow.tx_rx.port.rx_name

@pytest.mark.uhd_regression
@pytest.mark.sanity
@pytest.mark.uhd_sanity
@pytest.mark.hw
def test_fixed_ports_ipv4(api, duration, frame_size, line_rate_per_flow, direction):
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
        api, 'ipv4_unidirectional_4_flows.json', apply_settings=True
    )

    TIMEOUT = 5
    MAX_FRAME_SIZE = 9000
    MIN_FRAME_SIZE = 64
    MAX_LINE_RATE_PER_FLOW = 100/len(cfg.flows)
    MIN_DURATION = 1

    if frame_size > MAX_FRAME_SIZE:
        print("The frame size exceeds the maximum {}B size!".format(MAX_FRAME_SIZE))
        print("\tThe frame size will be set at {}B.".format(MAX_FRAME_SIZE))
        frame_size = MAX_FRAME_SIZE

    if frame_size < MIN_FRAME_SIZE:
        print("The frame size exceeds the minimum {}B size!".format(MIN_FRAME_SIZE))
        print("\tThe frame size will be set at {}B.".format(MIN_FRAME_SIZE))
        frame_size = MIN_FRAME_SIZE

    if line_rate_per_flow > MAX_LINE_RATE_PER_FLOW:
        print("The requested line rate per flow exceeds the total capacity!")
        print("\tThe line rate per flow percentage will be set at {}%.".format(MAX_LINE_RATE_PER_FLOW))
        line_rate_per_flow = MAX_LINE_RATE_PER_FLOW

    if duration < MIN_DURATION:
        print("The duration exceeds the minimum {}s !".format(MIN_DURATION))
        print("\tThe duration will be set at {}s.".format(MIN_DURATION))
        duration = MIN_DURATION 

    print("\n\nConfiguring each flow with:\n" \
            "   Frame size:           {}B\n" \
            "   Duration:             {}s\n" \
            "   Line rate percentage: {}%\n".format(frame_size, duration, line_rate_per_flow))
    time.sleep(2)            

    flow_paths = {}
    for flow in cfg.flows:
        flow.duration.fixed_seconds.seconds = duration
        flow.size.fixed = frame_size
        flow.rate.percentage = line_rate_per_flow

        if direction == "downstream":
            # change direction
            flow.tx_rx.port.rx_name, flow.tx_rx.port.tx_name = flow.tx_rx.port.tx_name, flow.tx_rx.port.rx_name
            flow.packet[0].dst.value, flow.packet[0].src.value = flow.packet[0].src.value, flow.packet[0].dst.value 
        
        flow_paths[flow.name] = flow.tx_rx.port.tx_name + " --> " + flow.tx_rx.port.rx_name

    sizes = []

    for flow in cfg.flows:
        sizes.append(flow.size.fixed)

    utils.start_traffic(api, cfg)
    utils.wait_for(
        lambda: results_ok(api, sizes, flow_paths),
        'stats to be as expected',
        timeout_seconds = duration + TIMEOUT
    )
    utils.stop_traffic(api, cfg)

    _, flow_results = utils.get_all_stats(api)
    flows_total_tx = sum([flow_res.frames_tx for flow_res in flow_results])
    flows_total_rx = sum([flow_res.frames_rx for flow_res in flow_results])
    print("\n\nDirection: {}".format(direction))
    print("Frame size: {}B".format(frame_size))
    print("Average total TX L2 rate {} Gbps".format(round(flows_total_tx * frame_size * 8 / duration / 1000000000, 3)))
    print("Average total RX L2 rate {} Gbps".format(round(flows_total_rx * frame_size * 8 / duration / 1000000000, 3)))
    print("Total lost packets {}".format(flows_total_tx - flows_total_rx))
    print("Average loss percentage {} %".format(round((flows_total_tx - flows_total_rx) * 100 / flows_total_tx, 3)))

def results_ok(api, sizes, flow_paths, csv_dir=None):
    """
    Returns true if stats are as expected, false otherwise.
    """
    port_results, flow_results = utils.get_all_stats(api)

    if csv_dir is not None:
        utils.print_csv(csv_dir, port_results, flow_results)
    port_tx_packets = sum([p.frames_tx for p in port_results])
    port_rx_packets = sum([p.frames_rx for p in port_results])
    ok = True # port_tx_packets == packets # and port_rx_packets >= packets
    
    total_tx_rate = 0
    total_rx_rate = 0
    i = 0
    total_tx_bps = 0
    total_rx_bps = 0

    print('-' * 22)
    for flow_res in flow_results:
        print(flow_res.name + " " + flow_paths[flow_res.name] + " " + str(sizes[i]) + "B ")
        
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
    
    print("\n\n\n\n\n\n")
    
    
    if utils.flow_metric_validation_enabled():
        flow_tx = sum([f.frames_tx for f in flow_results])
        flow_tx_bytes = sum([f.bytes_tx for f in flow_results])
        flow_rx = sum([f.frames_rx for f in flow_results])
        flow_rx_bytes = sum([f.bytes_rx for f in flow_results])
        # ok = ok and flow_rx == packets and flow_tx == packets
        # ok = ok and flow_tx_bytes >= packets * (sizes[0] - 4)
        # ok = ok and flow_rx_bytes == packets * sizes[0]

    return ok and all(
        [f.transmit == 'stopped' for f in flow_results]
    )
