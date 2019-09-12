#!/usr/bin/env python

import time, json, copy
from datetime import datetime as dt

from gauge_plugin import GaugeError
import balzers_pkg020_plugin
import vacom_mvc3_plugin, balzers_pkg020_plugin

def main():
    import argparse
    parser = argparse.ArgumentParser(add_help=False)
    def channel_descr(chan_descr):
        chan, _, descr = chan_descr.partition('=')
        return chan, descr
    parser.add_argument('--write-header', '-h', action='store_true', help='write a file header and log the start time, too')
    parser.add_argument('--logging-threshold', '-t', type=float, default=5., help='log whenever the value has changed more then this amount in percent')
    parser.add_argument('--max-logging-interval', '-l', type=float, default=120, help='also log a new value if this amount of seconds has passed')
    parser.add_argument('--sampling-interval', '-s', type=float, default=2, help='also log a new value if this amount of minutes has passed')
    parser.add_argument('--gauge-plugin', '-g', choices=('vacom', 'balzers'), required=True)
    parser.add_argument('--channel', '-c', action='append', type=channel_descr, required=True)
    parser.add_argument('--help', '-H', action='help', help='show this help message and exit')
    parser.add_argument('logfile', default=dt.now().isoformat().replace(':', '-'))
    args = parser.parse_args()
    filenames = [f'{args.logfile}_ch{chan[0]}.log' for chan in args.channel]
    if args.write_header:
        for i, chan in enumerate(args.channel):
            with open(filenames[i], 'a') as f:
                f.write('# vacuum_pumping_curve v1.0.0 \n')
                f.write(json.dumps({'filetype': 'vacuum_pumping_curve', 'version': 'v1.0.0'}) + '\n')
                f.write(json.dumps({'gauge_plugin': args.gauge_plugin, 'channel': chan}) + '\n')
                f.write(json.dumps({'action': 'pumping_started', 'ts': time.time(), 'comment': ''}) + '\n')
    try:
        start = time.time()
        last_sampling_time = 0.0
        last_logging_time = 0.0
        last_sample = None
        last_sample_stored = False
        if args.gauge_plugin == 'balzers':
            gauge = balzers_pkg020_plugin.BalzersPkg020(identifier='',channels=[ch[0] for ch in args.channel])
        elif args.gauge_plugin == 'vacom':
            gauge = vacom_mvc3_plugin.VacomMvc3(identifier='/dev/ttyUSB0', channels=[ch[0] for ch in args.channel])
        while True:
            try:
                readings = gauge.get_readings()
            except GaugeError:
                time.sleep(1.0)
                continue
            last_sampling_time = time.time()
            pressures = readings['pressures']
            print(f"{dt.now().isoformat(' ')} {time.time() - start:.1f} pressure values: {pressures} [mbar]")
            if last_sample:
                change_over_threshold = False
                for i in range(len(pressures)):
                    if abs((pressures[i] - last_sample['pressures'][i]) / last_sample['pressures'][i]) * 100 > args.logging_threshold:
                        change_over_threshold = True
            else:
                change_over_threshold = False
            last_logging_far_ago = time.time() - last_logging_time > args.max_logging_interval
            sample = readings
            sample.update({'ts': time.time()})
            if change_over_threshold or last_logging_far_ago:
                print("logging a new value now.")
                print(f"change_over_threshold={change_over_threshold}, last_logging_far_ago={last_logging_far_ago}")
                last_logging_time = time.time()
                last_value = pressures
                for i, chan in enumerate(args.channel):
                    with open(filenames[i], 'a') as f:
                        if last_sample and not last_sample_stored and change_over_threshold:
                            last_sample_copy = copy.copy(last_sample)
                            last_sample_copy['pressure'] = last_sample_copy['pressures'][i]
                            del last_sample_copy['pressures']
                            # also dump the sample from before so that line plots
                            # aren't 'cutting the corner' after sudden changes
                            json.dump(last_sample_copy, f)
                            f.write('\n')
                        sample_copy = copy.copy(sample)
                        sample_copy['pressure'] = sample_copy['pressures'][i]
                        del sample_copy['pressures']
                        json.dump(sample_copy, f)
                        f.write('\n')
                last_sample_stored = True
            else:
                last_sample = sample
                last_sample_stored = False
            time_since_last_sampling = time.time() - last_sampling_time
            time.sleep(args.sampling_interval - time_since_last_sampling)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
