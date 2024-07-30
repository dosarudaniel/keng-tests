import time
import utils

CSV_COLUMNS = [
    'in_speed',
    'in_frame_size',
    'in_rate_pps',
    'out_rate_pps',
    'tolerance',
    'status'
]

SUM_COLUMNS = [
    'in_speed',
    'in_frame_size',
    'max_steady_rate_pps',
]

CSV_DIR = utils.new_logs_dir()

def test_throughput_from_ixia_c_stat(api,
                                     settings):

    size = 64
    total_fetch = 100
    rate_in_pps = 337000 
    pps_tolerance = 5
    max_steady_rate_pps = 0
    pps_decrease = 500
    pass_percent = 85

    while True:
        total_pass = 0

        cfg = new_config(api, settings, size, rate_in_pps)
        utils.start_traffic(api, cfg)

        csv_file = '{}_frame_size_{}_pps_{}.csv'.format(settings.speed, size, rate_in_pps)
        for i in range(total_fetch):
            port_results, _ = utils.get_all_stats(api)
            out_rate_pps = sum([p.frames_tx_rate for p in port_results if p.name == 'tx'])

            exp_rate_pps = rate_in_pps * (1-(pps_tolerance/100))
            status = "Failed"
            if out_rate_pps >= exp_rate_pps:
                status = "Passed"
                total_pass += 1

            csv_dict = {
                'in_speed': settings.speed,
                'in_frame_size': size,
                'in_rate_pps': rate_in_pps,
                'out_rate_pps': out_rate_pps,
                'tolerance': pps_tolerance,
                'status': status, 
            }

            utils.append_csv_row(
                CSV_DIR,
                csv_file,
                CSV_COLUMNS,
                csv_dict)
            print(i)

            time.sleep(1)
        pass_rate = (total_pass/total_fetch) * 100
        if pass_rate >= pass_percent:
            max_steady_rate_pps = rate_in_pps
            sum_dict = {
                'in_speed': settings.speed,
                'in_frame_size': size,
                'max_steady_rate_pps': max_steady_rate_pps
            }
            utils.append_csv_row(
                CSV_DIR,
                'summary_info.csv',
                SUM_COLUMNS,
                sum_dict)
            break
        else:
            utils.stop_traffic(api, cfg)
            rate_in_pps = rate_in_pps - pps_decrease

def new_config(api, settings, size, rate_in_pps):
    config = api.config()
    tx, rx = (
        config.ports
        .port(name='tx', location=settings.ports[0])
        .port(name='rx', location=settings.ports[1])
    )
    ly = config.layer1.layer1(name='l1')[0]

    ly.speed = settings.speed
    ly.promiscuous = settings.promiscuous
    ly.mtu = settings.mtu
    ly.port_names = [tx.name, rx.name]

    flw, = config.flows.flow(name='f1')
    flw.size.fixed = size
    flw.rate.pps = rate_in_pps
    flw.tx_rx.port.tx_name = tx.name
    flw.tx_rx.port.rx_name = rx.name
    flw.packet.ethernet()
    flw.metrics.enable = True

    return config
