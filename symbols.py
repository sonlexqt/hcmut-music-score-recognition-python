def get_symbol_by_index(idx):
    symbol = 'NOT_FOUND'
    if idx is 0:
        symbol = 'DOT'
    elif idx is 1:
        symbol = 'SHARP'
    elif idx is 2:
        symbol = 'QUARTER_NOTE'
    elif idx is 3:
        symbol = 'HALF_NOTE'
    elif idx is 4:
        symbol = 'MEASURE_3_4'
    elif idx is 5:
        symbol = 'BAR'
    elif idx is 6:
        symbol = 'QUARTER_NOTE_REVERSED'
    elif idx is 7:
        symbol = 'BEAM_TWO_EIGHTH_NOTES'
    elif idx is 8:
        symbol = 'BEAM_TWO_EIGHTH_NOTES_REVERSED'
    elif idx is 9:
        symbol = 'FINAL_BAR'
    elif idx is 10:
        symbol = 'QUARTER_REST'
    elif idx is 11:
        symbol = 'HALF_NOTE_REVERSED'
    elif idx is 12:
        symbol = 'EIGHTH_NOTE_REVERSED'
    elif idx is 13:
        symbol = 'SHARP_DOUBLE'
    elif idx is 14:
        symbol = 'TREBLE_CLEF'
    elif idx is 15:
        symbol = 'EIGHT_NOTE'
    elif idx is 16:
        symbol = 'HALF_NOTE_WITH_DOT'
    elif idx is 17:
        symbol = 'TIE'
    elif idx is 18:
        symbol = 'MEASURE-4-4'
    elif idx is 19:
        symbol = 'QUARTER_NOTE_WITH_DOT'
    elif idx is 20:
        symbol = 'WHOLE_NOTE'
    return symbol


class Symbols:
    @staticmethod
    def get(index):
        return get_symbol_by_index(index)
