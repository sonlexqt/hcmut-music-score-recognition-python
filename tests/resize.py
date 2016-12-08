import cv2
from os import listdir
from os.path import isfile, join

DEFAULT_SIZE_WIDTH = 50
DEFAULT_SIZE_HEIGHT = 50

dir_path = '../images/symbols/'
image_files = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]

for file in image_files:
    print(file)
    img = cv2.imread(dir_path + file)
    img_resized = cv2.resize(img, (DEFAULT_SIZE_WIDTH, DEFAULT_SIZE_HEIGHT))
    cv2.imshow(file, img_resized)

cv2.waitKey(0)
