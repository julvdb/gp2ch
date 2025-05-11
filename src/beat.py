from enum import IntEnum, auto


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


class Beat:
    def __init__(self,
        bar_fraction: float,
        note: int,
        rhythm: int,
        dynamic: Dynamic
    ) -> None:
        self.bar_fraction = bar_fraction
        self.note = note
        self.rhythm = rhythm
        self.dynamic = dynamic
