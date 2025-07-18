import argparse
import shutil
from pathlib import Path
import xml.etree.ElementTree as ET

from .const import (
    TMP_DIR, TMP_GP_DIR, TMP_OUT_DIR,
    GPIF_PATH,
    INI_FILENAME, NOTES_FILENAME,
    ALBUM_FILENAME,
    DefaultValues
)
from .gp import extract_gp
from .chart import DrumChart


def convert_gpif_to_ch_chart(gpif_file: Path, split: bool=False) -> DrumChart:
    if not gpif_file.exists():
        raise FileNotFoundError(f"Error: {gpif_file} was not found.")

    # Parse the XML structure
    tree = ET.parse(gpif_file)
    root = tree.getroot()

    # Create the chart
    return DrumChart(root, split=split)


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
        "--album",
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
        "-s",
        "--split",
        default=False,
        action="store_true",
        required=False,
        help="If specified, split the audio into four stems using demucs."
    )
    args = parser.parse_args()

    # Parse the argments
    gp_file = Path(args.input)
    output_path = Path(args.output) if args.output else Path(DefaultValues.OUTPUT_DIR)
    image_file = Path(args.image) if args.image else None
    audio_file = Path(args.audio) if args.audio else None
    split = bool(args.split)

    # Raise an error if the output path already exists
    if output_path.exists():
        raise FileExistsError("The output folder already exists. Please rename or remove it.")

    # Extract the GP file to a temporary folder
    extract_gp(gp_file)

    # Convert the GPIF file inside the GP archive to a CH chart
    gpif_file = TMP_GP_DIR / GPIF_PATH
    chart = convert_gpif_to_ch_chart(gpif_file, split=split)

    # Create the CH output
    try:
        TMP_OUT_DIR.mkdir(parents=True, exist_ok=False)
    except OSError:
        raise OSError("A 'tmp' folder already exists, please delete it and try again.")
    chart.write_ini_file(TMP_OUT_DIR / INI_FILENAME)
    chart.write_notes_chart_file(TMP_OUT_DIR / NOTES_FILENAME)
    chart.write_audio_files(TMP_OUT_DIR, audio_file=audio_file)
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
