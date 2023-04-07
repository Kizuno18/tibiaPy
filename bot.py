import socket, struct, sys
from packet import ProtocolGameReceive, ProtocolGameSend
from opcodes import ProtocolCodes

# Essa é a classe principal do seu bot. Ela é responsável por fazer a conexão com o servidor, enviar os pacotes de login e de entrada no jogo e receber os pacotes do servidor.

class TibiaBot:
    def __init__(self, host, port, version, account_name, account_pass):
        self.host = host
        self.port = port
        self.version = version
        self.account_name = account_name
        self.account_pass = account_pass

    def connect_to_server(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def send_login_packet(self):
        writer = ProtocolGameSend()
        writer.write_byte(ProtocolCodes.C_LOGIN)
        writer.write_ushort(self.version)
        writer.write_string(self.account_name)
        writer.write_string(self.account_pass)
        self.sock.sendall(writer.data)

    def enter_game(self, character_name):
        writer = ProtocolGameSend()
        writer.write_byte(ProtocolCodes.S_ENTERGAME)
        writer.write_string(character_name)
        self.sock.sendall(writer.data)

    def send_logout(self):
        writer = ProtocolGameSend()
        writer.write_byte(ProtocolCodes.C_LOGOUT)
        self.sock.sendall(writer.data)
    
    def send_cancel_move(self):
        writer = ProtocolGameSend()
        writer.write_byte(ProtocolCodes.C_CANCEL_MOVE)
        self.sock.sendall(writer.data)
    def receive_packet(self):



        try:
            opcode = struct.unpack("<B", self.sock.recv(1))[0]
        except struct.error as e:
            print(f"Ocorreu um erro ao receber o pacote: {e}")
            print("A conexão pode ter sido encerrada pelo servidor. Fechando o bot.")
            self.sock.close()
            sys.exit(1)


        data = bytearray()
        while True:
            chunk = self.sock.recv(1024)
            if not chunk:
                break
            data.extend(chunk)

        reader = ProtocolGameReceive(data)
        return opcode, reader

    def send_ping_response(self):
        writer = ProtocolGameSend()
        writer.write_byte(ProtocolCodes.C_PING)
        self.sock.sendall(writer.data)


    def select_character(self, character_name):
        writer = ProtocolGameSend()
        writer.write_byte(ProtocolCodes.C_ENTER_GAME)
        writer.write_string(character_name)
        self.sock.sendall(writer.data)





