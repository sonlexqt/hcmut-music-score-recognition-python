from random import randint


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
