import os
from xlrd import open_workbook
from COPEx import *
from COPExObject2MSSConverter import COPExObject2MSSConverter


class MSSSymbolConverter(COPExObject2MSSConverter):

    def __init__(self, mapping_file_folder='.'):
        COPExObject2MSSConverter.__init__(self)

    def map(self, copex_obj):
        """
        Get the mapping for a COPExObject

        @param copex_obj the copex object
        @return a map with "ID" and "Attributes" which defines an MSS symbol or None if no mapping was found
        """

        if not isinstance(copex_obj, MSSObject):
            return None

        return None