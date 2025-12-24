import requests
import os
import time
import argparse
import math
from typing import Optional, Tuple, List
from dataclasses import dataclass

# types, classes and data structures:
type TileBounds = Tuple[float, float, float, float] # (minlon, minlat, maxlon, maxlat)
@dataclass(frozen=True, slots=True, kw_only=True)
class TileOption:
    name: str
    ext: str
    aliases: List[str]
@dataclass(frozen=True, slots=True, kw_only=True)
class LevelConfig:
    zoom: int
    bounds: TileBounds
@dataclass(frozen=True, slots=True, kw_only=True)
class TileDLArguments:
    key: str
    dir: str
    option: TileOption
    zoom: int
    bounds: TileBounds
    config: str = ""
@dataclass(frozen=True, slots=True, kw_only=True)
class BackoffConfig:
    initial_wait: float = 1.0
    max_wait: float = 60.0
    min_wait: float = 1.0
    fail_factor: float = 1.5
    success_factor: float = 0.9
    max_retries: int = 5
    timeout: int = 5
@dataclass(frozen=False, slots=True, kw_only=True)
class GlobalVariables:
    wait_sec: float = 1.0
    downloaded_count: int = 0
    total_downloaded_count: int = 0

# constants:
MIN_LON: float = -179.99999999
MAX_LON: float = 179.99999999
MIN_LAT: float = -85.0511
MAX_LAT: float = 85.0511
MAX_BOUNDS: TileBounds = (MIN_LON, MIN_LAT, MAX_LON, MAX_LAT)
URL_TEMPLATE: str = "https://api.maptiler.com/tiles/{t}/{z}/{x}/{y}.{e}?key={k}"
TILE_OPTIONS: List[TileOption] = [
    TileOption(name="satellite-v2", ext="jpg", aliases=["satellite", "satellite-v2", "satellitev2", "sat"]),
    TileOption(name="contours-v2", ext="pbf", aliases=["contours", "contours-v2", "contoursv2", "cnt"]),
    TileOption(name="terrain-rgb-v2", ext="webp", aliases=["terrain", "terrainrgb", "terrain-rgb", "terrain-rgb-v2", "terrainrgbv2", "trgb"]),
    TileOption(name="v3", ext="pbf", aliases=["v3", "v3tiles", "v3-tiles", "tilesv3", "tiles-v3"]),
    TileOption(name="v4", ext="pbf", aliases=["v4", "v4tiles", "v4-tiles", "tilesv4", "tiles-v4"]),
    TileOption(name="landform", ext="pbf", aliases=["landform", "lf", "landforms", "lfs"]),
]
TYPE_CHOICES: List[str] = [alias for option in TILE_OPTIONS for alias in option.aliases]

def parse_arguments() -> TileDLArguments:
    parser = argparse.ArgumentParser(description="Download tiles from MapTiler.")
    # required arguments: key
    parser.add_argument("-k", "--key", type=str, required=True, default="get_your_own_OpIi9ZULNHzrESv6T2vL", help="Your MapTiler API key.")
    # optional arguments: dir, type, zoom, bounds, config
    parser.add_argument("-d", "--dir", type=str, default="./tiles", help="Directory to save tiles")
    parser.add_argument("-t", "--type", type=str, choices=TYPE_CHOICES, metavar="TYPE", 
                        default="sat", help="Map Type (sat, v4, etc.)")
    parser.add_argument("-z", "--zoom", type=int, choices=range(0, 23), metavar="ZOOM", 
                        default=0, help="Zoom level (0-22), recommended 0-15")
    parser.add_argument("-b", "--bounds", type=float, nargs=4, metavar=("MINLON", "MINLAT", "MAXLON", "MAXLAT"), 
                        default=MAX_BOUNDS, help="Bounding box to download tiles")
    parser.add_argument("-c", "--config", type=str, default="", help="Path to configuration file")
    args = parser.parse_args()
    return TileDLArguments(
        key=args.key,
        dir=args.dir,
        option=next((option for option in TILE_OPTIONS if args.type in option.aliases), TILE_OPTIONS[0]),
        zoom=args.zoom,
        bounds=tuple(args.bounds),
        config=args.config
    )
def load_config(path: str) -> List[LevelConfig]:
    file_content: str # file content is a csv with headers: zoom,minlon,minlat,maxlon,maxlat
    try:
        with open(path, "r") as f:
            file_content = f.read()
    except Exception as e:
        print(f"Error reading configuration file: {e}")
        return []
    lines = file_content.strip().splitlines()
    if len(lines) < 2:
        print("Configuration file is empty or has no data.")
        return []
    headers = lines[0].split(",")
    expected_headers = ["zoom", "minlon", "minlat", "maxlon", "maxlat"]
    if [h.strip().lower() for h in headers] != expected_headers:
        print("Configuration file has invalid headers.")
        return []
    level_configs: List[LevelConfig] = []
    for line in lines[1:]:
        parts = line.split(",")
        if len(parts) != 5:
            print(f"Invalid line in configuration file: {line}")
            continue
        try:
            zoom = int(parts[0].strip())
            minlon = float(parts[1].strip())
            minlat = float(parts[2].strip())
            maxlon = float(parts[3].strip())
            maxlat = float(parts[4].strip())
            level_configs.append(LevelConfig(zoom=zoom, bounds=(minlon, minlat, maxlon, maxlat)))
        except ValueError as e:
            print(f"Error parsing line in configuration file: {line}. Error: {e}")
            continue
    return level_configs
def get_response_dynamic_backoff(gvar: GlobalVariables, bcfg: BackoffConfig, url: str) -> Optional[requests.Response]:
    for _ in range(bcfg.max_retries):
        try:
            response = requests.get(url, timeout=bcfg.timeout)
            if response.status_code == 200:
                gvar.wait_sec = max(bcfg.min_wait, gvar.wait_sec * bcfg.success_factor)  # decrease wait time on success
                return response
            else:
                print(f"\n\tError {response.status_code}.")
                print(f"\tRetrying in {gvar.wait_sec:.2f} seconds... ", end="", flush=True)
        except requests.Timeout:
            print(f"\n\tRequest timed out after {bcfg.timeout} seconds.")
            print(f"\tRetrying in {gvar.wait_sec:.2f} seconds... ", end="", flush=True)
        except requests.RequestException as e:
            print(f"\n\t{e}.")
            print(f"\tRetrying in {gvar.wait_sec:.2f} seconds... ", end="", flush=True)
        time.sleep(gvar.wait_sec)
        gvar.wait_sec = min(bcfg.max_wait, gvar.wait_sec * bcfg.fail_factor)  # increase wait time on failure
    print("\n\tMax retries reached.")
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
def get_tile_coords_list(bounds: TileBounds, zoom: int) -> List[Tuple[int, int]]:
    minlon, minlat, maxlon, maxlat = bounds
    tile_side_count: int = 2 ** zoom
    if bounds == MAX_BOUNDS:
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
def download_one_tile(gvar: GlobalVariables, args: TileDLArguments, bcfg: BackoffConfig, x: int, y: int) -> int:
    tile_dir: str = os.path.join(args.dir, str(args.zoom), str(x))
    tile_path: str = os.path.join(tile_dir, f"{y}.{args.option.ext}")
    if os.path.exists(tile_path):
        return 0 # tile already exists, will skip downloading
    url: str = URL_TEMPLATE.format(t=args.option.name, z=args.zoom, x=x, y=y, e=args.option.ext, k=args.key)
    response: Optional[requests.Response] = get_response_dynamic_backoff(gvar, bcfg, url)
    if response is not None:
        os.makedirs(tile_dir, exist_ok=True)
        with open(tile_path, "wb") as f:
            f.write(response.content)
        return response.status_code # return status code in case of success
    return -1 # failed to download after retries, tile not downloaded
def download_tiles(gvar: GlobalVariables, args: TileDLArguments, bcfg: BackoffConfig) -> None:
    tile_coords: List[Tuple[int, int]] = get_tile_coords_list(args.bounds, args.zoom)
    len_tiles = len(tile_coords) # number of tiles to download
    if len_tiles == 0:
        print("No tiles to download.")
        return
    len_digits = len(str(len_tiles)) # number of digits in the number of tiles
    side_digits = len(str(2 ** args.zoom)) # number of digits in the side count
    print(f"Downloading {len_tiles} tiles for zoom level {args.zoom}...")
    for i, (x, y) in enumerate(tile_coords):
        tile_progress = f"{i + 1:>{len_digits}}/{len_tiles:>{len_digits}}"
        tile_coords_progress = f"({x:>{side_digits}}, {y:>{side_digits}})"
        print(f"\033[2K\tDownloading {tile_progress}: {tile_coords_progress}... ", end="", flush=True)
        status_code = download_one_tile(gvar, args, bcfg, x, y)
        if status_code == 0: # tile already exists, skip it
            print(f"SKP", end="\r")
            continue
        elif status_code == 200: # tile downloaded successfully
            gvar.downloaded_count += 1
            print(f"OK ", end="\r")
        else: # error message and a new line
            print(f"\r\tError downloading tile {args.zoom:>2}/{x:>{side_digits}}/{y:>{side_digits}}: {status_code}{' ':>{side_digits}}")
        time.sleep(gvar.wait_sec) # wait before next request
    print(f"\n\t...{gvar.downloaded_count} new tiles downloaded.")

if __name__ == "__main__":
    args: TileDLArguments = parse_arguments()
    if not os.path.exists(args.dir):
        print(f"Directory {args.dir} does not exist. Creating it...")
        os.makedirs(args.dir)
    if not os.access(args.dir, os.W_OK):
        print(f"Directory {args.dir} is not writable. Exiting.")
        exit(1)
    level_configs: List[LevelConfig] = []
    bcfg: BackoffConfig = BackoffConfig()
    gvars: GlobalVariables = GlobalVariables()
    if args.config != "":
        if not os.path.exists(args.config):
            print(f"Configuration file {args.config} does not exist. Exiting.")
            exit(1)
        if not os.access(args.config, os.R_OK):
            print(f"Configuration file {args.config} is not readable. Exiting.")
            exit(1)
        print(f"Configuration file {args.config} is provided. Loading it...")
        level_configs = load_config(args.config)
        if not level_configs or len(level_configs) == 0:
            print("No valid level configurations found. Exiting.")
            exit(1)
        print(f"Loaded {len(level_configs)} level configurations from {args.config}.")
    else:
        level_configs = [LevelConfig(zoom=args.zoom, bounds=args.bounds)]
    for level in level_configs:
        current_arguments: TileDLArguments = TileDLArguments(
            key=args.key,
            dir=args.dir,
            option=args.option,
            zoom=level.zoom,
            bounds=level.bounds,
            config=args.config
        )
        print(f"Processing zoom level {level.zoom} with bounds {level.bounds}...")
        try:
            download_tiles(gvars, current_arguments, bcfg)
            gvars.total_downloaded_count += gvars.downloaded_count
            gvars.downloaded_count = 0 # reset for next level
        except KeyboardInterrupt:
            print(f"\n\t...{gvars.downloaded_count} new tiles downloaded.\nInterrupted by user.")
            exit(0)
    print(f"\nDone. Total new tiles downloaded: {gvars.total_downloaded_count}.")