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
# print("Max line gap: ")
# gap = int(input().strip())

# ------------------------------------------------------------------------------

def open_manuscript_bb_image(manuscript, page_number, stave_number, layer):
    if layer == 'main':
        image = cv.imread('./stave_boxes/' +
        f'{ manuscript }_{ page_number }_stave_{ stave_number }_bb.png')
    else:
        image = cv.imread(f'./stave_boxes_{ layer }/' +
            f'{ manuscript }_{ page_number }_stave_{ layer }_{ stave_number }_bb.png')
    return image


def grayscale_img(image):
    return cv.cvtColor(image, cv.COLOR_BGR2GRAY)


def threshold_img(grayscale_image, low, high):
    ret, threshold = cv.threshold(
        grayscale_image,
        low, high,
        cv.THRESH_BINARY_INV)

    return ret, threshold


def line_detection(grayscale_image, write_image, line_gap):
    skew = 0
    edges = cv.Canny(grayscale_image, 50, 150, apertureSize = 3)
    lines = cv.HoughLinesP(edges, 1, np.pi/180, 100,
        minLineLength = 100, maxLineGap = line_gap)
    lines = np.array(lines)
    lines = lines[np.argsort(lines[:,0,1])]
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
    for line in lines:
        x1,y1,x2,y2 = line[0]
        if -0.2 <= (y2-y1) / (x2 - x1) <= 0.2:
            cv.line(write_image, (x1,y1), (x2,y2), (0,255,0),2)
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

        if h > 15:
            epsilon = 0.01*cv.arcLength(c,True)
            approx = cv.approxPolyDP(c,epsilon,True)
            white_count = 0

            for point in approx:
                if comparison_image[point[0][1],point[0][0]] != 0:
                    white_count += 1
            # print('white: ', white_count)
            if white_count > 1:
                cv.drawContours(draw_image, [approx], -1,
                    (
                        random.randint(120,255),
                        random.randint(120,255),
                        random.randint(120,255)
                    ), 2)

                contours_filtered.append((x,y,w,h))
    contours_filtered = np.array(contours_filtered)
    contours_filtered = contours_filtered[np.argsort(contours_filtered[:,0])]
    return contours_filtered


def contour_overlap(contours):
    overlap = np.zeros(len(contours))
    for i, c in enumerate(contours):

        for c_n in contours[i+1:]:

            if (c[0] < c_n[0] + 4 < c[0] + c[2] or
                c_n[0] < c[0] + 4 < c_n[0] + c_n[2]):
                    overlap[i] = 1
                    print('overlap: ',
                        c[0], c[0]+c[2], ' | ', c_n[0], c_n[0]+c_n[2])
    return overlap


def write_neume_images(contours, write_image, overlap,
    manuscript, page_number, stave_number):
    neume_index = 0
    for i, c in enumerate(contours):
        if overlap[i] == 0:
            if c[0] < 5:
                resize = write_image[0:, c[0]:c[0]+c[2]+5]
            else:
                resize = write_image[0:, c[0]-5:c[0]+c[2]+5]
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
img_line = open_manuscript_bb_image(manu, page_num, stave_num, 'lines')
img_glyphs = open_manuscript_bb_image(manu, page_num, stave_num, 'glyphs')

grayscale = grayscale_img(image)
gray_line = grayscale_img(img_line)
gray_glyph = grayscale_img(img_glyphs)

ret, thresh = threshold_img(grayscale, 180, 255)
ret2, thresh_glyph = threshold_img(gray_glyph, 200, 255)

line_detection(gray_line, img_copy, 25)

erosion = erode_image(thresh, erode_list, iter)

cont_filt = draw_filter_contours(erosion, thresh_glyph, img_copy)

overlap = contour_overlap(cont_filt)

write_neume_images(cont_filt, img_clean, overlap, manu, page_num, stave_num)

neume_index = 0

for i, c in enumerate(cont_filt):

    if overlap[i] == 0:

        if c[0] < 5:
            resize = img_clean[0:, c[0]:c[0]+c[2]+5]
        else:
            resize = img_clean[0:, c[0]-5:c[0]+c[2]+5]

        resize = cv.resize(resize, (50, 200), interpolation = cv.INTER_AREA)
        cv.imwrite(f'./dataset/{ manu }_{ page_num }_{ stave_num }_{ neume_index }.png', resize)

        neume_index += 1

print(overlap)
fig1 = plt.figure(figsize=(20,11))
fig1 = plt.subplot(3,1,1)
fig1 = plt.imshow(thresh)
fig1 = plt.subplot(3,1,2)
fig1 = plt.imshow(erosion)
fig1 = plt.subplot(3,1,3)
fig1 = plt.imshow(img_copy)


plt.show()


# print(bound_coords)


# cv.waitKey()
