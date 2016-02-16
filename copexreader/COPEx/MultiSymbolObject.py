from COPExObject import *
from MemStream import *
from CoordLL84 import *
from KeyValueManager import *


class MultiSymbolObject(COPExObject):
    CLSID = "{C1FD308D-CE83-4294-855C-2613F97CC7B4}"

    def __init__(self):
        COPExObject.__init__(self)

    def read_object(self, byte_data):
        ms = MemStream(byte_data)
        # read version
        version = ms.read_dword()
        if version == 0x0200:
            # strings are UTF8 coded

            # cgm data can be ignored (read, but do not use)
            ms.read_bytes()

            lat, lng, hgt = ms.read_coordinate()
            self.coords = []
            self.coords.append(CoordLL84(lat, lng, hgt))

            self.symbol_string = ms.read_string().decode('UTF-8')
            self.display_name = ms.read_string().decode('UTF-8')
        elif version == 0x0100:
            # strings are ASCII coded

            # cgm data can be ignored (read, but do not use)
            ms.read_bytes()

            lat, lng, hgt = ms.read_coordinate()
            self.coords = []
            self.coords.append(CoordLL84(lat, lng, hgt))

            self.symbol_string = ms.read_string()
            self.display_name = ms.read_string()

    def __str__(self):
        str_ret = ""

        kvm = KeyValueManager(';')
        kvm.set_key_value_string(self.get_symbol_string())

        keys = ["LANGUAGE", "GZ", "ZZ0", "ZZ1", "ZZ2", "ZZ3"]
        for key in keys:
            str_ret += key + ": " + kvm.get_value(key) + "\n"

        return str_ret
