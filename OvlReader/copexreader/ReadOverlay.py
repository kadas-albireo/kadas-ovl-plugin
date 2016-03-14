######################################################
# (c) 2016 Airbus Defence and Space, Friedrichshafen
# @author A020449
######################################################

import zipfile
from xml.dom import minidom

from COPEx import *
import os

# define the overlay file here
base_dir = os.path.dirname(os.path.abspath(__file__)) + '\..\..\sample_ovl'
f = base_dir + r'\swissline_tab_all.ovl'
# f = base_dir + r'\swissline.ovl'
# f = base_dir + r'\swissline_MSS.ovl'
# f = base_dir + r'\swissline_lines.ovl'
# f = base_dir + r'\swissline_titel.ovl'
# f = base_dir + r'\swissline_docu.ovl'
# f = base_dir + r'\swissline_lines_areas.ovl'
# f = base_dir + r'\swissline_lines_menu.ovl'


def read_copex(copex_node):
    """
    Read COPEx specific data from a XML node.

    @param copex_node COPEx XML node
    """

    clsid = copex_node.getAttribute('clsid')
    # iid_name = copex_node.getAttribute('iidName')
    byte_data_node = copex_node.getElementsByTagName('ByteArray')

    if len(byte_data_node) > 0:
        byte_data_value = byte_data_node[0].getAttribute('Value')
        # byte_data_size = byte_data_node[0].getAttribute('Size')
        byte_data = bytearray.fromhex(byte_data_value)

        copex_obj = None
        if clsid == APP6aObject.CLSID:
            copex_obj = APP6aObject()
        elif clsid == MSSObject.CLSID:
            copex_obj = MSSObject()
        elif clsid == MultiSymbolObject.CLSID:
            copex_obj = MultiSymbolObject()
        elif clsid == MultiSymbolLineObject.CLSID:
            copex_obj = MultiSymbolLineObject()
        elif clsid == AnnotationObject.CLSID:
            copex_obj = AnnotationObject()
        else:
            print('Unknown clsid:' + clsid)

        if copex_obj is not None:
            copex_obj.read_object(byte_data)

            # print(copex_obj.get_display_name())
            print("==========================")
            print("Symboltype: " + type(copex_obj).__name__)
            print(copex_obj)


def main():
    # check if the file is a zip-file
    if zipfile.is_zipfile(f):

        zf = zipfile.ZipFile(f)
        file_list = zf.namelist()
        # check if Geogrid-OVL
        if 'geogrid50.xml' in file_list:
            xml_data = zf.read('geogrid50.xml')

            xml = minidom.parseString(xml_data)

            obj_list = xml.getElementsByTagName('object')

            for obj in obj_list:
                cls_name = obj.getAttribute('clsName')
                if 'CLSID_GraphicTAZ' == cls_name:
                    copex_attr = obj.getElementsByTagName('COPExObject')
                    if len(copex_attr) > 0:
                        read_copex(copex_attr[0])


if __name__ == '__main__':
    main()
