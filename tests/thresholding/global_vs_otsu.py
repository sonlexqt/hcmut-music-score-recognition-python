import cv2
IMG_FILE = '../../images/scores/scan/jingle-bells.jpg'
img = cv2.imread(IMG_FILE)
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# global thresholding
ret1, th1 = cv2.threshold(img_gray, 200, 255, cv2.THRESH_BINARY)
# Otsu's thresholding
ret2, th2 = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
# Otsu's thresholding after Gaussian filtering
blur = cv2.GaussianBlur(img_gray, (3, 3), 0)
ret3, th3 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

cv2.imshow('global', th1)
cv2.imshow('otsu', th2)
cv2.imshow('otsu_after_gaussian_filter', th3)
cv2.waitKey()
