import zipfile
import os
from xml.dom import minidom
from kadas_ovl.copexreader.COPEx import *
from .MultiSymbolConverter import MultiSymbolConverter
from .MSSSymbolConverter import MSSSymbolConverter
from .MultiSymbolLineConverter import MultiSymbolLineConverter
from .COPExObject2MSSConverter import COPExObject2MSSConverter


base_dir = os.path.dirname(os.path.abspath(__file__))

symbol2mss_converter = [
    MultiSymbolConverter(os.path.join(base_dir, 'mapping')),
    MultiSymbolLineConverter(os.path.join(base_dir, 'mapping')),
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
            # print(symbol_def)
            # print("MSS-Lib XML String: " + COPExObject2MSSConverter.get_mms_string(symbol_def))
            # print(copex_obj.get_symbol_string() +
            #       "\t" + COPExObject2MSSConverter.get_mms_string(symbol_def) +
            #       "\t" + get_image_name(copex_obj.get_symbol_string()))
            return COPExObject2MSSConverter.get_mms_string(symbol_def), ("PFEIL_Angriff" in copex_obj.get_symbol_string())
        else:
            # print("Conversion failed : " + copex_obj.get_symbol_string())
            # print("FAILED: " + copex_obj.get_symbol_string() +
            #       "\t" +
            #       "\t" + get_image_name(copex_obj.get_symbol_string()))
            return None
