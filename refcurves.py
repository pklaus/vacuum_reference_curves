#!/usr/bin/env python

import attr
from typing import List, Tuple
from datetime import datetime as dt
import json
import os
import glob

def get_refcurve_metadata(reffile):
    with open(reffile) as f:
        pass #print(f.read())
    return {'filename': reffile, 'date': 'date', 'name': 'name', 'comment': 'comment'}

def get_refcurves_metadata(root_directory='./data'):
    data = []
    for path in os.scandir(root_directory):
        data.append(recurse_folder(path, top_root=root_directory))
    return data

def recurse_folder(root: os.DirEntry, top_root=''):
    children = []
    for path in os.scandir(root):
        if path.is_dir():
            children.append(recurse_folder(path, top_root=top_root))
        if path.is_file() and path.name.endswith('.log'):
            filename = os.path.join(top_root, os.path.join(root.name, path.name))
            children.append({'filename': filename, 'date': 'date', 'name': path.name})
    return {'name': root.name, 'children': children}

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
    starts = [chunk for chunk in chunks if 'action' in chunk and chunk['action'] == 'pumping_started']
    return ReferenceCurve(name=name, filename=filename, start=starts[0]['ts'], data=(timestamps, pressure))

@attr.s
class ReferenceCurve:
    name: str = attr.ib()
    filename: str = attr.ib()
    start: float = attr.ib()
    data: Tuple[List[float], List[float]] = attr.ib()

def main():
    print(get_refcurves_metadata())

if __name__ == "__main__":
    main()
