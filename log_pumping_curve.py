#!/usr/bin/env python

import time, json
from datetime import datetime as dt

from gauge_plugin import GaugeError
import balzers_pkg020_plugin
import vacom_mvc3_plugin, balzers_pkg020_plugin

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-header', action='store_true', help='write a file header and log the start time, too')
    parser.add_argument('--logging-threshold', type=float, default=5., help='log whenever the value has changed more then this amount in percent')
    parser.add_argument('--max-logging-interval', type=float, default=120, help='also log a new value if this amount of seconds has passed')
    parser.add_argument('--sampling-interval', type=float, default=2, help='also log a new value if this amount of minutes has passed')
    parser.add_argument('logfile', default=dt.now().isoformat().replace(':', '-'))
    args = parser.parse_args()
    if args.write_header:
        with open(args.logfile, 'a') as f:
            f.write('# vacuum_pumping_curve v1.0.0 \n')
            f.write(json.dumps({'filetype': 'vacuum_pumping_curve', 'version': 'v1.0.0'}) + '\n')
            f.write(json.dumps({'action': 'pumping_started', 'ts': time.time(), 'comment': ''}) + '\n')
    try:
        start = time.time()
        last_sampling_time = 0.0
        last_logging_time = 0.0
        last_value = 1e10
        last_sample = None
        #gauge = balzers_pkg020_plugin.BalzersPkg020()
        gauge = vacom_mvc3_plugin.VacomMvc3(identifier='/dev/ttyUSB0', channel=3)
        while True:
            try:
                reading = gauge.get_reading()
            except GaugeError:
                time.sleep(1.0)
                continue
            last_sampling_time = time.time()
            pressure = reading['pressure']
            print(f"{dt.now().isoformat(' ')} {time.time() - start:.1f} pressure: {pressure:.4e} mbar")
            change_over_threshold = abs((pressure - last_value) / last_value) * 100 > args.logging_threshold
            last_logging_far_ago = time.time() - last_logging_time > args.max_logging_interval
            sample = reading
            sample.update({'ts': time.time()})
            if change_over_threshold or last_logging_far_ago:
                print("logging a new value now.")
                print(f"change_over_threshold={change_over_threshold}, last_logging_far_ago={last_logging_far_ago}")
                last_logging_time = time.time()
                last_value = pressure
                with open(args.logfile, 'a') as f:
                    if last_sample and change_over_threshold:
                        # also dump the sample from before so that line plots
                        # aren't 'cutting the corner' after sudden changes
                        json.dump(last_sample, f)
                        f.write('\n')
                    json.dump(sample, f)
                    f.write('\n')
                last_sample = None # prevent to potentially log the current value again
            else:
                last_sample = sample
            time_since_last_sampling = time.time() - last_sampling_time
            time.sleep(args.sampling_interval - time_since_last_sampling)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
