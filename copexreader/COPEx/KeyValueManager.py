

class KeyValueManager(object):
    """
    Class to parse and compose COPEx Symbolstrings

    kvm = KeyValueManager(";")
    kvm.set_key_value_string(key_value_string)
    value = kvm.get_value("key"

    """
    def __init__(self, delimiter=';'):
        """
        Constructs a KeyValueManager with the given delimiter as separator
        """
        self.__delimiter = delimiter
        self.__key_value_map = {}

    def encode(self, key_value_string):

        kvs = key_value_string
        kvs = kvs.replace("\\", "\\\\")
        kvs = kvs.replace("\"", "\\\"")
        kvs = kvs.replace(self.__delimiter, "\\" + self.__delimiter)

        return kvs

    def decode(self, key_value_string):

        kvs = key_value_string
        kvs = kvs.replace("\\\\", "\\")
        kvs = kvs.replace("\\\"", "\"")
        kvs = kvs.replace("\\" + self.__delimiter, self.__delimiter)

        return kvs

    def decompose(self, key_value_string):

        KVM_STATE_ENTRY = 0
        KVM_STATE_IN_KEY = 1
        KVM_STATE_IN_VALUE = 2
        KVM_STATE_IN_VALUE_QUOTE = 3
        KVM_STATE_IN_VALUE_QUOTE_ESCAPE = 4
        KVM_STATE_OK = 5

        state = KVM_STATE_IN_KEY
        key = ""
        value = ""

        if not key_value_string.endswith(self.__delimiter):
            key_value_string += self.__delimiter

        for current_char in key_value_string:

            if state == KVM_STATE_IN_KEY:

                if current_char == self.__delimiter:
                    # clear
                    key = ""
                    value = ""

                elif current_char == '=':
                    state = KVM_STATE_IN_VALUE

                else:
                    key += current_char

            elif state == KVM_STATE_IN_VALUE:

                if current_char == self.__delimiter:
                    state = KVM_STATE_OK
                elif current_char == '\"':
                    state = KVM_STATE_IN_VALUE_QUOTE
                else:
                    value += current_char

            elif state == KVM_STATE_IN_VALUE_QUOTE:

                if current_char == '\\':
                    state = KVM_STATE_IN_VALUE_QUOTE_ESCAPE
                elif current_char == '\"':
                    state = KVM_STATE_IN_VALUE
                else:
                    value += current_char

            elif state == KVM_STATE_IN_VALUE_QUOTE_ESCAPE:
                value += current_char

                if current_char == '\\':
                    state = KVM_STATE_IN_VALUE_QUOTE_ESCAPE
                else:
                    state = KVM_STATE_IN_VALUE_QUOTE

            if state == KVM_STATE_OK:
                if len(key) > 0 and len(value) > 0:
                    self.insert(key, value)

                state = KVM_STATE_IN_KEY
                key = ""
                value = ""

        return len(self.__key_value_map)

    def insert(self, key, value):

        self.__key_value_map[key] = value

    def set_delimiter(self, delimiter):
        self.__delimiter = delimiter

    def get_delimiter(self):
        return self.__delimiter

    def set_key_value_string(self, key_value_string):
        self.__key_value_map.clear()

        self.decompose(key_value_string)

    def get_key_value_string(self):

        kvs = ""
        for key in self.__key_value_map:
            value = self.__key_value_map[key]

            kvs += key + "=\"" + self.encode(value) + "\"" + self.__delimiter

        return kvs

    def set_value(self, key, value):

        self.insert(key, value)

    def get_value(self, key):
        if key in self.__key_value_map:
            return self.__key_value_map[key]

        return ""

    def remove_key(self, key):

        if key in self.__key_value_map:
            self.__key_value_map.pop(key, "")

    def exist_key(self, key):

        return key in self.__key_value_map

    def set_empty(self):

        self.__key_value_map.clear()

    def get_keys(self):

        return self.__key_value_map.keys()
