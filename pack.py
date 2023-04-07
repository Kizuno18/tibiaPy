import random
import socket
import struct
import zlib

OT_RSA = 109120132967399429278860960508995541528237502902798129123468757937266291492576446330739696001110603907230888610072655818825358503429057592827629436413108566029093628212635953836686562675849720620786279431090218017681061521755056710823876476444260558147179707119674283982419152118103759076030616683978566631413
headerSize = 6

class TibiaPacket(object):
    def __init__(self, packetBytes=bytearray()):
        self.header = packetBytes[:headerSize]
        self.packet = packetBytes[headerSize:]
        self.position = 0
        self.encryptionPos = 0

    def writeHeader(self):
        self.header = struct.pack('=HI', len(self.packet) + 4, zlib.adler32(self.packet)) + self.packet

    def readHeader(self):
        packetSize, adler32Checksum = struct.unpack('=HI', self.header)
        self.packetSize = packetSize
        self.adler32 = adler32Checksum
        return {'packetSize': packetSize, 'adler32Checksum': adler32Checksum}

    def xtea_decrypt_block(self, block):
        v0, v1 = struct.unpack('=2I', block)
        k = struct.unpack('=4I', xtea_key)
        delta, mask, rounds = 0x9E3779B9, 0xFFFFFFFF, 32
        sum = (delta * rounds) & mask
        for round in range(rounds):
            v1 = (v1 - (((v0 << 4 ^ v0 >> 5) + v0) ^ (sum + k[sum >> 11 & 3]))) & mask
            sum = (sum - delta) & mask
            v0 = (v0 - (((v1 << 4 ^ v1 >> 5) + v1) ^ (sum + k[sum & 3]))) & mask
        return struct.pack('=2I', v0, v1)

    def xtea_decrypt(self):
        self.packet = b''.join(self.xtea_decrypt_block(self.packet[i:i + 8]) for i in range(0, len(self.packet), 8))

    def trim_size(self):
        self.packet = self.packet[2:2+self.packetSize]

    def setEncryptionPos(self):
        self.encryptionPos = len(self.packet)

    def rsa_encrypt(self):
        m = sum(x*pow(256, i) for i, x in enumerate(reversed(self.packet[self.encryptionPos:])))
        c = pow(m, 65537, OT_RSA)
        self.packet[self.encryptionPos:] = bytearray((c >> i) & 255 for i in reversed(range(0, 1024, 8)))
        self.encryptionPos = 0

    def fillBytes(self):
        self.packet += bytearray(random.randint(0,255) for i in range(len(self.packet)-self.encryptionPos, 128))

    def writeU8(self, n):
        self.packet+=struct.pack('=B', n)

    def writeU16(self, n):
        self.packet+=struct.pack('=H', n)

    def writeU32(self, n):
        self.packet+=        self.packet+=struct.pack('=I', n)

    def writeString(self, s):
        if type(s) is str:
            s = bytes(str)
        stringLength = len(s)
        self.writeU16(stringLength)
        self.packet += struct.pack('%is' % (stringLength), s)

    def writeBytes(self, b):
        self.packet+=b

    def getU8(self):
        n = self.packet[self.position]
        self.position+=1
        return n

    def getU16(self):
        n = struct.unpack('=H', self.packet[self.position:self.position+2])[0]
        self.position+=2
        return n

    def getU32(self):
        n = struct.unpack('=I', self.packet[self.position:self.position+4])[0]
        self.position+=4
        return n

    def getString(self):
        stringLength = self.getU16()
        string = struct.unpack('=%is' % (stringLength), self.packet[self.position:self.position+stringLength])[0]
        self.position+=stringLength
        return string

    def getDouble(self, parameter_list):
        raise NotImplementedError

    def getPacket(self):
        return self.packet

    def getWholePacket(self):
        return self.header + self.packet

