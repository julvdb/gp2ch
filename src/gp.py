from enum import IntEnum, StrEnum, auto
from dataclasses import dataclass


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

    def __str__(self) -> str:
        return self.name

@dataclass
class Beat:
    beat_id: int
    notes: list[Note]
    rhythm: float
    dynamic: Dynamic
    grace_note_type: GraceNoteType
