from enum import StrEnum
from pathlib import Path
import xml.etree.ElementTree as ET

from math import log2

from .const import (
    GP_DRUM_KIT_TYPE,
    GP_INVALID_VOICE,
    GP_RHYTHM_DICT,
    GP_DEFAULT_DYNAMIC,
    DefaultValues,
    SongData,
    SyncTrackPointType, SyncTrackPoint,
    TrackPointType, TrackPoint,
)
from .gp import AntiAccent, Note, GraceNoteType, Dynamic, Beat
from .mapping import (
    GPMidiNote, CHMidiNote,
    CH_NOTE_TO_ACCENT, CH_NOTE_TO_GHOST,
    DRUMS_GP_TO_CH_MAPPING
)


class IniHeader(StrEnum):
    SONG = "song"

class IniSongEntry(StrEnum):
    NAME               = "name"
    ARTIST             = "artist"
    ALBUM              = "album"
    CHARTER            = "charter"
    FRETS              = "frets"
    PRO_DRUMS          = "pro_drums"

class NotesHeader(StrEnum):
    SONG         = "Song"
    SYNC_TRACK   = "SyncTrack"
    EVENTS       = "Events"
    EXPERT_DRUMS = "ExpertDrums"

class NotesSongEntry(StrEnum):
    RESOLUTION    = "Resolution"
    TITLE         = "Title"
    ARTIST        = "Artist"
    ALBUM         = "Album"
    CHARTER       = "Charter"
    GENRE         = "Genre"
    MUSIC_STREAM  = "MusicStream"
    OFFSET        = "Offset"
    PLAYER2       = "Player2"
    DIFFICULTY    = "Difficulty"
    PREVIEW_START = "PreviewStart"
    PREVIEW_END   = "PreviewEnd"
    MEDIA_TYPE    = "MediaType"


class DrumChart:
    def __init__(self, root: ET.Element) -> None:
        self._root = root

        # Guitar Pro data
        self._tempo_data: list[tuple[float,float]] = []                 # (master bar position, bpm)
        self._drum_track_id: int = -1                                   # track id of the drum track
        self._track_num_staves: dict[int,int] = {}                      # track id -> number of staves
        self._rhythm_data: dict[int,float] = {}                         # rhythm id -> rhythm value
        self._note_data: dict[int,Note] = {}                            # note id -> Note object
        self._beat_data: dict[int,Beat] = {}                            # beat id -> Beat object
        self._voice_data: dict[int,list[int]] = {}                      # voice id -> list of beat ids
        self._bar_data: dict[int,list[int]] = {}                        # bar id -> list of voice ids
        self._drum_bar_ids: list[int] = []                              # list of bar ids that are part of the drum track,
                                                                        # with index corresponding to the master bar id
        self._has_anacrusis: bool = False                               # True if there is an anacrusis
        self._time_signature_data: list[tuple[int,int,int]] = []        # (master bar id, numerator, denominator)
        self._section_data: list[tuple[int,str]] = []                   # (master bar id, section name)

        # Chart data
        self._resolution: int = -1
        self._num_master_bars: int = -1
        self._master_bar_start_ticks: list[float] = []                  # starting tick value of each master bar
        self._master_bar_end_ticks: list[float] = []                    # ending tick value of each master bar
        self._song_data: SongData = {}                                  # song data string -> value
        self._tick_tempo_data: list[tuple[float,float]] = []                          # (tick, bpm)
        self._sync_track_data: list[SyncTrackPoint] = []                # (tick, point type, data)
        self._events_data: list[tuple[int,str]] = []                    # (tick, event string)
        self._export_drums_data: list[TrackPoint] = []                  # (tick, point_type, data)

        # Load the Guitar Pro data
        self._retrieve_song_data()
        self._retrieve_tempo_data()
        self._retrieve_track_data()
        self._retrieve_rhythm_data()
        self._retrieve_note_data()
        self._retrieve_beat_data()
        self._retrieve_voice_data()
        self._retrieve_bar_data()
        self._retrieve_master_bar_data()

        # Create the chart data
        self._create_sync_track_data()
        self._create_events_data()
        self._create_expert_drums_data()


    def write_ini_file(self, filepath: Path) -> None:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as file:
            file.write(f"[{IniHeader.SONG}]\n")
            file.write(f"{IniSongEntry.NAME} = {self._song_data[NotesSongEntry.TITLE]}\n")
            file.write(f"{IniSongEntry.ARTIST} = {self._song_data[NotesSongEntry.ARTIST]}\n")
            file.write(f"{IniSongEntry.ALBUM} = {self._song_data[NotesSongEntry.ALBUM]}\n")
            file.write(f"{IniSongEntry.CHARTER} = {self._song_data[NotesSongEntry.CHARTER]}\n")
            file.write(f"{IniSongEntry.FRETS} = {self._song_data[NotesSongEntry.CHARTER]}\n")
            file.write(f"{IniSongEntry.PRO_DRUMS} = True\n")

    def write_notes_chart_file(self, filepath: Path) -> None:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as file:
            # Song
            file.write(f"[{NotesHeader.SONG}]\n")
            file.write("{\n")
            file.write(f"  {NotesSongEntry.RESOLUTION} = {self._song_data[NotesSongEntry.RESOLUTION]}\n")
            file.write(f"  {NotesSongEntry.TITLE} = \"{self._song_data[NotesSongEntry.TITLE]}\"\n")
            file.write(f"  {NotesSongEntry.ARTIST} = \"{self._song_data[NotesSongEntry.ARTIST]}\"\n")
            file.write(f"  {NotesSongEntry.ALBUM} = \"{self._song_data[NotesSongEntry.ALBUM]}\"\n")
            file.write(f"  {NotesSongEntry.CHARTER} = \"{self._song_data[NotesSongEntry.CHARTER]}\"\n")
            file.write(f"  {NotesSongEntry.GENRE} = \"{DefaultValues.SONG_GENRE}\"\n")
            file.write(f"  {NotesSongEntry.MUSIC_STREAM} = \"{DefaultValues.SONG_MUSIC_STREAM}\"\n")
            file.write(f"  {NotesSongEntry.OFFSET} = {self._song_data[NotesSongEntry.OFFSET]}\n")
            file.write(f"  {NotesSongEntry.PLAYER2} = {DefaultValues.SONG_PLAYER2}\n")
            file.write(f"  {NotesSongEntry.DIFFICULTY} = {DefaultValues.SONG_DIFFICULTY}\n")
            file.write(f"  {NotesSongEntry.PREVIEW_START} = {DefaultValues.SONG_PREVIEW_START}\n")
            file.write(f"  {NotesSongEntry.PREVIEW_END} = {DefaultValues.SONG_PREVIEW_END}\n")
            file.write(f"  {NotesSongEntry.MEDIA_TYPE} = \"{DefaultValues.SONG_MEDIA_TYPE}\"\n")
            file.write("}\n")

            # SyncTrack
            file.write(f"[{NotesHeader.SYNC_TRACK}]\n")
            file.write("{\n")
            for tick, point_type, data in self._sync_track_data:
                if point_type == SyncTrackPointType.TIME_SIGNATURE:
                    file.write(f"  {tick} = {point_type} {data[0]} {data[1]}\n")
                elif point_type == SyncTrackPointType.BPM:
                    file.write(f"  {tick} = {point_type} {data}\n")
            file.write("}\n")

            # Events
            file.write(f"[{NotesHeader.EVENTS}]\n")
            file.write("{\n")
            for tick, event_text in self._events_data:
                file.write(f"  {tick} = E \"{event_text}\"\n")
            file.write("}\n")

            # ExpertDrums
            file.write(f"[{NotesHeader.EXPERT_DRUMS}]\n")
            file.write("{\n")
            for tick, point_type, data in self._export_drums_data:
                if point_type == TrackPointType.NOTE:
                    for ch_note in data:
                        file.write(f"  {tick} = {point_type} {ch_note} 0\n")
                elif point_type == TrackPointType.STAR_POWER:
                    file.write(f"  {tick} = {point_type} {data[0]} {data[1]}\n")
                elif point_type == TrackPointType.EVENT:
                    file.write(f"  {tick} = {point_type} [{data}]\n")
            file.write("}\n")


    def _retrieve_song_data(self) -> None:
        # Title
        title_element = self._root.find("Score/Title")
        title = ""
        if title_element is not None and title_element.text:
            title = title_element.text

        # Artist
        artist_element = self._root.find("Score/Artist")
        artist = ""
        if artist_element is not None and artist_element.text:
            artist = artist_element.text

        # Album
        album_element = self._root.find("Score/Album")
        album = ""
        if album_element is not None and album_element.text:
            album = album_element.text

        # Charter
        charter_element = self._root.find("Score/Tabber")
        charter = ""
        if charter_element is not None and charter_element.text:
            charter = charter_element.text

        # Resolution
        self._resolution = int(DefaultValues.SONG_RESOLUTION)

        # Set the song data
        self._song_data = {
            NotesSongEntry.RESOLUTION: self._resolution,
            NotesSongEntry.TITLE:      title,
            NotesSongEntry.ARTIST:     artist,
            NotesSongEntry.ALBUM:      album,
            NotesSongEntry.CHARTER:    charter,
            NotesSongEntry.OFFSET:     int(DefaultValues.SONG_OFFSET),
        }

    def _retrieve_tempo_data(self) -> None:
        # Inspired by https://github.com/lmeullibre/gp-metronome-extractor
        for automation in self._root.findall(".//Automation[Type='Tempo']"):
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
            position = float(position_text)

            # Get the tempo value
            value_element = automation.find("Value")
            if value_element is None: continue
            value_text = value_element.text
            if value_text is None: continue
            tempo_value = value_text.split()[0]
            bpm = float(tempo_value)

            # Append the tempo to the list
            self._tempo_data.append((bar + position, bpm))

        # Sort the tempos by bar and position
        self._tempo_data.sort(key=lambda x: (x[0], x[1]))

        # Add the default tempo at the beginning
        # if no automation is present at 0
        if not self._tempo_data or self._tempo_data[0][0] != 0:
            default_tempo = self._root.find(".//Score/Properties/Tempo")
            if default_tempo is not None and default_tempo.text:
                default_bpm = int(default_tempo.text.split()[0])
                self._tempo_data.insert(0, (0, default_bpm))
            else:
                self._tempo_data.insert(0, (0, 120))

    def _retrieve_track_data(self) -> None:
        # Get the number of staves
        track_elements = self._root.findall(".//Tracks/Track")
        for track_element in track_elements:
            # Get the id
            track_id = int(track_element.get("id", -1))
            if track_id < 0: continue

            # Determine if the track is a drum track
            instrumentset_type_element = track_element.find(".//InstrumentSet/Type")
            if instrumentset_type_element is None: continue
            instrumentset_type_text = instrumentset_type_element.text
            if instrumentset_type_text == GP_DRUM_KIT_TYPE:
                self._drum_track_id = track_id

            # Get the number of staves
            staff_elements = track_element.findall(".//Staves/Staff")
            self._track_num_staves[track_id] = len(staff_elements)

        # Check if a drum track was found
        if self._drum_track_id < 0:
            raise ValueError("No drum track found in the GP file.")

    def _retrieve_rhythm_data(self) -> None:
        rhythm_elements = self._root.findall(".//Rhythms/Rhythm")
        for rhythm_element in rhythm_elements:
            # Get the id
            rhythm_id = int(rhythm_element.get("id", -1))
            if rhythm_id < 0: continue

            # Get the rhythm value
            value_element = rhythm_element.find(".//NoteValue")
            if value_element is None: continue
            value_text = value_element.text
            if value_text is None: continue
            rhythm_value = GP_RHYTHM_DICT.get(value_text, None)
            if rhythm_value is None: continue

            # Get the tuplet kind
            tuplet_element = rhythm_element.find(".//PrimaryTuplet")
            if tuplet_element is not None:
                tuplet_numer_text = tuplet_element.get("num", "1")
                tuplet_denom_text = tuplet_element.get("den", "1")
                try:
                    tuplet_numer = float(tuplet_numer_text)
                    tuplet_denom = float(tuplet_denom_text)

                    # Adjust the rhythm value
                    rhythm_value *= tuplet_numer/tuplet_denom
                except ValueError:
                    pass

            self._rhythm_data[rhythm_id] = rhythm_value

    def _retrieve_note_data(self) -> None:
        note_elements = self._root.findall(".//Notes/Note")
        for note_element in note_elements:
            # Get the id
            note_id = int(note_element.get("id", -1))
            if note_id < 0: continue

            # Get the midi note
            midi_note_element = note_element.find(".//Property[@name='Midi']/Number")
            if midi_note_element is None: continue
            midi_note_text = midi_note_element.text
            if midi_note_text is None: continue
            midi_note = int(midi_note_text)

            # Check if it's a tied note
            tied_note = False
            tie_element = note_element.find(".//Tie")
            if tie_element is not None:
                tie_destination = tie_element.get("destination", "false")
                if tie_destination == "true":
                    tied_note = True

            # Check if it's a ghost note
            ghost_note = False
            anti_accent_element = note_element.find(".//AntiAccent")
            if anti_accent_element is not None:
                anti_accent_text = anti_accent_element.text
                if anti_accent_text == AntiAccent.GHOST_NOTE:
                    ghost_note = True

            # Create the note
            note = Note(note_id, midi_note, tied_note, ghost_note)
            self._note_data[note_id] = note

    def _retrieve_beat_data(self) -> None:
        beat_elements = self._root.findall(".//Beats/Beat")
        for beat_element in beat_elements:
            # Get the id
            beat_id = int(beat_element.get("id", -1))
            if beat_id < 0: continue

            # Get the rhythm id
            rhythm_element = beat_element.find(".//Rhythm")
            if rhythm_element is None: continue
            rhythm_id = int(rhythm_element.get("ref", -1))
            if rhythm_id < 0: continue

            # Get the rhythm value
            rhythm = self._rhythm_data.get(rhythm_id, -1)
            if rhythm < 0: continue

            # Get the note ids (empty for rests)
            notes_element = beat_element.find(".//Notes")
            note_ids: list[int] = []
            if notes_element is not None:
                notes_text = notes_element.text
                if notes_text is not None:
                    note_ids = [int(note_str) for note_str in notes_text.split(" ")]

            # Get the notes
            notes: list[Note] = []
            for note_id in note_ids:
                # Get the note
                note = self._note_data.get(note_id, None)
                if note is None: continue

                # Append the note to the list
                notes.append(note)

            # Get the grace note type
            grace_note_type = GraceNoteType.NONE
            grace_note_element = beat_element.find(".//GraceNotes")
            if grace_note_element is not None:
                grace_note_text = grace_note_element.text
                if grace_note_text is not None:
                    try:
                        grace_note_type = GraceNoteType(grace_note_text)
                    except ValueError:
                        pass

            # Get the dynamic
            dynamic = Dynamic[GP_DEFAULT_DYNAMIC]
            dynamic_element = beat_element.find(".//Dynamic")
            if dynamic_element is not None:
                dynamic_text = dynamic_element.text
                if dynamic_text is not None:
                    try:
                        dynamic = Dynamic[dynamic_text]
                    except KeyError:
                        pass

            # Create the beat
            beat = Beat(beat_id, notes, rhythm, dynamic, grace_note_type)
            self._beat_data[beat_id] = beat

    def _retrieve_voice_data(self) -> None:
        voice_elements = self._root.findall(".//Voices/Voice")
        for voice_element in voice_elements:
            # Get the id
            voice_id = int(voice_element.get("id", -1))
            if voice_id < 0: continue

            # Get the beat ids
            beats_element = voice_element.findall(".//Beats")
            if beats_element is None: continue
            beat_ids_text = beats_element[0].text
            if beat_ids_text is None: continue
            beat_ids = [int(beat_str) for beat_str in beat_ids_text.split(" ")]

            # Save the the beat ids in the voice data
            self._voice_data[voice_id] = beat_ids

    def _retrieve_bar_data(self) -> None:
        # Find all Bar elements
        bar_elements = self._root.findall(".//Bars/Bar")
        for bar_element in bar_elements:
            # Get the bar number
            bar_number = int(bar_element.get("id", -1))
            if bar_number < 0: continue

            # Get the voice ids
            voices_element = bar_element.find(".//Voices")
            if voices_element is None: continue
            voices_text = voices_element.text
            if voices_text is None: continue
            voice_ids = [
                int(voice_str)
                for voice_str in voices_text.split(" ")
                if voice_str != str(GP_INVALID_VOICE)
            ]

            # Save the the beat ids in the bar data
            self._bar_data[bar_number] = voice_ids

    def _retrieve_master_bar_data(self) -> None:
        # Find out if there is an anacrusis
        anacrusis_element = self._root.find(".//Anacrusis")
        if anacrusis_element is not None:
            self._has_anacrusis = True
            # TODO: add support for anacrusis
            raise NotImplementedError("Anacruses (pickup bars) are not supported yet.")

        # Find all MasterBar elements
        master_bar_elements = self._root.findall(".//MasterBar")

        # Determine the number of master bars
        self._num_master_bars = len(master_bar_elements)
        if self._num_master_bars == 0: return

        # Iterate through the MasterBar elements
        for master_bar, master_bar_element in enumerate(master_bar_elements):
            # Time signature
            numer, denom = -1, -1
            time_signature_element = master_bar_element.find("Time")
            if time_signature_element is not None:
                time_signature = time_signature_element.text
                if time_signature is not None:
                    numer, denom = map(int, time_signature.split("/"))
                    self._time_signature_data.append((master_bar, numer, denom))

            # Section name
            section_element = master_bar_element.find("Section/Text")
            if section_element is not None:
                section_name = section_element.text
                if section_name:
                    section_name = section_name.replace("\n", "")
                    self._section_data.append((master_bar, section_name))

            # Bar number
            bars_element = master_bar_element.find("Bars")
            if bars_element is None: continue
            bars_text = bars_element.text
            if not bars_text: continue
            bar_ids = [int(bar_id_text) for bar_id_text in bars_text.split(" ")]

            # Determine which bar id is part of the drum track
            bar_id_idx = 0
            track_id = 0
            track_num_staves = self._track_num_staves.get(track_id, -1)
            if track_num_staves < 0: raise ValueError("Drum track not found.")
            while (
                track_id != self._drum_track_id and
                track_id < len(self._track_num_staves) and
                bar_id_idx < len(bar_ids)
            ):
                # Increment the bar id index by the amount of staves of the current track
                bar_id_idx += track_num_staves

                # Go to the next track
                track_id += 1
                track_num_staves = self._track_num_staves.get(track_id, -1)
                if track_num_staves < 0: raise ValueError("Drum track not found.")

            # Check if the bar id index is valid
            if bar_id_idx >= len(bar_ids):
                raise ValueError("No bar corresponding to drum track found.")

            # The found bar id corresponds to the drum track
            self._drum_bar_ids.append(bar_ids[bar_id_idx])

        # Sort the time signatures and sections by bar
        self._time_signature_data.sort(key=lambda x: x[0])
        self._section_data.sort(key=lambda x: x[0])


    def _master_bar_fraction_to_ch_ticks(self,
        fraction: float,
        ts: tuple[int,int]
    ) -> float:
        # Amount of quarter notes in the master bar
        quarter_notes = 4 * ts[0]/ts[1]
        # Amount of ticks in the whole master bar
        master_bar_ticks = self._resolution * quarter_notes
        # Convert the fraction to ticks
        ticks = fraction * master_bar_ticks
        return ticks

    def _rhythm_to_ch_ticks(self, rhythm: float) -> float:
        # Amount of quarter notes in the rhythm
        quarter_notes = 4 / rhythm
        # Convert the rhythm to ticks
        ticks = self._resolution * quarter_notes
        return ticks

    def _decrease_ch_notes_intensity(self, ch_notes: list[CHMidiNote]) -> None:
        # Decrease the intensity by removing accents or adding ghost notes
        for note in range(CHMidiNote.RED, CHMidiNote.GREEN + 1):
            if note not in ch_notes: continue
            accent = CHMidiNote(note + CH_NOTE_TO_ACCENT)
            ghost = CHMidiNote(note + CH_NOTE_TO_GHOST)
            if accent in ch_notes:
                ch_notes.remove(accent)
            elif ghost not in ch_notes:
                ch_notes.append(ghost)

    def _increase_ch_notes_intensity(self, ch_notes: list[CHMidiNote]) -> None:
        # Increase the intensity by adding accents or removing ghost notes
        for note in range(CHMidiNote.RED, CHMidiNote.GREEN + 1):
            if note not in ch_notes: continue
            accent = CHMidiNote(note + CH_NOTE_TO_ACCENT)
            ghost = CHMidiNote(note + CH_NOTE_TO_GHOST)
            if ghost in ch_notes:
                ch_notes.remove(ghost)
            elif accent not in ch_notes:
                ch_notes.append(accent)

    def _create_sync_track_data(self) -> None:
        tick = 0.
        ts_idx = 0
        ts_numer, ts_denom = -1, -1
        tempo_idx = 0
        bpm = self._tempo_data[tempo_idx][1]  # there is always a tempo at 0
        for master_bar in range(self._num_master_bars):
            # Save the starting tick of the master bar
            self._master_bar_start_ticks.append(tick)

            # Fractional position in terms of master bars
            master_bar_position = float(master_bar)

            # Check if there is a time signature change at this master bar
            if ts_idx < len(self._time_signature_data):
                ts_point = self._time_signature_data[ts_idx]
                if ts_point[0] == master_bar:
                    # If the master bar matches,
                    # add the time signature to the sync track data
                    ts_numer, ts_denom = self._time_signature_data[ts_idx][1:3]
                    self._sync_track_data.append((
                        round(tick), SyncTrackPointType.TIME_SIGNATURE,
                        (ts_numer, round(log2(ts_denom)))
                    ))
                    ts_idx += 1
            if ts_numer <= 0 or ts_denom <= 0:
                raise ValueError(f"Invalid time signature ({ts_numer}/{ts_denom}).")

            # Check if there are tempo changes at this master bar
            tempo_changed = False
            if tempo_idx < len(self._tempo_data):
                tempo_point = self._tempo_data[tempo_idx]
                master_bar_position_prev = master_bar_position

                # Add each tempo change in this master bar to the sync track data
                while int(tempo_point[0]) == master_bar:
                    # Increment the tick up to the tempo point
                    master_bar_fraction = tempo_point[0] - master_bar_position_prev
                    if master_bar_fraction > 1e-10:
                        tempo_changed = True
                    tick += self._master_bar_fraction_to_ch_ticks(
                        master_bar_fraction,
                        (ts_numer, ts_denom)
                    )

                    # Create the sync track point
                    bpm = tempo_point[1]
                    if bpm <= 0: raise ValueError(f"Invalid BPM value ({bpm}).")
                    self._tick_tempo_data.append((tick, bpm))
                    self._sync_track_data.append((
                        round(tick), SyncTrackPointType.BPM,
                        round(1000 * bpm)
                    ))
                    tempo_idx += 1

                    # Update the tempo point
                    master_bar_position_prev = tempo_point[0]
                    if tempo_idx < len(self._tempo_data):
                        tempo_point = self._tempo_data[tempo_idx]
                        master_bar_position = tempo_point[0]
                    else:
                        break

                # If there was no tempo change, go back to the previous position
                master_bar_position = master_bar_position_prev

            # Increment the tick up to the next master bar
            if tempo_changed:
                master_bar_fraction = master_bar+1 - master_bar_position
            else:
                master_bar_fraction = 1
            tick += self._master_bar_fraction_to_ch_ticks(
                master_bar_fraction,
                (ts_numer, ts_denom)
            )

            # Save the ending tick of the master bar
            self._master_bar_end_ticks.append(tick)

        # Sort the sync track data by tick
        self._sync_track_data.sort(key=lambda x: x[0])

    def _create_events_data(self) -> None:
        # Start
        self._events_data.append((0, "music_start"))

        # Sections
        for master_bar, section_name in self._section_data:
            # Get the starting tick of the section
            start_tick = round(self._master_bar_start_ticks[master_bar])
            # Add the section to the events data
            self._events_data.append((start_tick, f"section {section_name}"))

        # End
        end_tick = round(self._master_bar_end_ticks[-1])
        self._events_data.append((end_tick, "music_end"))
        self._events_data.append((end_tick, "end"))

        # Sort the events data by tick
        self._events_data.sort(key=lambda x: x[0])

    def _create_expert_drums_data(self) -> None:
        default_dynamic = Dynamic[GP_DEFAULT_DYNAMIC]

        # Amount to change the current note duration by
        delta_rhythm: float | None = None

        tick = 0.
        ts_idx = 0
        _, ts_numer, ts_denom = self._time_signature_data[ts_idx]
        tempo_idx = 0
        for master_bar in range(self._num_master_bars):
            # Get the bar id of the drum track
            if master_bar >= len(self._drum_bar_ids):
                raise ValueError(f"No drum data found for master bar {master_bar}.")
            bar_id = self._drum_bar_ids[master_bar]

            # Update the time signature
            while ts_idx+1 < len(self._time_signature_data):
                next_ts_bar, _, _ = self._time_signature_data[ts_idx+1]
                if next_ts_bar > master_bar: break
                # If the master bar matches, update the time signature
                ts_idx += 1
                _, ts_numer, ts_denom = self._time_signature_data[ts_idx]

            # Get the voices in this bar
            voice_ids = self._bar_data.get(bar_id, None)
            if voice_ids is None: continue

            # Start at the current position
            master_bar_position = float(master_bar)

            # Go through all notes in this bar
            for voice_id in voice_ids:
                # Get the beat ids in this voice
                beat_ids = self._voice_data.get(voice_id, None)
                if beat_ids is None: continue

                for beat_id in beat_ids:
                    # Get the beat object
                    beat = self._beat_data.get(beat_id, None)
                    if beat is None: continue

                    # Calculate the rhythm
                    rhythm = beat.rhythm
                    if delta_rhythm is not None:
                        rhythm = 1/(1/rhythm + 1/delta_rhythm)
                        delta_rhythm = None

                    # Convert the midi notes to CH notes
                    ch_notes: list[CHMidiNote] = []
                    for note in beat.notes:
                        # Skip if it's a tied note
                        if note.tied: continue

                        # Convert the midi note to a GP note
                        gp_note = GPMidiNote(note.midi)

                        # Convert the midi note to CH notes
                        midi_ch_notes = DRUMS_GP_TO_CH_MAPPING.get(gp_note, None)
                        if midi_ch_notes is None: continue
                        midi_ch_notes = midi_ch_notes.copy()

                        # Handle ghost notes
                        if note.ghost:
                            # Decrease the intensity
                            self._decrease_ch_notes_intensity(midi_ch_notes)

                        # Handle the beat dynamic
                        if beat.dynamic < default_dynamic:
                            # Decrease the intensity
                            self._decrease_ch_notes_intensity(midi_ch_notes)
                        elif beat.dynamic > default_dynamic:
                            # Increase the intensity
                            self._increase_ch_notes_intensity(midi_ch_notes)

                        # Add the notes to the list
                        ch_notes.extend(midi_ch_notes)

                    # Handle grace notes:
                    #   before beat -> subtract length of grace note from ticks
                    #   on beat     -> decrease length of next note by length of grace note
                    if beat.grace_note_type is GraceNoteType.BEFORE_BEAT:
                        tick -= self._rhythm_to_ch_ticks(beat.rhythm)
                    elif beat.grace_note_type is GraceNoteType.ON_BEAT:
                        delta_rhythm = -beat.rhythm

                    # Add the notes to the export drums data
                    if ch_notes:
                        self._export_drums_data.append((
                            round(tick), TrackPointType.NOTE,
                            ch_notes
                        ))

                    # Calculate the next master bar position
                    master_bar_fraction = (ts_denom/ts_numer) / rhythm
                    next_master_bar_position = master_bar_position + master_bar_fraction

                    # Update the current tick, master bar position, and bpm
                    while tempo_idx < len(self._tempo_data)-1:
                        tempo_position, _ = self._tempo_data[tempo_idx+1]

                        # Stop if the tempo change occurs later
                        if tempo_position > next_master_bar_position:
                            # Update the current tick
                            tick += self._master_bar_fraction_to_ch_ticks(
                                next_master_bar_position - master_bar_position,
                                (ts_numer, ts_denom)
                            )
                            # Update the current master bar position
                            master_bar_position = next_master_bar_position
                            break

                        # Update the current tick
                        tick += self._master_bar_fraction_to_ch_ticks(
                            tempo_position - master_bar_position,
                            (ts_numer, ts_denom)
                        )

                        # Update the current master bar position
                        master_bar_position = tempo_position

                        # Update the bpm
                        tempo_idx += 1

                    else:
                        # Update the current tick
                        tick += self._master_bar_fraction_to_ch_ticks(
                            next_master_bar_position - master_bar_position,
                            (ts_numer, ts_denom)
                        )
                        # Update the current master bar position
                        master_bar_position = next_master_bar_position
