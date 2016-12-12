from symbols import Symbols
from random import randint
import numpy as np
import cv2

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


def convert_coordinate(rect):
    left, top, right, bottom = Utils.get_rect_coordinates(rect)
    restored_p1 = (left, -top)
    restored_p2 = (right, -bottom)
    return [restored_p1, restored_p2]


def rectangles_sort_key(rect):
    left, top, right, bottom = Utils.get_rect_coordinates(rect)
    return left + top * top


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
    def sort_rectangles(rects):
        rects_converted = list(map(convert_coordinate, rects))
        rects_sorted = sorted(rects_converted, key=rectangles_sort_key)
        rects_restored = list(map(convert_coordinate, rects_sorted))
        return rects_restored

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
        symbol_gray = cv2.cvtColor(symbol_img, cv2.COLOR_BGR2GRAY)
        symbol_np_array = np.array(symbol_gray)
        new_comer = symbol_np_array.reshape(-1)[:, np.newaxis].astype(np.float32).T
        ret, results, neighbours, dist = knn.findNearest(new_comer, k=5)
        result_int = int(results[0][0])
        return Symbols.get(result_int)
