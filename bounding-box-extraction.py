import numpy as np
import cv2 as cv
import xml.etree.ElementTree as ET
import os

# ------------------------------------------------------------------------------

print('Which manuscript (CF or Ein) should be considered:')
manu = input().strip()

if manu == 'CF':
    print('Which Calvo file number (09-20, 24-27 currently) should be parsed: ')
elif manu == 'Ein':
    print('Which Ein file number (01v-05v, 02r-05r currently) should be parsed: ')
else:
    print('Please try again.')
    exit()

file = input().strip()

if not os.path.isdir('./position_dataset'):
    os.system('mkdir position_dataset')

os.system(f'rm -rf ./position_dataset/{ manu }_{ file }_*')

# ------------------------------------------------------------------------------

orig_img = cv.imread(f'./originals/{ manu }/{ manu }-0{ file }.png')
# neume_layer = cv.imread(f'./layer/{ manu }/'
#     + f'{ manu }-0{ file }/{ manu }-0{ file }_1.png')
# stave_layer = cv.imread(f'./layer/{ manu }/'
#     + f'{ manu }-0{ file }/{ manu }-0{ file }_2.png')

# ------------------------------------------------------------------------------
# Functions

glyph_coords = []
stave_tree = ET.parse(f'./xml/{ manu }-0{ file }-position.xml')
stave_root = stave_tree.getroot()
glyph_count = 0
sum = 0
label_dict = {}

for glyph in stave_root.find('glyphs'):
    uly = int(glyph.get('uly'))
    ulx = int(glyph.get('ulx'))
    nrows = int(glyph.get('nrows'))
    ncols = int(glyph.get('ncols'))
    # print(uly, ulx, nrows, ncols)
    label = glyph.find('ids').find('id').get('name')
    # print(label)
    glyph_count += 1
    sum += nrows
    glyph_coords.append([uly, ulx, nrows, ncols, label])

avg_neume_height = int(sum/glyph_count)

pic_count = 0
label_file = open('position_labels.txt', 'a+')
zeros = ''

for c in glyph_coords:
    print(c)
    bounding_box = orig_img[
        c[0]-2*avg_neume_height:c[0]+c[2]+2*avg_neume_height,
        c[1]:c[1]+c[3]]
    resize = cv.resize(bounding_box, (30,120), interpolation = cv.INTER_AREA)
    if pic_count < 1000:
        zeros = ''
    if pic_count < 100:
        zeros = '0'
    if pic_count < 10:
        zeros = '00'
    file_name = f'{ manu }_{ file }_' + zeros + f'{ pic_count }.png'
    cv.imwrite('./position_dataset/' + file_name, resize)
    label_file.write(file_name + '\t' + c[4] + '\n')

    pic_count += 1

label_file.close()

os.system('sort -k3 -n position_labels.txt -o position_labels.txt')
