from typing import Optional

import argparse
import shutil
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

from .const import (
    TMP_DIR, TMP_GP_DIR, TMP_OUT_DIR,
    GPIF_PATH,
    INI_FILENAME, NOTES_FILENAME,
    AUDIO_FILENAME, ALBUM_FILENAME,
    DefaultValues
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


def convert_gpif_to_ch_chart(gpif_file: Path) -> DrumChart:
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
        "-o",
        "--output",
        type=str,
        required=False,
        default=str(DefaultValues.OUTPUT_DIR),
        help="Path to the folder in which the output folder will be created."
    )
    parser.add_argument(
        "-m",
        "--image",
        type=str,
        required=False,
        help="Path to the album cover image file."
    )
    parser.add_argument(
        "-a",
        "--audio",
        type=str,
        required=False,
        help="Path to the audio file."
    )
    parser.add_argument(
        "-n",
        "--no-drums",
        default=False,
        action="store_true",
        required=False,
        help="If not 0, split the drums from the audio using demucs"
             " and add the drumless track to the output chart."
    )
    args = parser.parse_args()

    # Parse the argments
    gp_file = Path(args.input)
    output_path = Path(args.output) if args.output else Path(DefaultValues.OUTPUT_DIR)
    image_file = Path(args.image) if args.image else None
    audio_file = Path(args.audio) if args.audio else None
    no_drums = args.no_drums

    # Raise an error if the output path already exists
    if output_path.exists():
        raise FileExistsError("The output folder already exists. Please rename or remove it.")

    # Extract the GP file to a temporary folder
    extract_gp(gp_file)

    # Convert the GPIF file inside the GP archive to a CH chart
    gpif_file = TMP_GP_DIR / GPIF_PATH
    chart = convert_gpif_to_ch_chart(gpif_file)

    # Create the CH output
    try:
        TMP_OUT_DIR.mkdir(parents=True, exist_ok=False)
    except OSError:
        raise OSError("A 'tmp' folder already exists, please delete it and try again.")
    chart.write_ini_file(TMP_OUT_DIR / INI_FILENAME)
    chart.write_notes_chart_file(TMP_OUT_DIR / NOTES_FILENAME)
    chart.write_audio_file(
        TMP_OUT_DIR / AUDIO_FILENAME,
        audio_file=audio_file,
        no_drums=no_drums
    )
    if image_file is not None:
        chart.write_album_image_file(
            TMP_OUT_DIR / ALBUM_FILENAME,
            image_file
        )

    # Copy the output folder to the cwd
    shutil.move(TMP_OUT_DIR, output_path.parent)

    # Remove the tmp dir
    shutil.rmtree(TMP_DIR)


if __name__ == "__main__":
    main()
