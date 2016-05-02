#!/usr/bin/env python3

import pyprind

import argparse
import os
import json
from collections import namedtuple
from glob import glob
from os.path import join, basename, splitext

import time


Park = namedtuple('Park', 'id, name, area')


def parse_parks(obj):
    """Convert the JSON object for all parks into an array of Park objects."""
    parks = []
    for pid, data in obj.items():
        parks.append(Park(pid, data['name'], data['area']))
    return parks


def to_fetch(parks, output_dir):
    """
    Return lists of parks that need to be fetched and parks that have
    already been fetched.
    """
    files = glob(join(output_dir, '*.json'))
    existing = []
    for path in files:
        fn = basename(path)
        pid, _ = splitext(fn)
        existing.append(pid)
    todo = []
    done = []
    for park in parks:
        if park.id in existing:
            done.append(park)
        else:
            todo.append(park)
    return todo, done


def inspect_parks(parks):
    bar = pyprind.ProgBar(len(parks))
    for park in pyprind.prog_bar(parks):
        time.sleep(0.1)
        bar.update(item_id=park.name[:20])


def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=
        'Load find_parks JSON data for OpenStreetMap state parks, inspect '
        'the number of ways and nodes in each park, and output each park\'s '
        'data to a JSON file.')
    parser.add_argument('input_file', type=argparse.FileType('r'), help=
        'The JSON file with state park data')
    parser.add_argument('output_dir', type=str, help=
        'The directory where JSON files with park data will be written')
    return parser.parse_args()


def main():
    """Get data for each OSM way in the JSON file."""
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    parks = parse_parks(json.load(args.input_file))
    todo, done = to_fetch(parks, args.output_dir)
    done_msg = ''
    if done:
        done_msg = ' ({} already done)'.format(len(done))
    print('Inspecting {} parks{}'.format(len(todo), done_msg))

    inspect_parks(todo)


if __name__ == '__main__':
    main()
