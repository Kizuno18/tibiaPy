import random
import socket
import struct
import zlib
import os

OT_RSA = 109120132967399429278860960508995541528237502902798129123468757937266291492576446330739696001110603907230888610072655818825358503429057592827629436413108566029093628212635953836686562675849720620786279431090218017681061521755056710823876476444260558147179707119674283982419152118103759076030616683978566631413
headerSize = 6
class TibiaPacket(object):
    def __init__(self, packetBytes=bytearray()):
        self.header = packetBytes[:headerSize]
        self.packet = packetBytes[headerSize:]
        self.position = 0
        self.encryptionPos = 0
    '''header'''
    def writeHeader(self):
        self.header = struct.pack('=HI', len(self.packet) + 4, zlib.adler32(self.packet)) + self.packet
    def readHeader(self):
        if len(self.header) < headerSize:
            return None
        packetSize, adler32Checksum = struct.unpack('=HI', self.header)
        self.packetSize = packetSize
        self.adler32 = adler32Checksum
        return {'packetSize': packetSize, 'adler32Checksum': adler32Checksum}

    '''XTEA stuff'''
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
    '''RSA stuff'''
    def setEncryptionPos(self):
        self.encryptionPos = len(self.packet)
    def rsa_encrypt(self):
        m = sum(x*pow(256, i) for i, x in enumerate(reversed(self.packet[self.encryptionPos:])))
        c = pow(m, 65537, OT_RSA)
        self.packet[self.encryptionPos:] = bytearray((c >> i) & 255 for i in reversed(range(0, 1024, 8)))
        self.encryptionPos = 0
    def fillBytes(self):
        self.packet += bytearray(random.randint(0,255) for i in range(len(self.packet)-self.encryptionPos, 128))
    '''writters'''
    def writeU8(self, n):
        self.packet+=struct.pack('=B', n)
    def writeU16(self, n):
        self.packet+=struct.pack('=H', n)
    def writeU32(self, n):
        self.packet+=struct.pack('=I', n)
    def writeString(self, s):
        if type(s) is str:
            s = bytes(str)
        stringLength = len(s)
        self.writeU16(stringLength)
        self.packet += struct.pack('%is' % (stringLength), s)
    def writeBytes(self, b):
        self.packet+=b
    '''readers'''
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

    def getIp(self):
        ip_bytes = [str(self.getU8()) for _ in range(4)]
        ip_str = '.'.join(ip_bytes)
        return ip_str

    
    def getString(self):
        stringLength = self.getU16()
        #print(stringLength)
        buffer = self.packet[self.position:self.position+stringLength]
        #print(buffer)
        string = struct.unpack('=%is' % (stringLength), buffer)[0]
        self.position += stringLength
        return string
    def getDouble(self, parameter_list):
        raise NotImplementedError
    def getPacket(self):
        return self.packet
    def getWholePacket(self):
        return self.header + self.packet
def makeLoginPacket(xtea_key, acc_name, acc_password):
    packet = TibiaPacket() #get charlist packet (login)
    packet.writeU8(1)
    packet.writeU16(2)
    packet.writeU16(860)
    packet.writeU32(0x4BF78CAB)
    packet.writeU32(0x4BF11584)
    packet.writeU32(0x56E53417)
    packet.setEncryptionPos()
    packet.writeU8(0) #0 first RSA byte must be 0
    packet.writeBytes(xtea_key) #we're writing XTEA key, ist just a set of bytes so we i have to use dedicated function
    packet.writeString(acc_name)
    packet.writeString(acc_password)
    packet.fillBytes()
    packet.rsa_encrypt()
    packet.writeHeader()
    return packet.getWholePacket()
def makeEnterGamePacket(charname, timestamp, randomNumber):
    packet = TibiaPacket() #get charlist packet (login)
    packet.writeU8(10)
    packet.writeU16(2)
    packet.writeU16(860)
    #packet.writeU16(65)
    #packet.writeU32(0x4BF78CAB)
    #packet.writeU32(0x4BF11584)
    #packet.writeU32(0x56E53417)
    packet.setEncryptionPos()
    packet.writeU8(0) #0 first RSA byte must be 0
    packet.writeBytes(xtea_key) #we're writing XTEA key, ist just a set of bytes so we i have to use dedicated function
    packet.writeU8(0)
    packet.writeString(acc_name)
    packet.writeString(charname)
    packet.writeString(acc_password) 
    packet.fillBytes()
    packet.rsa_encrypt()
    packet.writeHeader()
    return packet.getWholePacket()
def loginPacketHandler(s):
    packetBytes = s.recv(headerSize)
    packetSize, adler32Checksum = struct.unpack('=HI', packetBytes)
    packetBytes += s.recv(packetSize - 2) # U16 size
    received_packet = TibiaPacket(packetBytes)
    received_packet.readHeader()
    received_packet.xtea_decrypt()
    received_packet.trim_size()
    received_packet.getPacket()
    index =0
    while received_packet.position < len(received_packet.getPacket()):
        packetCode = received_packet.getU8()
        #print(packetCode)
        if packetCode == 10: #servererror
            yield 'servererror', received_packet.getString()
        elif packetCode == 11: #loginerror
            yield 'loginerror', received_packet.getString()
        elif packetCode == 20: #loginservermotd
            yield 'loginservermotd', received_packet.getString()
        elif packetCode == 40: #session key
            global sessionkey
            sessionkey = received_packet.getString()
            yield 'sessionkey', sessionkey
        elif packetCode == 100: #charlist
            charactersCount = received_packet.getU8()
            for character in range(charactersCount):
                characters[character] = {}
                characters[character]["charName"] = received_packet.getString()
                #print(characters[character]["charName"])
                characters[character]["worldName"] = received_packet.getString()
                #print(characters[character]["worldName"])
                characters[character]["worldIp"] = received_packet.getIp()
                #print(characters[character]["worldIp"])
                characters[character]["worldPort"] = received_packet.getU16()
                #print(characters[character]["worldPort"])
            #print('premdays: ', received_packet.getU8() + received_packet.getU8())
            yield 'characters', characters
        else:
            yield 'unknown packet', '%i  %d (0x%x)' % (index, packetCode, packetCode)
def handleGamePackets(c):
    packetBytes = c.recv(1)
    packetSize, adler32Checksum = struct.unpack('=HI', packetBytes)
    packetBytes += c.recv(packetSize - 2) # U16 size
    received_packet = TibiaPacket(packetBytes)
    received_packet.readHeader()
    #print("alo")
    received_packet.getPacket()
    received_packet.trim_size()
    received_packet.getPacket()
    print('pos', received_packet.position)
    while received_packet.position < len(received_packet.getPacket()):
        packetCode = received_packet.getU8()
        print(packetCode)
        if packetCode == 31: #server challenge
            timestamp = received_packet.getU32()
            randomNumber = received_packet.getU8()
            #print(randomNumber)
            c.sendall(makeEnterGamePacket(sessionkey, characters[0]['name'], timestamp, randomNumber))
            yield 'serverchallenge', {'timestamp': timestamp, 'randomNumber': randomNumber}
    yield None, None
def recv_game_packets(s):
    
    packet = s.recv(4 + struct.unpack('=H', s.recv(2))[0])[4:]
    packet_bytes = iter(packet[2:2 + struct.unpack('=H', packet[:2])[0]])

    for packet_code in packet_bytes:
        if packet_code == 31: #GameServerChallenge
            timestamp = get_int(packet_bytes, 32)
            randomNumber = get_int(packet_bytes, 8)
            print(timestamp, randomNumber)
            yield 'GameServerChallenge', [timestamp, randomNumber]
        if packet_code == 33: #LoginError
            error_code = get_int(packet_bytes, 8)
            yield 'LoginError', error_code        
        if packet_code == 31: #LoginError 
           print("dnv?")
            
        else:
            yield ('unknown packet code %d (0x%x)' % (packet_code, packet_code), None)
from array import array
def get_int(packet_bytes, bits):
    try:
        value = sum(next(packet_bytes) * pow(256, i) for i in range(bits // 8))
        return value
    except StopIteration:
        return None

def generate_xtea_key():
    xtea_key = array('L', [0] * 4)
    for i in range(4):
        xtea_key[i] = random.getrandbits(32)
    return xtea_key
def handle_game_packets_after_enter_game(s):
    header_size = 2
    while True:
        # Recebendo o tamanho do pacote (2 primeiros bytes)
        packet_size_bytes = s.recv(header_size)
        while len(packet_size_bytes) < header_size:
            # Esperando por mais dados até que o tamanho mínimo seja alcançado
            packet_size_bytes += s.recv(header_size - len(packet_size_bytes))
        packet_size = struct.unpack('=H', packet_size_bytes)[0]

        # Recebendo o restante do pacote
        packet_data = s.recv(packet_size - header_size)

        received_packet = TibiaPacket(packet_data)
        header = received_packet.readHeader()
        if header is None:
            continue
        received_packet.trim_size()
        print(received_packet.getPacket())
            # Adicionar outros códigos de pacote conforme necessário
            # else:
            # Adicionar outros códigos de pacote conforme necessário
            # else:
                # ...

        # Tempo de espera antes de verificar novos pacotes (evita uso excessivo de CPU)
        #time.sleep(0.1)

acc_name = b'bigleoncio'
acc_password = b'1'

characters = {}
sessionkey = None
xtea_key = bytes(random.randint(0,255) for i in range(16))
#print('xtea_key', xtea_key)
with socket.socket() as c:
    try:
        c.connect(('127.0.0.1', 7171))
        c.sendall(makeLoginPacket(xtea_key, acc_name, acc_password))    
        for packet_name, packet_data in loginPacketHandler(c):
            if(packet_name == 'characters'):
                chars = packet_data
         
                with socket.socket() as c:
                    c.connect((chars[2]['worldIp'], chars[0]['worldPort']))
                    for packet_name, packet_data in recv_game_packets(c):
                        print(packet_name, packet_data)
                        if(packet_name == 'GameServerChallenge'):
                            print('sending enteragame packet')
                            c.sendall(makeEnterGamePacket(chars[1]['charName'], packet_data[0], packet_data[1]))
                            while True:
                                packet_name, packet_data = next(recv_game_packets(c))
                                print(packet_name, packet_data)
    except socket.error as e:
        print(f"Erro ao receber pacote: {e}")

