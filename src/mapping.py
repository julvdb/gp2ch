from enum import IntEnum


class GPMidiNote(IntEnum):
    RIDE2_CHOKE          = 29
    REVERSE_CYMBAL       = 30
    SNARE_SIDE_STICK2    = 31
    METRONOME            = 33
    METRONOME_BELL       = 34
    KICK2                = 35
    KICK                 = 36
    SNARE_SIDE_STICK1    = 37
    SNARE                = 38
    HAND_CLAP            = 39
    ELECTRIC_SNARE       = 40
    LOW_FLOOR_TOM        = 41
    HI_HAT_CLOSED        = 42
    VERY_LOW_TOM         = 43
    PEDAL_HI_HAT         = 44
    LOW_TOM              = 45
    HI_HAT_OPEN          = 46
    MID_TOM              = 47
    HIGH_TOM             = 48
    CRASH_HIGH           = 49
    HIGH_FLOOR_TOM       = 50
    RIDE_MIDDLE          = 51
    CHINA                = 52
    RIDE_BELL            = 53
    TAMBOURINE           = 54
    SPLASH               = 55
    COWBELL_MEDIUM       = 56
    CRASH_MEDIUM         = 57
    VIBRASLAP            = 58
    RIDE2_EDGE           = 59
    BONGO_HIGH           = 60
    BONGO_LOW            = 61
    CONGA_HIGH_MUTE      = 62
    CONGA_HIGH           = 63
    CONGA_LOW            = 64
    TIMBALE_HIGH         = 65
    TIMBALE_LOW          = 66
    AGOGO_HIGH           = 67
    AGOGO_LOW            = 68
    CABASA               = 69
    LEFT_MARACA          = 70
    WHISTLE_HIGH         = 71
    WHISTLE_LOW          = 72
    GUIRO                = 73
    GUIRO_SCRAP_RETURN   = 74
    CLAVES               = 75
    WOODBLOCK_HIGH       = 76
    WOODBLOCK_LOW        = 77
    CUICA_MUTE           = 78
    CUICA_OPEN           = 79
    TRIANGLE_MUTE        = 80
    TRIANGLE             = 81
    SHAKER               = 82
    JINGLE_BELL          = 83
    BELL_TREE            = 84
    CASTANETS            = 85
    SURDO                = 86
    SURDO_MUTE           = 87
    SNARE_RIM_SHOT       = 91
    HI_HAT_HALF          = 92
    RIDE_EDGE            = 93
    RIDE_CHOKE           = 94
    SPLASH_CHOKE         = 95
    CHINA_CHOKE          = 96
    CRASH_HIGH_CHOKE     = 97
    CRASH_MEDIUM_CHOKE   = 98
    COWBELL_LOW          = 99
    COWBELL_LOW_TIP      = 100
    COWBELL_MEDIUM_TIP   = 101
    COWBELL_HIGH         = 102
    COWBELL_HIGH_TIP     = 103
    BONGO_HIGH_MUTE      = 104
    BONGO_HIGH_SLAP      = 105
    BONGO_LOW_MUTE       = 106
    BONGO_LOW_SLAP       = 107
    CONGA_LOW_SLAP       = 108
    CONGA_LOW_MUTE       = 109
    CONGA_HIGH_SLAP      = 110
    TAMBOURINE_RETURN    = 111
    TAMBOURINE_ROLL      = 112
    TAMBOURINE_HAND      = 113
    GRANCASSA            = 114
    PIATTI               = 115
    PIATTI_HAND          = 116
    CABASA_RETURN        = 117
    LEFT_MARACA_RETURN   = 118
    RIGHT_MARACA         = 119
    RIGHT_MARACA_RETURN  = 120
    SHAKER_RETURN        = 122
    BELL_TREE_RETURN     = 123
    GOLPE_THUMB          = 124
    GOLPE_FINGER         = 125
    RIDE2_MIDDLE         = 126
    RIDE2_BELL           = 127


class CHMidiNote(IntEnum):
    NONE          = -1
    KICK          = 0
    RED           = 1
    YELLOW        = 2
    GREEN         = 3
    BLUE          = 4
    ORANGE        = 5
    KICK2         = 32
    RED_ACCENT    = 34
    YELLOW_ACCENT = 35
    BLUE_ACCENT   = 36
    GREEN_ACCENT  = 37
    ORANGE_ACCENT = 38
    RED_GHOST     = 40
    YELLOW_GHOST  = 41
    BLUE_GHOST    = 42
    GREEN_GHOST   = 43
    ORANGE_GHOST  = 44
    YELLOW_CYMBAL = 66
    BLUE_CYMBAL   = 67
    GREEN_CYMBAL  = 68


DRUMS_GP_TO_CH_MAPPING: dict[GPMidiNote,list[CHMidiNote]] = {
    GPMidiNote.KICK: [CHMidiNote.KICK],
    GPMidiNote.KICK2: [CHMidiNote.KICK2],

    GPMidiNote.SNARE: [CHMidiNote.RED],
    GPMidiNote.SNARE_RIM_SHOT: [CHMidiNote.RED, CHMidiNote.RED_ACCENT],
    GPMidiNote.SNARE_SIDE_STICK1: [CHMidiNote.RED, CHMidiNote.RED_GHOST],
    GPMidiNote.SNARE_SIDE_STICK2: [CHMidiNote.RED, CHMidiNote.RED_GHOST],
    GPMidiNote.ELECTRIC_SNARE: [CHMidiNote.RED],
    GPMidiNote.HAND_CLAP: [CHMidiNote.RED, CHMidiNote.RED_ACCENT],

    GPMidiNote.HIGH_FLOOR_TOM: [CHMidiNote.YELLOW],
    GPMidiNote.HIGH_TOM: [CHMidiNote.YELLOW],
    GPMidiNote.MID_TOM: [CHMidiNote.BLUE],
    GPMidiNote.LOW_TOM: [CHMidiNote.GREEN],
    GPMidiNote.VERY_LOW_TOM: [CHMidiNote.GREEN],
    GPMidiNote.LOW_FLOOR_TOM: [CHMidiNote.GREEN],

    GPMidiNote.HI_HAT_CLOSED: [CHMidiNote.YELLOW, CHMidiNote.YELLOW_CYMBAL, CHMidiNote.YELLOW_GHOST],
    GPMidiNote.HI_HAT_HALF: [CHMidiNote.YELLOW, CHMidiNote.YELLOW_CYMBAL],
    GPMidiNote.HI_HAT_OPEN: [CHMidiNote.YELLOW, CHMidiNote.YELLOW_CYMBAL, CHMidiNote.YELLOW_ACCENT],
    GPMidiNote.PEDAL_HI_HAT: [CHMidiNote.YELLOW, CHMidiNote.YELLOW_CYMBAL, CHMidiNote.YELLOW_GHOST],

    GPMidiNote.RIDE_EDGE: [CHMidiNote.BLUE, CHMidiNote.BLUE_CYMBAL, CHMidiNote.BLUE_ACCENT],
    GPMidiNote.RIDE_MIDDLE: [CHMidiNote.BLUE, CHMidiNote.BLUE_CYMBAL],
    GPMidiNote.RIDE_BELL: [CHMidiNote.BLUE, CHMidiNote.BLUE_CYMBAL, CHMidiNote.BLUE_ACCENT],
    GPMidiNote.RIDE_CHOKE: [CHMidiNote.BLUE, CHMidiNote.BLUE_CYMBAL, CHMidiNote.BLUE_ACCENT],
    GPMidiNote.RIDE2_EDGE: [CHMidiNote.BLUE, CHMidiNote.BLUE_CYMBAL, CHMidiNote.BLUE_ACCENT],
    GPMidiNote.RIDE2_MIDDLE: [CHMidiNote.BLUE, CHMidiNote.BLUE_CYMBAL],
    GPMidiNote.RIDE2_BELL: [CHMidiNote.BLUE, CHMidiNote.BLUE_CYMBAL, CHMidiNote.BLUE_ACCENT],
    GPMidiNote.RIDE2_CHOKE: [CHMidiNote.BLUE, CHMidiNote.BLUE_CYMBAL, CHMidiNote.BLUE_ACCENT],

    GPMidiNote.CRASH_HIGH: [CHMidiNote.GREEN, CHMidiNote.GREEN_CYMBAL],
    GPMidiNote.CRASH_HIGH_CHOKE: [CHMidiNote.GREEN, CHMidiNote.GREEN_CYMBAL, CHMidiNote.GREEN_ACCENT],
    GPMidiNote.CRASH_MEDIUM: [CHMidiNote.YELLOW, CHMidiNote.YELLOW_CYMBAL, CHMidiNote.YELLOW_ACCENT],
    GPMidiNote.CRASH_MEDIUM_CHOKE: [CHMidiNote.YELLOW, CHMidiNote.YELLOW_CYMBAL, CHMidiNote.YELLOW_ACCENT],
    GPMidiNote.CHINA: [CHMidiNote.BLUE, CHMidiNote.BLUE_CYMBAL],
    GPMidiNote.CHINA_CHOKE: [CHMidiNote.BLUE, CHMidiNote.BLUE_CYMBAL, CHMidiNote.BLUE_ACCENT],
    GPMidiNote.SPLASH: [CHMidiNote.BLUE, CHMidiNote.BLUE_CYMBAL],
    GPMidiNote.SPLASH_CHOKE: [CHMidiNote.BLUE, CHMidiNote.BLUE_CYMBAL, CHMidiNote.BLUE_ACCENT],
    GPMidiNote.REVERSE_CYMBAL: [CHMidiNote.GREEN, CHMidiNote.GREEN_CYMBAL],
    GPMidiNote.PIATTI: [CHMidiNote.GREEN, CHMidiNote.GREEN_CYMBAL],
    GPMidiNote.PIATTI_HAND: [CHMidiNote.GREEN, CHMidiNote.GREEN_CYMBAL],

    GPMidiNote.COWBELL_HIGH: [CHMidiNote.YELLOW],
    GPMidiNote.COWBELL_HIGH_TIP: [CHMidiNote.YELLOW, CHMidiNote.YELLOW_ACCENT],
    GPMidiNote.COWBELL_MEDIUM: [CHMidiNote.BLUE],
    GPMidiNote.COWBELL_MEDIUM_TIP: [CHMidiNote.BLUE, CHMidiNote.BLUE_ACCENT],
    GPMidiNote.COWBELL_LOW: [CHMidiNote.GREEN],
    GPMidiNote.COWBELL_LOW_TIP: [CHMidiNote.GREEN, CHMidiNote.GREEN_ACCENT],

    GPMidiNote.BONGO_HIGH_MUTE: [CHMidiNote.YELLOW, CHMidiNote.YELLOW_GHOST],
    GPMidiNote.BONGO_HIGH: [CHMidiNote.YELLOW],
    GPMidiNote.BONGO_HIGH_SLAP: [CHMidiNote.YELLOW, CHMidiNote.YELLOW_ACCENT],
    GPMidiNote.BONGO_LOW_MUTE: [CHMidiNote.BLUE, CHMidiNote.BLUE_GHOST],
    GPMidiNote.BONGO_LOW: [CHMidiNote.BLUE],
    GPMidiNote.BONGO_LOW_SLAP: [CHMidiNote.BLUE, CHMidiNote.BLUE_ACCENT],
    GPMidiNote.CONGA_HIGH_MUTE: [CHMidiNote.YELLOW, CHMidiNote.YELLOW_GHOST],
    GPMidiNote.CONGA_HIGH: [CHMidiNote.YELLOW],
    GPMidiNote.CONGA_HIGH_SLAP: [CHMidiNote.YELLOW, CHMidiNote.YELLOW_ACCENT],
    GPMidiNote.CONGA_LOW_MUTE: [CHMidiNote.BLUE, CHMidiNote.BLUE_GHOST],
    GPMidiNote.CONGA_LOW: [CHMidiNote.BLUE],
    GPMidiNote.CONGA_LOW_SLAP: [CHMidiNote.BLUE, CHMidiNote.BLUE_ACCENT],
    GPMidiNote.TIMBALE_HIGH: [CHMidiNote.YELLOW],
    GPMidiNote.TIMBALE_LOW: [CHMidiNote.BLUE],
    GPMidiNote.AGOGO_HIGH: [CHMidiNote.YELLOW, CHMidiNote.YELLOW_ACCENT],
    GPMidiNote.AGOGO_LOW: [CHMidiNote.BLUE, CHMidiNote.BLUE_ACCENT],
    GPMidiNote.SURDO: [CHMidiNote.GREEN],
    GPMidiNote.SURDO_MUTE: [CHMidiNote.GREEN, CHMidiNote.GREEN_GHOST],
    GPMidiNote.GRANCASSA: [CHMidiNote.GREEN],
    GPMidiNote.GOLPE_THUMB: [CHMidiNote.YELLOW],
    GPMidiNote.GOLPE_FINGER: [CHMidiNote.YELLOW, CHMidiNote.YELLOW_ACCENT],

    GPMidiNote.TAMBOURINE: [CHMidiNote.YELLOW, CHMidiNote.YELLOW_CYMBAL],
    GPMidiNote.TAMBOURINE_HAND: [CHMidiNote.YELLOW, CHMidiNote.YELLOW_CYMBAL],
    GPMidiNote.TAMBOURINE_RETURN: [CHMidiNote.YELLOW, CHMidiNote.YELLOW_CYMBAL],
    GPMidiNote.TAMBOURINE_ROLL: [CHMidiNote.YELLOW, CHMidiNote.YELLOW_CYMBAL],
    GPMidiNote.LEFT_MARACA: [CHMidiNote.YELLOW, CHMidiNote.YELLOW_CYMBAL],
    GPMidiNote.LEFT_MARACA_RETURN: [CHMidiNote.YELLOW, CHMidiNote.YELLOW_CYMBAL],
    GPMidiNote.RIGHT_MARACA: [CHMidiNote.YELLOW, CHMidiNote.YELLOW_CYMBAL],
    GPMidiNote.RIGHT_MARACA_RETURN: [CHMidiNote.YELLOW, CHMidiNote.YELLOW_CYMBAL],

    GPMidiNote.METRONOME: [CHMidiNote.RED, CHMidiNote.RED_GHOST],
    GPMidiNote.METRONOME_BELL: [CHMidiNote.RED, CHMidiNote.RED_ACCENT],
    GPMidiNote.CASTANETS: [CHMidiNote.RED, CHMidiNote.RED_GHOST],
    GPMidiNote.VIBRASLAP: [CHMidiNote.BLUE, CHMidiNote.BLUE_CYMBAL],
    GPMidiNote.CABASA: [CHMidiNote.YELLOW, CHMidiNote.YELLOW_CYMBAL],
    GPMidiNote.CABASA_RETURN: [CHMidiNote.YELLOW, CHMidiNote.YELLOW_CYMBAL],
    GPMidiNote.GUIRO: [CHMidiNote.YELLOW],
    GPMidiNote.GUIRO_SCRAP_RETURN: [CHMidiNote.BLUE],
    GPMidiNote.CLAVES: [CHMidiNote.YELLOW],
    GPMidiNote.WOODBLOCK_HIGH: [CHMidiNote.YELLOW],
    GPMidiNote.WOODBLOCK_LOW: [CHMidiNote.BLUE],
    GPMidiNote.CUICA_MUTE: [CHMidiNote.YELLOW, CHMidiNote.YELLOW_CYMBAL],
    GPMidiNote.CUICA_OPEN: [CHMidiNote.GREEN, CHMidiNote.GREEN_CYMBAL],
    GPMidiNote.TRIANGLE: [CHMidiNote.BLUE, CHMidiNote.BLUE_CYMBAL, CHMidiNote.BLUE_ACCENT],
    GPMidiNote.TRIANGLE_MUTE: [CHMidiNote.BLUE, CHMidiNote.BLUE_CYMBAL, CHMidiNote.BLUE_GHOST],
    GPMidiNote.SHAKER: [CHMidiNote.YELLOW, CHMidiNote.YELLOW_CYMBAL],
    GPMidiNote.SHAKER_RETURN: [CHMidiNote.YELLOW, CHMidiNote.YELLOW_CYMBAL],
    GPMidiNote.WHISTLE_HIGH: [CHMidiNote.YELLOW, CHMidiNote.YELLOW_CYMBAL],
    GPMidiNote.WHISTLE_LOW: [CHMidiNote.GREEN, CHMidiNote.GREEN_CYMBAL],
    GPMidiNote.JINGLE_BELL: [CHMidiNote.YELLOW, CHMidiNote.YELLOW_CYMBAL],
    GPMidiNote.BELL_TREE: [CHMidiNote.GREEN, CHMidiNote.GREEN_CYMBAL],
    GPMidiNote.BELL_TREE_RETURN: [CHMidiNote.GREEN, CHMidiNote.GREEN_CYMBAL],
}
