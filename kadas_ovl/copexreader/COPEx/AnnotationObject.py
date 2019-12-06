from .COPExObject import *
from .MemStream import *
from .CoordLL84 import *


class AnnotationObject(COPExObject):
    CLSID = "{C9184146-7335-4D0B-B7F8-8E6294267E4D}"

    def __init__(self):
        COPExObject.__init__(self)

    def read_object(self, byte_data):
        ms = MemStream(byte_data)
        # read version
        version = ms.read_dword()
        if version == 0x0100:
            # strings are UTF8 coded
            self.symbol_string = ms.read_string().decode('UTF-8')

            self.coords = []
            lat, lng, hgt = ms.read_coordinate()
            self.coords.append(CoordLL84(lat, lng, hgt))

            self.display_name = ms.read_string().decode('UTF-8')

    def __str__(self):
        return "Symbolstring: " + self.get_symbol_string()
