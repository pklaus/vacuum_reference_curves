#!/usr/bin/env python

import time, json
from datetime import datetime as dt

from labjack import ljm

from balzerspkg020_helpers import interpolate_log_aware
from balzerspkg020 import tables

handle = ljm.openS("ANY", "ANY", "ANY")


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
        while True:
            try:
                voltage = ljm.eReadName(handle, "AIN0")
            except ljm.ljm.LJMError:
                time.sleep(1.0)
                continue
            last_sampling_time = time.time()
            pressure = interpolate_log_aware(voltage, tables['tpr2'])
            print(f"{dt.now().isoformat(' ')} {time.time() - start:.1f} pressure: {pressure:.4e} mbar (voltage: {voltage:.4f} V)")
            change_over_threshold = abs((pressure - last_value) / last_value) * 100 > args.logging_threshold
            last_logging_far_ago = time.time() - last_logging_time > args.max_logging_interval
            if change_over_threshold or last_logging_far_ago:
                print("logging a new value now.")
                print(f"change_over_threshold={change_over_threshold}, last_logging_far_ago={last_logging_far_ago}")
                last_logging_time = time.time()
                last_value = pressure
                with open(args.logfile, 'a') as f:
                    json.dump({'pressure': pressure, 'voltage': voltage, 'ts': time.time()}, f)
                    f.write('\n')
            time_since_last_sampling = time.time() - last_sampling_time
            time.sleep(args.sampling_interval - time_since_last_sampling)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
