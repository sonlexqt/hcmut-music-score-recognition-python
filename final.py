import cv2
import numpy as np
import math


"""""""""""""""""""""""""""""""""""""""
CONSTANTS
"""""""""""""""""""""""""""""""""""""""
WTITLE_SOURCE_IMAGE = "Source Image"
WTITLE_ROI_IMAGE = "ROI Image"
WTITLE_ROI_IMAGE_THRESHOLDED = "ROI Image Thresholded"
WTITLE_CANDIDATE_POINTS = "Candidate Points"
WTITLE_ROTATED_IMAGE = "Rotated image"
WTITLE_IMG_WO_STAFFLINES = "Image without staff lines"
MAX_ROTATION_ANGLE = 30
MIN_ROTATION_ANGLE = - MAX_ROTATION_ANGLE
REC_LINE_WIDTH = 2
SPACE_BAR_KEY = 32
IMG_FILE = 'images/scores/auld-lang-syne.jpg'

"""""""""""""""""""""""""""""""""""""""
GLOBAL VARIABLES
"""""""""""""""""""""""""""""""""""""""
# TODO XIN change vars name later
is_dragging = False
is_roi_selected = False
is_roi_img_shown = False
roi_ref_points = []
img = None
roi_img = None
roi_img_gray = None
roi_img_thresh = None
blank_roi_img = None
rotated_img = None
# rotatedImgGray = None
# rotatedImgThresholded = None
# blankRotatedImg = None
# withoutStaffLines = None


"""""""""""""""""""""""""""""""""""""""
HELPER FUNCTIONS
"""""""""""""""""""""""""""""""""""""""


def mouse_drag_handler(event, x, y, flags, params):
    global is_dragging, is_roi_selected, roi_ref_points, img, roi_img

    if event == cv2.EVENT_LBUTTONDOWN and not is_dragging:
        roi_ref_points = [(x, y)]
        is_dragging = True

    if event == cv2.EVENT_MOUSEMOVE and is_dragging:
        img1 = img.copy()
        if len(roi_ref_points) is 1:
            roi_ref_points.append((x, y))
        else:
            roi_ref_points[1] = (x, y)
        point1 = roi_ref_points[0]
        point2 = roi_ref_points[1]
        cv2.rectangle(img1, point1, point2, (0, 0, 255), REC_LINE_WIDTH, 8, 0)
        cv2.imshow(WTITLE_SOURCE_IMAGE, img1)

    if event == cv2.EVENT_LBUTTONUP and is_dragging:
        if len(roi_ref_points) is 1:
            roi_ref_points.append((x, y))
        else:
            roi_ref_points[1] = (x, y)
        is_dragging = False
        roi_img = img[roi_ref_points[0][1]:roi_ref_points[1][1], roi_ref_points[0][0]:roi_ref_points[1][0]]

    if event == cv2.EVENT_LBUTTONUP:
        is_dragging = False
        is_roi_selected = True


def is_this_pixel_removed(i, j, value, image):
    height, width = image.shape[:2]
    max_cols = width
    if value > 0:
        if i == 0 or i == 1:
            return True
        if image[i - 1, j] > 0:
            if image[i - 2, j] > 0:
                return False
            if j >= 1 and image[i - 2, j - 1] > 0:
                return False
            if j < max_cols and image[i - 2, j + 1] > 0:
                return False
    return True


def calculate_entropy(PthetasAvg, length):
    res = 0
    for i in range(0, length):
        if PthetasAvg[i] != 0:
            res += PthetasAvg[i] * math.log(PthetasAvg[i])
    return -res

"""""""""""""""""""""""""""""""""""""""
STEPS
"""""""""""""""""""""""""""""""""""""""


def read_src_image():
    # Step 1
    global img
    img = cv2.imread(IMG_FILE, 1)
    if img is not None:
        cv2.imshow(WTITLE_SOURCE_IMAGE, img)
    else:
        raise FileNotFoundError('Input image is not found')


def roi_selection():
    # Step 2
    global roi_img, is_roi_img_shown
    cv2.setMouseCallback(WTITLE_SOURCE_IMAGE, mouse_drag_handler)
    while 1:
        if is_roi_selected:
            cv2.imshow(WTITLE_ROI_IMAGE, roi_img)
            is_roi_img_shown = True
        key = cv2.waitKey(0)
        if key == SPACE_BAR_KEY and is_roi_img_shown:
            break


def candidate_points_extraction():
    # Step 3
    global roi_img, roi_img_gray, roi_img_thresh, blank_roi_img
    roi_img_gray = cv2.cvtColor(roi_img, cv2.COLOR_BGR2GRAY)
    _, roi_img_thresh = cv2.threshold(roi_img_gray, 127, 255, cv2.THRESH_BINARY_INV)
    height, width = roi_img_thresh.shape[:2]
    blank_roi_img = np.zeros((height, width, 1), np.uint8)
    for i in range(0, height):
        for j in range(0, width):
            pixel_gray_scale_value = roi_img_thresh[i, j]
            if is_this_pixel_removed(i, j, pixel_gray_scale_value, roi_img_thresh):
                blank_roi_img[i, j] = pixel_gray_scale_value
    _, blank_roi_img = cv2.threshold(blank_roi_img, 127, 255, cv2.THRESH_BINARY)
    cv2.imshow(WTITLE_CANDIDATE_POINTS, blank_roi_img)
    cv2.waitKey(0)


def rotation_angle_estimation():
    global img, blank_roi_img, rotated_img
    height, width = blank_roi_img.shape[:2]
    entropy_ps_length = MAX_ROTATION_ANGLE - MIN_ROTATION_ANGLE + 1
    entropy_ps = [0] * entropy_ps_length
    for a in range(0, entropy_ps_length):
        # TODO XIN change variable name
        pthetas = [0] * height
        pthetas_avg = [0] * height
        sum_pthetas = 0
        angle = a - MAX_ROTATION_ANGLE
        center = (width / 2, height / 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated_roi_img = cv2.warpAffine(blank_roi_img, rotation_matrix, (height, width))
        # The next calculation will use rotated_roi_img instead
        for h in range(0, height):
            sum_of_rows = 0
            for w in range(0, width):
                try:
                    sum_of_rows += rotated_roi_img[h, w]
                except IndexError:
                    break  # Break out when list index out of range
            pthetas[h] = sum_of_rows
            sum_pthetas += pthetas[h]
        for h in range(0, height):
            pthetas_avg[h] = pthetas[h] / sum_pthetas
        entropy_ps[a] = calculate_entropy(pthetas_avg, height)
    min_a = 0
    min_entropy = entropy_ps[min_a]
    min_angle = min_a - MAX_ROTATION_ANGLE
    for a in range(0, entropy_ps_length):
        if entropy_ps[a] < min_entropy:
            min_a = a
            min_entropy = entropy_ps[a]
            min_angle = min_a - MAX_ROTATION_ANGLE
    print('Estimated rotation angle (deg):', min_angle)
    height, width = img.shape[:2]
    center = (height / 2, width / 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, min_angle, 1.0)
    # Maintain white background when using OpenCV warpAffine
    # (src, M, dsize, dst=None, flags=None, borderMode=None, borderValue=None)
    # TODO XIN fix rotated_img offset problem
    rotated_img = cv2.warpAffine(img, rotation_matrix, (width, height), cv2.INTER_AREA, cv2.BORDER_DEFAULT, cv2.BORDER_REPLICATE)
    cv2.imshow(WTITLE_ROTATED_IMAGE, rotated_img)
    cv2.waitKey(0)
    return 0

"""""""""""""""""""""""""""""""""""""""
MAIN
"""""""""""""""""""""""""""""""""""""""


def main():
    read_src_image()
    roi_selection()
    candidate_points_extraction()
    rotation_angle_estimation()

if __name__ == '__main__':
    main()
