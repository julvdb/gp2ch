import sys
import argparse
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

TMP_DIR = Path("tmp")
GPIF_PATH = Path("Content/score.gpif")


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
        zip_file.extractall(TMP_DIR)


def retrieve_tempos(root: ET.Element) -> list[tuple[int,int,float]]:
    """https://github.com/lmeullibre/gp-metronome-extractor"""
    tempos = []

    default_tempo = root.find(".//Score/Properties/Tempo")
    if default_tempo is not None and default_tempo.text:
        default_bpm = int(default_tempo.text.split()[0])
        tempos.append((0, 0, default_bpm))
    else:
        tempos.append((0, 0, 120))

    for automation in root.findall(".//Automation[Type='Tempo']"):
        # Get the bar number
        bar_element = automation.find("Bar")
        if bar_element is None: continue
        bar_text = bar_element.text
        if bar_text is None: continue
        bar = int(bar_text)

        # Get the position in the bar
        position_element = automation.find("Position")
        if position_element is None: continue
        position_text = position_element.text
        if position_text is None: continue
        position_decimal = float(position_text)
        # Convert to internal GP position
        position = int(position_decimal * 960)

        # Get the tempo value
        value_element = automation.find("Value")
        if value_element is None: continue
        value_text = value_element.text
        if value_text is None: continue
        tempo_value = value_text.split()[0]
        bpm = float(tempo_value)

        # Append the tempo to the list
        tempos.append((bar, position, bpm))

    total_bars = 0
    bars = root.findall(".//Score/Bars/Bar")
    if bars:
        total_bars = len(bars)
    else:
        master_bars = root.findall(".//MasterBar")
        if master_bars:
            total_bars = len(master_bars)

    if tempos:
        total_bars = max(total_bars, max(bar for bar, _, _ in tempos) + 1)

    tempos.sort(key=lambda x: (x[0], x[1]))
    if len(tempos) > 1 and tempos[0][:-1] == tempos[1][:-1]:
        tempos.pop(0)
    return tempos


def parse_gpif(gpif_file: Path) -> None:
    if not gpif_file.exists():
        raise FileNotFoundError(f"Error: {gpif_file} was not found.")

    # Parse the XML structure
    tree = ET.parse(gpif_file)
    root = tree.getroot()

    # Retrieve the tempo information
    tempos = retrieve_tempos(root)
    print(tempos)

    


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str, help="Path to the Guitar Pro (.gp) file.")
    args = parser.parse_args()

    # Read the file path from the args
    gp_file = Path(args.input_file)
    extract_gp(gp_file)

    # Parse the GPIF file
    gpif_file = TMP_DIR / GPIF_PATH
    parse_gpif(gpif_file)



if __name__ == "__main__":
    main()
