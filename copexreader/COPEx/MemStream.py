import struct


class MemStream(object):
    """
    Helper class to read attributes from serialized data.
    """
    def __init__(self, data):
        self.data = data
        self.idx_data = 0

    def read_dword(self):
        # unsigned Long, 4 bytes
        dw, = struct.unpack_from('L', self.data, self.idx_data)
        self.idx_data += 4

        return dw

    def read_string(self):
        # unsigned int (size_t)
        size, = struct.unpack_from('I', self.data, self.idx_data)
        self.idx_data += 4

        a = self.data[self.idx_data:self.idx_data + size]
        self.idx_data += size

        a.append(0)

        return a

    def read_double(self):
        dbl, = struct.unpack_from('d', self.data, self.idx_data)
        self.idx_data += 8

        return dbl

    def read_bytes(self):
        size = self.read_dword()
        byte_data = self.data[self.idx_data:self.idx_data + size]
        self.idx_data += size

        return byte_data

    def read_coordinate(self):
        lat = self.read_double()
        lng = self.read_double()
        hgt = self.read_double()

        return lat, lng, hgt
