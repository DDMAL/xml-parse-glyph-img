########################################
#
#   CURRENT FUNCTIONING PARAMETER VALUES
#   ------------------------------------
#
#   Erosion dimensions: 3 3
#   Erosion iterations: 5
#   Max line gap: 25
#
#   PAST VALUES
#   ------------------------------------
#
#   (4,4), 3, 25 |

import cv2 as cv
import numpy as np
import random
import matplotlib.pyplot as plt
import os

print("Enter stave number: ")
stave_num = input().strip()
print("Erosion dimensions: ")
erode = input()
erode_list = erode.split()
print("Erosion iterations: ")
iter = int(input().strip())
# print("Max line gap: ")
# gap = int(input().strip())

manu = os.listdir('./stave_boxes')[0].split('_')[0]
page_num = os.listdir('./stave_boxes')[0].split('_')[1]

os.system(f'rm -rf ./dataset/{ manu }_{ page_num }_{ stave_num }*')

image = cv.imread(f'./stave_boxes/{ manu }_{ page_num }_stave_{ stave_num }_bb.png')
img_copy = image.copy()
img_clean = image.copy()
img_line = cv.imread(f'./stave_boxes_lines/{ manu }_{ page_num }_stave_lines_{ stave_num }_bb.png')
img_glyphs = cv.imread(f'./stave_boxes_glyphs/{ manu }_{ page_num }_stave_glyphs_{ stave_num }_bb.png')

n, m, r = image.shape

if not os.path.isdir('./dataset'):
    os.system('mkdir dataset')

# cv.imshow('Copy', img_copy)
# cv.waitKey(0)

grayscale = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
gray_line = cv.cvtColor(img_line, cv.COLOR_BGR2GRAY)
gray_glyph = cv.cvtColor(img_glyphs, cv.COLOR_BGR2GRAY)


ret, thresh = cv.threshold(grayscale,180,255,cv.THRESH_BINARY_INV)

ret2, thresh_glyph = cv.threshold(gray_glyph,200,255,cv.THRESH_BINARY_INV)

# cv.imshow('glyphs', thresh_glyph)


edges = cv.Canny(gray_line, 50, 150, apertureSize = 3)
lines = cv.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength = 100, maxLineGap = 25)

lines = np.array(lines)

# stave_coords = stave_coords[np.argsort(stave_coords[:,1])]

lines = lines[np.argsort(lines[:,0,1])]

lu = [10**20, 10**20]
lb = [10**20, 0]
ru = [0, 10**20]
rb = [0, 0]
min_x = 10**20

skew = 0

avg_slope = np.mean(
    (lines[:,0,3] - lines[:,0,1]) / (lines[:,0,2]-lines[:,0,0])
)

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

        if abs(x1-lb[0]) < 100 and y1 > lb[1]:
            lb[1] = y1

        if x1 <= min_x:
            lu[0] = x1
            lb[0] = x1
            min_x = x1

        if y1 <= lu[1]:
            lu[1] = y1

        # if x2 >= rb[0]:
        #     rb[0] = x2
        #     ru[0] = x2
            # if y2 <= ru[1]:
            #     ru[1] = y2
            # if y2 >= rb[1]:
            #     rb[1] = y2

    # print(x1,y1,x2,y2)
        cv.line(img_copy, (x1,y1), (x2,y2), (0,255,0),2)

# cv.line(img_copy, (lu[0], lu[1]), (lb[0], lb[1]), (255,0,0),2)

# cv.imshow('lines please!!!', img_line)

# print('lu: ', lu[0], lu[1])
# print('lb: ', lb[0], lb[1])


kernel = np.ones((int(erode_list[0]), int(erode_list[1])),np.uint8)
erosion = cv.erode(thresh, kernel, iterations = iter)

kern_final = np.ones((2,2), np.uint8)
erosion = cv.erode(erosion, kern_final, iterations = 1)

# cv.imshow('thresh', erosion)
# cv.waitKey()

contours, hierarchy = cv.findContours(erosion.copy(), cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)

contour_count = 0

cont_filt = []

for index, c in enumerate(contours):

    x,y,w,h=cv.boundingRect(c)

    if h > 15:
        epsilon = 0.01*cv.arcLength(c,True)
        approx = cv.approxPolyDP(c,epsilon,True)
        white_count = 0

        for point in approx:
            if thresh_glyph[point[0][1],point[0][0]] != 0:
                white_count += 1
        # print('white: ', white_count)
        if white_count > 1:
            cv.drawContours(img_copy, [approx], -1,
                (
                    random.randint(120,255),
                    random.randint(120,255),
                    random.randint(120,255)
                ), 2)

            cont_filt.append((x,y,w,h))

cont_filt = np.array(cont_filt)
cont_filt = cont_filt[np.argsort(cont_filt[:,0])]

overlap = np.zeros(len(cont_filt))


for i, c in enumerate(cont_filt):

    for c_n in cont_filt[i+1:]:

        if c[0] < c_n[0] + 4 < c[0] + c[2] or c_n[0] < c[0] + 4 < c_n[0] + c_n[2]:
            overlap[i] = 1
            print('overlap: ', c[0], c[0]+c[2], ' | ', c_n[0], c_n[0]+c_n[2])

neume_index = 0


# print(cont_filt)

# print(cont_filt)

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
