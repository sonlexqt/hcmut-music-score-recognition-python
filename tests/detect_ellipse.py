import cv2
import numpy as np


def auto_canny(image, sigma=0.33):
    # compute the median of the single channel pixel intensities
    v = np.median(image)

    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)

    # return the edged image
    return edged


src = cv2.imread('img_without_staff_lines.jpg')
gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (3, 3), 0)

auto = auto_canny(blurred)

# show the images
cv2.imshow("Edges", auto)

im2, contours, hierarchy = cv2.findContours(auto.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
# cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:10]
# screenCnt = None
cv2.drawContours(src, contours, -1, (0, 255, 0), 1)
cv2.imshow("Contours", src)

cv2.waitKey(0)
