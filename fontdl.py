# url example for font tiles:
# https://api.maptiler.com/fonts/{font}/{range}.pbf?key={key}
# fonts such as: noto-sans-bold
# range such as: 5120-5375
# each font file is 256 glyphs, each font stack has 256 files
# for example, to download noto-sans-bold font stack, we need files from 0-255, 256-511, ..., up to 65280-65535
# key such as: QOCNp1pWErFc8sgXrGwI
import requests
import os
import time
import argparse
from typing import Optional, Tuple, List
from dataclasses import dataclass

# constants:
URL_TEMPLATE: str = "https://api.maptiler.com/fonts/{font}/{range}.pbf?key={key}"
DEFAULT_FONTS: List[str] = ["noto-sans-regular", "noto-sans-italic", "noto-sans-bold"]
# types, classes and data structures:
@dataclass(frozen=True, slots=True, kw_only=True)
class FontDLArguments:
    key: str
    dir: str
    fonts: List[str]
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
    current_range_begin: int = 0
    current_range_end: int = 0
    current_fontname: str = ""

def justify_fontname(fontname: str) -> str: # input fontname such as "Noto Sans Bold", output "noto-sans-bold"
    return fontname.lower().replace(" ", "-")
def parse_arguments() -> FontDLArguments:
    parser = argparse.ArgumentParser(description="Download font tiles from MapTiler API.")
    parser.add_argument("-k", "--key", type=str, required=True, default="get_your_own_OpIi9ZULNHzrESv6T2vL", help="Your MapTiler API key.")
    parser.add_argument("-d", "--dir", type=str, default="./fonts", help="Directory to save downloaded font files.")
    parser.add_argument("-f", "--fonts", type=str, default=DEFAULT_FONTS, nargs='+', help="Font stack name(s) to download (e.g., 'Noto Sans Bold').")
    args = parser.parse_args()
    return FontDLArguments(
        key=args.key,
        dir=args.dir,
        fonts=[justify_fontname(fn) for fn in args.fonts]
    )
def restore_fontname(fontname: str) -> str: # input fontname such as "noto-sans-bold", output "Noto Sans Bold"
    return " ".join([word.capitalize() for word in fontname.split("-")])
def get_response_dynamic_backoff(gvar: GlobalVariables, bcfg: BackoffConfig, url: str) -> Optional[requests.Response]:
    for _ in range(bcfg.max_retries):
        try:
            response = requests.get(url, timeout=bcfg.timeout)
            if response.status_code == 200:
                gvar.wait_sec = max(bcfg.min_wait, gvar.wait_sec * bcfg.success_factor)  # decrease wait time on success
                return response
            elif response.status_code == 204:
                print(f"\n\tNo content (204), skipping this tile.")
                return None
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
def download_one_pbf(gvar: GlobalVariables, args: FontDLArguments, bcfg: BackoffConfig) -> int:
    font_dir: str = os.path.join(args.dir, restore_fontname(gvar.current_fontname))
    tile_path: str = os.path.join(font_dir, f"{gvar.current_range_begin}-{gvar.current_range_end}.pbf")
    if os.path.exists(tile_path):
        return 0 # tile already exists, will skip downloading
    url: str = URL_TEMPLATE.format(font=gvar.current_fontname, range=f"{gvar.current_range_begin}-{gvar.current_range_end}", key=args.key)
    response: Optional[requests.Response] = get_response_dynamic_backoff(gvar, bcfg, url)
    if response is not None:
        os.makedirs(font_dir, exist_ok=True)
        with open(tile_path, "wb") as f:
            f.write(response.content)
        return response.status_code # return status code in case of success
    return -1 # failed to download after retries, tile not downloaded
def download_one_font(gvar: GlobalVariables, args: FontDLArguments, bcfg: BackoffConfig) -> None:
    ranges: List[Tuple[int, int]] = [(i, i + 255) for i in range(0, 65536, 256)]
    len_ranges: int = len(ranges)
    print(f"Downloading font stack '{restore_fontname(gvar.current_fontname)}' with {len_ranges} files...")
    for i, (range_begin, range_end) in enumerate(ranges):
        gvar.current_range_begin = range_begin
        gvar.current_range_end = range_end
        tile_progress: str = f"{i + 1:>{len(str(len_ranges))}}/{len_ranges:>{len(str(len_ranges))}}"
        print(f"\033[2K\tDownloading {tile_progress}: range {range_begin}-{range_end}... ", end="", flush=True)
        status_code: int = download_one_pbf(gvar, args, bcfg)
        if status_code == 0: # tile already exists, skip it
            print(f"SKP", end="\r")
            continue
        elif status_code == 200: # tile downloaded successfully
            gvar.downloaded_count += 1
            print(f"OK ", end="\r")
        else: # error message and a new line
            print(f"\r\tError downloading range {range_begin}-{range_end}: {status_code}{' ':>{len(str(len_ranges))}}")
        time.sleep(gvar.wait_sec) # wait before next request
    print(f"\n\t...{gvar.downloaded_count} new files downloaded.")
    gvar.total_downloaded_count += gvar.downloaded_count
    gvar.downloaded_count = 0 # reset for next font

if __name__ == "__main__":
    args: FontDLArguments = parse_arguments()
    if not os.path.exists(args.dir):
        print(f"Directory {args.dir} does not exist. Creating it...")
        os.makedirs(args.dir)
    if not os.access(args.dir, os.W_OK):
        print(f"Directory {args.dir} is not writable. Exiting.")
        exit(1)
    bcfg: BackoffConfig = BackoffConfig()
    gvars: GlobalVariables = GlobalVariables()
    for fontname in args.fonts:
        gvars.current_fontname = fontname
        try:
            download_one_font(gvars, args, bcfg)
        except KeyboardInterrupt:
            print(f"\n\t...{gvars.downloaded_count} new files downloaded.\nInterrupted by user.")
            gvars.total_downloaded_count += gvars.downloaded_count
            break
    print(f"Done. Total new files downloaded: {gvars.total_downloaded_count}.")