import struct

class Packet:
    def __init__(self, data):
        self.data = data

    def get_data(self):
        return self.data

    def add_uint8(self, value):
        self.data += struct.pack('<B', value)

    def add_uint16(self, value):
        self.data += struct.pack('<H', value)

    def add_uint32(self, value):
        self.data += struct.pack('<I', value)

    def add_string(self, value):
        self.add_uint16(len(value))
        self.data += value.encode()

    def get_uint8(self):
        value = struct.unpack('<B', self.data[:1])[0]
        self.data = self.data[1:]
        return value

    def get_uint16(self):
        value = struct.unpack('<H', self.data[:2])[0]
        self.data = self.data[2:]
        return value

    def get_uint32(self):
        value = struct.unpack('<I', self.data[:4])[0]
        self.data = self.data[4:]
        return value

    def get_string(self):
        length = self.get_uint16()
        value = self.data[:length].decode()
        self.data = self.data[length:]
        return value
