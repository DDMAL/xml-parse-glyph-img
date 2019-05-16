import numpy as np
import cv2
import xml.etree.ElementTree as ET

img = cv2.imread('CF-012.png', 1)

cv2.imshow('image', img)

def find_min_diff(arr):
    len = len(arr)
    diff = 10**20
    for i in range(len-1):
        for j in range(i+1, len):
            if abs(arr[i]-arr[j]) < diff:
                diff = abs(arr[i]-arr[j])

    return diff


# Find tags for neumes from xml

neume_tree = ET.parse('./xml/CF-012-neumes.xml')
neume_root = neume_tree.getroot()
neumes = neume_root.find('glyphs')

# stave tree

stave_coords = []

stave_tree = ET.parse('./xml/stave-coordinates.xml')
stave_root = stave_tree.getroot()

for stave in stave_root.findall('staves'):
    bounding_box = stave.find('bounding_box')
    stave_coords.append([0, int(bounding_box.find('uly').text),
        int(bounding_box.find('nrows').text)])

col = 1

stave_coords = np.array(stave_coords)

stave_coords = stave_coords[np.argsort(stave_coords[:,col])]

index = 0
increment = 0

for y_dim in stave_coords:
    print(y_dim[0])
    if y_dim[0] == 0:
        y_dim[0] = index + 1
        for y_dim_next in stave_coords[index+1:]:
            if y_dim[1] <= y_dim_next[1] <= y_dim[1] + y_dim[2]:
                y_dim_next[0] = index + 1
                increment = 1
        if increment:
            index += 1
    increment = 0

final_stave_coords = []

index = 1

for y_dim in stave_coords:
    if y_dim[0] == index:
        final_stave_coords.append([y_dim[1],y_dim[1]+y_dim[2]])
        for y_dim_next in stave_coords[index:]:
            if y_dim_next[0] == index:
                final_stave_coords[index-1][1] = y_dim_next[1] + y_dim_next[2]
        index += 1

neume_coords = []

for neume_index, neume in enumerate(neumes.findall('glyph')):

    ulx = int(neume.get('ulx'))
    uly = int(neume.get('uly'))
    nrows = int(neume.get('nrows'))
    ncols = int(neume.get('ncols'))
    print(neume_index, uly, ulx, nrows, ncols)

    neume_coords.append([ulx, uly, nrows, ncols])

for index, neume_coord in enumerate(neume_coords):
    for neume_coord_next in neume_coords[index+1:]:
        if abs(neume_coord[index][0] + neume_coord[index][2] \
            - neume_coord_next[index+1][0]) <= 20:
            

    # Write the bounding boxes

    cv2.imwrite(f'./bounding_boxes/neume_bb_{ neume_index }_CF-012.png', \
        img[uly:uly+nrows, ulx:ulx+ncols])

    # Write the extended column shapes

    stave_top = -1
    stave_bottom = -1

    for coord in final_stave_coords:
        if coord[0] <= uly <= coord[1]:
            stave_top = coord[0] - 10
            stave_bottom = coord[1] + 10
        elif coord[0] - 80 <= uly <= coord[1] + 80:
            stave_top = coord[0] - 60
            stave_bottom = coord[1] + 60

    cv2.imwrite(f'./columns/neume_col_{ neume_index }_CF-012.png', \
        img[stave_top:stave_bottom, ulx:ulx+ncols])

# print(final_stave_coords)
# print(stave_coords)
