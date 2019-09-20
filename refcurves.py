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

def get_refcurves_metadata(root_directory='./data_v1.1.0'):
    data = []
    for path in os.scandir(root_directory):
        data.append(recurse_folder(path, top_root=root_directory))
    data.sort(key=lambda x: x['name'])
    return data

def recurse_folder(root: os.DirEntry, top_root=''):
    children = []
    for path in os.scandir(root):
        if path.is_dir():
            children.append(recurse_folder(path, top_root=os.path.join(top_root, root.name)))
        if path.is_file() and path.name.endswith('.log'):
            filename = os.path.join(top_root, os.path.join(root.name, path.name))
            children.append({'filename': filename, 'date': 'date', 'name': path.name})
    children.sort(key=lambda x: x['name'])
    dirname = os.path.join(top_root, root.name)
    icon_path = os.path.join(dirname, 'icon.svg')
    entry = {'name': root.name, 'dirname': dirname, 'children': children}
    if glob.glob(icon_path):
        entry['icon'] = icon_path
    return entry

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
    first_start = starts[0]['ts'] if len(starts) else float('nan')
    return ReferenceCurve(name=name, filename=filename, start=first_start, data=(timestamps, pressure))

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
