import struct

class TibiaPacketReader:
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def read_byte(self):
        result = struct.unpack_from("<B", self.data, self.pos)[0]
        self.pos += 1
        return result

    def read_string(self):
        length = self.read_byte()
        result = self.data[self.pos:self.pos + length].decode("utf-8")
        self.pos += length
        return result


class TibiaPacketWriter:
    def __init__(self):
        self.data = bytearray()

    def write_byte(self, value):
        self.data.extend(struct.pack("<B", value))

    def write_string(self, value):
        encoded_value = value.encode("utf-8")
        self.write_byte(len(encoded_value))
        self.data.extend(encoded_value)

    def get_data(self):
        return self.data
