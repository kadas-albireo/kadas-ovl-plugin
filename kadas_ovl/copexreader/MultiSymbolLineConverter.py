import os
from kadas_ovl.copexreader.xlrd import open_workbook
from kadas_ovl.copexreader.COPEx import *
from COPExObject2MSSConverter import COPExObject2MSSConverter


class MultiSymbolLineConverter(COPExObject2MSSConverter):
    """
    Converts COPExCOPExMultiSymbolObjects with LANGUAGE="AXXI" or LANGUAGE="Armee".
    The mapping mus be defines in a Excel file called AXXI.xlsx.
    """
    MAPPING_FILE = 'MultiSymbolLineObject.xlsx'

    def __init__(self, mapping_file_folder='.'):
        COPExObject2MSSConverter.__init__(self)

        self.mapping_COLOR = []
        self.mapping_LINE_PATTERN = []
        self.mapping_GRO = []
        self.mapping_BASISTYP_LINIENOBJ = []
        self._create_mapping(mapping_file_folder + os.sep + self.MAPPING_FILE)

    def _get_safe_string(self, string):
        """
        Returns always a string with no spaces
        """
        if type(string) is float:
            string = str(int(string))

        if string is not None:
            return str(string).replace(" ", "")

        return ""

    def _create_mapping(self, mapping_table):
        """
        reads the mapping table and prepares the internal data.
        """

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

        sheet = book.sheet_by_name('GRO')
        for row in range(sheet.nrows):
            key = sheet.cell(row, 0).value
            value = sheet.cell(row, 1).value
            self.mapping_GRO.append([key, value])

        sheet = book.sheet_by_name('BASISTYP-LINIENOBJ')
        for row in range(sheet.nrows):
            key = [
                self._get_safe_string(sheet.cell(row, 0).value),   # 0 LINIENART-BASISTYP
                self._get_safe_string(sheet.cell(row, 1).value),   # 1 LINIENOBJ(0)-KOMPONENTENNAME
                self._get_safe_string(sheet.cell(row, 2).value),   # 2 LINIENOBJ(0)-OBJEKTTYP
                self._get_safe_string(sheet.cell(row, 3).value).replace(' ', '').replace(';', ''),   # 3 LINIENOBJ(0)-OBJEKTINHALT
                self._get_safe_string(sheet.cell(row, 4).value),   # 4 LINIENOBJ(0)-OBJECTID
                self._get_safe_string(sheet.cell(row, 5).value),   # 5 LINIENOBJ(1)-KOMPONENTENNAME
                self._get_safe_string(sheet.cell(row, 6).value),   # 6 LINIENOBJ(1)-OBJEKTTYP
                self._get_safe_string(sheet.cell(row, 7).value).replace(' ', '').replace(';', ''),   # 7 LINIENOBJ(1)-OBJEKTINHALT
                self._get_safe_string(sheet.cell(row, 8).value)    # 8 LINIENOBJ(1)-OBJECTID
            ]

            value = [
                sheet.cell(row, 9).value,   # 9  ID
                sheet.cell(row, 10).value   # 10 XE
            ]

            # ensure a mapping exist
            if len(value[0]) == 15:
                self.mapping_BASISTYP_LINIENOBJ.append([key, value])

    def map(self, copex_obj):
        """
        Get the mapping for a COPExObject

        @param copex_obj the copex object
        @return a map with "ID" and "Attributes" which defines an MSS symbol or None if no mapping was found
        """

        if not isinstance(copex_obj, MultiSymbolLineObject):
            return None

        kvm = KeyValueManager(';')
        kvm.set_key_value_string(copex_obj.get_symbol_string())
        kvm_la = KeyValueManager(';')
        kvm_la.set_key_value_string(kvm.get_value('LINIENART'))

        kvm_lineobjs = []
        idx = 0
        while kvm.get_value("LINIENOBJ" + str(idx)) != "":
            kvm_lo = KeyValueManager(";")
            kvm_lo.set_key_value_string(kvm.get_value("LINIENOBJ" + str(idx)))
            kvm_lineobjs.append(kvm_lo)
            idx += 1

        sym_id = "***************"
        attrs = {}
        # first handle special objects
        klassen_name = kvm_la.get_value("KLASSENNAME")
        if klassen_name == "$Text":
            # Text object
            txt = ""
            for kvm_lo in kvm_lineobjs:
                if kvm_lo.get_value("OBJEKTTYP") == "TXT":
                    txt = kvm_lo.get_value("OBJEKTINHALT")
                    break

            if txt == "AL":
                sym_id = "G*G*OLT-----***"

            elif txt == "RIPL":
                sym_id = "G*G*GL---------"
                attrs["XE"] = "9SCHTLFR-------"

        elif klassen_name == "$Grenze":
            # Grenze / Boundary
            # RIGHT_NEIGHBOUR	TXT	RE Trt	RE Tgt	LEFT_NEIGHBOUR	TXT	LI Trt	LI Tgt	ECHELON	TXT	XX
            # get the symbol id for the troop size
            sym_id = "G*G*GLB---*****"
            for kvm_lo in kvm_lineobjs:
                if kvm_lo.get_value("KOMPONENTENNAME") == "RIGHT_NEIGHBOUR":
                    attrs["T"] = kvm_lo.get_value("OBJEKTINHALT")

                elif kvm_lo.get_value("KOMPONENTENNAME") == "LEFT_NEIGHBOUR":
                    attrs["T1"] = kvm_lo.get_value("OBJEKTINHALT")

                elif kvm_lo.get_value("KOMPONENTENNAME") == "ECHELON":
                    # set echelon in symid
                    symbol_from_GRO = "***************"
                    echelon = kvm_lo.get_value("OBJEKTINHALT")
                    for mapping_GRO in self.mapping_GRO:
                        if mapping_GRO[0] == echelon:
                            symbol_from_GRO = mapping_GRO[1]
                            break

                    sym_id = self._merge_id(
                        [
                            sym_id,
                            symbol_from_GRO
                        ]
                    )

        else:
            # use mapping table to map BASISTTYP and LO0 and LO2 to SYMID
            kvm_lo0 = KeyValueManager(";")
            kvm_lo0.set_key_value_string(kvm.get_value("LINIENOBJ0"))
            kvm_lo1 = KeyValueManager(";")
            kvm_lo1.set_key_value_string(kvm.get_value("LINIENOBJ1"))
            key = [
                kvm_la.get_value("BASISTYP").replace(" ", ""),
                kvm_lo0.get_value("KOMPONENTENNAME").replace(" ", ""),
                kvm_lo0.get_value("OBJEKTTYP").replace(" ", ""),
                kvm_lo0.get_value("OBJEKTINHALT").replace(" ", "").replace(';', ''),
                kvm_lo0.get_value("OBJECTID").replace(" ", ""),
                kvm_lo1.get_value("KOMPONENTENNAME").replace(" ", ""),
                kvm_lo1.get_value("OBJEKTTYP").replace(" ", ""),
                kvm_lo1.get_value("OBJEKTINHALT").replace(" ", "").replace(';', ''),
                kvm_lo1.get_value("OBJECTID").replace(" ", "")
            ]

            mapping_found = False
            for mapping in self.mapping_BASISTYP_LINIENOBJ:
                if mapping[0] == key:
                    sym_id = mapping[1][0]
                    if mapping[1][1] != "":
                        attrs["XE"] = mapping[1][1]
                    mapping_found = True
                    break

            if not mapping_found:
                # try a simpler mapping - map only the "BASISTYP"
                key = [
                    kvm_la.get_value("BASISTYP").replace(" ", ""),
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    ''
                ]
                for mapping in self.mapping_BASISTYP_LINIENOBJ:
                    if mapping[0] == key:
                        sym_id = mapping[1][0]
                        if mapping[1][1] != "":
                            attrs["XE"] = mapping[1][1]
                        mapping_found = True
                        break

        # get symbol id for planned/anticipated from line pattern
        symbol_from_LINE_PATTERN = {self.MAP_KEY_ID: "***************"}
        for mapping_LINE_PATTERN in self.mapping_LINE_PATTERN:
            if mapping_LINE_PATTERN[0] == kvm_la.get_value('LINE_PATTERN'):
                symbol_from_LINE_PATTERN[self.MAP_KEY_ID] = mapping_LINE_PATTERN[1]
                break

        # get the symbol id for the friend/foe from color
        symbol_from_COLOR = {self.MAP_KEY_ID: "***************"}
        for mapping_COLOR in self.mapping_COLOR:
            color = kvm_la.get_value('COLOR').replace(" ", "")
            if mapping_COLOR[0] == color:
                symbol_from_COLOR[self.MAP_KEY_ID] = mapping_COLOR[1]
                break

        # the different symbol ids will now be merged.
        # the important on is the first, ...
        sym_id = self._merge_id(
            [
                sym_id,
                symbol_from_COLOR[self.MAP_KEY_ID],
                symbol_from_LINE_PATTERN[self.MAP_KEY_ID]
            ]
        )

        if "*" not in sym_id[4:9]:
            symbol_MSS = {
                self.MAP_KEY_ID: sym_id
            }

            if len(attrs) > 0:
                symbol_MSS[self.MAP_KEY_ATTRIBUTES] = attrs

            return symbol_MSS

        return None
