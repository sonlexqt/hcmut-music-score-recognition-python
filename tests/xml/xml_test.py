from xml.etree.ElementTree import Element, SubElement, tostring, fromstring
from xml.dom import minidom


def prettify(elem):
    # Return a pretty-printed XML string for the Element.
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

score_partwise = Element('score-partwise')
part_list = SubElement(score_partwise, 'part-list')
score_part = SubElement(part_list, 'score-part')
score_part.attrib['id'] = 'P1'
part_name = SubElement(score_part, 'part-name')
part_name.text = 'P1'
part = SubElement(score_partwise, 'part')
part.attrib['id'] = 'P1'

xin = Element('xin')
heo = Element('heo')
score_partwise.extend([xin, heo])

print(tostring(score_partwise))

