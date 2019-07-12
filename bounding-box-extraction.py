import numpy as np
import cv2 as cv
import xml.etree.ElementTree as ET
import os
import subprocess
import statistics

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

print('Is this for the training (0) or testing (1) dataset?')
choice = int(input().strip())

set = ''
if choice == 1:
    set = 'test'
elif choice == 0:
    set = 'train'

if not os.path.isdir(f'./position_{ set }'):
    os.system(f'mkdir position_{ set }')



os.system(f'rm -rf ./position_{ set }/{ manu }_{ file }_*')

# ------------------------------------------------------------------------------

orig_img = cv.imread(f'./originals/{ manu }/{ manu }-0{ file }.png')
# neume_layer = cv.imread(f'./layer/{ manu }/'
#     + f'{ manu }-0{ file }/{ manu }-0{ file }_1.png')
# stave_layer = cv.imread(f'./layer/{ manu }/'
#     + f'{ manu }-0{ file }/{ manu }-0{ file }_2.png')

# ------------------------------------------------------------------------------
# Functions

glyph_coords = []
# glyph_types = []
stave_tree = ET.parse(f'./xml/{ manu }-0{ file }-position-updated.xml')
stave_root = stave_tree.getroot()
glyph_count = 0
sum = 0
label_dict = {}
labels = ['l1', 'l2', 'l3', 'l4', 's1', 's2', 's3', 's4', 's5']
# types = ['punctum', 'virga', 'inclinatum', 'custos', 'c_clef', 'f_clef',
#     'oblique2', 'oblique3', 'oblique4',
#     'podatus2', 'podatus3', 'podatus4', 'podatus5']

types = ['c_clef', 'custos', 'f_clef', 'inclinatum',
    'oblique2', 'oblique3', 'oblique4',
    'podatus2', 'podatus3', 'podatus4', 'podatus5', 'punctum', 'virga', ]

for glyph in stave_root.find('glyphs'):
    uly = int(glyph.get('uly'))
    ulx = int(glyph.get('ulx'))
    nrows = int(glyph.get('nrows'))
    ncols = int(glyph.get('ncols'))
    # print(uly, ulx, nrows, ncols)
    label = glyph.find('pitch-estimation').find('position').get('name')
    type = glyph.find('ids').find('id').get('name')
    # print(type, types.index(type))
    # print(label)
    glyph_count += 1
    sum += nrows
    glyph_coords.append([uly, ulx, nrows, ncols, labels.index(label), types.index(type), 0])
    # glyph_types.append(type)

avg_neume_height = int(sum/glyph_count)

anh = avg_neume_height
glyph_coords = np.array(glyph_coords)
avg_neume_y = np.mean(glyph_coords, axis=0)
glyph_coords = glyph_coords[np.lexsort((glyph_coords[:,1], glyph_coords[:,0]))]

temp = [0,0,0,0,0,0]
staves = 0
for c in glyph_coords:
    if c[0] - temp[0] > 100:
        staves += 1
    c[6] = staves
    temp = c

glyph_coords = glyph_coords[np.lexsort((glyph_coords[:,1], glyph_coords[:,6]))]

# print(staves, avg_neume_y)

os.system(f'sed -i \'\' \'/{ manu }_{ file }_/d\' position_{ set }.txt')

pic_count = 0
label_file = open(f'position_{ set }.txt', 'a+')
zeros = ''

for c in glyph_coords:
    # print(c)
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
    cv.imwrite(f'./position_{ set }/' + file_name, resize)
    # print(types[c[5]])
    label_file.write(file_name + '\t' + labels[c[4]] + '\t' + types[c[5]] + '\n')

    pic_count += 1

label_file.close()

os.system(f'sort -k3 -n position_{ set }.txt -o position_{ set }.txt')
# os.system('sort -u position_labels.txt -o position_labels.txt')

# sort = subprocess.Popen(['sort', '-k3', '-n', 'position_labels.txt', '-o', 'position_labels.txt'], stdout=subprocess.PIPE)
# sort = subprocess.Popen(['sort', '-k3', '-n', 'position_labels.txt'], stdout=subprocess.PIPE)
# filter = subprocess.Popen(['uniq', '-u'], stdin=sort.stdout)
#
# filter.communicate()
