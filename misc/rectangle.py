from random import randint


class Rectangle:
    """Common base class for all rectangles"""

    def __init__(self, left, top, width, height):
        self.pos = (left, top)
        self.width = width
        self.height = height

    def get_coordinates(self):
        top = self.pos[0]
        left = self.pos[1]
        right = self.pos[0] + self.width
        bottom = self.pos[1] - self.height
        return top, left, right, bottom

    def is_equal(self, rect):
        top1, left1, width1, height1 = self.get_coordinates()
        top2, left2, width2, height2 = rect.get_coordinates()
        return top1 == top2 and left1 == left2 and width1 == width2 and height1 == height2

    def is_intersected(self, rect):
        intersection = Rectangle.intersection(self, rect)
        if intersection:
            return True
        else:
            return False

    def is_in_list(self, list):
        for rect in list:
            if self.is_equal(rect):
                return True
        return False

    def print(self):
        print('left:', self.pos[0])
        print('top:', self.pos[1])
        print('width:', self.width)
        print('height:', self.height)

    @staticmethod
    def get_random(max_rect_size, max_plot_width, max_plot_height):
        rect_width = randint(1, max_rect_size)
        rect_height = randint(1, max_rect_size)
        left = randint(-max_plot_width, max_plot_width - rect_width)
        top = randint(-max_plot_height + rect_height, max_plot_height)
        return Rectangle(left, top, rect_width, rect_height)

    @staticmethod
    def union(rect1, rect2):
        # rect1's coordinates
        left1, top1, right1, bottom1 = rect1.get_coordinates()
        # rect2's coordinates
        left2, top2, right2, bottom2 = rect2.get_coordinates()
        # Calculate the union
        left = min(left1, left2)
        top = max(top1, top2)
        right = max(right1, right2)
        bottom = min(bottom1, bottom2)
        width = abs(right - left)
        height = abs(top - bottom)
        return Rectangle(left, top, width, height)

    @staticmethod
    def intersection(rect1, rect2):
        # rect1's coordinates
        left1, top1, right1, bottom1 = rect1.get_coordinates()
        # rect2's coordinates
        left2, top2, right2, bottom2 = rect2.get_coordinates()
        # Calculate the intersection
        left = max(left1, left2)
        top = min(top1, top2)
        right = min(right1, right2)
        bottom = max(bottom1, bottom2)
        if left < right and top > bottom:
            width = abs(right - left)
            height = abs(top - bottom)
            return Rectangle(left, top, width, height)
        else:
            return None
