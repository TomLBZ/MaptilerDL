### A Script to Download MapTiler Tiles by Zoom Level

To download a specific zoom level of tiles from MapTiler API, you can use the following command:
```bash
python3 tiledl.py dir type zoom --key <API_KEY>
```
where `zoom` is the zoom level you want to download. For example, to download satellite tiles at zoom level 10 at the current directory under `tiles` folder, you would run:
```bash
python3 tiledl.py tiles sat 10 --key <API_KEY>
```
### TileDL Download by Bounding Box at Specific Zoom Level
To download tiles within a specific bounding box at a specific zoom level, you can use the following command:
```bash
python3 tiledl.py dir type zoom --minlon --minlat --maxlon --maxlat --key <API_KEY>
```
where:
| Parameter | Description |
|-----------|-------------|
| `dir`    | The directory where the downloaded tiles will be saved. |
| `type`    | The type of tiles to download (e.g., `sat`, `cnt`, `trgb`). |
| `zoom`    | The zoom level of the tiles to download. |
| `--minlon` | The minimum longitude of the bounding box. |
| `--minlat` | The minimum latitude of the bounding box. |
| `--maxlon` | The maximum longitude of the bounding box. |
| `--maxlat` | The maximum latitude of the bounding box. |
| `--key`    | Your MapTiler API key. |
### Supported Tile Types
| Tile Type | Description | Alternative Name |
|----------|-------------|------------------|
| `satellite-v2` | Satellite imagery tiles | `sat`, `satellite`, `satellitev2`, `satellite-v2` |
| `contours-v2` | Contour lines tiles | `cnt`, `contours`, `contoursv2`, `contours-v2` |
| `terrain-rgb-v2` | Terrain RGB tiles | `trgb`, `terrain`, `terrainrgb`, `terrain-rgb`, `terrainrgbv2`, `terrain-rgb-v2` |
| `v3` | MapTiler v3 tiles | `v3`, `v3tiles`, `v3-tiles` |
| `v4` | MapTiler v4 tiles | `v4`, `v4tiles`, `v4-tiles` |
### Example Command
To download tiles of type `sat` at zoom level `10` within a bounding box defined by the coordinates `(min_lon, min_lat) = (0, 0)` and `(max_lon, max_lat) = (1, 1)` under a folder named `test`, you would run:
```bash
python3 tiledl.py test sat 10 --minlon 0 --minlat 0 --maxlon 1 --maxlat 1 --key <API_KEY>
```
### Download Sample Data for Singapore
To download tiles for a region, at different zoom levels different bounding boxes should be used. Here are example bounding boxes for different zoom levels in Singapore:
- For zoom levels `0` to `6`, the tiles for the entire globe should be downloaded.
- For zoom levels `7` to `9`, the tiles should be downloaded based on the specified bounding box `80 -20 120 20`.
- For zoom levels `10` to `12`, the tiles should be downloaded based on the specified bounding box `102 -1 106 3`.
- For zoom levels `13` to `15`, the tiles should be downloaded based on the specified bounding box `103.5 0.9 104.2 1.6`.
- For zoom levels `16` onwards (if applicable), the tiles should be downloaded based on the specified bounding box `103.6920359 1.1304753 104.0120359 1.4504753`.

Example command to download the `v4` tiles for Singapore at different zoom levels:
```bash
# for zoom levels 0 to 6
python3 tiledl.py ~/tiles v4 0 --minlon -180 --minlat -90 --maxlon 180 --maxlat 90 --key <API_KEY>
# repeat the above command changing zoom level from 1 to 6

# for zoom levels 7 to 9
python3 tiledl.py ~/tiles v4 7 --minlon 80 --minlat -20 --maxlon 120 --maxlat 20 --key <API_KEY>
# repeat the above command changing zoom level from 7 to 9

# for zoom levels 10 to 12
python3 tiledl.py ~/tiles v4 10 --minlon 102 --minlat -1 --maxlon 106 --maxlat 3 --key <API_KEY>
# repeat the above command changing zoom level from 10 to 12

# for zoom levels 13 to 15
python3 tiledl.py ~/tiles v4 13 --minlon 103.5 --minlat 0.9 --maxlon 104.2 --maxlat 1.6 --key <API_KEY>
# repeat the above command changing zoom level from 13 to 15

# for zoom level 16 onwards
python3 tiledl.py ~/tiles v4 16 --minlon 103.6920359 --minlat 1.1304753 --maxlon 104.0120359 --maxlat 1.4504753 --key <API_KEY>
# repeat the above command changing zoom level from 16 onwards
```