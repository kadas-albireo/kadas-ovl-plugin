import zipfile
import os
import sys
from xml.dom import minidom
from OvlReader.copexreader.COPEx import *
from MultiSymbolConverter import MultiSymbolConverterAXXI, MultiSymbolConverterBABS
from MSSSymbolConverter import MSSSymbolConverter
from MultiSymbolLineConverter import MultiSymbolLineConverter
from COPExObject2MSSConverter import COPExObject2MSSConverter


base_dir = os.path.dirname(os.path.abspath(__file__))
# f = base_dir + r'\swissline.ovl'
# f = base_dir + r'\swissline_MSS.ovl'
# f = base_dir + r'\swissline_lines.ovl'
# f = base_dir + r'\swissline_titel.ovl'
# f = base_dir + r'\swissline_docu.ovl'
# f = base_dir + r'\swissline_lines_areas.ovl'
# f = base_dir + r'\swissline_lines_menu.ovl'
# f = base_dir + '\..\..\sample_ovl' + r'\swissline_tab_all.ovl'

symbol2mss_converter = [
    MultiSymbolConverterAXXI(base_dir + '/mapping'),
    MultiSymbolConverterBABS(base_dir + '/mapping'),
    MultiSymbolLineConverter(base_dir + '/mapping'),
    MSSSymbolConverter()
]

mapping_found = 0
symbol_count = 0


def get_image_name(symbol_string):
    """
    Creates a filename from a symbol string.
    This function removes all chars which must not in a filename.
    :param symbol_string: string
    :return: string
    """
    symstr = symbol_string
    symstr = symstr.replace("*", "")
    symstr = symstr.replace("\"", "")
    symstr = symstr.replace(";", "")
    symstr = symstr.replace(",", "")
    symstr = symstr.replace(" ", "")
    symstr = symstr.replace("\\", "")
    symstr = symstr.replace(":", "")
    symstr = symstr.replace("/", "")
    symstr = symstr.replace(">", "")
    symstr = symstr.replace("<", "")
    symstr = symstr.replace("|", "")

    if len(symstr) > 250:
        symstr = symstr[0:250]

    return symstr


def read_copex(clsid, byte_data_value):
    """
    Read COPEx specific data from a XML node.

    @param copex_node COPEx XML node
    """
    global mapping_found
    global symbol_count

    byte_data = bytearray.fromhex(byte_data_value)
    # print byte_data.decode("utf-8")

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

        symbol_count += 1
        symbol_def = None
        for converter in symbol2mss_converter:
            symbol_def = converter.map(copex_obj)
            if symbol_def is not None:
                break

        if symbol_def is not None:
            mapping_found += 1
            # print COPExObject2MSSConverter.get_mms_string(symbol_def)
            # print(symbol_def)
            # print("MSS-Lib XML String: " + COPExObject2MSSConverter.get_mms_string(symbol_def))
            return (COPExObject2MSSConverter.get_mms_string(symbol_def))

        else:
            pass
            # print("Conversion failed : " + copex_obj.get_symbol_string())
            # print(copex_obj.get_symbol_string() +
            #       "\t" +
            #       "\t" + get_image_name(copex_obj.get_symbol_string()))


def main():

    if zipfile.is_zipfile(f):

        zf = zipfile.ZipFile(f)
        file_list = zf.namelist()
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

    print("SymbolCount:" + str(symbol_count))
    print("Mapping found:" + str(mapping_found))


if __name__ == '__main__':
    main()
