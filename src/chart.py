from typing import Any
type SongInfo = dict[str, Any]
type TempoPoint = tuple[int, int, float]

from enum import Enum, StrEnum
from pathlib import Path
import xml.etree.ElementTree as ET


class Chart:
    class Header(StrEnum):
        SONG         = "Song"
        SYNC_TRACK   = "SyncTrack"
        EVENTS       = "Events"
        EXPERT_DRUMS = "ExpertDrums"

    class SongInfo(StrEnum):
        RESOLUTION = "Resolution"
        TITLE      = "Title"
        ARTIST     = "Artist"
        ALBUM      = "Album"
        YEAR       = "Year"
        GENRE      = "Genre"
        CHARTER    = "Charter"
        OFFSET     = "Offset"

    class Defaults(Enum):
        RESOLUTION = 480
        TITLE      = "Unknown Title"
        ARTIST     = "Unknown Artist"
        ALBUM      = "Unknown Album"
        YEAR       = "Unknown Year"
        GENRE      = "Unknown Genre"
        CHARTER    = "Unknown Charter"
        OFFSET     = 0


    def __init__(self, root: ET.Element) -> None:
        self._root = root

        # Attributes
        self._song_info: SongInfo = {}
        self._tempo_points: list[TempoPoint] = []

        # Load the chart
        self._retrieve_song_info()
        self._retrieve_tempo_automation()


    def write_notes_to_file(self, filepath: Path) -> None:
        print("TODO: Write notes to file")


    def _retrieve_song_info(self) -> None:
        # Title
        title = self._root.find("Score/Title")
        if title is not None and title.text:
            title = title.text
        else:
            title = self.Defaults.TITLE

        # Artist
        artist = self._root.find("Score/Artist")
        if artist is not None and artist.text:
            artist = artist.text
        else:
            artist = self.Defaults.ARTIST

        # Album
        album = self._root.find("Score/Album")
        if album is not None and album.text:
            album = album.text
        else:
            album = self.Defaults.ALBUM

        # Charter
        charter = self._root.find("Score/Tabber")
        if charter is not None and charter.text:
            charter = charter.text
        else:
            charter = self.Defaults.CHARTER

        self._song_info = {
            self.SongInfo.RESOLUTION: self.Defaults.RESOLUTION,
            self.SongInfo.TITLE:      title,
            self.SongInfo.ARTIST:     artist,
            self.SongInfo.ALBUM:      album,
            self.SongInfo.YEAR:       self.Defaults.YEAR,
            self.SongInfo.GENRE:      self.Defaults.GENRE,
            self.SongInfo.CHARTER:    charter,
            self.SongInfo.OFFSET:     self.Defaults.OFFSET,
        }

    def _retrieve_tempo_automation(self) -> None:
        """https://github.com/lmeullibre/gp-metronome-extractor"""
        default_tempo = self._root.find(".//Score/Properties/Tempo")
        if default_tempo is not None and default_tempo.text:
            default_bpm = int(default_tempo.text.split()[0])
            self._tempo_points.append((0, 0, default_bpm))
        else:
            self._tempo_points.append((0, 0, 120))

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
            position_decimal = float(position_text)
            # Convert to internal GP position
            position = int(position_decimal * 960)

            # Get the tempo value
            value_element = automation.find("Value")
            if value_element is None: continue
            value_text = value_element.text
            if value_text is None: continue
            tempo_value = value_text.split()[0]
            bpm = float(tempo_value)

            # Append the tempo to the list
            self._tempo_points.append((bar, position, bpm))

        # Determine the total number of bars in the score
        total_bars = 0
        bars = self._root.findall(".//Score/Bars/Bar")
        if bars:
            total_bars = len(bars)
        else:
            master_bars = self._root.findall(".//MasterBar")
            if master_bars:
                total_bars = len(master_bars)
        if self._tempo_points:
            total_bars = max(
                total_bars,
                max(bar for bar, _, _ in self._tempo_points) + 1
            )

        # Sort the tempos by bar and position
        self._tempo_points.sort(key=lambda x: (x[0], x[1]))

        # Remove the default tempo if an automation is present at 0
        if len(self._tempo_points) > 1 and \
            self._tempo_points[0][:-1] == self._tempo_points[1][:-1]:
            self._tempo_points.pop(0)
