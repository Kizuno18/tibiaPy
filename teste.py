import socket
import struct

server_address = ('beta.king-baiak.net', 7272)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(server_address)
def create_login_packet(account_number, password, character_name):
    packet = struct.pack('>H', 6 + len(account_number) + len(password) + len(character_name) + 3)
    packet += struct.pack('>B', 0x0A)
    packet += struct.pack('>H', len(account_number) + 1)
    packet += bytes(account_number, 'utf-8') + b'\x00'
    packet += struct.pack('>H', len(password) + 1)
    packet += bytes(password, 'utf-8') + b'\x00'
    packet += struct.pack('>H', len(character_name) + 1)
    packet += bytes(character_name, 'utf-8') + b'\x00'
    return packet
account_number = '1'
password = '1'
character_name = 'Account manager'

login_packet = create_login_packet(account_number, password, character_name)
sock.sendall(login_packet)

response = sock.recv(1024)
print(response)
