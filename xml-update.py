import xml.etree.ElementTree as ET
import fileinput
import os

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

stave_tree = ET.parse(f'./xml/{ manu }-0{ file }-position.xml')
stave_root = stave_tree.getroot()

f1 = open(f'./xml/{ manu }-0{ file }-position.xml', 'r')
f2 = open(f'./xml/{ manu }-0{ file }-position-updated.xml', 'w')

positions = []

for glyph in stave_root.find('glyphs'):
    positions.append(glyph.find('ids').find('id').get('name'))

inc = 0
for line in f1:
    if f2.write(line.replace('<glyph ', f'<glyph number="{ inc }" ')) and '<glyph ' in line:
        inc += 1
f1.close()
f2.close()




with open(f'./xml/{ manu }-0{ file }-position-updated.xml', "r") as in_file:
    buf = in_file.readlines()

inc = 0

with open(f'./xml/{ manu }-0{ file }-position-updated.xml', "w") as out_file:
    for line in buf:
        # print('yeet')
        if "</ids>" in line:
            # print('yeet')
            line = line + \
                '\t\t\t<type name=""/>\n' + \
                '\t\t\t<pitch-estimation>\n' + \
                f'\t\t\t\t<position name="{ positions[inc] }"/>\n' + \
                '\t\t\t\t<pitch name=""/>\n' + \
                '\t\t\t</pitch-estimation>\n'

            inc += 1
        out_file.write(line)

# formatter = xmlformatter.Formatter(indent="1", indent_char="\t", encoding_output="ISO-8859-1", preserve=["literal"])
# formatter.format_file(f'./xml/{ manu }-0{ file }-position-copy.xml')
