from pack import TibiaPacket, makeLoginPacket, makeEnterGamePacket, loginPacketHandler, handleGamePackets
from login import characters, sessionkey, xtea_key
import socket

with socket.socket() as c:  # client
    print(characters, sessionkey)
    c.connect((characters[0]['worldIp'], characters[0]['worldPort']))
    for packet, data in handleGamePackets(c):
        print(packet, data)
