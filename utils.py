# Import libraries
from random import randint
import numpy as np
import cv2
# Import modules
import symbol

train = None
train_labels = None
knn = None


def union(rect1, rect2):
    # rect1's coordinates
    left1, top1, right1, bottom1 = Utils.get_rect_coordinates(rect1)
    # rect2's coordinates
    left2, top2, right2, bottom2 = Utils.get_rect_coordinates(rect2)
    # Calculate the union
    left = min(left1, left2)
    top = max(top1, top2)
    right = max(right1, right2)
    bottom = min(bottom1, bottom2)
    return [(left, top), (right, bottom)]


def intersection(rect1, rect2):
    # rect1's coordinates
    left1, top1, right1, bottom1 = Utils.get_rect_coordinates(rect1)
    # rect2's coordinates
    left2, top2, right2, bottom2 = Utils.get_rect_coordinates(rect2)
    # Calculate the intersection
    left = max(left1, left2)
    top = min(top1, top2)
    right = min(right1, right2)
    bottom = max(bottom1, bottom2)
    if left < right and top > bottom:
        return [(left, top), (right, bottom)]
    else:
        return None


def is_intersected(rect1, rect2):
    intersect = intersection(rect1, rect2)
    if intersect:
        return True
    else:
        return False


def need_to_be_merged(rect, result):
    for res_rect in result:
        if is_intersected(rect, res_rect):
            return True
    return False


def recursively_merge(rect, result):
    is_clean = True
    merged_rect = None
    for idx, res_rect in enumerate(result):
        if rect == res_rect:
            continue
        if is_intersected(rect, res_rect):
            is_clean = False
            result[idx] = union(rect, res_rect)
            merged_rect = res_rect
            break
    if not is_clean:
        return recursively_merge(merged_rect, result)


def remove_duplicates(rects):
    res = []
    for r in rects:
        if not r in res:
            res.append(r)
    return res


def symbols_in_group_sort_key(rect):
    left, top, right, bottom = Utils.get_rect_coordinates(rect)
    return left


def treble_clefs_sort_key(treble_clef):
    left, top, right, bottom = Utils.get_rect_coordinates(treble_clef)
    return top


def is_rect_in_bounds(rect, upper_bound, lower_bound):
    rect_converted = Utils.convert_coordinate(rect)
    left, top, right, bottom = Utils.get_rect_coordinates(rect_converted)
    if upper_bound < top < lower_bound:
        return True
    else:
        return False

"""
MAIN CLASS
"""


class Utils:
    @staticmethod
    def generate_random_color():
        r = lambda: randint(0, 255)
        color = '#%02X%02X%02X' % (r(), r(), r())
        return color

    @staticmethod
    def remove_overlapping_rectangles(rects):
        rects_merged = []
        for rect in rects:
            if need_to_be_merged(rect, rects_merged):
                recursively_merge(rect, rects_merged)
            else:
                rects_merged.append(rect)
        return remove_duplicates(rects_merged)

    @staticmethod
    def get_rect_coordinates(rect_input):
        res_left = rect_input[0][0]
        res_top = rect_input[0][1]
        res_right = rect_input[1][0]
        res_bottom = rect_input[1][1]
        return res_left, res_top, res_right, res_bottom

    @staticmethod
    def sort_rectangles(rects, treble_clefs, staff_lines, staff_height):
        res = []
        for idx, treble_clef in enumerate(treble_clefs):
            # Create a new symbols group
            symbols_group = []
            # Get this treble position
            treble_clef_converted = Utils.convert_coordinate(treble_clef)
            left, top, right, bottom = Utils.get_rect_coordinates(treble_clef_converted)
            # Buffer the position each direction by 1/2 staff height
            buffer = staff_height / 2
            # Get the bounds
            upper_bound = top - buffer
            lower_bound = bottom + buffer
            # Push symbols to this group, including this treble clef
            symbols_group = [rect for rect in rects if is_rect_in_bounds(rect, upper_bound, lower_bound)]
            # Sort this symbols group base on rect.x value
            symbols_group_sorted = sorted(symbols_group, key=symbols_in_group_sort_key)
            # Push this symbols group to res
            res.append(symbols_group_sorted)
        return res

    @staticmethod
    def init_knn():
        global train, train_labels, knn
        # Load the data
        with np.load('symbols_knn_data.npz') as data:
            train = data['train']
            train_labels = data['train_labels']
        knn = cv2.ml.KNearest_create()
        knn.train(train, cv2.ml.ROW_SAMPLE, train_labels)

    @staticmethod
    def recognize_symbol(symbol_img):
        global knn
        # symbol_gray = cv2.cvtColor(symbol_img, cv2.COLOR_BGR2GRAY)
        symbol_np_array = np.array(symbol_img)
        new_comer = symbol_np_array.reshape(-1)[:, np.newaxis].astype(np.float32).T
        ret, results, neighbours, dist = knn.findNearest(new_comer, k=5)
        result_int = int(results[0][0])
        return Utils.get_symbol_by_index(result_int)

    @staticmethod
    def sort_treble_clefts(treble_clefs):
        treble_clefs_converted = list(map(Utils.convert_coordinate, treble_clefs))
        treble_clefs_sorted = sorted(treble_clefs_converted, key=treble_clefs_sort_key)
        treble_clefs_restored = list(map(Utils.convert_coordinate, treble_clefs_sorted))
        return treble_clefs_restored

    @staticmethod
    def remove_other_rectangles(rects_merged, treble_clefs):
        first_tc = treble_clefs[0]
        first_tc_converted = Utils.convert_coordinate(first_tc)
        left1, top1, right1, bottom1 = Utils.get_rect_coordinates(first_tc_converted)

        last_tc = treble_clefs[len(treble_clefs) - 1]
        last_tc_converted = Utils.convert_coordinate(last_tc)
        left2, top2, right2, bottom2 = Utils.get_rect_coordinates(last_tc_converted)
        # This is a "buffer", used for keeping some symbols that should not be removed
        buffer = bottom2 - top2
        # Define the bounds
        upper_bound = top1 - buffer
        lower_bound = bottom2 + buffer
        # Only get the symbols between the bounds
        result = [rect for rect in rects_merged if is_rect_in_bounds(rect, upper_bound, lower_bound)]
        return result

    @staticmethod
    def convert_coordinate(rect):
        # Convert coordinate from the Descartes to OpenCV and vice versa
        left, top, right, bottom = Utils.get_rect_coordinates(rect)
        restored_p1 = (left, -top)
        restored_p2 = (right, -bottom)
        return [restored_p1, restored_p2]

    @staticmethod
    def get_symbol_by_index(idx):
        sbl = None
        if idx == 0:
            # DOT
            sbl = symbol.SymbolDot()
        elif idx == 1:
            # KEY_SIGNATURE_1_#
            sbl = symbol.SymbolKeySignature('KEY_SIGNATURE_1_#', 1)
        elif idx == 2:
            # NOTE_QUARTER_UP
            sbl = symbol.SymbolSingleNote('NOTE_QUARTER_UP', 1/4, 'up', 37, False)
        elif idx == 3:
            # NOTE_HALF_UP
            sbl = symbol.SymbolSingleNote('NOTE_HALF_UP', 1/2, 'up', 37, False)
        elif idx == 4:
            # TIME_SIGNATURE_3_4
            sbl = symbol.SymbolTimeSignature('TIME_SIGNATURE_3_4', 3, 4)
        elif idx == 5:
            # BAR
            sbl = symbol.SymbolBar('BAR_SINGLE', 'single')
        elif idx == 6:
            # NOTE_QUARTER_DOWN
            sbl = symbol.SymbolSingleNote('NOTE_QUARTER_DOWN', 1/4, 'down', 0, False)
        elif idx == 7:
            # BEAM_2_EIGHTH_NOTES_UP
            sbl = symbol.SymbolBeamNote('BEAM_2_EIGHTH_NOTES_UP', [1/8, 1/8], 'up', [36, 36])
        elif idx == 8:
            # BEAM_2_EIGHTH_NOTES_DOWN
            sbl = symbol.SymbolBeamNote('BEAM_2_EIGHTH_NOTES_DOWN', [1/8, 1/8], 'down', [0, 0])
        elif idx == 9:
            # FINAL_BAR
            sbl = symbol.SymbolBar('BAR_DOUBLE', 'double')
        elif idx == 10:
            # REST_QUARTER
            sbl = symbol.SymbolRest('REST_QUARTER', 4)
        elif idx == 11:
            # NOTE_HALF_DOWN
            sbl = symbol.SymbolSingleNote('NOTE_HALF_DOWN', 1/2, 'down', 0, False)
        elif idx == 12:
            # NOTE_EIGHTH_DOWN
            sbl = symbol.SymbolSingleNote('NOTE_EIGHTH_DOWN', 1/8, 'down', 0, False)
        elif idx == 13:
            # KEY_SIGNATURE_2_#
            sbl = symbol.SymbolKeySignature('KEY_SIGNATURE_2_#', 2)
        elif idx == 14:
            # CLEF_TREBLE
            sbl = symbol.SymbolClef('CLEF_TREBLE', 'treble')
        elif idx == 15:
            # NOTE_EIGHTH_UP
            sbl = symbol.SymbolSingleNote('NOTE_EIGHTH_UP', 1/8, 'up', 37, False)
        elif idx == 16:
            # NOTE_HALF_UP_WITH_DOT
            sbl = symbol.SymbolSingleNote('NOTE_HALF_UP_WITH_DOT', 1/2, 'up', 37, True)
        elif idx == 17:
            # TIE
            sbl = symbol.SymbolTie()
        elif idx == 18:
            # TIME_SIGNATURE_4_4
            sbl = symbol.SymbolTimeSignature('TIME_SIGNATURE_4_4', 4, 4)
        elif idx == 19:
            # NOTE_QUARTER_UP_WITH_DOT
            sbl = symbol.SymbolSingleNote('NOTE_QUARTER_UP_WITH_DOT', 1/4, 'up', 37, True)
        elif idx == 20:
            # NOTE_WHOLE
            sbl = symbol.SymbolSingleNote('NOTE_WHOLE', 1, 'up', 0, False)
        else:
            print('!FAIL Symbol recognition - getting index:', idx)
        return sbl

    @staticmethod
    def get_note_type(duration):
        if duration == 1:
            return 'whole'
        elif duration == 1/2:
            return 'half'
        elif duration == 1/4:
            return 'quarter'
        elif duration == 1/8:
            return 'eighth'
        elif duration == 1/16:
            return '16th'
        else:
            print('! ERROR: No note type matched for duration:', duration)

    @staticmethod
    def get_key_signature_affected_notes(number):
        res = None
        if number == 0:
            res = []
        elif number == 1:
            res = ['F']
        elif number == 2:
            res = ['F', 'C']
        elif number == 3:
            res = ['F', 'C', 'G']
        elif number == 4:
            res = ['F', 'C', 'G', 'D']
        elif number == 5:
            res = ['F', 'C', 'G', 'D', 'A']
        elif number == 6:
            res = ['F', 'C', 'G', 'D', 'A', 'E']
        elif number == 7:
            res = ['F', 'C', 'G', 'D', 'A', 'E', 'B']
        elif number == -1:
            res = ['B']
        elif number == -2:
            res = ['B', 'E']
        elif number == -3:
            res = ['B', 'E', 'A']
        elif number == -4:
            res = ['B', 'E', 'A', 'D']
        elif number == -5:
            res = ['B', 'E', 'A', 'D', 'G']
        elif number == -6:
            res = ['B', 'E', 'A', 'D', 'G', 'C']
        elif number == -7:
            res = ['B', 'E', 'A', 'D', 'G', 'C', 'F']
        else:
            print('! ERROR: No affected notes for key signature number:', number)
        return res
