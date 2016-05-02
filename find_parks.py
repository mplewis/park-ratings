#!/usr/bin/env python3

import overpy
import geojson
from pyproj import Proj
from shapely.geometry import Polygon

import argparse
import json


def parks_in_area(min_lat, min_lon, max_lat, max_lon):
    """Get all state parks in a bounding box from OSM."""
    state_parks_query = """
    way
      ["leisure"="park"]
      ["name"~"State Park"]
      ({}, {}, {}, {});
      (._;>;);
    out body;
    """.format(min_lat, min_lon, max_lat, max_lon)
    api = overpy.Overpass()
    results = api.query(state_parks_query)
    return results.ways


def way_to_geojson_polygon(way):
    """Convert an area's coordinates to a GeoJSON polygon."""
    raw = way.get_nodes()
    clean = [(float(n.lat), float(n.lon)) for n in raw]
    return geojson.Polygon(clean)


def way_to_lon_lat(way):
    """Convert a way to two lists: all lon coords, and all lat coords."""
    raw = way.get_nodes()
    lons = [float(n.lon) for n in raw]
    lats = [float(n.lat) for n in raw]
    return lons, lats


def lon_lat_to_xy(lons, lats):
    """
    Project lists of lon/lat coords onto the Earth and convert them to
    Cartesian coordinates in meters.
    """
    min_lats = min(lats)
    max_lats = max(lats)
    mid_lats = (min_lats + max_lats) / 2
    mid_lons = (min(lons) + max(lons)) / 2
    proj_tmpl = ("+proj=aea +lat_1={} +lat_2={} +lat_0={} +lon_0={}"
                 .format(min_lats, max_lats, mid_lats, mid_lons))
    proj = Proj(proj_tmpl)
    return proj(lons, lats)


def xy_to_polygon(xs, ys):
    """Convert a list of X and Y coordinates to a Shapely polygon."""
    return Polygon(zip(xs, ys))


def area_of_way(way):
    """Calculate the area of a way in square meters."""
    lons, lats = way_to_lon_lat(way)
    xs, ys = lon_lat_to_xy(lons, lats)
    poly = xy_to_polygon(xs, ys)
    return poly.area


def process_parks(ways):
    """Turn Overpy way objects into just the JSON we need."""
    clean = {}
    for way in ways:
        data = {}
        data['name'] = way.tags['name']
        data['geojson'] = way_to_geojson_polygon(way)
        data['area'] = area_of_way(way)
        clean[way.id] = data
    return clean


def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=
        'Search OpenStreetMap for state parks in a bounding box, then output '
        'their info to a JSON file.')
    parser.add_argument('min_lat', type=float, help=
        'The lower latitude bound')
    parser.add_argument('min_lon', type=float, help=
        'The lower longitude bound')
    parser.add_argument('max_lat', type=float, help=
        'The upper latitude bound')
    parser.add_argument('max_lon', type=float, help=
        'The upper longitude bound')
    parser.add_argument('output_file', type=argparse.FileType('w'), help=
        'The JSON file to output park data to')
    return parser.parse_args()


def main():
    """Get state park data from OSM and save it to a file."""
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

    raw = parks_in_area(min_lat, min_lon, max_lat, max_lon)
    clean = process_parks(raw)
    json.dump(clean, args.output_file)


if __name__ == '__main__':
    main()
