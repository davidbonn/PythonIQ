#!/usr/bin/env python3
"""
    Exerciser code for Redis GEO* operations.

    Usage:

        python3 ./geo.py cmd
            [--verbose]
            [--redis url]                       -- url for redis, default redis://localhost
            [--name name]                       -- name of geosearch structure, default "geo"
            [--input file]                      -- file to read coordinates from, or "builtin"
            [--latitude lat] [--longitude lon]  -- specify latitude and longitude to search
            [--radius km]                       -- within radius
            [--width km] [--height km]          -- within a rectangle
            [--count max]                       -- up to max entries returned
            [--any]                             -- return any of max, rather than closest
            [--descending]                      -- sort in descending order by distance
            [--ascending]                       -- sort in descending order by distance

        cmd can be:
            "create"    -- will add entries from input file or "builtin"
            "search"    -- will search and print results
            "count"     -- print how many entries there are
            "expunge"   -- delete set
"""

import argparse
import json
import redis
import math

"""builtin data to use, from places to stay in the Presidential Range, NH"""
Data = [
    {
        "name": "Rattle River Shelter",
        "latitude": 44.38027,
        "longitude": -70.10808,
    },
    {
        "name": "Imp Shelter",
        "latitude": 44.32922,
        "longitude": -71.15022,
    },
    {
        "name": "Carter Notch Hut",
        "latitude": 44.25931,
        "longitude": -71.19578,
    },
    {
        "name": "Joe Dodge Lodge",
        "latitude": 44.25705,
        "longitude": -71.25369,
    },
    {
        "name": "Osgood Tent Site",
        "latitude": 44.30875,
        "longitude": -71.25426,
    },
    {
        "name": "Madison Spring Hut",
        "latitude": 44.32769,
        "longitude": -71.28321,
    },
    {
        "name": "Lake of the Clouds Hut",
        "latitude": 44.25884,
        "longitude": -71.31892,
    },
    {
        "name": "Mizpal Spring Hut",
        "latitude": 44.21946,
        "longitude": -71.36966,
    },
    {
        "name": "Ethan Pond Shelter",
        "latitude": 44.17793,
        "longitude": -71.43102,
    },
    {
        "name": "Zealand Fals Hut",
        "latitude": 44.19656,
        "longitude": -71.50119,
    },
    {
        "name": "Galehead Hut",
        "latitude": 44.18893,
        "longitude": -71.57389,
    },
    {
        "name": "Greenleaf Hut",
        "latitude": 44.16061,
        "longitude": -71.66172,
    },
    {
        "name": "Guyot Shelter",
        "latitude": 44.16255,
        "longitude": -71.54218,
    },
]

Verbose = False
Redis = redis.from_url("redis://localhost")  # opens lazily so no error if not present


def main():
    """
        parse arguments, do minimal error checking, dispatch to respective
        functions ( create(), search(), expunge(), and count() ) to do actual work.
    """
    global Verbose, Redis

    ap = argparse.ArgumentParser()
    ap.add_argument("command", type=str, nargs=1)
    ap.add_argument("--verbose", action='store_true', default=False)
    ap.add_argument("--redis", type=str, required=False)
    ap.add_argument("--name", type=str, default="geo")
    ap.add_argument("--input", type=str, default="builtin")
    ap.add_argument("--latitude", type=float, required=False)
    ap.add_argument("--longitude", type=float, required=False)
    ap.add_argument("--radius", type=float, required=False)
    ap.add_argument("--width", type=float, required=False)
    ap.add_argument("--height", type=float, required=False)
    ap.add_argument("--count", type=int, default=None)
    ap.add_argument("--any", action='store_true', default=False)
    ap.add_argument("--descending", action='store_true', default=False)
    ap.add_argument("--ascending", action='store_true', default=False)
    ap.add_argument("--bearing", action='store_true', default=False)

    args = ap.parse_args()
    cmd = args.command[0]

    if cmd not in ["create", "search", "count", "expunge"]:
        print(f"[error] Invalid command {cmd}")
        exit(1)

    Verbose = args.verbose

    if args.redis:
        Redis = redis.from_url(args['redis'])

    if cmd == "create":
        create(args.name, args.input)
    elif cmd == "count":
        count(args.name)
    elif cmd == "search":
        search(args)
    elif cmd == "expunge":
        expunge(args.name)


def create(name, source):
    """
        create redis geo object

    :param name: name of redis geo object
    :param source: source to read from, json file or "builtin"
    """

    if source == "builtin":
        global Data
        return load_data(name, Data)
    else:
        with open(source, 'r') as f:
            stuff = json.load(f)

        return load_data(name, stuff)


def count(name):
    """
    print number of entries in redis geo object

    :param name: name of geo object in redis to count
    """
    rc = Redis.zcard(name)

    print(f"{rc} entries in {name}")


def expunge(name):
    """
        removes a sorted set we don't need anymore

    :param name: object to expunge
    :return:
    """
    if Verbose:
        print(f"[info] Deleting {name}")

    Redis.delete(name)


def search(args):
    """
        do redis geo search operation and print results, one per line

    :param args: -- parsed arguments
    """
    lat = args.latitude
    lon = args.longitude

    if lat is None or lon is None:
        print(f"[error] Must specify both --latitude and --longitude")
        exit(1)

    radius = args.radius

    sorting = None

    if args.ascending:
        sorting = 'ASC'

    if args.descending:
        sorting = 'DESC'

    if radius is None:
        h = args.height
        w = args.width

        if h is None or w is None:
            print(f"[error] Must specify both --width and --height or --radius")
            exit(1)

        results = Redis.geosearch(
            args.name, latitude=lat, longitude=lon, width=w, height=h, unit='km',
            sort=sorting, count=args.count, any=args.any,
            withcoord=True, withdist=True
        )
    else:
        if Verbose:
            print(f"[info] For radius {radius:.3f}km")
        results = Redis.geosearch(
            args.name, latitude=lat, longitude=lon, radius=radius, unit='km',
            sort=sorting, count=args.count, any=args.any,
            withcoord=True, withdist=True
        )

    if Verbose:
        print(f"[info] from {lat:.5f},{lon:.5f}, {len(results)} entries found")

    print_search(results, args)


def print_search(results, args):
    """
        prints results from Redis.geosearch()

    :param results: from Redis.geosearch()
    :param args:  from argparse
    """
    for ent in results:
        what, distance, loc = ent
        what = what.decode('utf-8')
        lon, lat = loc
        out = f"{what}:  {distance:.3f} km at {lat:.5f},{lon:.5f}"

        if args.bearing:
            degrees = bearing((args.latitude, args.longitude), (lat, lon))
            out += f" at {degrees} degrees"

        print(out)


def bearing(p1, p2):
    """
    compute compass bearing (degrees) from p1 to p2
    works best over fairly short distances 

    code inspired by:
        https://towardsdatascience.com/calculating-the-bearing-between-two-geospatial-coordinates-66203f57e4b4

    :param p1: starting position -- tuple latitude longitude
    :param p2: ending position -- tuple latitude longitude
    :return: int bearing from starting to ending position (degrees)
    """

    lat_1, lon_1 = p1
    lat_2, lon_2 = p2

    lat_1 = math.radians(lat_1)
    lat_2 = math.radians(lat_2)
    lon_1 = math.radians(lon_1)
    lon_2 = math.radians(lon_2)

    delta_l = lon_2 - lon_1

    x = math.cos(lat_2) * math.sin(delta_l)
    y = math.cos(lat_1) * math.sin(lat_2) - math.sin(lat_1) * math.cos(lat_2) * math.cos(delta_l)

    rc = int(math.degrees(math.atan2(x, y)))

    if rc < 0:
        rc += 360

    return rc


def load_data(name, entries):
    """
    load geospatial data from a list of dicts

    :param name: redis geo name
    :param entries: list of dicts
    """
    for ent in entries:
        what = ent['name']
        lat = ent['latitude']
        lon = ent['longitude']

        if Verbose:
            print(f"Adding: {what} at {lat:.5f},{lon:.5f}")

        Redis.geoadd(name, (lon, lat, what))


if __name__ == '__main__':
    main()
