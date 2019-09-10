import attr
from typing import List, Tuple
from datetime import datetime as dt
import json


def get_refcurves_metadata():
    data = [
        {'name': 'empty UFO reference curves', 'children': [
            {
              'filename': 'data/2019-09-05.log',
              'date': '2019-09-05',
              'name': 'first pumping',
              'comment': 'This was actually <b>the first time</b> the chamber was pumped!'
            },
            {
              'filename': 'data/2019-09-06.log',
              'date': '2019-09-06',
              'name': 'second pumping',
            },
            {
              'filename': 'data/2019-09-09.log',
              'date': '2019-09-09',
              'name': 'third pumping',
            },
            {
              'filename': 'data/2019-09-10.log',
              'date': '2019-09-10',
              'name': 'fourth pumping',
            },
            {
              'filename': 'data/2019-09-10_2nd.log',
              'date': '2019-09-10',
              'name': 'fifth pumping (2nd this day)',
            },
        ]},
        {'name': 'UFO reference curves with content', 'children': [
            {'name': 'heatsinks', 'children': [
                {'date': '2019-09-05', 'name': 'test with PRESTO heatsink'},
                {'date': '2019-09-07', 'name': 'test with new quadrant heatsink'},
            ]},
            {'name': 'electrical feedthroughs', 'children': [
                {'date': '2019-09-05', 'name': 'run with FPC feedthrough'},
                {'date': '2019-09-07', 'name': 'run with PCB sealing'},
            ]},
        ]},
    ]
    return data

def get_refcurve(name):
    filename = name
    with open(filename, 'r') as f:
        content = f.read()
    chunks = [json.loads(line) for line in content.split('\n') if line.strip().startswith('{')]
    pressure_readings = [chunk for chunk in chunks if 'pressure' in chunk]
    # only keep pressure_readings older than...
    #pressure_readings = [pr for pr in pressure_readings if pr['ts'] < dt(2019, 9, 5, 22, 0).timestamp()]
    timestamps = [pr['ts'] for pr in pressure_readings]
    pressure = [pr['pressure'] for pr in pressure_readings]
    voltage = [pr['voltage'] for pr in pressure_readings]
    starts = [chunk for chunk in chunks if 'action' in chunk and chunk['action'] == 'pumping_started']
    return ReferenceCurve(name=name, filename=filename, start=starts[0]['ts'], data=(timestamps, pressure))

@attr.s
class ReferenceCurve:
    name: str = attr.ib()
    filename: str = attr.ib()
    start: float = attr.ib()
    data: Tuple[List[float], List[float]] = attr.ib()
