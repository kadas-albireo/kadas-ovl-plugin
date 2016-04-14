import os
from OvlReader.copexreader.xlrd import open_workbook
from OvlReader.copexreader.COPEx import *
from COPExObject2MSSConverter import COPExObject2MSSConverter


class MultiSymbolConverterBABS(COPExObject2MSSConverter):
    """
    Converts COPExCOPExMultiSymbolObjects with LANGUAGE="BABS".
    The mapping must be defined in a Excel file called BABS.xlsx.
    """
    MAPPING_FILE = 'BABS.xlsx'

    def __init__(self, mapping_file_folder='.'):
        COPExObject2MSSConverter.__init__(self)

        self.mapping_file_folder = mapping_file_folder

        # these are the MultiSymbolObject Keys we are necessary for the mapping
        self.str_multisymbol_keys = ["GZ", "ZZ1", "TEXT0", "TEXT2", "TEXT7"]
        # these are the MSS Keys from the mapping
        self.str_mss_keys = ["ID", "H", "XE", "XJ", "XH"]
        # main mapping table for the symbol definition
        self.mapping_GZ_ZZ1_TEXT0_TEXT2_TEXT7 = []
        self.mapping_GZ = []
        self.mapping_ZZ0 = []
        self.mapping_COLOR = []
        self.mapping_LINE_PATTERN = []
        self._create_babs_mapping(mapping_file_folder + os.sep + self.MAPPING_FILE)

    def _create_babs_mapping(self, mapping_table):
        book = open_workbook(mapping_table)

        sheet = book.sheet_by_name('COLOR')
        for row in range(sheet.nrows):
            key = sheet.cell(row, 0).value.replace(" ", "")
            value = sheet.cell(row, 1).value
            self.mapping_COLOR.append([key, value])

        sheet = book.sheet_by_name('LINE_PATTERN')
        for row in range(sheet.nrows):
            key = sheet.cell(row, 0).value
            value = sheet.cell(row, 1).value
            self.mapping_LINE_PATTERN.append([key, value])

        sheet = book.sheet_by_name('GZ')
        for row in range(sheet.nrows):
            key = sheet.cell(row, 0).value
            value = sheet.cell(row, 1).value
            self.mapping_GZ.append([key, value])

        sheet = book.sheet_by_name('ZZ0')
        for row in range(sheet.nrows):
            key = sheet.cell(row, 0).value
            value = sheet.cell(row, 1).value
            self.mapping_ZZ0.append([key, value])

        sheet = book.sheet_by_name('GZ-ZZ1-TEXT0-TEXT2-TEXT7')
        for row in range(sheet.nrows):
            key = []
            for idx in range(0, len(self.str_multisymbol_keys)):
                key.append(sheet.cell(row, idx).value)

            value = []
            for idx in range(len(self.str_multisymbol_keys), len(self.str_multisymbol_keys) + len(self.str_mss_keys)):
                value.append(sheet.cell(row, idx).value)

            self.mapping_GZ_ZZ1_TEXT0_TEXT2_TEXT7.append([key, value])

    def map(self, copex_obj):
        """
        Get the mapping for a COPExObject

        @param copex_obj the copex object
        @return a map with "ID" and "Attributes" which defines an MSS symbol or None if no mapping was found
        """

        if not isinstance(copex_obj, MultiSymbolObject):
            return None

        kvm = KeyValueManager(';')
        kvm.set_key_value_string(copex_obj.get_symbol_string())

        lang = kvm.get_value('LANGUAGE').upper()

        if lang == "BABS_P":
            pass

        elif lang == "BABS":
            # try to get the symbol direct from the mapping table
            symbol_from_GZ_to_TEXT7 = {self.MAP_KEY_ID: "***************"}
            key = []
            for k in self.str_multisymbol_keys:
                key.append(kvm.get_value(k))

            mapping_found = False
            for mapping in self.mapping_GZ_ZZ1_TEXT0_TEXT2_TEXT7:
                if mapping[0] == key:
                    mapping_found = True
                    symbol_from_GZ_to_TEXT7[self.MAP_KEY_ID] = mapping[1][0]
                    idx = 1
                    attrs = {}
                    for k in self.str_mss_keys[1:]:
                        if mapping[1][idx] != "":
                            attrs[k] = mapping[1][idx]
                        idx += 1
                    symbol_from_GZ_to_TEXT7[self.MAP_KEY_ATTRIBUTES] = attrs

                    break

            # try to get a symbol id from the basic sign (this is also a friend/foe identification)
            symbol_from_GZ = {self.MAP_KEY_ID: "***************"}
            for mapping_GZ in self.mapping_GZ:
                if mapping_GZ[0] == kvm.get_value('GZ'):
                    symbol_from_GZ[self.MAP_KEY_ID] = mapping_GZ[1]

            # get symbol id for planned/anticipated from line pattern
            symbol_from_LINE_PATTERN = {self.MAP_KEY_ID: "***************"}
            for mapping_LINE_PATTERN in self.mapping_LINE_PATTERN:
                if mapping_LINE_PATTERN[0] == kvm.get_value('LINE_PATTERN'):
                    symbol_from_LINE_PATTERN[self.MAP_KEY_ID] = mapping_LINE_PATTERN[1]

            # get the symbol id for the friend/foe from color
            symbol_from_COLOR = {self.MAP_KEY_ID: "***************"}
            for mapping_COLOR in self.mapping_COLOR:
                if mapping_COLOR[0] == kvm.get_value('COLOR').replace(" ", ""):
                    symbol_from_COLOR[self.MAP_KEY_ID] = mapping_COLOR[1]

            # get the symbol id for the troop size
            symbol_from_ZZ0 = {self.MAP_KEY_ID: "***************"}
            for mapping_ZZ0 in self.mapping_ZZ0:
                if mapping_ZZ0[0] == kvm.get_value('ZZ0'):
                    symbol_from_ZZ0[self.MAP_KEY_ID] = mapping_ZZ0[1]

            ###############################################
            # map text values
            text_value_map = {
                # "TEXT0": "",    # TEXT0	Organisation
                # "TEXT1": "",    # TEXT1	Naehere Kennzeichnung
                "TEXT2": "M",  # TEXT2	Fuehrung
                "TEXT4": "H",  # TEXT4	Nummerierung
                "TEXT5": "G",  # TEXT5	Ortsbezeichnung
                "TEXT7": "H"  # TEXT7	Zusatzangaben
            }

            attrs = {}
            if self.MAP_KEY_ATTRIBUTES in symbol_from_GZ_to_TEXT7:
                attrs = symbol_from_GZ_to_TEXT7[self.MAP_KEY_ATTRIBUTES]

            for key in text_value_map:
                if kvm.get_value(key) is not "":
                    mss_key = text_value_map[key]
                    if mss_key not in attrs:
                        attrs[mss_key] = kvm.get_value(key)

            symbol_from_GZ_to_TEXT7[self.MAP_KEY_ATTRIBUTES] = attrs

            # the different symbol ids will now be merged.
            # the important one is the first, ...
            sym_id = self._merge_id(
                    [
                        symbol_from_GZ_to_TEXT7[self.MAP_KEY_ID],
                        symbol_from_GZ[self.MAP_KEY_ID],
                        symbol_from_COLOR[self.MAP_KEY_ID],
                        symbol_from_ZZ0[self.MAP_KEY_ID],
                        symbol_from_LINE_PATTERN[self.MAP_KEY_ID]
                    ]
            )

            # do we have a valid "Function ID"
            if "*" not in sym_id[4:9]:
                # yes, the a mapping was found
                symbol_from_GZ_to_TEXT7[self.MAP_KEY_ID] = sym_id
                return symbol_from_GZ_to_TEXT7

        return None


class MultiSymbolConverterAXXI(COPExObject2MSSConverter):
    """
    Converts COPExCOPExMultiSymbolObjects with LANGUAGE="AXXI" or LANGUAGE="Armee".
    The mapping mus be defines in a Excel file called AXXI.xlsx.
    """
    MAPPING_FILE = 'AXXI.xlsx'

    def __init__(self, mapping_file_folder='.'):
        COPExObject2MSSConverter.__init__(self)

        self.mapping_file_folder = mapping_file_folder

        # these are the MultiSymbolObject Keys we are necessary for the mapping
        self.str_multisymbol_keys = ["GZ", "ZZ1", "ZZ3", "TEXT0", "TEXT8"]
        self.str_multisymbol_keys_simple = ["ZZ1", "ZZ3", "TEXT0"]
        # these are the MSS Keys from the mapping
        self.str_mss_keys = ["ID", "H", "XE", "XA", "XA1", "XB", "XD", "XH"]
        self.str_mss_keys_simple = ["ID", "XE", "XA", "XA1"]
        # main mapping table for the symbol definition
        self.mapping_GZ_ZZ1_ZZ3_TEXT0_TEXT8 = []
        # simplified mapping table for the symbol definition
        self.mapping_ZZ1_ZZ3_TEXT0 = []
        self.mapping_GZ = []
        self.mapping_ZZ0 = []
        self.mapping_COLOR = []
        self.mapping_LINE_PATTERN = []
        self._create_axxi_mapping(mapping_file_folder + os.sep + self.MAPPING_FILE)

    def _create_axxi_mapping(self, mapping_table):
        book = open_workbook(mapping_table)

        sheet = book.sheet_by_name('COLOR')
        for row in range(sheet.nrows):
            key = sheet.cell(row, 0).value.replace(" ", "")
            value = sheet.cell(row, 1).value
            self.mapping_COLOR.append([key, value])

        sheet = book.sheet_by_name('LINE_PATTERN')
        for row in range(sheet.nrows):
            key = sheet.cell(row, 0).value
            value = sheet.cell(row, 1).value
            self.mapping_LINE_PATTERN.append([key, value])

        sheet = book.sheet_by_name('GZ')
        for row in range(sheet.nrows):
            key = sheet.cell(row, 0).value
            value = sheet.cell(row, 1).value
            self.mapping_GZ.append([key, value])

        sheet = book.sheet_by_name('ZZ0')
        for row in range(sheet.nrows):
            key = sheet.cell(row, 0).value
            value = sheet.cell(row, 1).value
            self.mapping_ZZ0.append([key, value])

        sheet = book.sheet_by_name('GZ-ZZ1-ZZ3-TEXT0-TEXT8')
        for row in range(sheet.nrows):
            key = []
            for idx in range(0, len(self.str_multisymbol_keys)):
                key.append(sheet.cell(row, idx).value)

            value = []
            for idx in range(len(self.str_multisymbol_keys), len(self.str_multisymbol_keys) + len(self.str_mss_keys)):
                value.append(sheet.cell(row, idx).value)

            self.mapping_GZ_ZZ1_ZZ3_TEXT0_TEXT8.append([key, value])

        # room for improvement:
        # - create mapping from ZZ1_ZZ3_TEXT0 only
        # - remove LogFo and StabsFo from ZZ3 amd append manually the MSS attributes
        # - TEXT8 is "Freitext" -> H
        sheet = book.sheet_by_name('GZ-ZZ1-ZZ3-TEXT0-TEXT8')
        for row in range(sheet.nrows):
            key = [
                # 0 - GZ
                sheet.cell(row, 1).value,  # 1 - ZZ1
                sheet.cell(row, 2).value,  # 2 - ZZ3
                sheet.cell(row, 3).value,  # 3 - TEXT0
                # 4 - TEXT8
            ]

            value = [
                sheet.cell(row, 5).value,  # 5 - ID
                # 6 - H
                sheet.cell(row, 7).value,  # 7 - XE
                sheet.cell(row, 8).value,  # 8 - XA
                sheet.cell(row, 9).value,  # 9 - XA1
                # 10- XB
            ]

            self.mapping_ZZ1_ZZ3_TEXT0.append([key, value])

    def map(self, copex_obj):
        """
        Get the mapping for a COPExObject

        @param copex_obj the copex object
        @return a map with "ID" and "Attributes" which defines an MSS symbol or None if no mapping was found
        """

        if not isinstance(copex_obj, MultiSymbolObject):
            return None

        kvm = KeyValueManager(';')
        kvm.set_key_value_string(copex_obj.get_symbol_string())

        lang = kvm.get_value('LANGUAGE').upper()
        if lang in ["AXXI", "ARMEE"]:
            # try to get the symbol direct from the mapping table
            symbol_from_GZ_to_TEXT8 = {self.MAP_KEY_ID: "***************"}
            key = []
            for k in self.str_multisymbol_keys:
                key.append(kvm.get_value(k))

            mapping_found = False
            for mapping in self.mapping_GZ_ZZ1_ZZ3_TEXT0_TEXT8:
                if mapping[0] == key:
                    mapping_found = True
                    symbol_from_GZ_to_TEXT8[self.MAP_KEY_ID] = mapping[1][0]
                    idx = 1
                    attrs = {}
                    for k in self.str_mss_keys[1:]:
                        if mapping[1][idx] != "":
                            attrs[k] = mapping[1][idx]
                        idx += 1
                    symbol_from_GZ_to_TEXT8[self.MAP_KEY_ATTRIBUTES] = attrs

                    break
            if not mapping_found:
                ##############################################
                # try simpler mapping TBD! not working!
                zz3 = kvm.get_value("ZZ3")
                isLogFo = "Log_Fo" in zz3
                isStabsFo = "Stabs_Fo" in zz3
                isLVbFo = "LVb_Fo" in zz3

                key = []
                for k in self.str_multisymbol_keys_simple:
                    if k == "ZZ3":
                        zz3 = zz3.replace("Log_Fo", "").replace("  ", " ").strip()
                        zz3 = zz3.replace("Stabs_Fo", "").replace("  ", " ").strip()
                        zz3 = zz3.replace("LVb_Fo", "").replace("  ", " ").strip()
                        key.append(zz3)
                    else:
                        key.append(kvm.get_value(k))

                for mapping in self.mapping_ZZ1_ZZ3_TEXT0:
                    if mapping[0] == key:
                        symbol_from_GZ_to_TEXT8[self.MAP_KEY_ID] = mapping[1][0]
                        idx = 1
                        attrs = {}
                        for k in self.str_mss_keys_simple[1:]:
                            if mapping[1][idx] != "":
                                attrs[k] = mapping[1][idx]
                            idx += 1

                        xb_attr = ""
                        if isLogFo:
                            xb_attr += "L"
                        if isStabsFo:
                            xb_attr += "S"
                        if isLVbFo:
                            xb_attr += "T"

                        if xb_attr != "":
                            attrs["XB"] = xb_attr

                        symbol_from_GZ_to_TEXT8[self.MAP_KEY_ATTRIBUTES] = attrs

            # try to get a symbol id from the basic sign (this is also a friend/foe identification)
            symbol_from_GZ = {self.MAP_KEY_ID: "***************"}
            for mapping_GZ in self.mapping_GZ:
                if mapping_GZ[0] == kvm.get_value('GZ'):
                    symbol_from_GZ[self.MAP_KEY_ID] = mapping_GZ[1]
                    break

            # get symbol id for planned/anticipated from line pattern
            symbol_from_LINE_PATTERN = {self.MAP_KEY_ID: "***************"}
            for mapping_LINE_PATTERN in self.mapping_LINE_PATTERN:
                if mapping_LINE_PATTERN[0] == kvm.get_value('LINE_PATTERN'):
                    symbol_from_LINE_PATTERN[self.MAP_KEY_ID] = mapping_LINE_PATTERN[1]
                    break

            # get the symbol id for the friend/foe from color
            symbol_from_COLOR = {self.MAP_KEY_ID: "***************"}
            for mapping_COLOR in self.mapping_COLOR:
                if mapping_COLOR[0] == kvm.get_value('COLOR').replace(" ", ""):
                    symbol_from_COLOR[self.MAP_KEY_ID] = mapping_COLOR[1]
                    break

            # get the symbol id for the troop size
            symbol_from_ZZ0 = {self.MAP_KEY_ID: "***************"}
            for mapping_ZZ0 in self.mapping_ZZ0:
                if mapping_ZZ0[0] == kvm.get_value('ZZ0'):
                    symbol_from_ZZ0[self.MAP_KEY_ID] = mapping_ZZ0[1]
                    break

            ###############################################
            # map text values
            text_value_map = {
                "TEXT2": "W",  # TEXT2	Datum/Zeit		        W
                "TEXT5": "T",  # TEXT5	Nr. der Formation		T
                "TEXT6": "F",  # TEXT6	Verst./Vermindert		F
                "TEXT8": "H",  # TEXT8	Freitext		        H  (XF/XE/XB)
                "TEXT9": "M"  # TEXT9	Nr. vorges. Kommando	M
            }

            attrs = {}
            if self.MAP_KEY_ATTRIBUTES in symbol_from_GZ_to_TEXT8:
                attrs = symbol_from_GZ_to_TEXT8[self.MAP_KEY_ATTRIBUTES]

            for key in text_value_map:
                if kvm.get_value(key) is not "":
                    mss_key = text_value_map[key]
                    if mss_key not in attrs:
                        attrs[mss_key] = kvm.get_value(key)

            symbol_from_GZ_to_TEXT8[self.MAP_KEY_ATTRIBUTES] = attrs

            # the different symbol ids will now be merged.
            # the important one is the first, ...
            sym_id = self._merge_id(
                    [
                        symbol_from_GZ_to_TEXT8[self.MAP_KEY_ID],
                        symbol_from_GZ[self.MAP_KEY_ID],
                        symbol_from_COLOR[self.MAP_KEY_ID],
                        symbol_from_ZZ0[self.MAP_KEY_ID],
                        symbol_from_LINE_PATTERN[self.MAP_KEY_ID]
                    ]
            )

            # do we have a valid "Function ID"
            if "*" not in sym_id[4:9]:
                # yes, the a mapping was found
                symbol_from_GZ_to_TEXT8[self.MAP_KEY_ID] = sym_id
                return symbol_from_GZ_to_TEXT8

        return None


class MultiSymbolConverterZDV(COPExObject2MSSConverter):
    """
    Converts COPExCOPExMultiSymbolObjects with LANGUAGE="ZDV1/11".
    """

    def __init__(self, mapping_file_folder='.'):
        COPExObject2MSSConverter.__init__(self)

        # these are the MultiSymbolObject Keys we are necessary for the mapping
        self.str_multisymbol_keys = ["GZ", "ZZ0", "ZZ1", "ZZ2", "ZZ3", "TEXT0", "TEXT8"]
        # these are the MSS Keys from the mapping
        self.str_mss_keys = ["ID", "H", "XE", "XA", "XA1", "XB", "XD", "XH"]
        # main mapping table for the symbol definition
        self.mapping_GZ_ZZ1_ZZ3_TEXT0_TEXT8 = [
            # ["GZ", "ZZ0", "ZZ1", "ZZ2", "ZZ3", "TEXT0", "TEXT8"], ["ID", "H", "XE", "XA", "XA1", "XB", "XD", "XH"]
            [['Sperre', '', '', '', '', '', 'x'], ['G*G*GPPO--*****', '', '', '', '', '', '', '']],
        ]
        self.mapping_COLOR = [
            ['0,0,255', '*F*************'],
            ['0,0,0', '*F*************'],
            ['255,0,0', '*H*************'],
            ['0,255,0', '*N*************'],
            ['255,255,0', '*U*************'],
            ['0,255,255', '***************'],
            ['0,136,0', '*N*************'],
            ['255,128,0', '*U*************']
        ]
        self.mapping_LINE_PATTERN = [
            ['SOLID', '***P***********'],
            ['DASH', '***A***********'],
            ['DOT', '***A***********'],
            ['DASHDOT', '***A***********']
        ]

    def map(self, copex_obj):
        """
        Get the mapping for a COPExObject

        @param copex_obj the copex object
        @return a map with "ID" and "Attributes" which defines an MSS symbol or None if no mapping was found
        """

        if not isinstance(copex_obj, MultiSymbolObject):
            return None

        kvm = KeyValueManager(';')
        kvm.set_key_value_string(copex_obj.get_symbol_string())

        lang = kvm.get_value('LANGUAGE').upper()
        if lang in ["ZDV1/11"]:
            # try to get the symbol direct from the mapping table
            symbol_from_GZ_to_TEXT8 = {self.MAP_KEY_ID: "***************"}
            key = []
            for k in self.str_multisymbol_keys:
                key.append(kvm.get_value(k))

            for mapping in self.mapping_GZ_ZZ1_ZZ3_TEXT0_TEXT8:
                if mapping[0] == key:
                    symbol_from_GZ_to_TEXT8[self.MAP_KEY_ID] = mapping[1][0]
                    idx = 1
                    attrs = {}
                    for k in self.str_mss_keys[1:]:
                        if mapping[1][idx] != "":
                            attrs[k] = mapping[1][idx]
                        idx += 1
                    symbol_from_GZ_to_TEXT8[self.MAP_KEY_ATTRIBUTES] = attrs

                    break

            # get symbol id for planned/anticipated from line pattern
            symbol_from_LINE_PATTERN = {self.MAP_KEY_ID: "***************"}
            for mapping_LINE_PATTERN in self.mapping_LINE_PATTERN:
                if mapping_LINE_PATTERN[0] == kvm.get_value('LINE_PATTERN'):
                    symbol_from_LINE_PATTERN[self.MAP_KEY_ID] = mapping_LINE_PATTERN[1]
                    break

            # get the symbol id for the friend/foe from color
            symbol_from_COLOR = {self.MAP_KEY_ID: "***************"}
            for mapping_COLOR in self.mapping_COLOR:
                if mapping_COLOR[0] == kvm.get_value('COLOR').replace(" ", ""):
                    symbol_from_COLOR[self.MAP_KEY_ID] = mapping_COLOR[1]
                    break

            # the different symbol ids will now be merged.
            # the important one is the first, ...
            sym_id = self._merge_id(
                    [
                        symbol_from_GZ_to_TEXT8[self.MAP_KEY_ID],
                        symbol_from_COLOR[self.MAP_KEY_ID],
                        symbol_from_LINE_PATTERN[self.MAP_KEY_ID]
                    ]
            )

            # do we have a valid "Function ID"
            if "*" not in sym_id[4:9]:
                # yes, the a mapping was found
                symbol_from_GZ_to_TEXT8[self.MAP_KEY_ID] = sym_id
                return symbol_from_GZ_to_TEXT8

        return None


class MultiSymbolConverter(COPExObject2MSSConverter):
    def __init__(self, mapping_file_folder='.'):
        COPExObject2MSSConverter.__init__(self)

        self.multi_symbol_converters = [
            MultiSymbolConverterBABS(mapping_file_folder),
            MultiSymbolConverterAXXI(mapping_file_folder),
            MultiSymbolConverterZDV(mapping_file_folder)
        ]

    def map(self, copex_obj):
        """
        Get the mapping for a COPExObject

        @param copex_obj the copex object
        @return a map with "ID" and "Attributes" which defines an MSS symbol or None if no mapping was found
        """

        for converter in self.multi_symbol_converters:
            mapping = converter.map(copex_obj)

            if mapping is not None:
                return mapping

        return None
