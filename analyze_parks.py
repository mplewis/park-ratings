#!/usr/bin/env python3

import argparse
import csv
import json
from glob import glob
from os.path import join


def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=
        'Load OpenStreetMap state park inspection data from a directory and '
        'output a report CSV.')
    parser.add_argument('input_dir', type=str, help=
        'The directory with state park inspection JSON data')
    parser.add_argument('output_file', type=argparse.FileType('w'), help=
        'The CSV file to output report data to')
    return parser.parse_args()


def main():
    """Read all park inspections and compile them into a report."""
    args = parse_args()

    parks = []
    for fn in glob(join(args.input_dir, '*.json')):
        with open(fn) as f:
            data = json.load(f)
            park = (
                data['id'],
                data['name'],
                data['area'],
                data['way_count'],
                data['node_count'],
            )
            parks.append(park)

    fieldnames = ['OpenStreetMap ID', 'Name', 'Area (m²)', 'Way Count',
                  'Node Count']
    writer = csv.writer(args.output_file)
    writer.writerow(fieldnames)
    for park in parks:
        writer.writerow(park)

    print('{} parks written to {}.'.format(len(parks), args.output_file.name))

if __name__ == '__main__':
    main()
