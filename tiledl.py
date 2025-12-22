import requests
import os
import time
import argparse
import math
from typing import Optional, Tuple, List
from dataclasses import dataclass

# types, classes and data structures:
type TileRange = Tuple[float, float, float, float] # (minlon, minlat, maxlon, maxlat)
@dataclass(frozen=True, slots=True, kw_only=True)
class TileOption:
    name: str
    ext: str
    aliases: List[str]
@dataclass(frozen=True, slots=True, kw_only=True)
class Arguments:
    key: str
    dir: str
    option: TileOption
    zoom: int
    range: TileRange

# constants:
MIN_LON: float = -179.99999999
MAX_LON: float = 179.99999999
MIN_LAT: float = -85.0511
MAX_LAT: float = 85.0511
MAX_RANGE: TileRange = (MIN_LON, MIN_LAT, MAX_LON, MAX_LAT)
URL_TEMPLATE: str = "https://api.maptiler.com/tiles/{t}/{z}/{x}/{y}.{e}?key={k}"
TILE_OPTIONS: List[TileOption] = [
    TileOption(name="satellite-v2", ext="jpg", aliases=["satellite", "satellite-v2", "satellitev2", "sat"]),
    TileOption(name="contours-v2", ext="pbf", aliases=["contours", "contours-v2", "contoursv2", "cnt"]),
    TileOption(name="terrain-rgb-v2", ext="webp", aliases=["terrain", "terrainrgb", "terrain-rgb", "terrain-rgb-v2", "terrainrgbv2", "trgb"]),
    TileOption(name="v3", ext="pbf", aliases=["v3", "v3tiles", "v3-tiles", "tilesv3", "tiles-v3"]),
    TileOption(name="v4", ext="pbf", aliases=["v4", "v4tiles", "v4-tiles", "tilesv4", "tiles-v4"])
]
TYPE_CHOICES: List[str] = [alias for option in TILE_OPTIONS for alias in option.aliases]

# global variables:
_wait_sec: float = 1.0 # start with waiting for 1 second between calls

def parse_arguments() -> Arguments:
    parser = argparse.ArgumentParser(description="Download tiles from MapTiler.")
    # required arguments: key
    parser.add_argument("-k", "--key", type=str, required=True, default="get_your_own_OpIi9ZULNHzrESv6T2vL", help="Your MapTiler API key.")
    # optional arguments: dir, type, zoom, range
    parser.add_argument("-d", "--dir", type=str, default="./tiles", help="Directory to save tiles")
    parser.add_argument("-t", "--type", type=str, choices=TYPE_CHOICES, metavar="TYPE", 
                        default="sat", help="Map Type (sat, v4, etc.)")
    parser.add_argument("-z", "--zoom", type=int, choices=range(0, 23), metavar="ZOOM", 
                        default=0, help="Zoom level (0-22), recommended 0-15")
    parser.add_argument("-r", "--range", type=float, nargs=4, metavar=("MINLON", "MINLAT", "MAXLON", "MAXLAT"), 
                        default=MAX_RANGE, help="Bounding box to download tiles")
    args = parser.parse_args()
    return Arguments(
        key=args.key,
        dir=args.dir,
        option=next((option for option in TILE_OPTIONS if args.type in option.aliases), TILE_OPTIONS[0]),
        zoom=args.zoom,
        range=tuple(args.range)
    )

def get_response_with_dynamic_wait_retry(url: str, max_retries: int = 5) -> Optional[requests.Response]:
    global _wait_sec
    for _ in range(max_retries):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                _wait_sec = max(1.0, _wait_sec * 0.9)  # decrease wait time on success
                return response
            else:
                print(f"Error: Received status code {response.status_code}. Retrying in {_wait_sec:.2f} seconds...")
        except requests.RequestException as e:
            print(f"Request failed: {e}. Retrying in {_wait_sec:.2f} seconds...")
        time.sleep(_wait_sec)
        _wait_sec *= 1.5  # increase wait time on failure
    print("Max retries reached. Failed to get a successful response.")
    return None

def lnglat_to_tile_coords(lng: float, lat: float, z: int) -> Tuple[int, int]:
    if z == 0:
        return 0, 0
    n = 2.0 ** z
    deg2rad = math.pi / 180.0
    lon = max(-179.99999999, min(179.99999999, lng)) # prevent overflow
    lon_n = lon / 360.0 + 0.5
    lat = max(-85.0511, min(85.0511, lat)) # prevent overflow
    lat_rad = lat * deg2rad
    tan_lat = math.tan(lat_rad)
    sec_lat = 1 / math.cos(lat_rad)
    lat_n = (1 - math.log(tan_lat + sec_lat) / math.pi) / 2.0
    x = int(n * lon_n)
    y = int(n * lat_n)
    return x, y

def get_tile_coords_list(tile_range: TileRange, zoom: int) -> List[Tuple[int, int]]:
    minlon, minlat, maxlon, maxlat = tile_range
    tile_side_count: int = 2 ** zoom
    if tile_range == MAX_RANGE:
        return [(x, y) for x in range(tile_side_count) for y in range(tile_side_count)]
    else:
        x1, y1 = lnglat_to_tile_coords(minlon, minlat, zoom)
        x2, y2 = lnglat_to_tile_coords(maxlon, maxlat, zoom)
        minx, miny = min(x1, x2), min(y1, y2)
        maxx, maxy = max(x1, x2), max(y1, y2)
        if minx < 0 or miny < 0 or maxx >= tile_side_count or maxy >= tile_side_count:
            print("Coordinates are out of bounds.")
            return []
        print(f"Tile coordinates: ({minx}, {miny}) to ({maxx}, {maxy})")
        return [(x, y) for x in range(minx, maxx + 1) for y in range(miny, maxy + 1)]

def download_one_tile(args: Arguments, x: int, y: int) -> int:
    tile_dir: str = os.path.join(args.dir, str(args.zoom), str(x))
    tile_path: str = os.path.join(tile_dir, f"{y}.{args.option.ext}")
    if os.path.exists(tile_path):
        return 0 # tile already exists, will skip downloading
    url: str = URL_TEMPLATE.format(t=args.option.name, z=args.zoom, x=x, y=y, e=args.option.ext, k=args.key)
    response: Optional[requests.Response] = get_response_with_dynamic_wait_retry(url)
    if response is not None:
        os.makedirs(tile_dir, exist_ok=True)
        with open(tile_path, "wb") as f:
            f.write(response.content)
        return response.status_code # return status code in case of success
    return -1 # failed to download after retries, tile not downloaded

def download_tiles(args: Arguments):
    tile_coords: List[Tuple[int, int]] = get_tile_coords_list(args.range, args.zoom)
    len_tiles = len(tile_coords) # number of tiles to download
    if len_tiles == 0:
        print("No tiles to download.")
        return
    len_digits = len(str(len_tiles)) # number of digits in the number of tiles
    side_digits = len(str(2 ** args.zoom)) # number of digits in the side count
    print(f"Downloading {len_tiles} tiles for zoom level {args.zoom}...")
    downloaded_count = 0
    for i, (x, y) in enumerate(tile_coords):
        tile_progress = f"{i + 1:>{len_digits}}/{len_tiles:>{len_digits}}"
        tile_coords_progress = f"({x:>{side_digits}}, {y:>{side_digits}})"
        print(f"\tDownloading {tile_progress}: {tile_coords_progress}... ", end="")
        status_code = download_one_tile(args, x, y)
        if status_code == 0: # tile already exists, skip it
            print(f"SKP", end="\r")
            continue
        elif status_code == 200: # tile downloaded successfully
            downloaded_count += 1
            print(f"OK ", end="\r")
        else: # error message and a new line
            print(f"\r\tError downloading tile {args.zoom:>2}/{x:>{side_digits}}/{y:>{side_digits}}: {status_code}{' ':>{side_digits}}")
        time.sleep(_wait_sec) # wait before next request
    print(f"\n...{downloaded_count} new tiles downloaded.")

if __name__ == "__main__":
    args: Arguments = parse_arguments()
    if not os.path.exists(args.dir):
        print(f"Directory {args.dir} does not exist. Creating it...")
        os.makedirs(args.dir)
    download_tiles(args)
    print("Done.")