from enum import StrEnum
from pathlib import Path
import xml.etree.ElementTree as ET

from .const import (
    GP_DRUM_KIT_TYPE, GP_INVALID_VOICE, GP_RHYTHM_DICT,
    SongData,
    SyncTrackPointType, SyncTrackPoint,
    DefaultValues
)
from .beat import Dynamic, Beat


class DrumChart:
    class Header(StrEnum):
        SONG         = "Song"
        SYNC_TRACK   = "SyncTrack"
        EVENTS       = "Events"
        EXPERT_DRUMS = "ExpertDrums"

    class SongEntry(StrEnum):
        RESOLUTION = "Resolution"
        TITLE      = "Title"
        ARTIST     = "Artist"
        ALBUM      = "Album"
        CHARTER    = "Charter"
        OFFSET     = "Offset"


    def __init__(self, root: ET.Element) -> None:
        self._root = root

        # Guitar Pro data
        self._tempo_data: list[tuple[float,float]] = []          # (master bar fraction, bpm)
        self._drum_track_id: int = -1                            # track id of the drum track
        self._track_num_staves: dict[int,int] = {}               # track id -> number of staves
        self._rhythm_data: dict[int,int] = {}                    # rhythm id -> rhythm value
        self._note_data: dict[int,int] = {}                      # note id -> midi note value
        self._beat_data: dict[int,Beat] = {}                     # beat id -> Beat object
        self._voice_data: dict[int,list[int]] = {}               # voice id -> list of beat ids
        self._bar_data: dict[int,list[int]] = {}                 # bar id -> list of voice ids
        self._drum_bar_ids: list[int] = []                       # list of bar ids that are part of the drum track,
                                                                 # with index corresponding to the master bar id
        self._has_anacrusis: bool = False                        # True if there is an anacrusis
        self._time_signature_data: list[tuple[int,int,int]] = [] # (master bar id, numerator, denominator)
        self._section_data: list[tuple[int,str]] = []            # (master bar id, section name)

        # Chart data
        self._resolution: int = -1
        self._num_master_bars: int = -1
        self._song_data: SongData = {}
        self._sync_track_data: list[SyncTrackPoint] = []

        # Load the Guitar Pro data
        self._retrieve_song_data()
        self._retrieve_tempo_data()
        self._retrieve_track_data()
        print(self._drum_track_id)
        print(self._track_num_staves)
        self._retrieve_rhythm_data()
        print(self._rhythm_data)
        self._retrieve_note_data()
        print(self._note_data)
        self._retrieve_beat_data()
        print(self._beat_data)
        self._retrieve_voice_data()
        print(self._voice_data)
        self._retrieve_bar_data()
        print(self._bar_data)
        self._retrieve_master_bar_data()
        print(self._has_anacrusis)
        print(self._drum_bar_ids)
        print(self._time_signature_data)
        print(self._section_data)
        exit()

        # Create the chart data
        self._create_sync_track_data()
        self._create_events_data()
        self._create_expert_drums_data()


    def write_notes_to_file(self, filepath: Path) -> None:
        with open(filepath, "w") as file:
            # Song
            file.write(f"[{self.Header.SONG}]\n")
            file.write("{\n")
            file.write(f"  {self.SongEntry.RESOLUTION} = {self._song_data[self.SongEntry.RESOLUTION]}\n")
            file.write(f"  {self.SongEntry.TITLE} = \"{self._song_data[self.SongEntry.TITLE]}\"\n")
            file.write(f"  {self.SongEntry.ARTIST} = \"{self._song_data[self.SongEntry.ARTIST]}\"\n")
            file.write(f"  {self.SongEntry.ALBUM} = \"{self._song_data[self.SongEntry.ALBUM]}\"\n")
            file.write(f"  {self.SongEntry.CHARTER} = \"{self._song_data[self.SongEntry.CHARTER]}\"\n")
            file.write(f"  {self.SongEntry.OFFSET} = {self._song_data[self.SongEntry.OFFSET]}\n")
            file.write("}\n")

            # SyncTrack
            file.write(f"[{self.Header.SYNC_TRACK}]\n")
            file.write("{\n")
            # file.write(f"{}")
            file.write("}\n")

            # Events
            file.write(f"[{self.Header.EVENTS}]\n")
            file.write("{\n")
            file.write("}\n")

            # ExpertDrums
            file.write(f"[{self.Header.EXPERT_DRUMS}]\n")
            file.write("{\n")
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
            self.SongEntry.RESOLUTION: self._resolution,
            self.SongEntry.TITLE:      title,
            self.SongEntry.ARTIST:     artist,
            self.SongEntry.ALBUM:      album,
            self.SongEntry.CHARTER:    charter,
            self.SongEntry.OFFSET:     int(DefaultValues.SONG_OFFSET),
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
            track_id = int(track_element.attrib.get("id", -1))
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
            rhythm_id = int(rhythm_element.attrib.get("id", -1))
            if rhythm_id < 0: continue

            # Get the rhythm value
            value_element = rhythm_element.find(".//NoteValue")
            if value_element is None: continue
            value_text = value_element.text
            if value_text is None: continue
            rhythm_value = GP_RHYTHM_DICT.get(value_text, None)
            if rhythm_value is None: continue
            self._rhythm_data[rhythm_id] = rhythm_value

    def _retrieve_note_data(self) -> None:
        note_elements = self._root.findall(".//Notes/Note")
        for note_element in note_elements:
            # Get the id
            note_id = int(note_element.attrib.get("id", -1))
            if note_id < 0: continue

            # Get the midi note
            midi_note_element = note_element.find(".//Property[@name='Midi']/Number")
            if midi_note_element is None: continue
            midi_note_text = midi_note_element.text
            if midi_note_text is None: continue
            midi_note = int(midi_note_text)
            self._note_data[note_id] = midi_note

    def _retrieve_beat_data(self) -> None:
        beat_elements = self._root.findall(".//Beats/Beat")
        for beat_element in beat_elements:
            # Get the id
            beat_id = int(beat_element.attrib.get("id", -1))
            if beat_id < 0: continue

            # Get the dynamic
            dynamic_element = beat_element.find(".//Dynamic")
            if dynamic_element is None: continue
            dynamic_text = dynamic_element.text
            if dynamic_text is None: continue
            try:
                dynamic = Dynamic[dynamic_text]
            except KeyError:
                continue

            # Get the rhythm id
            rhythm_element = beat_element.find(".//Rhythm")
            if rhythm_element is None: continue
            rhythm_id = int(rhythm_element.attrib.get("ref", -1))
            if rhythm_id < 0: continue

            # Get the rhythm value
            rhythm = self._rhythm_data.get(rhythm_id, -1)
            if rhythm < 0: continue

            # Get the note id
            notes_element = beat_element.find(".//Notes")
            if notes_element is None: continue
            notes_text = notes_element.text
            if notes_text is None: continue
            note_ids = [int(note_str) for note_str in notes_text.split(" ")]

            # Get the MIDI note values
            midi_notes: list[int] = []
            for note_id in note_ids:
                # Get the note value
                midi_note = self._note_data.get(note_id, -1)
                if midi_note < 0: continue

                # Append the note value to the list
                midi_notes.append(midi_note)

            # Create the beat
            beat = Beat(beat_id, midi_notes, rhythm, dynamic)
            self._beat_data[beat_id] = beat

    def _retrieve_voice_data(self) -> None:
        voice_elements = self._root.findall(".//Voices/Voice")
        for voice_element in voice_elements:
            # Get the id
            voice_id = int(voice_element.attrib.get("id", -1))
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
            bar_number = int(bar_element.attrib.get("id", -1))
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


    def _create_sync_track_data(self) -> None:
        tick = 0
        ts_idx = 0
        tempo_idx = 0
        ts_numer, ts_denom = -1, -1
        bpm = -1
        for master_bar in range(self._num_master_bars):
            # Check if there is a time signature change at this bar
            if ts_idx < len(self._time_signature_data):
                ts_point = self._time_signature_data[ts_idx]
                if ts_point[0] == master_bar:
                    # If the bar matches,
                    # add the time signature to the sync track data
                    ts_numer, ts_denom = self._time_signature_data[ts_idx][1:3]
                    self._sync_track_data.append((
                        tick, SyncTrackPointType.TIME_SIGNATURE,
                        (ts_numer, ts_denom)
                    ))
                    ts_idx += 1
            if ts_numer <= 0 or ts_denom <= 0: continue

            # Check if there are tempo changes at this bar
            if tempo_idx < len(self._tempo_data):
                tempo_point = self._tempo_data[tempo_idx]

                # Add each tempo change in this bar to the sync track data
                # and increment the current tick
                while int(tempo_point[0]) == master_bar:
                    bpm = tempo_point[1]
                    self._sync_track_data.append((
                        tick, SyncTrackPointType.BPM,
                        bpm
                    ))
                    tempo_idx += 1

                    # Calculate the next tick
                    # TODO

                    # Update the tempo point
                    if tempo_idx < len(self._tempo_data):
                        tempo_point = self._tempo_data[tempo_idx]
                    else:
                        break


            if bpm <= 0: continue

        print(self._sync_track_data)
        exit()

    def _create_events_data(self) -> None:
        print("TODO: Create Events data")

    def _create_expert_drums_data(self) -> None:
        print("TODO: Create ExpertDrums data")
