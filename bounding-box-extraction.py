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

