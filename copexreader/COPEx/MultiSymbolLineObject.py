from COPExObject import *
from MemStream import *
from CoordLL84 import *
from KeyValueManager import *


class MultiSymbolLineObject(COPExObject):
    CLSID = "{D2B5BBF4-E847-4726-B60A-F3DCB1500F5B}"

    def __init__(self):
        COPExObject.__init__(self)
        self.kvm = KeyValueManager(';')

    def read_object(self, byte_data):
        ms = MemStream(byte_data)
        # read version
        version = ms.read_dword()
        if version == 0x0200:
            # strings are UTF8 coded
            coord_count = ms.read_dword()

            self.coords = []
            for i in range(0, coord_count):
                lat, lng, hgt = ms.read_coordinate()
                self.coords.append(CoordLL84(lat, lng, hgt))

            self.display_name = ms.read_string().decode('UTF-8')
            self.symbol_string = ms.read_string().decode('UTF-8')
        elif version == 0x0100:
            # strings are ASCII coded
            coord_count = ms.read_dword()

            self.coords = []
            for i in range(0, coord_count):
                lat, lng, hgt = ms.read_coordinate()
                self.coords.append(CoordLL84(lat, lng, hgt))

            self.display_name = ms.read_string()
            self.symbol_string = ms.read_string()

        self.kvm.set_key_value_string(self.symbol_string)

    def get_klassen_name(self):
        kvm_la = KeyValueManager(';')
        kvm_la.set_key_value_string(self.kvm.get_value('LINIENART'))

        return kvm_la.get_value('KLASSENNAME')

    def get_klassen_art_name(self):
        kvm_la = KeyValueManager(';')
        kvm_la.set_key_value_string(self.kvm.get_value('LINIENART'))

        return kvm_la.get_value('KLASSENART')

    def get_basis_typ(self):
        kvm_la = KeyValueManager(';')
        kvm_la.set_key_value_string(self.kvm.get_value('LINIENART'))

        return kvm_la.get_value('BASISTYP')

    def get_basis_form(self):
        kvm_la = KeyValueManager(';')
        kvm_la.set_key_value_string(self.kvm.get_value('LINIENART'))

        return kvm_la.get_value('BASISFORM')

    def __str__(self):
        str_ret = ""

        la_keys = ["BASISTYP", "BASISFORM"]
        kvm_line_art = KeyValueManager(';')
        kvm_line_art.set_key_value_string(self.kvm.get_value('LINIENART'))
        for key in la_keys:
            str_ret += "LINIENART " + key + ": " + kvm_line_art.get_value(key) + "\n"

        lo_idx = 0
        lo_keys = ["OBJEKTTYP", "OBJEKTINHALT"]
        while True:
            lo_str = 'LINIENOBJ' + str(lo_idx)

            if self.kvm.get_value(lo_str) == "":
                break

            kvm_line_obj = KeyValueManager(';')
            kvm_line_obj.set_key_value_string(self.kvm.get_value(lo_str))

            for key in lo_keys:
                str_ret += lo_str + " " + key + ": " + kvm_line_obj.get_value(key) + "\n"

            lo_idx += 1

        return str_ret
