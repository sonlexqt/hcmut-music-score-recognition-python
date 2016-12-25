# Import libraries
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
# Import modules
import utils

SYMBOL_SIZE = 50


class Symbol:
    def __init__(self, class_name):
        self.class_name = class_name
        self.name = 'DEFAULT_NAME'

    def get_xml_elem(self, divisions):
        text = 'Default get_xml_elem method with divisions = ' + str(divisions) + ' - name: ' \
               + self.name + ' - class_name: ' + self.class_name
        elem_comment = Comment(text)
        return [elem_comment]


class SymbolDot(Symbol):
    def __init__(self):
        super().__init__('dot')
        self.name = 'DOT'

    def get_xml_elem(self, divisions):
        elem_bar = Element('dot')
        return [elem_bar]


# class SymbolsAccidental(Symbols):
#     def __init__(self, name, s_type):
#         super().__init__('accidental')
#         self.name = name
#         self.type = s_type  # sharp, flat, double_sharp, double_flat


class SymbolSingleNote(Symbol):
    def __init__(self, name, duration, direction, offset, has_dot):
        super().__init__('note')
        self.number_of_notes = 1
        self.name = name
        self.duration = duration
        self.direction = direction
        self.offset = offset
        self.pitch_step = 'G'  # Default pitch step = 'G'
        self.pitch_alter = 0  # Default alter value = 0
        self.pitch_octave = 4  # Default pitch octave = 4
        self.has_dot = has_dot

    def set_pitch(self, step, octave):
        self.pitch_step = step
        self.pitch_octave = octave

    def calculate_pitch(self, rect, group_index, symbol_index, staff_lines, staff_line_space, staff_line_width):
        rect_converted = utils.Utils.convert_coordinate(rect)
        left, top, right, bottom = utils.Utils.get_rect_coordinates(rect_converted)
        rect_width = abs(right - left)
        rect_height = abs(top - bottom)
        note_pos = top + rect_height * self.offset / SYMBOL_SIZE
        middle_line_index = group_index * 5 + 2
        middle_line = staff_lines[middle_line_index]
        middle_line_pos = middle_line[0] + middle_line[1] / 2
        distance = abs(middle_line_pos - note_pos)
        staff_line_space_extended = staff_line_space + staff_line_width
        module = int(round(distance * 2 / staff_line_space_extended)) % 7
        note_step = self.pitch_step
        note_octave = self.pitch_octave
        if self.direction == 'up':
            if module == 0:
                note_step = 'A'
            elif module == 1:
                note_step = 'G'
            elif module == 2:
                note_step = 'F'
            elif module == 3:
                note_step = 'E'
            elif module == 4:
                note_step = 'D'
            elif module == 5:
                note_step = 'C'
            elif module == 6:
                note_step = 'B'
        elif self.direction == 'down':
            if module == 0:
                note_step = 'A'
            elif module == 1:
                note_step = 'B'
            elif module == 2:
                note_step = 'C'
            elif module == 3:
                note_step = 'D'
            elif module == 4:
                note_step = 'E'
            elif module == 5:
                note_step = 'F'
            elif module == 6:
                note_step = 'G'
            # Decide if this note's octave is 4 or 5
            if distance > staff_line_space * 0.75:
                note_octave = 5
        self.set_pitch(note_step, note_octave)
        return 0

    def get_xml_elem(self, divisions):
        elem_note = Element('note')
        # pitch
        elem_pitch = SubElement(elem_note, 'pitch')
        elem_step = SubElement(elem_pitch, 'step')
        elem_step.text = self.pitch_step
        elem_alter = SubElement(elem_pitch, 'alter')
        elem_alter.text = str(self.pitch_alter)
        elem_octave = SubElement(elem_pitch, 'octave')
        elem_octave.text = str(self.pitch_octave)
        # duration
        duration = int(self.duration / (1 / 4) * divisions)
        if self.has_dot:
            duration *= 1.5
        elem_duration = SubElement(elem_note, 'duration')
        elem_duration.text = str(int(duration))
        # type
        note_type = utils.Utils.get_note_type(self.duration)
        elem_type = SubElement(elem_note, 'type')
        elem_type.text = str(note_type)
        # dot
        if self.has_dot:
            elem_dot = SubElement(elem_note, 'dot')
        # stem
        elem_stem = SubElement(elem_note, 'stem')
        elem_stem.text = str(self.direction)
        return [elem_note]


class SymbolBeamNote(Symbol):
    def __init__(self, name, durations, direction, offsets):
        super().__init__('note')
        self.number_of_notes = 2
        self.name = name
        self.direction = direction
        self.durations = durations
        self.offsets = offsets
        self.pitch_steps = ['G', 'G']  # # Default pitch step = 'G'
        self.pitch_alters = [0, 0]  # Default alter = 0
        self.pitch_octaves = [4, 4]  # Default pitch octave = 4

    def set_pitch(self, steps, octaves):
        self.pitch_steps = steps
        self.pitch_octaves = octaves

    def calculate_pitch(self, rect, group_index, symbol_index, staff_lines, staff_line_space, staff_line_width):
        rect_converted = utils.Utils.convert_coordinate(rect)
        left, top, right, bottom = utils.Utils.get_rect_coordinates(rect_converted)
        rect_width = abs(right - left)
        rect_height = abs(top - bottom)

        note_pitches = []
        note_octaves = []
        for i in range(0, self.number_of_notes):
            offset = self.offsets[i]
            note_pos = top + rect_height * offset / SYMBOL_SIZE
            middle_line_index = group_index * 5 + 2
            middle_line = staff_lines[middle_line_index]
            middle_line_pos = middle_line[0]
            distance = abs(middle_line_pos - note_pos)
            staff_line_space_extended = staff_line_space + staff_line_width
            module = int(round(distance * 2 / staff_line_space_extended)) % 7
            note_step = self.pitch_steps[i]
            note_octave = self.pitch_octaves[i]
            if self.direction == 'up':
                if module == 0:
                    note_step = 'A'
                elif module == 1:
                    note_step = 'G'
                elif module == 2:
                    note_step = 'F'
                elif module == 3:
                    note_step = 'E'
                elif module == 4:
                    note_step = 'D'
                elif module == 5:
                    note_step = 'C'
                elif module == 6:
                    note_step = 'B'
            elif self.direction == 'down':
                if module == 0:
                    note_step = 'A'
                elif module == 1:
                    note_step = 'B'
                elif module == 2:
                    note_step = 'C'
                elif module == 3:
                    note_step = 'D'
                elif module == 4:
                    note_step = 'E'
                elif module == 5:
                    note_step = 'F'
                elif module == 6:
                    note_step = 'G'
                # Decide if this note's octave is 4 or 5
                if distance > staff_line_space * 0.75:
                    note_octave = 5
            note_pitches.append(note_step)
            note_octaves.append(note_octave)
        self.set_pitch(note_pitches, note_octaves)
        return 0

    def get_xml_elem(self, divisions):
        elems_notes = []
        for i in range(0, self.number_of_notes):
            elem_note = Element('note')
            # pitch
            elem_pitch = SubElement(elem_note, 'pitch')
            elem_step = SubElement(elem_pitch, 'step')
            elem_step.text = self.pitch_steps[i]
            elem_alter = SubElement(elem_pitch, 'alter')
            elem_alter.text = str(self.pitch_alters[i])
            elem_octave = SubElement(elem_pitch, 'octave')
            elem_octave.text = str(self.pitch_octaves[i])
            # duration
            duration = int(self.durations[i] / (1/4) * divisions)
            elem_duration = SubElement(elem_note, 'duration')
            elem_duration.text = str(duration)
            # type
            note_type = utils.Utils.get_note_type(self.durations[i])
            elem_type = SubElement(elem_note, 'type')
            elem_type.text = str(note_type)
            # stem
            elem_stem = SubElement(elem_note, 'stem')
            elem_stem.text = str(self.direction)
            # beam
            elem_beam = SubElement(elem_note, 'beam')
            elem_beam.attrib['number'] = str(1)
            if i is 0:
                elem_beam.text = 'begin'
            else:
                elem_beam.text = 'end'
            elems_notes.append(elem_note)
        return elems_notes


class SymbolTimeSignature(Symbol):
    def __init__(self, name, beats, beat_type):
        super().__init__('time_signature')
        self.name = name
        self.beats = beats
        self.beat_type = beat_type

    def get_xml_elem(self, divisions):
        elem_time = Element('time')
        elem_beats = SubElement(elem_time, 'beats')
        elem_beats.text = str(self.beats)
        elem_beat_type = SubElement(elem_time, 'beat-type')
        elem_beat_type.text = str(self.beat_type)
        return [elem_time]


class SymbolBar(Symbol):
    def __init__(self, name, bar_type):
        super().__init__('bar')
        self.name = name
        self.type = bar_type

    def get_xml_elem(self, divisions):
        elem_bar = Element('bar')
        return [elem_bar]


class SymbolRest(Symbol):
    def __init__(self, name, duration):
        super().__init__('rest')
        self.name = name
        self.duration = duration


class SymbolKeySignature(Symbol):
    def __init__(self, name, key_signature_number):
        super().__init__('key_signature')
        self.name = name
        self.number = key_signature_number
        self.affected_notes = utils.Utils.get_key_signature_affected_notes(self.number)

    def get_xml_elem(self, divisions):
        elem_key = Element('key')
        elem_fifths = SubElement(elem_key, 'fifths')
        elem_fifths.text = str(self.number)
        return [elem_key]


class SymbolClef(Symbol):
    def __init__(self, name, clef_type):
        super().__init__('clef')
        self.name = name
        self.type = clef_type

    def get_xml_elem(self, divisions):
        elem_clef = Element('clef')
        elem_sign = SubElement(elem_clef, 'sign')
        elem_sign.text = 'G'
        elem_line = SubElement(elem_clef, 'line')
        elem_line.text = '2'
        return [elem_clef]


class SymbolTie(Symbol):
    def __init__(self):
        super().__init__('tie')
        self.name = 'TIE'
