from xml.etree.ElementTree import Element, SubElement
from xml.etree import ElementTree
from xml.dom import minidom


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

root = Element('score-partwise')
part_list = SubElement(root, "part-list")
part_list.attrib['my-attr'] = 'my-attr-value'

print(prettify(root))
