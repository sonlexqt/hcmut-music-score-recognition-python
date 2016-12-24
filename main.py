# Import libraries
import cv2
import numpy as np
import math
from xml.etree.ElementTree import Element, SubElement, tostring, fromstring
from xml.dom import minidom
# Import modules
from utils import Utils
from symbol import Symbol
from measure import Measure
from staff import Staff
from score import Score

"""""""""""""""""""""""""""""""""""""""
FOR TESTING
"""""""""""""""""""""""""""""""""""""""
IMG_PATH = 'images/scores/'
IMG_1 = '1-jingle-bells.jpg'
IMG_2 = '2-silent-night.jpg'
IMG_3 = '3-happy-birthday.jpg'
IMG_4 = '4-we-wish-you-a-merry-christmas.jpg'
IMG_5 = '5-auld-lang-syne.jpg'
IMG_6 = 'new.png'
IMG_7 = 'new.jpg'
IMG_TEST = IMG_1
IMG_FILE = IMG_PATH + IMG_TEST

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
score = None

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


def estimate_staff_info(img_rotated):
    global staff_lines, staff_line_width, staff_line_space, staff_height
    # Threshold the img_rotated before estimating
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

    # Estimate the staff_line_width
    number_of_rows = 0
    number_of_lines = 0
    for h in range(0, height):
        if pthetas[h] == 255:
            number_of_rows += 1
            if h >= 1 and pthetas[h - 1] != 255:
                # Count this case as a new line
                number_of_lines += 1
    staff_line_width = number_of_rows / number_of_lines

    # Estimate staff_lines, staff_line_space & staff_height
    staff_lines = []  # Contains elements with format (index, width)
    current_staff_index = -1

    # staff_lines
    for i, value in enumerate(pthetas):
        if value == 255 and i > 0:
            if pthetas[i - 1] == 0:
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
            this_staff_line_space = this_staff_line[0] - last_staff_line[0] - staff_line_width
            sum_staff_lines_space += this_staff_line_space
            if (i + 1) % 5 == 0:
                # If this is the last line of a staff group
                first_staff_line = staff_lines[i + 1 - 5]
                this_staff_height = this_staff_line[0] - first_staff_line[0] + staff_line_width
                sum_staff_height += this_staff_height

    staff_groups = len(staff_lines) / 5
    num_staff_lines_space = len(staff_lines) - staff_groups
    avg_staff_line_space = sum_staff_lines_space / num_staff_lines_space
    # staff_line_space
    staff_line_space = avg_staff_line_space
    avg_staff_height = sum_staff_height / staff_groups
    # staff_height
    staff_height = avg_staff_height

    print('=== Estimated staff lines data:')
    print('staff_lines:')
    print(staff_lines)
    print('staff_line_width:', staff_line_width)
    print('staff_line_space:', staff_line_space)
    print('staff_height:', staff_height)
    return 0


def prettify(elem):
    # Return a pretty-printed XML string for the Element.
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

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
    print('=== Estimated rotation angle (deg):', min_angle)
    img_height, img_width = img.shape[:2]
    img_center = (img_height / 2, img_width / 2)
    rotation_matrix = cv2.getRotationMatrix2D(img_center, min_angle, 1.0)
    # Maintain white background when using OpenCV warpAffine
    # cv2.warpAffine(src, M, dsize, dst=None, flags=None, borderMode=None, borderValue=None)
    img_rotated = cv2.warpAffine(img, rotation_matrix, (img_width, img_height),
                                 cv2.INTER_AREA, cv2.BORDER_DEFAULT, cv2.BORDER_REPLICATE)
    cv2.imshow(WTITLE_IMG_ROTATED, img_rotated)
    cv2.waitKey(0)


def adaptive_removal():
    # Step 5
    global img_rotated, img_without_staff_lines, staff_line_width, staff_lines
    img_rotated_gray = cv2.cvtColor(img_rotated, cv2.COLOR_BGR2GRAY)
    _, img_rotated_thresh = cv2.threshold(img_rotated_gray, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # Get the staff lines info
    estimate_staff_info(img_rotated)

    img_without_staff_lines = img_rotated_thresh.copy()
    wsl_height, wsl_width = img_without_staff_lines.shape[:2]
    blank_rotated_img = np.zeros((wsl_height, wsl_width), np.uint8)

    # Z is the number of times we need to run the staff line removal method
    Z = math.ceil(staff_line_width / 2)
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

    # Now redraw the removed staff lines
    img_without_staff_lines_rgb = cv2.cvtColor(img_without_staff_lines, cv2.COLOR_GRAY2RGB)
    img_without_staff_lines_overlay = img_without_staff_lines_rgb.copy()
    for staff_line in staff_lines:
        rect_x = staff_line[0]
        rect_width = staff_line[1]
        p1 = (0, rect_x)
        p2 = (wsl_width, rect_x + rect_width)
        # Draw a red rectangle for each staff_line
        cv2.rectangle(img_without_staff_lines_overlay, p1, p2, (0, 0, 255), cv2.FILLED, 8, 0)
    # Apply the overlay
    alpha = 0.3
    cv2.addWeighted(img_without_staff_lines_overlay, alpha, img_without_staff_lines_rgb,
                    1 - alpha, 0, img_without_staff_lines_rgb)
    cv2.imshow(WTITLE_IMG_WITHOUT_STAFFLINES, img_without_staff_lines_rgb)
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

    cv2.imshow(WTITLE_CONNECTED_COMPONENTS, img_without_staff_lines_rgb)
    cv2.waitKey(0)
    return 0


def recognize_symbols():
    global rects_merged, img_without_staff_lines, staff_lines, staff_height, staff_line_space, staff_line_width, score
    img_without_staff_lines_rgb = cv2.cvtColor(img_without_staff_lines, cv2.COLOR_GRAY2RGB)
    treble_clefs = []
    # Initialize the kNN system
    Utils.init_knn()

    # First: detect the treble clefs in order to group the symbols
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
            recognized_sbl = Utils.recognize_symbol(sub_image_resized)
            # This case is for making sure it's a treble clef !
            # if recognized_sbl.name == Symbols.get(14).name:  # 14 is index of TREBLE_CLEF
            #     treble_clefs.append(rect)
            treble_clefs.append(rect)

    # Sort the treble clefs by their position
    treble_clefs = Utils.sort_treble_clefts(treble_clefs)
    print('=== There are', len(treble_clefs), 'treble_clefs:')
    print(treble_clefs)
    # Remove all the other rectangles outside of the treble clefs
    rects_symbols = Utils.remove_other_rectangles(rects_merged, treble_clefs)
    # Sort the symbols into groups
    rects_sorted = Utils.sort_rectangles(rects_symbols, treble_clefs, staff_lines, staff_height)

    # Start recognizing symbols
    # Initialize score
    score = Score()
    for group_index, group in enumerate(rects_sorted):
        # Initialize staff
        current_staff = Staff()
        current_measure = None
        for i, rect in enumerate(group):
            if i == 0:
                current_measure = Measure()

            left, top, right, bottom = Utils.get_rect_coordinates(rect)
            # Now need to convert the Descartes coordinate system back to the OpenCV coordinate system
            restored_p1 = (left, -top)
            restored_p2 = (right, -bottom)
            rect_width = abs(right - left)
            rect_height = abs(top - bottom)
            x = restored_p1[0]
            y = restored_p1[1]
            # cv2.rectangle(img_without_staff_lines_rgb, restored_p1, restored_p2, (0, 0, 255), 1, 8, 0)
            # cv2.putText(img_without_staff_lines_rgb, str(i), (int(x + rect_width / 4), y + rect_height + 10),
            #             cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 0, 255))
            estimated_bar_width = staff_line_width * BAR_WIDTH_RATIO
            this_symbol = None
            if rect_width <= estimated_bar_width:
                # Check if this is a bar
                if math.isclose(staff_height, rect_height, rel_tol=BAR_HEIGHT_REL_TOL):
                    this_symbol = Utils.get_symbol_by_index(5)  # 5 is index of 'bar'
                else:
                    # Check if this is a dot
                    estimated_dot_height = staff_line_width * DOT_HEIGHT_RATIO
                    if rect_height <= estimated_dot_height:
                        this_symbol = Utils.get_symbol_by_index(0)  # 0 is index of 'dot'
                    else:
                        this_symbol = Utils.get_symbol_by_index(-1)  # -1 means can't recognize this symbol
            else:
                # Else
                sub_image = img_without_staff_lines[y:y + rect_height, x:x + rect_width]
                _, sub_image = cv2.threshold(sub_image, 127, 255, cv2.THRESH_BINARY_INV)
                sub_image_resized = cv2.resize(sub_image, (DEFAULT_SYMBOL_SIZE_WIDTH, DEFAULT_SYMBOL_SIZE_HEIGHT))
                this_symbol = Utils.recognize_symbol(sub_image_resized)
                if this_symbol.class_name == 'key_signature':
                    # Set this staff's key signature (optional)
                    current_staff.set_key_signature(this_symbol)
                if this_symbol.class_name == 'time_signature':
                    # Set this staff's time signature (required)
                    current_staff.set_time_signature(this_symbol)
                if this_symbol.class_name == 'note':
                    # This is a note
                    # Draw a blue rectangle for each note
                    cv2.rectangle(img_without_staff_lines_rgb, restored_p1, restored_p2, (255, 0, 0), 2, 8, 0)
                    this_symbol.calculate_pitch(rect, group_index, i, staff_lines, staff_line_space, staff_line_width)
                    # print('* symbol', i, 'staff', group_index, ':', this_symbol.get_pitch())

            # Add this symbol to current_measure
            current_measure.add_symbols(this_symbol)
            # Draw a red rectangle for each symbol
            cv2.rectangle(img_without_staff_lines_rgb, restored_p1, restored_p2, (0, 0, 255), 1, 8, 0)
            if this_symbol:
                cv2.putText(img_without_staff_lines_rgb, this_symbol.name,
                            (int(x - rect_width / 2), y + rect_height + 10),
                            cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 0, 255))
                if this_symbol.class_name is 'bar':
                    # Add current_measure to current_staff
                    current_staff.add_measure(current_measure)
                    # Then, create a new measure
                    current_measure = Measure()
            else:
                print('symbol', i, 'at group_index', group_index, 'not found')
        # Add current_staff to the score
        score.add_staff(current_staff)

    cv2.imshow(WTITLE_RECOGNIZED_SYMBOLS, img_without_staff_lines_rgb)
    cv2.waitKey(0)
    return 0


def save_as_structured_data():
    global score
    elem_score_partwise = Element('score-partwise')
    elem_part_list = SubElement(elem_score_partwise, 'part-list')
    elem_score_part = SubElement(elem_part_list, 'score-part')
    elem_score_part.attrib['id'] = 'P1'
    elem_part_name = SubElement(elem_score_part, 'part-name')
    elem_part_name.text = 'P1'
    elem_part = SubElement(elem_score_partwise, 'part')
    elem_part.attrib['id'] = 'P1'
    staffs = score.staffs

    measures_count = 0
    default_divisions = 2
    for staff_idx, staff in enumerate(staffs):
        measures = staff.measures
        for measure_idx, measure in enumerate(measures):
            measures_count += 1
            elem_measure = SubElement(elem_part, 'measure')
            elem_measure.attrib['number'] = str(measures_count)
            elem_attributes = None
            if measures_count == 1:
                # Add 'attributes' element
                elem_attributes = SubElement(elem_measure, 'attributes')
                elem_divisions = SubElement(elem_attributes, 'divisions')
                elem_divisions.text = str(default_divisions)

            # Rearrange clef, key, time
            if measures_count == 1:
                symbols = measure.symbols
                clef_index = None
                time_index = None
                for symbol_idx, symbol in enumerate(symbols):
                    if symbol.class_name == 'clef':
                        clef_index = symbol_idx
                    if symbol.class_name == 'time_signature':
                        time_index = symbol_idx
                # Rearrange the elements
                if clef_index < time_index:
                    symbols[clef_index], symbols[time_index] = symbols[time_index], symbols[clef_index]
                    pass

            # Measure 1st loop: Re-arrange stuffs
            symbols = measure.symbols
            for symbol_idx, symbol in enumerate(symbols):
                # Check for the dots
                if symbol.class_name == 'dot' and symbol_idx > 0:
                    previous_sbl = symbols[symbol_idx - 1]
                    if previous_sbl.class_name == 'note' and previous_sbl.number_of_notes == 1:
                        previous_sbl.has_dot = True

            # Measure 2nd loop: Get the xml elements
            symbols = measure.symbols
            for symbol_idx, symbol in enumerate(symbols):
                elem_symbol = symbol.get_xml_elem(default_divisions)
                if symbol.class_name in ('clef', 'time_signature', 'key_signature') and measures_count == 1:
                    # Only add children to 'attributes' element
                    # If these children are from the 1st measure in the 1st staff
                    elem_attributes.extend(elem_symbol)
                else:
                    if symbol.class_name in ('clef', 'bar', 'dot'):
                        # Don't append these to elem_measure
                        pass
                    else:
                        # Append this symbol to elem_measure
                        # Use extend here instead of append because there are cases
                        # that elem_symbol contains more than 1 elem
                        elem_measure.extend(elem_symbol)

    print(prettify(elem_score_partwise))
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
    save_as_structured_data()

if __name__ == '__main__':
    main()
