import matplotlib.pyplot as plt
import numpy as np
from numpy import array
import cv2

IMG_PATH = '../../images/scores/'
IMG_1 = '1-jingle-bells.jpg'
IMG_2 = '2-silent-night.jpg'
IMG_3 = '3-happy-birthday.jpg'
IMG_4 = '4-we-wish-you-a-merry-christmas.jpg'
IMG_5 = '5-auld-lang-syne.jpg'
IMG_TEST = IMG_3
IMG_FILE = IMG_PATH + IMG_TEST
IMG_FILE = 'img_rotated.jpg'
im = cv2.imread(IMG_FILE)
im_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
height, width = im.shape[:2]
dpi = 80
plt.figure(figsize=(width/dpi, height/dpi), dpi=dpi)

y_pos = np.arange(height)
# data = np.random.randint(0, width, size=height)
data = np.empty(height)
data.fill(0)

_, im_thresh = cv2.threshold(im_gray, 127, 255, cv2.THRESH_BINARY_INV)
# Calculate horizontal projection
for h in range(0, height):
    sum_of_rows = 0
    for w in range(0, width):
        sum_of_rows += im_thresh[h, w] / 255
    data[h] = sum_of_rows
# Get the maximum of the projection(T)
T = data[0]
for h in range(0, height):
    if data[h] > T:
        T = data[h]

ratio = width / T
for h in range(0, height):
    data[h] *= ratio

data = array(data)
bars_list = plt.barh(y_pos, data, align='center', alpha=0.4)
for bar in bars_list:
    bar.set_color('r')
    pass

plt.yticks(y_pos)

plt.imshow(im)
plt.show()
