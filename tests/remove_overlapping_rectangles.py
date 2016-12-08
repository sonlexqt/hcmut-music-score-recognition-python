# Import the cv2 library
import cv2
from utils import Utils

IMAGE_1 = 'auld-lang-syne.jpg'
IMAGE_2 = 'happy-birthday.jpg'
IMAGE_3 = 'silent-night.jpg'
IMAGE_4 = 'we-wish-you-a-merry-xmas.jpg'
# Read the image you want connected components of
images_path = 'images/scores/'
music_score = IMAGE_1
origin = cv2.imread(images_path + music_score)
src = cv2.imread(images_path + music_score, cv2.CV_8UC1)
# Threshold it so it becomes binary
ret, thresh = cv2.threshold(src, 127, 255, cv2.THRESH_BINARY_INV)
# You need to choose 4 or 8 for connectivity type
connectivity = 8
# Perform the operation
output = cv2.connectedComponentsWithStats(thresh, connectivity, cv2.CV_32S)
# Get the results
# The first cell is the number of labels
num_labels = output[0]
print('num_labels:')
print(num_labels)
# The second cell is the label matrix
labels = output[1]
# The third cell is the stat matrix
stats = output[2]
# The fourth cell is the centroid matrix
centroids = output[3]

rects_init = []
rects_result = []

for i in range(0, num_labels):
    left = stats[i, cv2.CC_STAT_LEFT]
    top = stats[i, cv2.CC_STAT_TOP]
    width = stats[i, cv2.CC_STAT_WIDTH]
    height = stats[i, cv2.CC_STAT_HEIGHT]
    right = left + width
    bottom = top + height
    # p1 = (left, top)
    # p2 = (right, bottom)
    # Need to convert the OpenCV coordinate system to Descartes coordinate system
    reversed_p1 = (left, -top)
    reversed_p2 = (right, -bottom)
    rects_init.append([reversed_p1, reversed_p2])

# Need to remove the biggest rectangle
# TODO XIN this should be done in the "connectedComponentsWithStats" function above
rects_init.pop(0)
rects_result = Utils.remove_overlapping_rectangles(rects_init)

for rect in rects_result:
    left, top, right, bottom = Utils.get_rect_coordinates(rect)
    # p1 = (left, top)
    # p2 = (right, bottom)
    # Now need to convert the Descartes coordinate system back to the OpenCV coordinate system
    restored_p1 = (left, -top)
    restored_p2 = (right, -bottom)
    cv2.rectangle(origin, restored_p1, restored_p2, (0, 0, 255), 1, 8, 0)

print(rects_init)
print(len(rects_init))
print(rects_result)
print(len(rects_result))
cv2.imshow("result", origin)
cv2.waitKey(0)
