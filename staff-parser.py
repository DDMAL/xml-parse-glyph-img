import numpy as np
import cv2
import xml.etree.ElementTree as ET

img = cv2.imread('CF-012.png', 1)

staff_tree = ET.parse('./xml/staff-coordinates.xml')
staff_root = staff_tree.getroot()
# staffs = staff_root.find('staves')

uly_temp = 0
index = 0

for staff in staff_root.findall('staves'):
    uly = int(staff.find('bounding_box').find('uly').text)
    ulx = int(staff.find('bounding_box').find('ulx').text)
    ncols = int(staff.find('bounding_box').find('ncols').text)
    nrows = int(staff.find('bounding_box').find('nrows').text)

    print(uly, ulx)

    # if abs(uly - uly_temp) > 200:
    cv2.imwrite(f'./staff_boxes/staff_{ index }_bb.png',
        img[uly:uly+nrows, ulx:ulx+ncols])
    index += 1
#
#     uly_temp = uly

# x_len = 0
# y_len = 0
#
# for stave_index, stave in enumerate(staff_root.findall('staves')):
#     print(stave_index)
#     for stave_next in staff_root.findall('staves')[stave_index+1:]:
#         if int(stave_next.find('bounding_box').find('ulx').text) > int(stave.find('bounding_box').find('ulx').text):
#             print('yeet!')
#         else:
#             break
