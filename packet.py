import struct

#considere as fontes abaixo:
#1.https://github.com/cymruu/python-tibia/blob/master/packet.py
#2.https://github.com/cymruu/python-tibia/blob/master/bot.py
#3.https://github.com/mehah/otclient/blob/7e8dd15eb435a26f4dc3510af22ff5b7e68ece45/src/client/protocolcodes.h
#4.https://github.com/avelino/Otxserver-New/blob/faf56b1d268a44d4586ba52bc330ab158fe1500e/src/protocolgamebase.cpp
#5.https://github.com/mehah/otclient/blob/7e8dd15eb435a26f4dc3510af22ff5b7e68ece45/src/client/protocolgameparse.cpp
#6.https://github.com/mehah/otclient/blob/5ff15df7107a650e9106d1e473c347e5639be360/src/client/game.cpp
#7.https://github.com/mehah/otclient/tree/main/src/client
#8.https://github.com/avelino/Otxserver-New/tree/master/src
#9.https://github.com/mehah/otclient
#10.https://github.com/OTCv8/otcv8-dev
#11.https://github.com/avelino/Otxserver-New
# 
# Essa classe é responsável por receber os pacotes do servidor

class ProtocolGameReceive:
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

    def read_ipv4(self):
        ipv4_bytes = struct.unpack_from("<4B", self.data, self.pos)
        self.pos += 4
        return ".".join(map(str, ipv4_bytes))

    def read_ushort(self):
        result = struct.unpack_from("<H", self.data, self.pos)[0]
        self.pos += 2
        return result

    def read_uint(self):
        result = struct.unpack_from("<I", self.data, self.pos)[0]
        self.pos += 4
        return result

    def read_ulong(self):
        result = struct.unpack_from("<Q", self.data, self.pos)[0]
        self.pos += 8
        return result
    
    def read_position(self):
        x = self.read_ushort()
        y = self.read_ushort()
        z = self.read_byte()
        return x, y, z
    
    def read_item(self):
        item_id = self.read_ushort()
        count = self.read_byte()
        return item_id, count
    
    def read_item_list(self):
        items = []
        for _ in range(self.read_byte()):
            items.append(self.read_item())
        return items
    
    def skip_bytes(self, count):
        self.pos += count

    def get_remaining_bytes(self):
        return self.data[self.pos:]
    
    def get_remaining_bytes_count(self):
        return len(self.data) - self.pos
    
    def get_remaining_bytes_as_string(self):
        return self.data[self.pos:].decode("utf-8")
    
    def get_remaining_bytes_as_string_list(self):
        return self.data[self.pos:].decode("utf-8").split("\n")
    
    def get_remaining_bytes_as_string_list_without_empty_lines(self):
        return [line for line in self.data[self.pos:].decode("utf-8").split("\n") if line != ""]
    
# Essa classe é responsável por enviar os pacotes para o servidor


class ProtocolGameSend:
    def __init__(self):
        self.data = bytearray()

    def write_byte(self, value):
        self.data.extend(struct.pack("<B", value))

    def write_string(self, value):
        encoded_value = value.encode("utf-8")
        self.write_byte(len(encoded_value))
        self.data.extend(encoded_value)

    def write_ushort(self, value):
        self.data.extend(struct.pack("<H", value))

    def write_uint(self, value):
        self.data.extend(struct.pack("<I", value))

    def write_ulong(self, value):
        self.data.extend(struct.pack("<Q", value))
        
    def write_position(self, x, y, z):
        self.write_ushort(x)
        self.write_ushort(y)
        self.write_byte(z)

    def write_item(self, item_id, count):
        self.write_ushort(item_id)
        self.write_byte(count)

    def write_item_list(self, items):
        self.write_byte(len(items))
        for item in items:
            self.write_item(item[0], item[1])
    
    def write_bytes(self, bytes):
        self.data.extend(bytes)

    def get_data(self):
        return self.data
    
    def get_data_as_string(self):
        return self.data.decode("utf-8")
    
    def get_data_as_string_list(self):
        return self.data.decode("utf-8").split("\n")
    
    def get_data_as_string_list_without_empty_lines(self):
        return [line for line in self.data.decode("utf-8").split("\n") if line != ""]

