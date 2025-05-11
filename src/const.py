from typing import Any

from pathlib import Path
from enum import StrEnum


# Guitar Pro constants
GPIF_PATH = Path("Content/score.gpif")
GP_RHYTHM_DICT = {
    "Whole":    1,
    "Half":     2,
    "Quarter":  4,
    "Eighth":   8,
    "16th":    16,
    "32nd":    32,
    "64th":    64
}

# Temporary directories
TMP_DIR = Path("tmp")
TMP_GP_DIR = TMP_DIR / "gp"
TMP_OUT_DIR = TMP_DIR / "out"

# Output filenames
SONG_FILENAME = "song.ogg"
NOTES_FILENAME = "notes.chart"

# .chart file data
class SyncTrackPointType(StrEnum):
    BPM            = "B"
    TIME_SIGNATURE = "TS"

type SongData = dict[str, Any]
type SyncTrackPoint = tuple[int, SyncTrackPointType, Any]

class DefaultValues:
    SONG_RESOLUTION = 480
    SONG_OFFSET     = 0
