##########################################################
#
#   CURRENT FUNCTIONING PARAMETER VALUES
#   (In and around these values tends to work pretty well)
#   ------------------------------------------------------
#
#   Erosion dimensions: 3 3
#   Erosion iterations: 5
#   Max line gap: 25
#
#   PAST VALUES
#   ------------------------------------------------------
#
#   (4,4), 3, 25 |

# ------------------------------------------------------------------------------

import cv2 as cv
import numpy as np
import random
import matplotlib.pyplot as plt
import os

# ------------------------------------------------------------------------------

print("Enter stave number: ")
stave_num = input().strip()
print("Erosion dimensions: ")
erode = input()
erode_list = erode.split()
print("Erosion iterations: ")
iter = int(input().strip())
print("Gray val (0-255): ")
gray = int(input().strip())
# print("Max line gap: ")
# gap = int(input().strip())

# ------------------------------------------------------------------------------

def open_manuscript_bb_image(manuscript, page_number, stave_number, layer):
    if layer == 'main':
        image = cv.imread('./stave_boxes/' +
        f'{ manuscript }_{ page_number }_stave_{ stave_number }_bb.png')
    else:
        image = cv.imread(f'./stave_boxes_{ layer }/' +
            f'{ manuscript }_{ page_number }' +
            f'_stave_{ layer }_{ stave_number }_bb.png')
    return image


def grayscale_img(image):
    return cv.cvtColor(image, cv.COLOR_BGR2GRAY)


def threshold_img(grayscale_image, low, high):
    ret, threshold = cv.threshold(
        grayscale_image,
        low, high,
        cv.THRESH_BINARY_INV)

    return ret, threshold


def line_detection(grayscale_image, display_image, write_image, line_gap):
    skew = 0
    edges = cv.Canny(grayscale_image, 50, 150, apertureSize = 3)
    lines = cv.HoughLinesP(edges, 1, np.pi/180, 100,
        minLineLength = 100, maxLineGap = line_gap)
    lines = np.array(lines)
    lines = lines[np.argsort(lines[:,0,2])]
    avg_slope = np.mean(
        (lines[:,0,3] - lines[:,0,1]) / (lines[:,0,2]-lines[:,0,0]))
    if avg_slope > 0.001:
        print('downward skew')
        skew = -1
    elif avg_slope < -0.001:
        print('upward skew')
        skew = 1
    else:
        print('close to level')
        skew = 0
    ends = lines[-16:]
    ends = ends[np.argsort(ends[:,0,3])]
    new_line = 1
    i = 0
    temp = 0
    while i < len(ends):
        line = ends[i]
        x1,y1,x2,y2 = line[0]
        if temp == 0 or y2 - temp > 30:
            m = (y2-y1) / (x2 - x1)
            b = m * (-1 * x1) + y1
            if -0.2 <= (y2-y1) / (x2 - x1) <= 0.2:
                # cv.line(display_image, (x1,y1), (int(x2*1.2),int(m*x2*1.2+b)), (80,90,110),6)
                cv.line(write_image, (x1,y1), (int(x2*1.2),int(m*x2*1.2+b)), (80,90,110),6)
        temp = y2
        i += 1
    return 0


def erode_image(image, erode_dimensions, erode_iterations):
    kernel = np.ones(
        (int(erode_dimensions[0]), int(erode_dimensions[1])),np.uint8)
    erosion = cv.erode(image, kernel, iterations = erode_iterations)
    kernel_final = np.ones((2,2), np.uint8)
    erosion = cv.erode(erosion, kernel_final, iterations = 1)
    return erosion


def draw_filter_contours(eroded_image, comparison_image, draw_image):
    contour_count = 0
    contours_filtered = []
    contours, hierarchy = cv.findContours(
        eroded_image.copy(), cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)
    for index, c in enumerate(contours):
        x,y,w,h=cv.boundingRect(c)
        if h > 10:
            epsilon = 0.01*cv.arcLength(c,True)
            approx = cv.approxPolyDP(c,epsilon,True)
            white_count = 0
            for point in approx:
                if comparison_image[point[0][1],point[0][0]] != 0:
                    white_count += 1
            if white_count > 1:
                cv.drawContours(draw_image, [approx], -1,
                    (
                        random.randint(120,255),
                        random.randint(120,255),
                        random.randint(120,255)
                    ), 2)
                contours_filtered.append((x,y,w,h))
    contours_filtered = np.array(contours_filtered)
    contours_filtered = contours_filtered[np.lexsort((contours_filtered[:,1],
        contours_filtered[:,0]))]
    return contours_filtered


def contour_overlap(contours):
    overlap = np.zeros(len(contours))
    overlap_filter = []
    remove = np.zeros(len(contours))
    remove_index = 0
    contours_filtered = []
    for i, c in enumerate(contours):
        j = i
        for c_n in contours[i+1:]:
            j += 1
            if (c[0] < c_n[0] + 4 < c[0] + c[2] or
                c_n[0] < c[0] + 4 < c_n[0] + c_n[2]):
                if c[1] < c_n[1]:
                    overlap[i] = 1
                    remove_index = j
                else:
                    overlap[j] = 1
                    remove_index = i
                remove[remove_index] = 1
                print('overlap: ',
                    c[0], c[0]+c[2], ' | ', c_n[0], c_n[0]+c_n[2])
    for i, c in enumerate(contours):
        if remove[i] != 1:
            contours_filtered.append(c)
            overlap_filter.append(overlap[i])
    contours_filtered = np.array(contours_filtered)
    return contours_filtered, overlap_filter

# c[0] = (x,y,w,h)

def clef_finder(contours, overlap):
    contours_filtered = []
    clef_check_counter = 0
    matches = []
    i = 0
    for c in contours[:-1]:
        if i >= len(contours) - 1:
            break
        if overlap[i] == 0 and overlap[i+1] == 1:
            clef_check_counter += 1
        if clef_check_counter == 1 and (contours[i][1] < contours[i+1][1] + 4 < contours[i][1] + contours[i][3] or
            contours[i+1][1] < contours[i][1] + 4 < contours[i+1][1] + contours[i+1][3]):
            clef_check_counter += 1
        if clef_check_counter == 2 and (contours[i+1][0]-contours[i][0] <= 60):
            clef_check_counter += 1
        if clef_check_counter == 3:
            if (i != 0 and contours[i][0] - contours[i-1][0] > 400) or i == 0:
                clef_check_counter += 1
        if clef_check_counter == 4:
            contours_filtered.append(
            (
                contours[i][0],
                contours[i][1],
                contours[i+1][2] + contours[i+1][0] - contours[i][0] + 2,
                max(contours[i][3], contours[i+1][3])
            ))
            i += 2
        else:
            contours_filtered.append(contours[i])
            i += 1
        clef_check_counter = 0

    contours_filtered.append(contours[-1])
    contours_filtered = np.array(contours_filtered)
    return contours_filtered, matches

def write_neume_images(contours, write_image, last_image,
    manuscript, page_number, stave_number):
    neume_index = 0
    for i, c in enumerate(contours):
        # if overlap[i] == 0:
        if c[0] < 5:
            resize = write_image[0:, c[0]:c[0]+c[2]+5]
        else:
            resize = write_image[0:, c[0]-5:c[0]+c[2]+5]
        if i == len(contours) - 1:
            print('yeet')
            resize = last_image[0:, c[0]-5:c[0]+c[2]+5]
        resize = cv.resize(resize, (50, 200), interpolation = cv.INTER_AREA)
        cv.imwrite(f'./dataset/{ manu }' +
            f'_{ page_number }_{ stave_number }' +
            f'_{ neume_index }.png', resize)

        neume_index += 1
    return 0

# ------------------------------------------------------------------------------

manu = os.listdir('./stave_boxes')[0].split('_')[0]
page_num = os.listdir('./stave_boxes')[0].split('_')[1]

if not os.path.isdir('./dataset'):
    os.system('mkdir dataset')

# Remove previous staff images
os.system(f'rm -rf ./dataset/{ manu }_{ page_num }_{ stave_num }*')

image = open_manuscript_bb_image(manu, page_num, stave_num, 'main')
img_copy = image.copy()
img_clean = image.copy()
img_disp = image.copy()
img_line = open_manuscript_bb_image(manu, page_num, stave_num, 'lines')
img_glyphs = open_manuscript_bb_image(manu, page_num, stave_num, 'glyphs')

grayscale = grayscale_img(image)
gray_line = grayscale_img(img_line)
gray_glyph = grayscale_img(img_glyphs)

ret, thresh = threshold_img(grayscale, gray, 255)
ret2, thresh_glyph = threshold_img(gray_glyph, gray, 255)

line_detection(gray_line, img_disp, img_copy, 25)

erosion = erode_image(thresh, erode_list, iter)

cont_filt = draw_filter_contours(erosion, thresh_glyph, img_disp)

cont_filt, overlap = contour_overlap(cont_filt)
print(cont_filt)
print(overlap)
cont_filt, match = clef_finder(cont_filt, overlap)
print(cont_filt, match)
write_neume_images(cont_filt, image, img_copy, manu, page_num, stave_num)
print('The stave was number', stave_num)
print('The gray number was', gray)
# print(overlap)
# print(remove)

fig1 = plt.figure(figsize=(20,10))
fig1 = plt.subplot(3,1,1)
fig1 = plt.imshow(thresh)
fig1 = plt.subplot(3,1,2)
fig1 = plt.imshow(erosion)
fig1 = plt.subplot(3,1,3)
fig1 = plt.imshow(img_disp)

plt.show()
