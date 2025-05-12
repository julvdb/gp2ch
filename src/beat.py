from enum import IntEnum, auto
from dataclasses import dataclass


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
    rhythm: int
    dynamic: Dynamic
