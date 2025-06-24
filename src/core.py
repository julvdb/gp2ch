from typing import Optional

import argparse
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

from pydub import AudioSegment

from .const import (
    TMP_GP_DIR, TMP_OUT_DIR,
    GPIF_PATH,
    INI_FILENAME, SONG_FILENAME, NOTES_FILENAME,
    COUNTDOWN_TIME
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


def extract_audio_filepath_from_gpif(root: ET.Element) -> Path | None:
    # Try to find the embedded audio file path
    audio_element = root.find("Assets/Asset/EmbeddedFilePath")
    if audio_element is None:
        return None
    audio_path_text = audio_element.text
    if not audio_path_text:
        return None
    audio_path = TMP_GP_DIR / audio_path_text
    if not audio_path.exists() or not audio_path.is_file():
        return None
    return audio_path

def export_audio_to_ogg(filepath: Path) -> None:
    # Load the audio file and add silence
    audio = AudioSegment.from_file(filepath)  # type: AudioSegment
    countdown_silence = AudioSegment.silent(duration=COUNTDOWN_TIME * 1000)
    audio = countdown_silence + audio

    # Export the audio file to OGG format
    TMP_OUT_DIR.mkdir(parents=True, exist_ok=True)
    audio.export(TMP_OUT_DIR / SONG_FILENAME, format="ogg")


def parse_gpif(gpif_file: Path, audio_file: Optional[Path]=None) -> None:
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
    if audio_file is None or not audio_file.exists() or not audio_file.is_file():
        audio_file = extract_audio_filepath_from_gpif(root)
        if audio_file is None or not audio_file.exists() or not audio_file.is_file():
            raise FileNotFoundError(
                f"Error: No audio file found in {gpif_file} "
                f"and no valid audio file specified."
            )
    export_audio_to_ogg(audio_file)


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
    args = parser.parse_args()

    # Read the GP file path from the args
    gp_file = Path(args.input)
    extract_gp(gp_file)

    # Read the audio file path from the args
    audio_file = Path(args.audio) if args.audio else None

    # Parse the GPIF file
    gpif_file = TMP_GP_DIR / GPIF_PATH
    parse_gpif(gpif_file, audio_file=audio_file)


if __name__ == "__main__":
    main()
