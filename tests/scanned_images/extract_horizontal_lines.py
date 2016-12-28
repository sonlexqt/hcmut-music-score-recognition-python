import cv2
import numpy as np

kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 1))
print(kernel)
