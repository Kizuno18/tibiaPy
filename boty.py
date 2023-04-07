import socket
from packe import TibiaPacket, TibiaXTEAEncrypt

SERVER_IP = "4.228.215.116"
SERVER_PORT = 7171
TIBIA_VERSION = 860

ACC_NAME = "1"
ACC_PASSWORD = "1"
CHAR_NAME = "Account Manager"

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_IP, SERVER_PORT))
    
    # Enviar pacote de login
    login_packet = TibiaPacket(0x01, TIBIA_VERSION, ACC_NAME, ACC_PASSWORD)
    encrypted_login_packet = TibiaXTEAEncrypt(login_packet, b"")
    sock.sendall(encrypted_login_packet)

    # Receber pacote de personagens
    sock.recv(1024)  # Ignorar pacote de adler32
    xtea_key = sock.recv(1024)  # Chave XTEA do servidor

    # Enviar pacote de seleção de personagem
    enter_game_packet = TibiaPacket(0x0A, CHAR_NAME, "", xtea_key)
    encrypted_enter_game_packet = TibiaXTEAEncrypt(enter_game_packet, b"")
    sock.sendall(encrypted_enter_game_packet)

    # Receber pacotes de jogo
    while True:
        data = sock.recv(1024)
        if not data:
            break
        print("Recebido:", data)

    sock.close()

if __name__ == "__main__":
    main()
