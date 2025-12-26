# MapTilerDL: Scripts to Download MapTiler Tiles and Fonts
This repository contains Python scripts to download map tiles and font files from the MapTiler API for offline use. The repository includes two main scripts: [`tiledl.py`](./tiledl.py) for downloading map tiles and [`fontdl.py`](./fontdl.py) for downloading font files.

## Tile Downloader Usage
### Argument Table
| Argument | Description | Default | Required |
|-----------|-------------|---------|---------|
| `--key` / `-k`   | Your MapTiler API key. | `get_your_own_OpIi9ZULNHzrESv6T2vL` | Yes |
| `--dir` / `-d`   | The directory where the downloaded tiles will be saved. | `./tiles` | No |
| `--type` / `-t`  | The type of tiles to download,<br> (e.g., `sat`, `cnt`, `trgb`). | `sat` | No |
| `--zoom` / `-z`  | The zoom level of the tiles to download. | `0` | No |
| `--bounds` / `-b` | The bounding box for tiles,<br> specified as `minlon minlat maxlon maxlat`. | `-180 -90 180 90` | No |
| `--config` / `-c` | Path to a [configuration file](#configuration-file) for batch download of different zoom / bounding box settings. | `""` | No |
| `--help` / `-h`   | Show help message and exit. | N/A | N/A |

To download a specific zoom level of tiles from MapTiler API, you can use the following command:
```bash
python3 tiledl.py -k <API_KEY> -d <dir> -t <type> -z <zoom> -b <bounds>
```
### Supported Tile Types
| Tile Type | Description | Alias | Extension |
|----------|-------------|------------------|---------|
| `satellite-v2` | Satellite imagery tiles | `sat`, `satellite`, `satellitev2`, `satellite-v2` | `jpg` |
| `contours-v2` | Contour lines tiles | `cnt`, `contours`, `contoursv2`, `contours-v2` | `pbf` |
| `terrain-rgb-v2` | Terrain RGB tiles | `trgb`, `terrain`, `terrainrgb`, `terrain-rgb`, `terrainrgbv2`, `terrain-rgb-v2` | `webp` |
| `v3` | MapTiler Planet v3 tiles | `v3`, `v3tiles`, `v3-tiles`, `tilesv3`, `tiles-v3` | `pbf` |
| `v4` | MapTiler Planet v4 tiles | `v4`, `v4tiles`, `v4-tiles`, `tilesv4`, `tiles-v4` | `pbf` |
| `landform` | Landform tiles | `landform`, `lf`, `landforms`, `lfs` | `pbf` |

### Configuration File
You can create a configuration file to specify multiple zoom levels and bounding boxes for batch downloading. The configuration file should be in comma-separated `csv` format with headers `zoom,minlon,minlat,maxlon,maxlat`.
- **Edit in Excel**
    | zoom | minlon | minlat | maxlon | maxlat |
    |------|--------|--------|--------|--------|
    | 0    | -180   | -90    | 180    | 90    |
    | ...  | ...    | ...    | ...    | ...    |
- **Edit in Text Editor**
    ```csv
    zoom,minlon,minlat,maxlon,maxlat
    0,-180,-90,180,90
    ...,...,...,...,...
    ```
Some example configuration files are provided in this repository for downloading tiles for Singapore. They are:
- [sg_sat.csv](./configs/sg_sat.csv): Configuration file for downloading `satellite` tiles for Singapore.
- [sg_cnt.csv](./configs/sg_cnt.csv): Configuration file for downloading `contour` tiles for Singapore.
- [sg_trgb.csv](./configs/sg_trgb.csv): Configuration file for downloading `terrain-rgb` tiles for Singapore.
- [sg_vx.csv](./configs/sg_vx.csv): Configuration file for downloading `v3` or `v4` tiles for Singapore.
- [sg_lf.csv](./configs/sg_lf.csv): Configuration file for downloading `landform` tiles for Singapore.

#### *Important Notes*
- When using a configuration file, the `--zoom` and `--bounds` arguments will be ignored.
- When creating a configuration file, ***only*** include the zoom levels and bounding boxes that are ***available for the selected tile type***. Some tile types may not have data for all zoom levels or regions.
- Make sure header names are correct and there are no extra spaces.

### Examples
1. To download all satellite tiles at zoom level 2 at the `./tiles` folder, you would run:
    ```bash
    python3 tiledl.py -k <API_KEY> -z 2
    ```
2. To download contour tiles at zoom level 5 for a specific bounding box (`-10 -10 10 10`) and save them in a custom directory(`./contour_tiles`), you would run:
    ```bash
    python3 tiledl.py -k <API_KEY> -d ./contour_tiles -t cnt -z 5 -b -10 -10 10 10
    ```
3. To download landform tiles at zoom level 8 using the provided config file ([sg_lf.csv](./configs/sg_lf.csv)) and save them in a custom directory(`~/tiles/landform`), you would run:
    ```bash
    python3 tiledl.py -k <API_KEY> -d ~/tiles/landform -t lf -c ./configs/sg_lf.csv
    ```
### Download Tile Data for Singapore
To download tiles for a region, at different zoom levels different bounding boxes should be used. Here are example bounding boxes for different zoom levels in Singapore:
- For zoom levels `0` to `6`, the tiles for the entire globe should be downloaded.
- For zoom levels `7` to `9`, the tiles should be downloaded based on the specified bounding box `80 -20 120 20`.
- For zoom levels `10` to `12`, the tiles should be downloaded based on the specified bounding box `102 -1 106 3`.
- For zoom levels `13` to `15`, the tiles should be downloaded based on the specified bounding box `103.5 0.9 104.2 1.6`.
- For zoom levels `16` onwards (if applicable), the tiles should be downloaded based on the specified bounding box `103.6920359 1.1304753 104.0120359 1.4504753`.

Example command to download the `sat` tiles for Singapore using the provided config file ([sg_sat.csv](./configs/sg_sat.csv)) and save them in the `~/tiles/sat` directory:
```bash
python3 tiledl.py -k <API_KEY> -d ~/tiles/sat -t sat -c ./configs/sg_sat.csv
```

Example command to download the `v4` tiles manually without using a configuration file for Singapore at different zoom levels under the `~/tiles/v4` directory:
```bash
# for zoom levels 0 to 6
python3 tiledl.py -k <API_KEY> -d ~/tiles/v4 -t v4 -z 0
# repeat the above command changing zoom level from 1 to 6

# for zoom levels 7 to 9
python3 tiledl.py -k <API_KEY> -d ~/tiles/v4 -t v4 -z 7 -b 80 -20 120 20
# repeat the above command changing zoom level from 7 to 9

# for zoom levels 10 to 12
python3 tiledl.py -k <API_KEY> -d ~/tiles/v4 -t v4 -z 10 -b 102 -1 106 3
# repeat the above command changing zoom level from 10 to 12

# for zoom levels 13 to 15
python3 tiledl.py -k <API_KEY> -d ~/tiles/v4 -t v4 -z 13 -b 103.5 0.9 104.2 1.6
# repeat the above command changing zoom level from 13 to 15

# for zoom level 16 onwards
python3 tiledl.py -k <API_KEY> -d ~/tiles/v4 -t v4 -z 16 -b 103.6920359 1.1304753 104.0120359 1.4504753
# repeat the above command changing zoom level from 16 onwards
```
## Font Downloader Usage
### Argument Table
| Argument | Description | Default | Required |
|-----------|-------------|---------|---------|
| `--key` / `-k`   | Your MapTiler API key. | `get_your_own_OpIi9ZULNHzrESv6T2vL` | Yes |
| `--dir` / `-d`   | The directory where the downloaded fonts will be saved. | `./fonts` | No |
| `--fonts` / `-f`  | Space-separated list of font names to download,<br>if there is a space in the font's name, enclose it in quotes. | `'Noto Sans Regular' 'Noto Sans Italic' 'Noto Sans Bold'` | No |
| `--config` / `-c` | Path to a [configuration file](#configuration-file-1) for batch downloading fonts. | `""` | No |
| `--help` / `-h`   | Show help message and exit. | N/A | N/A |

To download specific font tiles from MapTiler API, you can use the following command:
```bash
python3 fontdl.py -k <API_KEY> -d <dir> -f <font1> <font2> ...
```
### Configuration File
You can create a configuration file to specify multiple font names for batch downloading. The configuration file should contain one font name per line.
- **Edit in Text Editor**
    ```
    Noto Sans Regular
    Noto Sans Italic
    Noto Sans Bold
    ...
    ```
Some example configuration files are provided in this repository for downloading different font stacks. They are:
- [sat.txt](./fontlists/sat.txt): Configuration file for downloading the fonts needed for the `satellite` map style.
- [vx.txt](./fontlists/vx.txt): Configuration file for downloading the fonts needed for the `v3` or `v4` map styles.
#### *Important Notes*
- When using a configuration file, the `--fonts` argument will be ignored.
- Make sure to only include valid font names that are available in the MapTiler API.
### Examples
1. To download the default fonts (`Noto Sans Regular`, `Noto Sans Italic`, `Noto Sans Bold`) from MapTiler API and save them in the `./fonts` folder, you would run:
    ```bash
    python3 fontdl.py -k <API_KEY>
    ```
2. To download specific fonts such as `Noto Sans Bold` and `Noto Sans Italic` and save them in a custom directory(`./my_fonts`), you would run:
    ```bash
    python3 fontdl.py -k <API_KEY> -d ./my_fonts -f "Noto Sans Bold" "Noto Sans Italic"
    ```
3. To download fonts using the provided config file ([vx.txt](./fontlists/vx.txt)) and save them in the `~/fonts/vx` directory, you would run:
    ```bash
    python3 fontdl.py -k <API_KEY> -d ~/fonts/vx -c ./fontlists/vx.txt
    ```