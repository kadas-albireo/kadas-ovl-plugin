from COPExObject import *
from MemStream import *
from CoordLL84 import *


class MSSObject(COPExObject):
    CLSID = "{AE42E103-74BD-44E2-A15A-BD4F40362167}"

    def __init__(self):
        COPExObject.__init__(self)

    def read_object(self, byte_data):
        ms = MemStream(byte_data)
        # read version
        version = ms.read_dword()
        if version == 0x0200:
            # strings are UTF8 coded
            self.symbol_string = ms.read_string().decode('UTF-8')
            lat, lng, hgt = ms.read_coordinate()
            self.coords = []
            self.coords.append(CoordLL84(lat, lng, hgt))
            self.display_name = ms.read_string().decode('UTF-8')
        elif version == 0x0100:
            # strings are ASCII coded
            self.symbol_string = ms.read_string()
            lat, lng, hgt = ms.read_coordinate()
            self.coords = []
            self.coords.append(CoordLL84(lat, lng, hgt))
            self.display_name = ms.read_string()

    def __str__(self):
        return "Symbolstring: " + self.get_symbol_string()

