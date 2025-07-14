from typing_extensions import override

from enum import IntEnum, StrEnum, auto
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile

from .const import TMP_GP_DIR


class Accent(IntEnum):
    NONE         = -1
    STACCATO     =  1
    HEAVY_ACCENT =  4
    ACCENT       =  8

class AntiAccent(StrEnum):
    NONE       = ""
    GHOST_NOTE = "Normal"

@dataclass
class Note:
    note_id: int
    midi: int
    tied: bool
    accent: Accent
    anti_accent: AntiAccent


class GraceNoteType(StrEnum):
    NONE        = ""
    BEFORE_BEAT = "BeforeBeat"
    ON_BEAT     = "OnBeat"

class Dynamic(IntEnum):
    PPP = auto()
    PP  = auto()
    P   = auto()
    MP  = auto()
    MF  = auto()
    F   = auto()
    FF  = auto()
    FFF = auto()

    @override
    def __str__(self) -> str:
        return self.name

@dataclass
class Beat:
    beat_id: int
    notes: list[Note]
    rhythm: float
    dynamic: Dynamic
    grace_note_type: GraceNoteType


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
