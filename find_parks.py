#!/usr/bin/env python3

import argparse
import overpy


def parse_args():
    parser = argparse.ArgumentParser(description=
        'Search OpenStreetMap for state parks in a bounding box, then output '
        'their info to a file.')
    parser.add_argument('min_lat', type=float, help=
        'The lower latitude bound')
    parser.add_argument('min_lon', type=float, help=
        'The lower longitude bound')
    parser.add_argument('max_lat', type=float, help=
        'The upper latitude bound')
    parser.add_argument('max_lon', type=float, help=
        'The upper longitude bound')
    parser.add_argument('output_file', type=argparse.FileType('w'), help=
        'The file to output park data to')
    return parser.parse_args()

def main():
    args = parse_args()

    # order lat, lon ascending just in case the user got it wrong
    min_lat = args.min_lat
    max_lat = args.max_lat
    min_lon = args.min_lon
    max_lon = args.max_lon
    if min_lat > max_lat:
        min_lat, max_lat = max_lat, min_lat
    if min_lon > max_lon:
        min_lon, max_lon = max_lon, min_lon

    print(min_lat, min_lon, max_lat, max_lon)

if __name__ == '__main__':
    main()
