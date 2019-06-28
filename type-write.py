import xml.etree.ElementTree as ET
import fileinput
import os
import cv2 as cv
import xmlformatter

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

stave_tree = ET.parse(f'./xml/{ manu }-0{ file }-position-updated.xml')
stave_root = stave_tree.getroot()

image = cv.imread(f'./originals/{ manu }/{ manu }-0{ file }.png')
inc = 0
for glyph in stave_root.find('glyphs'):
    uly = int(glyph.get('uly'))
    ulx = int(glyph.get('ulx'))
    nrows = int(glyph.get('nrows'))
    ncols = int(glyph.get('ncols'))

    type_class = glyph.find('ids').find('id')

    cv.imshow('image', image[uly-100:uly+nrows+100,ulx-20:ulx+ncols+20])
    cv.waitKey(2)
    print('Type: ')
    type = str(input().strip())
    if type == '':
        type_class.set('name', 'punctum')
    elif type == 'i':
        type_class.set('name', 'inclinatum')
    elif type == 'v':
        type_class.set('name', 'virga')
    elif type == 'c':
        type_class.set('name', 'custos')
    elif type == 'cc':
        type_class.set('name', 'c_clef')
    elif type == 'fc':
        type_class.set('name', 'f_clef')
    elif type == 'p2':
        type_class.set('name', 'podatus2')
    elif type == 'p3':
        type_class.set('name', 'podatus3')
    elif type == 'p4':
        type_class.set('name', 'podatus4')
    elif type == 'p5':
        type_class.set('name', 'podatus5')
    elif type == 'o2':
        type_class.set('name', 'oblique2')
    elif type == 'o3':
        type_class.set('name', 'oblique3')
    elif type == 'o4':
        type_class.set('name', 'oblique4')
    elif type == 'o5':
        type_class.set('name', 'oblique5')
    else:
        type_class.set('name', type)
    # if inc == 20:
    #     break
    # inc += 1

stave_tree.write(f'./xml/{ manu }-0{ file }-position-updated.xml')
