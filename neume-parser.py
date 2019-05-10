import numpy as np
import cv2
import xml.etree.ElementTree as ET

img = cv2.imread('CF-012.png', 1)

cv2.imshow('image', img)

# Find tags for neumes from xml

neume_tree = ET.parse('./xml/CF-012-neumes.xml')
neume_root = neume_tree.getroot()
neumes = neume_root.find('glyphs')

barline_tree = ET.parse('./xml/CF-012-barlines.xml')


for neume_index, neume in enumerate(neumes.findall('glyph')):
    print(neume.get('uly'), neume.get('ulx'), neume.get('nrows'), neume.get('ncols'))
    ulx = int(neume.get('ulx'))
    uly = int(neume.get('uly'))
    nrows = int(neume.get('nrows'))
    ncols = int(neume.get('ncols'))

    # Write the bounding boxes

    cv2.imwrite(f'./bounding_boxes/neume_bb_{ neume_index }_CF-012.png', \
        img[uly:uly+nrows, ulx:ulx+ncols])

    # Write the extended column shapes

    cv2.imwrite(f'./columns/neume_col_{ neume_index }_CF-012.png', \
        img[uly-150:uly+nrows+150, ulx:ulx+ncols])

for
