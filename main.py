import cv2
import numpy as np
import math
from utils import Utils
from symbols import Symbols

"""""""""""""""""""""""""""""""""""""""
FOR TESTING
"""""""""""""""""""""""""""""""""""""""
IMG_PATH = 'images/scores/'
IMG_1 = 'auld-lang-syne'
IMG_2 = 'auld-lang-syne-2'
IMG_3 = 'happy-birthday'
IMG_4 = 'silent-night'
IMG_5 = 'we-wish-you-a-merry-xmas'
IMG_6 = 'jingle-bells'
IMG_EXTENSION = '.jpg'
IMG_TEST = IMG_4
IMG_FILE = IMG_PATH + IMG_TEST + IMG_EXTENSION

"""""""""""""""""""""""""""""""""""""""
CONSTANTS
"""""""""""""""""""""""""""""""""""""""
WTITLE_IMG_SOURCE = "Source Image"
WTITLE_IMG_ROI = "ROI Image"
WTITLE_CANDIDATE_POINTS = "Candidate Points"
WTITLE_IMG_ROTATED = "Rotated image"
WTITLE_IMG_ROTATED_THRESH = "Rotated image thresh"
WTITLE_IMG_WITHOUT_STAFFLINES = "Image without staff lines"
WTITLE_CONNECTED_COMPONENTS = "Connected components"
WTITLE_RECOGNIZED_SYMBOLS = "Recognized symbols"
MAX_ROTATION_ANGLE = 30
MIN_ROTATION_ANGLE = - MAX_ROTATION_ANGLE
REC_LINE_WIDTH = 2
SPACE_BAR_KEY = 32
HISTOGRAM_BINARY_RATIO = 2
BAR_WIDTH_RATIO = 7
DOT_HEIGHT_RATIO = 5
TREBLE_CLEF_HEIGHT_RATIO = 1.5
BAR_HEIGHT_REL_TOL = 0.1
DEFAULT_SYMBOL_SIZE_WIDTH = 50
DEFAULT_SYMBOL_SIZE_HEIGHT = 50

"""""""""""""""""""""""""""""""""""""""
GLOBAL VARIABLES
"""""""""""""""""""""""""""""""""""""""
is_dragging = False
is_roi_selected = False
is_roi_img_shown = False
roi_ref_points = []  # Contains the two ref points of the ROI
staff_lines = []  # The rects containing the staff lines
staff_line_width = 0
staff_line_space = 0
staff_height = 0
# The matrices
img = None
img_roi = None
img_candidate_points = None
img_rotated = None
img_without_staff_lines = None
# The rectangles containing the symbols
rects_merged = []
rects_recognized = []

"""""""""""""""""""""""""""""""""""""""
HELPER FUNCTIONS
"""""""""""""""""""""""""""""""""""""""


def mouse_drag_handler(event, x, y, flags, params):
    global is_dragging, is_roi_selected, roi_ref_points, img, img_roi

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
        cv2.imshow(WTITLE_IMG_SOURCE, img1)

    if event == cv2.EVENT_LBUTTONUP and is_dragging:
        if len(roi_ref_points) is 1:
            roi_ref_points.append((x, y))
        else:
            roi_ref_points[1] = (x, y)
        is_dragging = False
        img_roi = img[roi_ref_points[0][1]:roi_ref_points[1][1], roi_ref_points[0][0]:roi_ref_points[1][0]]

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


def calculate_entropy(pthetas_avg, length):
    res = 0
    for i in range(0, length):
        if pthetas_avg[i] != 0:
            res += pthetas_avg[i] * math.log(pthetas_avg[i])
    return -res


def get_staff_info(data):
    global staff_lines, staff_line_space, staff_height
    staff_lines = []  # Contains elements with format (index, width)
    current_staff_index = -1

    for i, value in enumerate(data):
        if value == 255 and i > 0:
            if data[i - 1] == 0:
                current_staff_index += 1
                staff_lines.append((i, 1))
            else:
                current = staff_lines[current_staff_index]
                index = current[0]
                width = current[1]
                staff_lines[current_staff_index] = (index, width + 1)

    sum_staff_lines_space = 0
    sum_staff_height = 0
    for i, this_staff_line in enumerate(staff_lines):
        if i % 5 == 0:  # The staff_lines list index stats from 0
            continue
        else:
            last_staff_line = staff_lines[i - 1]
            this_staff_line_space = this_staff_line[0] - last_staff_line[0]
            sum_staff_lines_space += this_staff_line_space
            if (i + 1) % 5 == 0:
                # If this is the last line of a staff group
                first_staff_line = staff_lines[i + 1 - 5]
                this_staff_height = this_staff_line[0] - first_staff_line[0]
                sum_staff_height += this_staff_height

    staff_groups = len(staff_lines) / 5
    num_staff_lines_space = len(staff_lines) - staff_groups
    avg_staff_line_space = sum_staff_lines_space / num_staff_lines_space
    staff_line_space = avg_staff_line_space
    avg_staff_height = sum_staff_height / staff_groups
    staff_height = avg_staff_height
    return 0

"""""""""""""""""""""""""""""""""""""""
STEPS
"""""""""""""""""""""""""""""""""""""""


def read_src_image():
    # Step 1
    global img
    img = cv2.imread(IMG_FILE, 1)
    if img is not None:
        cv2.imshow(WTITLE_IMG_SOURCE, img)
    else:
        raise FileNotFoundError('Input image is not found')


def roi_selection():
    # Step 2
    global img_roi, is_roi_img_shown
    cv2.setMouseCallback(WTITLE_IMG_SOURCE, mouse_drag_handler)
    while 1:
        if is_roi_selected:
            cv2.imshow(WTITLE_IMG_ROI, img_roi)
            is_roi_img_shown = True
        key = cv2.waitKey(0)
        if key == SPACE_BAR_KEY and is_roi_img_shown:
            break


def candidate_points_extraction():
    # Step 3
    global img_roi, img_candidate_points
    roi_img_gray = cv2.cvtColor(img_roi, cv2.COLOR_BGR2GRAY)
    _, roi_img_thresh = cv2.threshold(roi_img_gray, 127, 255, cv2.THRESH_BINARY_INV)
    height, width = roi_img_thresh.shape[:2]
    img_candidate_points = np.zeros((height, width), np.uint8)
    for i in range(0, height):
        for j in range(0, width):
            pixel_gray_scale_value = roi_img_thresh[i, j]
            if is_this_pixel_removed(i, j, pixel_gray_scale_value, roi_img_thresh):
                img_candidate_points[i, j] = pixel_gray_scale_value
    _, img_candidate_points = cv2.threshold(img_candidate_points, 127, 255, cv2.THRESH_BINARY)
    cv2.imshow(WTITLE_CANDIDATE_POINTS, img_candidate_points)
    cv2.waitKey(0)


def rotation_angle_estimation():
    # Step 4
    global img, img_candidate_points, img_rotated
    height, width = img_candidate_points.shape[:2]
    entropy_ps_length = MAX_ROTATION_ANGLE - MIN_ROTATION_ANGLE + 1
    entropy_ps = [0] * entropy_ps_length
    for a in range(0, entropy_ps_length):
        pthetas = [0] * height
        pthetas_avg = [0] * height
        sum_pthetas = 0
        angle = a - MAX_ROTATION_ANGLE
        center = (width / 2, height / 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated_roi_img = cv2.warpAffine(img_candidate_points, rotation_matrix, (height, width))
        # The next calculation will use rotated_roi_img instead
        for h in range(0, height):
            sum_of_rows = 0
            for w in range(0, width):
                # TODO XIN weird error: index out of bounds (have to try-catch)
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
    img_height, img_width = img.shape[:2]
    img_center = (img_height / 2, img_width / 2)
    rotation_matrix = cv2.getRotationMatrix2D(img_center, min_angle, 1.0)
    # Maintain white background when using OpenCV warpAffine
    # (src, M, dsize, dst=None, flags=None, borderMode=None, borderValue=None)
    img_rotated = cv2.warpAffine(img, rotation_matrix, (img_width, img_height),
                                 cv2.INTER_AREA, cv2.BORDER_DEFAULT, cv2.BORDER_REPLICATE)
    cv2.imshow(WTITLE_IMG_ROTATED, img_rotated)
    cv2.waitKey(0)


def adaptive_removal():
    # Step 5
    global img_rotated, img_without_staff_lines, staff_line_width
    height, width = img_rotated.shape[:2]
    pthetas = [0] * height
    img_rotated_gray = cv2.cvtColor(img_rotated, cv2.COLOR_BGR2GRAY)
    _, img_rotated_thresh = cv2.threshold(img_rotated_gray, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    cv2.imshow(WTITLE_IMG_ROTATED_THRESH, img_rotated_thresh)
    # Calculate horizontal projection
    for h in range(0, height):
        sum_of_rows = 0
        for w in range(0, width):
            sum_of_rows += img_rotated_thresh[h, w]
        pthetas[h] = sum_of_rows
    # Get the maximum of the projection(T)
    T = pthetas[0]
    for h in range(0, height):
        if pthetas[h] > T:
            T = pthetas[h]
    # Then the projection is binarized using a threshold of half of the maximum
    for h in range(0, height):
        if pthetas[h] > (T / HISTOGRAM_BINARY_RATIO):
            pthetas[h] = 255
        else:
            pthetas[h] = 0
    # Get staff_lines & staff_line_space info
    get_staff_info(pthetas)
    # Estimate the staff line width
    number_of_rows = 0
    number_of_lines = 0
    for h in range(0, height):
        if pthetas[h] == 255:
            number_of_rows += 1
            if h >= 1 and pthetas[h - 1] != 255:
                # Count this case as a new line
                number_of_lines += 1
    W = number_of_rows / number_of_lines
    staff_line_width = W
    # Z is the number of times we need to run the staff line removal method
    Z = math.ceil(W / 2)
    img_without_staff_lines = img_rotated_thresh.copy()
    wsl_height, wsl_width = img_without_staff_lines.shape[:2]
    blank_rotated_img = np.zeros((wsl_height, wsl_width), np.uint8)
    for z in range(0, Z):
        for i in range(0, wsl_height):
            for j in range(0, wsl_width):
                pixel_gray_scale_value = img_without_staff_lines[i, j]
                if is_this_pixel_removed(i, j, pixel_gray_scale_value, img_without_staff_lines):
                    # Yes: copy this pixel to blank_rotated_img
                    blank_rotated_img[i, j] = pixel_gray_scale_value
        img_without_staff_lines = img_without_staff_lines - blank_rotated_img
    # Perform dilation to restore the missing details
    dilate_structuring_element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    img_without_staff_lines = cv2.dilate(img_without_staff_lines, dilate_structuring_element)
    _, img_without_staff_lines = cv2.threshold(img_without_staff_lines, 127, 255, cv2.THRESH_BINARY_INV)
    cv2.imshow(WTITLE_IMG_WITHOUT_STAFFLINES, img_without_staff_lines)
    cv2.waitKey(0)
    return 0


def get_connected_components():
    # Step 6
    global img_without_staff_lines, staff_line_width, staff_height, rects_merged
    img_without_staff_lines_rgb = cv2.cvtColor(img_without_staff_lines, cv2.COLOR_GRAY2RGB)
    _, thresh = cv2.threshold(img_without_staff_lines, 127, 255, cv2.THRESH_BINARY_INV)
    connectivity = 8
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh, connectivity, cv2.CV_32S)
    rects_init = []

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

    # Need to remove the biggest rectangle (this won't happen in C++)
    rects_init.pop(0)
    rects_merged = Utils.remove_overlapping_rectangles(rects_init)

    for i, rect in enumerate(rects_merged):
        left, top, right, bottom = Utils.get_rect_coordinates(rect)
        # p1 = (left, top)
        # p2 = (right, bottom)
        # Now need to convert the Descartes coordinate system back to the OpenCV coordinate system
        restored_p1 = (left, -top)
        restored_p2 = (right, -bottom)
        # Draw a red rectangle for each symbol
        cv2.rectangle(img_without_staff_lines_rgb, restored_p1, restored_p2, (0, 0, 255), 1, 8, 0)

    print('rects_merged')
    print(rects_merged)
    print(len(rects_merged))

    cv2.imshow(WTITLE_CONNECTED_COMPONENTS, img_without_staff_lines_rgb)
    cv2.waitKey(0)
    return 0


def recognize_symbols():
    global rects_merged, rects_recognized, img_without_staff_lines
    img_without_staff_lines_rgb = cv2.cvtColor(img_without_staff_lines, cv2.COLOR_GRAY2RGB)
    treble_clefs = []
    # Initialize the kNN system
    Utils.init_knn()

    for i, rect in enumerate(rects_merged):
        left, top, right, bottom = Utils.get_rect_coordinates(rect)
        # p1 = (left, top)
        # p2 = (right, bottom)
        # Now need to convert the Descartes coordinate system back to the OpenCV coordinate system
        restored_p1 = (left, -top)
        restored_p2 = (right, -bottom)
        rect_width = abs(right - left)
        rect_height = abs(top - bottom)
        y = restored_p1[1]
        x = restored_p1[0]
        sub_image = img_without_staff_lines[y:y + rect_height, x:x + rect_width]
        _, sub_image = cv2.threshold(sub_image, 127, 255, cv2.THRESH_BINARY_INV)
        sub_image_resized = cv2.resize(sub_image, (DEFAULT_SYMBOL_SIZE_WIDTH, DEFAULT_SYMBOL_SIZE_HEIGHT))
        estimated_treble_clef_height = staff_height * TREBLE_CLEF_HEIGHT_RATIO
        if rect_height >= estimated_treble_clef_height:
            # This one has a big chance of being a treble clef
            # Check if it's really a treble clef
            if Utils.recognize_symbol(sub_image_resized) == Symbols.get(14):  # 14 is index of TREBLE_CLEF
                treble_clefs.append(rect)

    # Sort the treble clefs by their position
    treble_clefs = Utils.sort_treble_clefts(treble_clefs)
    # Remove all the other rectangles outside of the treble clefs
    rects_symbols = Utils.remove_other_rectangles(rects_merged, treble_clefs)
    print('rects_symbols')
    print(rects_symbols)
    print(len(rects_symbols))
    # This is the array containing the recognition result
    rects_recognized = [0] * len(rects_symbols)

    for i, rect in enumerate(rects_symbols):
        left, top, right, bottom = Utils.get_rect_coordinates(rect)
        # p1 = (left, top)
        # p2 = (right, bottom)
        # Now need to convert the Descartes coordinate system back to the OpenCV coordinate system
        restored_p1 = (left, -top)
        restored_p2 = (right, -bottom)
        rect_width = abs(right - left)
        rect_height = abs(top - bottom)
        y = restored_p1[1]
        x = restored_p1[0]
        estimated_bar_width = staff_line_width * BAR_WIDTH_RATIO
        if rect_width <= estimated_bar_width:
            # Check if this is a bar
            if math.isclose(staff_height, rect_height, rel_tol=BAR_HEIGHT_REL_TOL):
                rects_recognized[i] = Symbols.get(5)
            else:
                # Check if this is a dot
                estimated_dot_height = staff_line_width * DOT_HEIGHT_RATIO
                if rect_height <= estimated_dot_height:
                    rects_recognized[i] = Symbols.get(0)
                else:
                    rects_recognized[i] = Symbols.get(-1)
        else:
            # Else
            sub_image = img_without_staff_lines[y:y + rect_height, x:x + rect_width]
            _, sub_image = cv2.threshold(sub_image, 127, 255, cv2.THRESH_BINARY_INV)
            sub_image_resized = cv2.resize(sub_image, (DEFAULT_SYMBOL_SIZE_WIDTH, DEFAULT_SYMBOL_SIZE_HEIGHT))
            rects_recognized[i] = Utils.recognize_symbol(sub_image_resized)
        # Draw a red rectangle for each symbol
        cv2.rectangle(img_without_staff_lines_rgb, restored_p1, restored_p2, (0, 0, 255), 1, 8, 0)
        cv2.putText(img_without_staff_lines_rgb, rects_recognized[i], (int(x + rect_width / 4), y + rect_height + 10),
                    cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 0, 255))

    cv2.imshow(WTITLE_RECOGNIZED_SYMBOLS, img_without_staff_lines_rgb)
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
    adaptive_removal()
    get_connected_components()
    recognize_symbols()

if __name__ == '__main__':
    main()
