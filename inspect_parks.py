#!/usr/bin/env python3

import overpy
import pyprind

import argparse
import os
import json
from collections import namedtuple
from glob import glob
from os.path import join, basename, splitext


# Holds data on each state park.
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


def inside_way(way):
    """Get all the ways inside a given OSM way."""
    query = """
    way({});
    map_to_area->.a;
    way(area.a);
    (._;>;);
    out;
    """.format(way.id)
    api = overpy.Overpass()
    return api.query(query)


def inspect_park(park):
    """Fetch OSM metrics for a park."""
    contents = inside_way(park)
    return {
        'id': park.id,
        'name': park.name,
        'area': park.area,
        'node_count': len(contents.nodes),
        'way_count': len(contents.ways),
    }


def inspect_parks(parks, output_dir):
    """Request data for each park, process it, and write it to disk."""
    bar = pyprind.ProgBar(len(parks))
    for park in pyprind.prog_bar(parks):
        data = inspect_park(park)
        fn = join(output_dir, '{}.json'.format(park.id))
        with open(fn, 'w') as f:
            json.dump(data, f)
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

    inspect_parks(todo, args.output_dir)


if __name__ == '__main__':
    main()
