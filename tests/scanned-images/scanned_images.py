import cv2
import numpy as np

img = cv2.imread('temp.jpg', 0)
_, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
kernel = np.ones((1, 1), np.uint8)
opening = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

cv2.imshow('original', img)
cv2.imshow('opening', opening)
cv2.waitKey()
