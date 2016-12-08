import cv2

"""
Constants
"""
WTITLE_SOURCE_IMAGE = "Source Image"
WTITLE_ROI_IMAGE = "ROI Image"
WTITLE_ROI_IMAGE_THRESHOLDED = "ROI Image Thresholded"
WTITLE_CANDIDATE_POINTS = "Candidate Points"
WTITLE_ROTATED_IMAGE = "Rotated image"
WTITLE_IMG_WO_STAFFLINES = "Image without staff lines"
MAX_ROTATION_ANGLE = 30
MIN_ROTATION_ANGLE = - MAX_ROTATION_ANGLE
REC_LINE_WIDTH = 2

"""
Global variables
"""
# TODO XIN change vars name later
is_dragging = False
is_roi_selected = False
roi_ref_points = []
img = None
roi_img = None
# roiImgGray = None
# roiImgThresholded = None
# blankRoiImg = None
# rotatedImg = None
# rotatedImgGray = None
# rotatedImgThresholded = None
# blankRotatedImg = None
# withoutStaffLines = None

IMG_FILE = 'images/scores/auld-lang-syne.jpg'


def read_src_image():
    global img
    img = cv2.imread(IMG_FILE, 1)
    if img is not None:
        cv2.imshow(WTITLE_SOURCE_IMAGE, img)
    else:
        raise FileNotFoundError('Input image is not found')


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


def roi_selection():
    global roi_img
    cv2.setMouseCallback(WTITLE_SOURCE_IMAGE, mouse_drag_handler)
    while True:
        if is_roi_selected:
            print('show roi img now')
            cv2.imshow(WTITLE_ROI_IMAGE, roi_img)
        key = cv2.waitKey(0)
        if key == 27:
            break


def main():
    read_src_image()
    roi_selection()

if __name__ == '__main__':
    main()
