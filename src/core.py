from typing import Optional

import argparse
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

from .const import (
    TMP_GP_DIR, TMP_OUT_DIR,
    GPIF_PATH,
    INI_FILENAME, AUDIO_FILENAME, NOTES_FILENAME,
)
from .chart import DrumChart


def extract_gp(gp_file: Path) -> None:
    # Check if the file is valid
    if not gp_file.exists():
        raise FileNotFoundError(f"Error: {gp_file} does not exist.")
    # Check if it is a file
    if not gp_file.is_file():
        raise FileNotFoundError(f"Error: {gp_file} is not a file.")
    # Check if it is a .gp file
    if gp_file.suffix != ".gp":
        raise ValueError(f"Error: {gp_file} is not a .gp file.")

    # Extract the .gp file
    with ZipFile(gp_file, 'r') as zip_file:
        zip_file.extractall(TMP_GP_DIR)


def convert_gpif_to_ch_chart(gpif_file: Path, audio_file: Optional[Path]=None) -> DrumChart:
    if not gpif_file.exists():
        raise FileNotFoundError(f"Error: {gpif_file} was not found.")

    # Parse the XML structure
    tree = ET.parse(gpif_file)
    root = tree.getroot()

    # Create the chart
    return DrumChart(root)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Path to the Guitar Pro (.gp) file."
    )
    parser.add_argument(
        "-a",
        "--audio",
        type=str,
        required=False,
        help="Path to the audio file."
    )
    parser.add_argument(
        "-nd",
        "--no-drums",
        type=int,
        default=0,
        required=False,
        help="If not 0, split the drums from the audio using demucs"
             " and add the drumless track to the output chart."
    )
    args = parser.parse_args()

    # Parse the argments
    gp_file = Path(args.input)
    audio_file = Path(args.audio) if args.audio else None
    no_drums = args.no_drums != 0

    # Extract the GP file to a temporary folder
    extract_gp(gp_file)

    # Convert the GPIF file inside the GP archive to a CH chart
    gpif_file = TMP_GP_DIR / GPIF_PATH
    chart = convert_gpif_to_ch_chart(gpif_file, audio_file=audio_file)

    # Create the CH output
    TMP_OUT_DIR.mkdir(parents=True, exist_ok=True)
    chart.write_ini_file(TMP_OUT_DIR / INI_FILENAME)
    chart.write_notes_chart_file(TMP_OUT_DIR / NOTES_FILENAME)
    chart.write_audio_file(TMP_OUT_DIR / AUDIO_FILENAME, no_drums=no_drums)


if __name__ == "__main__":
    main()
