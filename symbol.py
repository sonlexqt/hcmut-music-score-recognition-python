import utils

SYMBOL_SIZE = 50


class Symbol:
    def __init__(self, class_name):
        self.class_name = class_name
        self.name = 'DEFAULT_NAME'

    def get_name(self):
        return self.name

    def get_class_name(self):
        return self.class_name


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
        # TODO XIN default octave = 4. When is octave != 4 ?
        self.pitch_octave = 4
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
