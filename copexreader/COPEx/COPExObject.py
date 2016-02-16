class COPExObject(object):
    """
    Base class for all COPEx objects.
    """
    def __init__(self):
        self.symbol_string = ""
        self.display_name = ""
        self.coords = []

    def get_symbol_string(self):
        return self.symbol_string

    def get_display_name(self):
        return self.display_name

    def get_coords(self):
        return self.coords

    def read_object(self, byte_data):
        pass
