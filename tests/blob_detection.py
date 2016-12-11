# Standard imports
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


# Read image
img = cv2.imread('../images/symbols/rect-99.jpg')
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# edges = auto_canny(img)
_, edges = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY_INV)

cv2.imshow('edges', edges)

lines = cv2.HoughLines(edges, 1, np.pi/180, 40)

print('lines:')
print(lines)

if lines.any():
    for line in lines:
        rho, theta = line[0]
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*a)
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*a)
        cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

cv2.imshow('RESULT', img)
cv2.waitKey(0)
