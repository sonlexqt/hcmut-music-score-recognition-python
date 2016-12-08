import matplotlib.pyplot as plt
import matplotlib.patches as patches
from utils import Utils
from random import randint


def generate_random_color():
    r = lambda: randint(0, 255)
    color = '#%02X%02X%02X' % (r(), r(), r())
    return color


def generate_random_rect(max_rect_size, max_plot_width, max_plot_height):
    rect_width = randint(1, max_rect_size)
    rect_height = randint(1, max_rect_size)
    left = randint(-max_plot_width, max_plot_width - rect_width)
    top = randint(-max_plot_height + rect_height, max_plot_height)
    return [(left, top), (left + rect_width, top - rect_height)]


def generate_random_rects(max_rect_size, max_plot_width, max_plot_height, num_of_rects):
    res = []
    for i in range(0, num_of_rects):
        rect = generate_random_rect(max_rect_size, max_plot_width, max_plot_height)
        res.append(rect)
    return res

""" Constants """
MAX_PLOT_WIDTH = 20
MAX_PLOT_HEIGHT = 5
MAX_RECT_SIZE = 4
NUM_OF_RECTS = 30


fig1 = plt.figure(figsize=(15, 15))
ax1 = fig1.add_subplot(211, aspect='equal')
ax1.set_xlim([-MAX_PLOT_WIDTH, MAX_PLOT_WIDTH])
ax1.set_ylim([-MAX_PLOT_HEIGHT, MAX_PLOT_HEIGHT])
ax2 = fig1.add_subplot(212, aspect='equal')
ax2.set_xlim([-MAX_PLOT_WIDTH, MAX_PLOT_WIDTH])
ax2.set_ylim([-MAX_PLOT_HEIGHT, MAX_PLOT_HEIGHT])

rects_init = generate_random_rects(MAX_RECT_SIZE, MAX_PLOT_WIDTH, MAX_PLOT_HEIGHT, NUM_OF_RECTS)
rects_final = Utils.remove_overlapping_rectangles(rects_init)

print(rects_init)
print(len(rects_init))
print(rects_final)
print(len(rects_final))

for rect in rects_init:
    left, top, right, bottom = Utils.get_rect_coordinates(rect)
    width = abs(right - left)
    height = abs(top - bottom)
    ax1.add_patch(
        patches.Rectangle(
            (left, bottom),  # (x,y) (left, bottom) or lower left
            width,  # width
            height,  # height
            facecolor=generate_random_color(),
            alpha=0.2,
        )
    )

for rect in rects_final:
    left, top, right, bottom = Utils.get_rect_coordinates(rect)
    width = abs(right - left)
    height = abs(top - bottom)
    ax2.add_patch(
        patches.Rectangle(
            (left, bottom),  # (x,y) (left, bottom) or lower left
            width,  # width
            height,  # height
            facecolor='red',
            alpha=0.2,
        )
    )
plt.show()
