import numpy as np
import cv2
import math


def calculate_entropy(pthetas_avg, length):
    res = 0
    for i in range(0, length):
        if pthetas_avg[i] != 0:
            res += pthetas_avg[i] * math.log(pthetas_avg[i])
    return -res


img_candidate_points = cv2.imread('img_candidate_points.jpg', 0)
height, width = img_candidate_points.shape[:2]

step = 10
step_angles = np.arange(start=-80, stop=80 + 10, step=step)
entropy_ps_length = len(step_angles)
entropy_ps = [0] * entropy_ps_length
i = 0
for angle in step_angles:
    pthetas = [0] * height
    pthetas_avg = [0] * height
    sum_pthetas = 0
    center = (width / 2, height / 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated_roi_img = cv2.warpAffine(img_candidate_points, rotation_matrix, (height, width))
    cv2.imshow('angle: ' + str(angle), rotated_roi_img)
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

    if sum_pthetas > 0:
        for h in range(0, height):
            pthetas_avg[h] = pthetas[h] / sum_pthetas
        entropy_ps[i] = calculate_entropy(pthetas_avg, height)
    else:
        entropy_ps[i] = 100

    print('=========')
    print('i', i)
    print('angle', angle)
    print('sum_pthetas', sum_pthetas)
    print('entropy_ps[i]', entropy_ps[i])
    i += 1

print(entropy_ps)

min_a = 0
min_entropy = entropy_ps[min_a]
min_angle = step_angles[0]
i = 0
for angle in step_angles:
    if entropy_ps[i] < min_entropy:
        min_a = i
        min_entropy = entropy_ps[i]
        min_angle = angle
    i += 1
print('=== Estimated rotation angle (deg):', min_angle)
# img_height, img_width = img.shape[:2]
# img_center = (img_height / 2, img_width / 2)
# rotation_matrix = cv2.getRotationMatrix2D(img_center, min_angle, 1.0)
# Maintain white background when using OpenCV warpAffine
# cv2.warpAffine(src, M, dsize, dst=None, flags=None, borderMode=None, borderValue=None)
# img_rotated = cv2.warpAffine(img, rotation_matrix, (img_width, img_height),
#                              cv2.INTER_AREA, cv2.BORDER_DEFAULT, cv2.BORDER_REPLICATE)
# cv2.imshow(WTITLE_IMG_ROTATED, img_rotated)
cv2.waitKey(0)

# for a in range(0, entropy_ps_length):
#     pthetas = [0] * height
#     pthetas_avg = [0] * height
#     sum_pthetas = 0
#     angle = a - MAX_ROTATION_ANGLE
#     center = (width / 2, height / 2)
#     rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
#     rotated_roi_img = cv2.warpAffine(img_candidate_points, rotation_matrix, (height, width))
#     # The next calculation will use rotated_roi_img instead
#     for h in range(0, height):
#         sum_of_rows = 0
#         for w in range(0, width):
#             # TODO XIN weird error: index out of bounds (have to try-catch)
#             try:
#                 sum_of_rows += rotated_roi_img[h, w]
#             except IndexError:
#                 break  # Break out when list index out of range
#         pthetas[h] = sum_of_rows
#         sum_pthetas += pthetas[h]
#     for h in range(0, height):
#         pthetas_avg[h] = pthetas[h] / sum_pthetas
#     entropy_ps[a] = calculate_entropy(pthetas_avg, height)
# min_a = 0
# min_entropy = entropy_ps[min_a]
# min_angle = min_a - MAX_ROTATION_ANGLE
# for a in range(0, entropy_ps_length):
#     if entropy_ps[a] < min_entropy:
#         min_a = a
#         min_entropy = entropy_ps[a]
#         min_angle = min_a - MAX_ROTATION_ANGLE
# print('=== Estimated rotation angle (deg):', min_angle)
# img_height, img_width = img.shape[:2]
# img_center = (img_height / 2, img_width / 2)
# rotation_matrix = cv2.getRotationMatrix2D(img_center, min_angle, 1.0)
# # Maintain white background when using OpenCV warpAffine
# # cv2.warpAffine(src, M, dsize, dst=None, flags=None, borderMode=None, borderValue=None)
# img_rotated = cv2.warpAffine(img, rotation_matrix, (img_width, img_height),
#                              cv2.INTER_AREA, cv2.BORDER_DEFAULT, cv2.BORDER_REPLICATE)
# cv2.imshow(WTITLE_IMG_ROTATED, img_rotated)
# cv2.waitKey(0)
