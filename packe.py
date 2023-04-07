import struct
from io import BytesIO

PROTOCOL_VERSION = 860

class Packet(BytesIO):
    def add_byte(self, byte):
        self.write(struct.pack("B", byte))

    def add_ushort(self, ushort):
        self.write(struct.pack("H", ushort))

    def add_uint(self, uint):
        self.write(struct.pack("I", uint))

    def add_string(self, string):
        self.add_ushort(len(string))
        self.write(string.encode("latin-1"))

    def get_byte(self):
        return struct.unpack("B", self.read(1))[0]

    def get_ushort(self):
        return struct.unpack("H", self.read(2))[0]

    def get_uint(self):
        return struct.unpack("I", self.read(4))[0]

    def get_string(self):
        length = self.get_ushort()
        return self.read(length).decode("latin-1")

    def send(self, socket):
        data = self.getvalue()
        size = len(data) + 4
        socket.send(struct.pack("I", size) + data)
