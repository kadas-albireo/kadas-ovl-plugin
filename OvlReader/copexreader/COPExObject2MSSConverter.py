from xlrd import open_workbook
from COPEx import *


class COPExObject2MSSConverter(object):
    MAP_KEY_ID = "ID"
    MAP_KEY_ATTRIBUTES = "Attributes"

    def __init__(self):
        pass

    def map(self, copex_obj):
        """
        Get the mapping for a COPExObject

        @param copex_obj the copex object
        @return a map with "ID" and "Attributes" which defines an MSS symbol or None if no mapping was found
        """
        return None

    @staticmethod
    def get_mms_string(symbol_def):
        if COPExObject2MSSConverter.MAP_KEY_ID not in symbol_def:
            return ""

        mms_str = "<Symbol ID=\"" + symbol_def[COPExObject2MSSConverter.MAP_KEY_ID] + "\">"

        if COPExObject2MSSConverter.MAP_KEY_ATTRIBUTES in symbol_def:
            attrs = symbol_def[COPExObject2MSSConverter.MAP_KEY_ATTRIBUTES]

            for attr in attrs:
                mms_str += "<Attribute ID=\"" + attr + "\">" + attrs[attr] + "</Attribute>"

        mms_str += "</Symbol>"

        return mms_str

    @staticmethod
    def _merge_id(ids):
        """
        Merges an array symbols_ids to one symbol id. Based on the first id all "*" values will be replaced by the next
        ids.
        @param ids array with symbols ids. The important id must be the first
        @return a single symbol id
        """
        sym_id = "***************"
        for id1 in ids:
            sym_id_temp = ""
            if len(id1) < len(sym_id):
                continue

            for i in range(0, len(sym_id)):
                if sym_id[i] == "*":
                    sym_id_temp += id1[i]
                else:
                    sym_id_temp += sym_id[i]
            sym_id = sym_id_temp

        return sym_id
