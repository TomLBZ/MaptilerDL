# This file downloads tiles from a url.

TYPE_NAMES = {
    "satellite-v2": ["satellite", "satellite-v2", "satellitev2", "sat"],
    "contours-v2": ["contours", "contours-v2", "contoursv2", "cnt"],
    "terrain-rgb-v2": ["terrain", "terrainrgb", "terrain-rgb", "terrain-rgb-v2", "terrainrgbv2", "trgb"],
    "v3": ["v3", "v3tiles", "v3-tiles"]
}
EXT_NAME = {
    "satellite-v2": "jpg",
    "contours-v2": "pbf",
    "terrain-rgb-v2": "webp",
    "v3": "pbf"
}
API_KEY = "get_your_own_OpIi9ZULNHzrESv6T2vL"
URL_TEMPLATE = "https://api.maptiler.com/tiles/{t}/{z}/{x}/{y}.{e}?key={k}"
CSV_FNAME = "tile_download.csv"
REST_COUNT_PER_LVL = 5
REST_LVLS = 3
_csv = []

# zoom level is 0 - 22
# x and y are tile coordinates
# when zoom level is 0, there is only one tile (0, 0)
# when zoom level is 1, there are 4 tiles (0, 0), (0, 1), (1, 0), (1, 1)
# ...
import requests
import os
import time
import random
import argparse
import math
def download_tile(t, z, x, y, d):
    tile_dir = os.path.join(d, str(z), str(x))
    tile_path = os.path.join(tile_dir, f"{y}.{EXT_NAME[t]}")
    if os.path.exists(tile_path):
        return -1
    url = URL_TEMPLATE.format(t=t, z=z, x=x, y=y, e=EXT_NAME[t], k=API_KEY)
    response = requests.get(url)
    if response.status_code == 200:
        os.makedirs(tile_dir, exist_ok=True)
        with open(tile_path, "wb") as f:
            f.write(response.content)
        _csv.append((z, x, y, 1))
    else:
        _csv.append((z, x, y, 0))
    return response.status_code
def lnglat_to_tile_coords(lng, lat, z):
    if z == 0:
        return 0, 0
    n = 2.0 ** z
    deg2rad = math.pi / 180.0
    lon_deg = lng / 360.0 + 0.5
    lat = max(-89.99999999, min(80.99999999, lat))
    lat_deg = (1 - math.log(math.tan(lat * deg2rad) + 1 / math.cos(lat * deg2rad)) / math.pi) / 2.0
    x = int(n * lon_deg)
    y = int(n * lat_deg)
    return x, y
def get_tile_coords_list(z, mincoords = None, maxcoords = None):
    tile_side_count = 2 ** z
    if mincoords is None or maxcoords is None:
        return [(x, y) for x in range(tile_side_count) for y in range(tile_side_count)]
    else:
        x1, y1 = lnglat_to_tile_coords(mincoords[0], mincoords[1], z)
        x2, y2 = lnglat_to_tile_coords(maxcoords[0], maxcoords[1], z)
        minx, miny = min(x1, x2), min(y1, y2)
        maxx, maxy = max(x1, x2), max(y1, y2)
        if minx < 0 or miny < 0 or maxx >= tile_side_count or maxy >= tile_side_count:
            print("Coordinates are out of bounds.")
            return []
        print(f"Tile coordinates: ({minx}, {miny}) to ({maxx}, {maxy})")
        return [(x, y) for x in range(minx, maxx + 1) for y in range(miny, maxy + 1)]
def get_rest_time(count, max_level):
    if count == 0: # at the beginning, no sleep
        return 0 # no sleep
    sleep_time = 0
    level = max_level + 1
    while level > 0:
        if count % (REST_COUNT_PER_LVL ** level) == 0:
            sleep_time = random.uniform(2 ** (level - 1), 2 ** level)
            break
        level -= 1
    return sleep_time
def download_tiles(map_type, z, mincoords = None, maxcoords = None, tiles_dir = "tiles"):
    tile_coords = get_tile_coords_list(z, mincoords, maxcoords)
    len_tiles = len(tile_coords) # number of tiles to download
    if len_tiles == 0:
        print("No tiles to download.")
        return
    len_digits = len(str(len_tiles)) # number of digits in the number of tiles
    side_digits = len(str(2 ** z)) # number of digits in the side count
    print(f"Downloading {len_tiles} tiles for zoom level {z}...")
    api_call_counter = 0
    for i, (x, y) in enumerate(tile_coords):
        tile_progress = f"{i + 1:>{len_digits}}/{len_tiles:>{len_digits}}"
        tile_coords_progress = f"({x:>{side_digits}}, {y:>{side_digits}})"
        print(f"\tDownloading {tile_progress}: {tile_coords_progress}... ", end="")
        status_code = download_tile(map_type, z, x, y, tiles_dir)
        if status_code == -1: # tile already exists, skip it
            print(f"SKP", end="\r")
        elif status_code == 200: # tile downloaded successfully
            api_call_counter += 1 
            print(f"OK ", end="\r")
        else: # error message and a new line
            api_call_counter += 1
            print(f"\r\tError downloading tile {z:>2}/{x:>{side_digits}}/{y:>{side_digits}}: {status_code}{' ':>{side_digits}}")
        sleep_time = get_rest_time(api_call_counter, REST_LVLS)
        if sleep_time > 0:
            print(f"\tDownloading {tile_progress}: Rest - {sleep_time:.2f}s...{' ':>{side_digits}}", end="\r")
            time.sleep(sleep_time)
    if len(_csv) > 0: # when there are new tiles
        csv_path = os.path.join(tiles_dir, CSV_FNAME)
        if os.path.exists(csv_path): # append to the csv file if it exists
            with open(csv_path, "a") as f:
                for row in _csv:
                    f.write(",".join(map(str, row)) + "\n")
        else: # create the csv file if it doesn't exist
            with open(csv_path, "w") as f:
                f.write("z,x,y,status\n")
                for row in _csv:
                    f.write(",".join(map(str, row)) + "\n")
    print(f"\n...{len(_csv)} new tiles downloaded.")
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download tiles from MapTiler.")
    parser.add_argument("dir", type=str, help="Directory to save tiles")
    parser.add_argument("type", type=str, help="Map Type (satellite, terrain, etc.)")
    parser.add_argument("zoom", type=int, help="Zoom level (0-22)")
    parser.add_argument("--minlon", type=float, help="Minimum longitude")
    parser.add_argument("--minlat", type=float, help="Minimum latitude")
    parser.add_argument("--maxlon", type=float, help="Maximum longitude")
    parser.add_argument("--maxlat", type=float, help="Maximum latitude")
    args = parser.parse_args()
    # check if type is valid
    map_type = ""
    for key, values in TYPE_NAMES.items():
        if args.type in values:
            map_type = key
            break
    if map_type == "":
        print(f"Invalid map type: {args.type}")
        print("Valid map types are: " + ", ".join([f"{key} ({', '.join(values)})" for key, values in TYPE_NAMES.items()]))
        exit(1)
    minlon_exists = args.minlon is not None
    minlat_exists = args.minlat is not None
    maxlon_exists = args.maxlon is not None
    maxlat_exists = args.maxlat is not None
    mincoords = (args.minlon, args.minlat) if minlon_exists and minlat_exists else None
    maxcoords = (args.maxlon, args.maxlat) if maxlon_exists and maxlat_exists else None
    z = args.zoom if args.zoom is not None else 0
    if z < 0 or z > 22:
        print("Zoom level must be between 0 and 22.")
        exit(1)
    if args.dir is None:
        print("Directory must be specified.")
        exit(1)
    if not os.path.exists(args.dir):
        print(f"Directory {args.dir} does not exist. Creating it...")
        os.makedirs(args.dir)
    download_tiles(map_type, z, mincoords, maxcoords, args.dir)
    print("Done.")