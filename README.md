# MapTilerDL: A Script to Download MapTiler Tiles
This script allows you to download map tiles from the MapTiler API for offline use. You can specify the type of tiles, zoom level, bounding box, and output directory.

## Usage
### Argument Table
| Argument | Description | Default | Required |
|-----------|-------------|---------|---------|
| `--key` / `-k`   | Your MapTiler API key. | `get_your_own_OpIi9ZULNHzrESv6T2vL` | Yes |
| `--dir` / `-d`   | The directory where the downloaded tiles will be saved. | `./tiles` | No |
| `--type` / `-t`  | The type of tiles to download,<br> (e.g., `sat`, `cnt`, `trgb`). | `sat` | No |
| `--zoom` / `-z`  | The zoom level of the tiles to download. | `0` | No |
| `--range` / `-r` | The bounding box for tiles,<br> specified as `minlon minlat maxlon maxlat`. | `-180 -90 180 90` | No |
| `--help` / `-h`   | Show help message and exit. | N/A | N/A |

To download a specific zoom level of tiles from MapTiler API, you can use the following command:
```bash
python3 tiledl.py -k <API_KEY> -d <dir> -t <type> -z <zoom> -r <range>
```
### Supported Tile Types
| Tile Type | Description | Alias | Extension |
|----------|-------------|------------------|---------|
| `satellite-v2` | Satellite imagery tiles | `sat`, `satellite`, `satellitev2`, `satellite-v2` | `jpg` |
| `contours-v2` | Contour lines tiles | `cnt`, `contours`, `contoursv2`, `contours-v2` | `pbf` |
| `terrain-rgb-v2` | Terrain RGB tiles | `trgb`, `terrain`, `terrainrgb`, `terrain-rgb`, `terrainrgbv2`, `terrain-rgb-v2` | `webp` |
| `v3` | MapTiler Planet v3 tiles | `v3`, `v3tiles`, `v3-tiles`, `tilesv3`, `tiles-v3` | `pbf` |
| `v4` | MapTiler Planet v4 tiles | `v4`, `v4tiles`, `v4-tiles`, `tilesv4`, `tiles-v4` | `pbf` |

### Examples
1. To download all satellite tiles at zoom level 2 at the `./tiles` folder, you would run:
    ```bash
    python3 tiledl.py -k <API_KEY> -z 2
    ```
2. To download contour tiles at zoom level 5 for a specific bounding box (`-10 -10 10 10`) and save them in a custom directory(`./contour_tiles`), you would run:
    ```bash
    python3 tiledl.py -k <API_KEY> -d ./contour_tiles -t cnt -z 5 -r -10 -10 10 10
    ```
## Download Tile Data for Singapore
To download tiles for a region, at different zoom levels different bounding boxes should be used. Here are example bounding boxes for different zoom levels in Singapore:
- For zoom levels `0` to `6`, the tiles for the entire globe should be downloaded.
- For zoom levels `7` to `9`, the tiles should be downloaded based on the specified bounding box `80 -20 120 20`.
- For zoom levels `10` to `12`, the tiles should be downloaded based on the specified bounding box `102 -1 106 3`.
- For zoom levels `13` to `15`, the tiles should be downloaded based on the specified bounding box `103.5 0.9 104.2 1.6`.
- For zoom levels `16` onwards (if applicable), the tiles should be downloaded based on the specified bounding box `103.6920359 1.1304753 104.0120359 1.4504753`.

Example command to download the `v4` tiles for Singapore at different zoom levels under the `~/tiles/v4` directory:
```bash
# for zoom levels 0 to 6
python3 tiledl.py -k <API_KEY> -d ~/tiles/v4 -t v4 -z 0
# repeat the above command changing zoom level from 1 to 6

# for zoom levels 7 to 9
python3 tiledl.py -k <API_KEY> -d ~/tiles/v4 -t v4 -z 7 -r 80 -20 120 20
# repeat the above command changing zoom level from 7 to 9

# for zoom levels 10 to 12
python3 tiledl.py -k <API_KEY> -d ~/tiles/v4 -t v4 -z 10 -r 102 -1 106 3
# repeat the above command changing zoom level from 10 to 12

# for zoom levels 13 to 15
python3 tiledl.py -k <API_KEY> -d ~/tiles/v4 -t v4 -z 13 -r 103.5 0.9 104.2 1.6
# repeat the above command changing zoom level from 13 to 15

# for zoom level 16 onwards
python3 tiledl.py -k <API_KEY> -d ~/tiles/v4 -t v4 -z 16 -r 103.6920359 1.1304753 104.0120359 1.4504753
# repeat the above command changing zoom level from 16 onwards
```