import argparse
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

from pydub import AudioSegment

from .const import (
    TMP_GP_DIR, TMP_OUT_DIR,
    GPIF_PATH,
    INI_FILENAME, SONG_FILENAME, NOTES_FILENAME
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


def convert_audio_to_ogg(root: ET.Element) -> None:
    # Try to find the embedded audio file path
    audio_element = root.find("Assets/Asset/EmbeddedFilePath")
    if audio_element is None:
        return
    audio_path_text = audio_element.text
    if not audio_path_text:
        return
    audio_path = TMP_GP_DIR / audio_path_text
    if not audio_path.exists():
        return

    # Load the audio file
    audio = AudioSegment.from_file(audio_path)

    # Export the audio file to OGG format
    TMP_OUT_DIR.mkdir(parents=True, exist_ok=True)
    audio.export(TMP_OUT_DIR / SONG_FILENAME, format="ogg")


def parse_gpif(gpif_file: Path) -> None:
    if not gpif_file.exists():
        raise FileNotFoundError(f"Error: {gpif_file} was not found.")

    # Parse the XML structure
    tree = ET.parse(gpif_file)
    root = tree.getroot()

    # Create the chart
    chart = DrumChart(root)
    chart.write_ini_file(TMP_OUT_DIR / INI_FILENAME)
    chart.write_notes_chart_file(TMP_OUT_DIR / NOTES_FILENAME)

    # Convert the audio to OGG
    convert_audio_to_ogg(root)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_file", type=str,
        help="Path to the Guitar Pro (.gp) file."
    )
    args = parser.parse_args()

    # Read the file path from the args
    gp_file = Path(args.input_file)
    extract_gp(gp_file)

    # Parse the GPIF file
    gpif_file = TMP_GP_DIR / GPIF_PATH
    parse_gpif(gpif_file)


if __name__ == "__main__":
    main()
