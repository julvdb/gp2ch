from enum import IntEnum, StrEnum, auto
from dataclasses import dataclass


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
    midi_notes: list[int]
    rhythm: float
    dynamic: Dynamic
    grace_note_type: GraceNoteType
