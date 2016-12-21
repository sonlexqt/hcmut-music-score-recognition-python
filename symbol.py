import utils

SYMBOL_SIZE = 50


def get_symbol_by_index(idx):
    symbol = None
    if idx is 0:
        # DOT
        symbol = SymbolDot()
    elif idx is 1:
        # KEY_SIGNATURE_1_#
        symbol = SymbolKeySignature('KEY_SIGNATURE_1_#', '1_#')
    elif idx is 2:
        # NOTE_QUARTER_UP
        symbol = SymbolNote('NOTE_QUARTER_UP', 1, 1 / 4, 'up', 37, False)
    elif idx is 3:
        # NOTE_HALF_UP
        symbol = SymbolNote('NOTE_HALF_UP', 1, 1 / 2, 'up', 37, False)
    elif idx is 4:
        # TIME_SIGNATURE_3_4
        symbol = SymbolTimeSignature('TIME_SIGNATURE_3_4', '3_4')
    elif idx is 5:
        # BAR
        symbol = SymbolBar('BAR_SINGLE', 'single')
    elif idx is 6:
        # NOTE_QUARTER_DOWN
        symbol = SymbolNote('NOTE_QUARTER_DOWN', 1, 1 / 4, 'down', 0, False)
    elif idx is 7:
        # BEAM_2_EIGHTH_NOTES_UP
        symbol = SymbolNote('BEAM_2_EIGHTH_NOTES_UP', 2, 1 / 4, 'up', 36, False)
    elif idx is 8:
        # BEAM_2_EIGHTH_NOTES_DOWN
        symbol = SymbolNote('BEAM_2_EIGHTH_NOTES_DOWN', 2, 1 / 4, 'down', 0, False)
    elif idx is 9:
        # FINAL_BAR
        symbol = SymbolBar('BAR_DOUBLE', 'double')
    elif idx is 10:
        # REST_QUARTER
        symbol = SymbolRest('REST_QUARTER', 4)
    elif idx is 11:
        # NOTE_HALF_DOWN
        symbol = SymbolNote('NOTE_HALF_DOWN', 1, 1 / 2, 'down', 0, False)
    elif idx is 12:
        # NOTE_EIGHTH_DOWN
        symbol = SymbolNote('NOTE_EIGHTH_DOWN', 1, 1 / 8, 'down', 0, False)
    elif idx is 13:
        # KEY_SIGNATURE_2_#
        symbol = SymbolKeySignature('KEY_SIGNATURE_2_#', '2_#')
    elif idx is 14:
        # CLEF_TREBLE
        symbol = SymbolClef('CLEF_TREBLE', 'treble')
    elif idx is 15:
        # NOTE_EIGHTH_UP
        symbol = SymbolNote('NOTE_EIGHTH_UP', 1, 1 / 8, 'up', 37, False)
    elif idx is 16:
        # NOTE_HALF_UP_WITH_DOT
        symbol = SymbolNote('NOTE_HALF_UP_WITH_DOT', 1, 1 / 2, 'up', 37, True)
    elif idx is 17:
        # TIE
        symbol = SymbolTie()
    elif idx is 18:
        # TIME_SIGNATURE_4_4
        symbol = SymbolTimeSignature('TIME_SIGNATURE_4_4', '4_4')
    elif idx is 19:
        # NOTE_QUARTER_UP_WITH_DOT
        symbol = SymbolNote('NOTE_QUARTER_UP_WITH_DOT', 1, 1 / 4, 'up', 37, True)
    elif idx is 20:
        # NOTE_WHOLE
        symbol = SymbolNote('NOTE_WHOLE', 1, 1, 'up', 0, False)
    else:
        print('!FAIL Symbol recognition - getting index:', idx)
    return symbol


class Symbol:
    def __init__(self, class_name):
        self.class_name = class_name
        self.name = 'DEFAULT_NAME'

    def get_name(self):
        return self.name

    def get_class_name(self):
        return self.class_name

    @staticmethod
    def get(index):
        return get_symbol_by_index(index)


class SymbolDot(Symbol):
    def __init__(self):
        super().__init__('dot')
        self.name = 'DOT'


# class SymbolsAccidental(Symbols):
#     def __init__(self, name, s_type):
#         super().__init__('accidental')
#         self.name = name
#         self.type = s_type  # sharp, flat, double_sharp, double_flat


class SymbolNote(Symbol):
    def __init__(self, name, number_of_notes, duration, direction, offset, with_dot):
        super().__init__('note')
        self.name = name
        self.number_of_notes = number_of_notes
        self.duration = duration
        self.direction = direction
        self.offset = offset
        self.pitch_step = None
        self.pitch_octave = None
        self.with_dot = with_dot

    def set_pitch(self, step, octave):
        self.pitch_step = step
        self.pitch_octave = octave

    def get_pitch(self):
        return self.pitch_step

    def calculate_pitch(self, rect, group_index, symbol_index, staff_lines, staff_line_space):
        rect_converted = utils.Utils.convert_coordinate(rect)
        left, top, right, bottom = utils.Utils.get_rect_coordinates(rect_converted)
        rect_width = abs(right - left)
        rect_height = abs(top - bottom)
        note_pos = top + rect_height * self.offset / SYMBOL_SIZE

        middle_line_index = group_index * 5 + 2
        middle_line = staff_lines[middle_line_index]
        middle_line_pos = middle_line[0]

        distance = abs(middle_line_pos - note_pos)
        module = int(distance * 2 / staff_line_space) % 7
        if self.direction == 'up':
            if module == 0:
                self.set_pitch('A', None)
            elif module == 1:
                self.set_pitch('G', None)
            elif module == 2:
                self.set_pitch('F', None)
            elif module == 3:
                self.set_pitch('E', None)
            elif module == 4:
                self.set_pitch('D', None)
            elif module == 5:
                self.set_pitch('C', None)
            elif module == 6:
                self.set_pitch('B', None)
        elif self.direction == 'down':
            if module == 0:
                self.set_pitch('B', None)
            elif module == 1:
                self.set_pitch('C', None)
            elif module == 2:
                self.set_pitch('D', None)
            elif module == 3:
                self.set_pitch('E', None)
            elif module == 4:
                self.set_pitch('F', None)
            elif module == 5:
                self.set_pitch('G', None)
            elif module == 6:
                self.set_pitch('A', None)
        return 0


class SymbolTimeSignature(Symbol):
    def __init__(self, name, time_signature_type):
        super().__init__('time_signature')
        self.name = name
        self.type = time_signature_type


class SymbolBar(Symbol):
    def __init__(self, name, bar_type):
        super().__init__('bar')
        self.name = name
        self.type = bar_type


class SymbolRest(Symbol):
    def __init__(self, name, duration):
        super().__init__('rest')
        self.name = name
        self.duration = duration


class SymbolKeySignature(Symbol):
    def __init__(self, name, key_signature_type):
        super().__init__('key_signature')
        self.name = name
        self.type = key_signature_type


class SymbolClef(Symbol):
    def __init__(self, name, clef_type):
        super().__init__('clef')
        self.name = name
        self.type = clef_type


class SymbolTie(Symbol):
    def __init__(self):
        super().__init__('tie')
        self.name = 'TIE'
