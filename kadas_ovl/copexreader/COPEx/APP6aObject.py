from .COPExObject import *
from .MemStream import *
from .CoordLL84 import *


class APP6aObject(COPExObject):
    """
    COPEx APP6aObject
    """

    CLSID = "{E8032F4A-A3B2-446A-B71F-6B3D43DDF5E5}"

    def __init__(self):
        COPExObject.__init__(self)

    def read_object(self, byte_data):
        """
        Reads serialized APP6aObject data.

        @param byte_data    [in] array of serialized bytes
        """

        ms = MemStream(byte_data)
        # read version
        version = ms.read_dword()
        if version == 0x0200:
            # strings are UTF8 coded
            self.symbol_string = ms.read_string().decode('UTF-8')
            coord_count = ms.read_dword()

            self.coords = []
            for i in range(0, coord_count):
                lat, lng, hgt = ms.read_coordinate()
                self.coords.append(CoordLL84(lat, lng, hgt))

            self.display_name = ms.read_string().decode('UTF-8')
        elif version == 0x0100:
            # strings are ASCII coded
            self.symbol_string = ms.read_string()
            coord_count = ms.read_dword()

            self.coords = []
            for _ in range(0, coord_count):
                lat, lng, hgt = ms.read_coordinate()
                self.coords.append(CoordLL84(lat, lng, hgt))

            self.display_name = ms.read_string()

    def __str__(self):
        return "Symbolstring: " + self.get_symbol_string()
