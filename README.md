### A Script to Download MapTiler Tiles by Zoom Level

***Before running the script, please modify it to include your own API key!***

To download a specific zoom level of tiles from MapTiler API, you can use the following command:
```bash
python3 tiledl.py dir type zoom
```
where `zoom` is the zoom level you want to download. For example, to download satellite tiles at zoom level 10 at the current directory under `tiles` folder, you would run:
```bash
python3 tiledl.py tiles sat 10
```
### TileDL Download by Bounding Box at Specific Zoom Level
To download tiles within a specific bounding box at a specific zoom level, you can use the following command:
```bash
python3 tiledl.py dir type zoom --minlon --minlat --maxlon --maxlat
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

| Tile Type | Description | Alternative Name |
|----------|-------------|------------------|
| `satellite-v2` | Satellite imagery tiles | `sat`, `satellite`, `satellitev2`, `satellite-v2` |
| `contours-v2` | Contour lines tiles | `cnt`, `contours`, `contoursv2`, `contours-v2` |
| `terrain-rgb-v2` | Terrain RGB tiles | `trgb`, `terrain`, `terrainrgb`, `terrain-rgb`, `terrainrgbv2`, `terrain-rgb-v2` |
| `v3` | MapTiler v3 tiles | `v3`, `v3tiles`, `v3-tiles` |
### Example Command
To download tiles of type `sat` at zoom level `10` within a bounding box defined by the coordinates `(min_lon, min_lat) = (0, 0)` and `(max_lon, max_lat) = (1, 1)` under a folder named `test`, you would run:
```bash
python3 tiledl.py test sat 10 --minlon 0 --minlat 0 --maxlon 1 --maxlat 1
```
** Note:** The bounding box coordinates should be in radians. The script will automatically calculate the tile numbers based on the provided bounding box and zoom level.
### Downloaded Sample Data
The downloaded sample data is stored in the `tiles` directory, they are satellite tiles of the specified zoom levels in `.jpg` format.
- For zoom levels `0` to `6`, the tiles for the entire globe is downloaded.
- For zoom levels `7` to `9`, the tiles are downloaded based on the specified bounding box `80 -20 120 20`.
- For zoom levels `10` to `12`, the tiles are downloaded based on the specified bounding box `102 -1 106 3`.
- For zoom levels `13` to `15`, the tiles are downloaded based on the specified bounding box `103.5 0.9 104.2 1.6`.
- For zoom levels `16` onwards (if applicable), the tiles are downloaded based on the specified bounding box `103.6920359 1.1304753 104.0120359 1.4504753`.