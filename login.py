from packet import TibiaPacket, makeLoginPacket, makeEnterGamePacket, loginPacketHandler, handleGamePackets
import socket

acc_name = b'bot1xd'
acc_password = b'dupa123'

characters = {}
sessionkey = None
xtea_key = bytes(random.randint(0, 255) for i in range(16))

with socket.socket() as c:
    c.connect(('144.217.149.144', 7171))
    c.sendall(makeLoginPacket(xtea_key, acc_name, acc_password))
    for packet, data in loginPacketHandler(c):
        print(packet, data)
