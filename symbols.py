def get_symbol_by_index(idx):
    symbol = 'NOT_FOUND'
    if idx is 0:
        symbol = 'DOT'
    elif idx is 1:
        symbol = 'ACCIDENTAL_SHARP'
    elif idx is 2:
        symbol = 'NOTE_QUARTER_UP'
    elif idx is 3:
        symbol = 'NOTE_HALF_UP'
    elif idx is 4:
        symbol = 'TIME_SIGNATURE_3_4'
    elif idx is 5:
        symbol = 'BAR'
    elif idx is 6:
        symbol = 'NOTE_QUARTER_DOWN'
    elif idx is 7:
        symbol = 'BEAM_2_EIGHTH_NOTES_UP'
    elif idx is 8:
        symbol = 'BEAM_2_EIGHTH_NOTES_DOWN'
    elif idx is 9:
        symbol = 'FINAL_BAR'
    elif idx is 10:
        symbol = 'REST_QUARTER'
    elif idx is 11:
        symbol = 'NOTE_HALF_DOWN'
    elif idx is 12:
        symbol = 'NOTE_EIGHTH_DOWN'
    elif idx is 13:
        symbol = 'KEY_SIGNATURE_DOUBLE_#'
    elif idx is 14:
        symbol = 'CLEF_TREBLE'
    elif idx is 15:
        symbol = 'NOTE_EIGHTH_UP'
    elif idx is 16:
        symbol = 'NOTE_HALF_UP_WITH_DOT'
    elif idx is 17:
        symbol = 'TIE'
    elif idx is 18:
        symbol = 'TIME_SIGNATURE_4_4'
    elif idx is 19:
        symbol = 'NOTE_QUARTER_UP_WITH_DOT'
    elif idx is 20:
        symbol = 'NOTE_WHOLE'
    return symbol


class Symbols:
    @staticmethod
    def get(index):
        return get_symbol_by_index(index)
