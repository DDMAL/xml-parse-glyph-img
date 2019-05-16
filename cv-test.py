########################################
#
#   CURRENT FUNCTIONING PARAMETER VALUES
#   ------------------------------------
#
#   Erosion dimensions: 4 4
#   Erosion iterations: 3

import cv2 as cv
import numpy as np
import random

print("Enter stave number: ")
num = input().strip()
print("Erosion dimensions: ")
erode = input()
erode_list = erode.split()
print("Erosion iterations: ")
iter = input().strip()
print("Max line gap: ")
gap = int(input().strip())

image = cv.imread(f'./stave_boxes/stave_{ str(num) }_bb.png')
img_copy = image.copy()
img_line = image.copy()

# cv.imshow('Copy', img_copy)
# cv.waitKey(0)

grayscale = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
ret, thresh = cv.threshold(grayscale,200,255,cv.THRESH_BINARY_INV)

edges = cv.Canny(grayscale, 50, 150, apertureSize = 3)
lines = cv.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength = 100, maxLineGap = gap)

lu = [10**20, 10**20]
lb = [10**20, 0]
ru = [0, 10**20]
rb = [0, 0]

for line in lines:
    x1,y1,x2,y2 = line[0]

    if -0.5 <= (y2-y1) / (x2 - x1) <= 0.5:

        if x1 <= lu[0]:
            lu[0] = x1
            lb[0] = x1
            # if y1 <= lu[1]:
            #     lu[1] = y1
            # if y1 >= lb[1]:
            #     lb[1] = y1

        if x2 >= rb[0]:
            rb[0] = x2
            ru[0] = x2
            # if y2 <= ru[1]:
            #     ru[1] = y2
            # if y2 >= rb[1]:
            #     rb[1] = y2

    # print(x1,y1,x2,y2)
    cv.line(img_line, (x1,y1), (x2,y2), (0,255,0),2)

# cv.imshow('lines please!!!', img_line)

print('x: ', lu[0], lb[0], ru[0], rb[0])


kernel = np.ones((int(erode_list[0]), int(erode_list[1])),np.uint8)
erosion = cv.erode(thresh, kernel, iterations = int(iter))

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

        cv.drawContours(img_line, [approx], -1,
            (
                random.randint(0,255),
                random.randint(0,255),
                random.randint(0,255)
            ), 2)

        cont_filt.append(c)

cv.imshow('Bounding rect',img_line)

bound_coords = np.zeros([len(cont_filt), 5])

for i, c in enumerate(cont_filt):
    x,y,w,h=cv.boundingRect(c)

    if bound_coords[i][0] == 0:
        bound_coords[i][0] = i + 1
        for j, c_n in enumerate(cont_filt[i+1:]):
            # print('j', j+i)
            x_n, y_n, w_n, h_n = cv.boundingRect(c_n)
            if not (x > x_n + w_n or x_n > x + w):
                # print('overlap')
                bound_coords[j+i][0] = i + 1
                # print(x,w,x_n,w_n)


# print(bound_coords)


cv.waitKey()
