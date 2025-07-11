from pathlib import Path
from enum import StrEnum
import xml.etree.ElementTree as ET
import multiprocessing

from pydub import AudioSegment
import demucs.api
import demucs.audio

from .const import TMP_GP_DIR, TMP_AUDIO_DIR, COUNTDOWN_TIME


class AudioStem(StrEnum):
    DRUMS  = "drums"
    BASS   = "bass"
    OTHER  = "other"
    VOCALS = "vocals"


def extract_audio_filepath_from_gpif(root: ET.Element) -> Path | None:
    # Try to find the embedded audio file path
    audio_element = root.find(".//EmbeddedFilePath")
    if audio_element is None:
        return None
    audio_path_text = audio_element.text
    if not audio_path_text:
        return None
    audio_path = TMP_GP_DIR / audio_path_text
    if not audio_path.exists() or not audio_path.is_file():
        return None
    return audio_path


def split_audio_track(audio_file: Path) -> dict[AudioStem,Path]:
    # Separate the stems
    ncores = multiprocessing.cpu_count() - 1
    separator = demucs.api.Separator(
        model="htdemucs_ft",
        jobs=ncores,
        progress=True
    )
    _, separated = separator.separate_audio_file(audio_file)

    # Create temporary audio files for each stem
    filenames: dict[AudioStem,Path] = {}
    TMP_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    for stem in AudioStem:
        stem_audio = separated[stem]
        stem_file  = TMP_AUDIO_DIR / f"{stem}.wav"
        demucs.audio.save_audio(stem_audio, stem_file,  separator.samplerate)
        filenames[stem] = stem_file

    return filenames


def export_audio_to_ogg(filepath: Path, out_filepath: Path) -> None:
    # Load the audio file and add silence
    audio: AudioSegment = AudioSegment.from_file(filepath)
    countdown_silence = AudioSegment.silent(duration=COUNTDOWN_TIME * 1000)
    audio: AudioSegment = countdown_silence + audio

    # Export the audio file to OGG format
    out_filepath.parent.mkdir(parents=True, exist_ok=True)
    audio.export(out_filepath, format="ogg")
