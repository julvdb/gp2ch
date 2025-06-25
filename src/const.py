from typing import Any

from pathlib import Path
from enum import StrEnum


# Guitar Pro constants
GPIF_PATH = Path("Content/score.gpif")
GP_DRUM_KIT_TYPE = "drumKit"
GP_INVALID_VOICE = -1
GP_DEFAULT_DYNAMIC = "MF"
GP_RHYTHM_DICT = {
    "Whole":    1,
    "Half":     2,
    "Quarter":  4,
    "Eighth":   8,
    "16th":    16,
    "32nd":    32,
    "64th":    64
}

# Chart constants
COUNTDOWN_TIME = 2  # seconds

# Output filenames
INI_FILENAME = "song.ini"
AUDIO_FILENAME = "song.ogg"
NOTES_FILENAME = "notes.chart"

# Temporary directories
TMP_DIR = Path("tmp")
TMP_GP_DIR = TMP_DIR / "gp"
TMP_AUDIO_DIR = TMP_DIR / "audio"
TMP_OUT_DIR = TMP_DIR / "out"


# .chart file data
class DefaultValues:
    INI_DIFFICULTY     = -1
    SONG_BPM           = 120  # beats/min
    SONG_RESOLUTION    = 480  # ticks
    SONG_GENRE         = "rock"
    SONG_MUSIC_STREAM  = AUDIO_FILENAME
    SONG_OFFSET        = 0    # seconds
    SONG_PLAYER2       = "bass"
    SONG_DIFFICULTY    = 0
    SONG_PREVIEW_START = 0    # ticks(?)
    SONG_PREVIEW_END   = 0    # ticks(?)
    SONG_MEDIA_TYPE    = "cd"

class SyncTrackPointType(StrEnum):
    BPM            = "B"
    TIME_SIGNATURE = "TS"

class TrackPointType(StrEnum):
    NOTE       = "N"
    STAR_POWER = "S"
    EVENT      = "E"


SongData = dict[str, Any]
SyncTrackPoint = tuple[int, SyncTrackPointType, Any]
TrackPoint = tuple[int, TrackPointType, Any]
