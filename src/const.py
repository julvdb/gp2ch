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
ALBUM_SIZE = (512, 512)

# Output filenames
INI_FILENAME = "song.ini"
NOTES_FILENAME = "notes.chart"
ALBUM_FILENAME = "album.png"
MUSIC_STREAM_FILENAME = "song.ogg"
DRUMS_STREAM_FILENAME = "drums_1.ogg"
BASS_STREAM_FILENAME = "bass.ogg"
GUITAR_STREAM_FILENAME = "guitar.ogg"
VOCALS_STREAM_FILENAME = "vocals.ogg"

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
    SONG_MUSIC_STREAM  = MUSIC_STREAM_FILENAME
    SONG_DRUMS_STREAM  = DRUMS_STREAM_FILENAME
    SONG_BASS_STREAM   = BASS_STREAM_FILENAME
    SONG_GUITAR_STREAM = GUITAR_STREAM_FILENAME
    SONG_VOCALS_STREAM = VOCALS_STREAM_FILENAME
    SONG_OFFSET        = 0    # seconds
    SONG_PLAYER2       = "bass"
    SONG_DIFFICULTY    = 0
    SONG_PREVIEW_START = 0    # ticks(?)
    SONG_PREVIEW_END   = 0    # ticks(?)
    SONG_MEDIA_TYPE    = "cd"
    OUTPUT_DIR         = "out"

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
