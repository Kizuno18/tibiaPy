import socket
from tibiapacket import TibiaPacketReader, TibiaPacketWriter
from protocolcodes import ProtocolCodes

WORLD_NAME = "King-BAIAK"
ACCOUNT_NAME = "1"
ACCOUNT_PASS = "1"

HOST = "beta.king-baiak.net"
PORT = 7172
VERSION = 860


class OpcodeInterpreter:
    def __init__(self, protocol_codes):
        self.protocol_codes = protocol_codes
        self.character_list_received = False

    def interpret(self, opcode, reader):
        if opcode == self.protocol_codes.S_LOGIN_ERROR:
            return self.handle_login_error(reader)
        elif opcode == self.protocol_codes.S_LOGIN_SUCCESS:
            return self.handle_login_success(reader)
        elif opcode == self.protocol_codes.S_CHARACTER_LIST:
            if not self.character_list_received:
                self.character_list_received = True
                return self.handle_character_list(reader)
        # ... (adicione mais handlers conforme necessário)
        else:
            print(f"Opcode não reconhecido: {opcode}")

    def handle_login_error(self, reader):
        error_message = reader.read_string()
        print("Erro de login:", error_message)

    def handle_login_success(self, reader):
        print("Login efetuado com sucesso!")

    def handle_character_list(self, reader):
        character_list = []
        characters_count = reader.read_byte()
        for _ in range(characters_count):
            character_name = reader.read_string()
            world_name = reader.read_string()
            world_ip = reader.read_ipv4()
            world_port = reader.read_ushort()
            character_list.append((character_name, world_name, world_ip, world_port))
        
        worlds_count = reader.read_byte()
        for _ in range(worlds_count):
            world_name = reader.read_string()
            world_ip = reader.read_ipv4()
            world_port = reader.read_ushort()

        premium_days = reader.read_ushort()

        print("Lista de personagens:")
        for character_name, world_name, world_ip, world_port in character_list:
            print(f"{character_name} ({world_name}) - {world_ip}:{world_port}")
        
        return character_list


# Conexão com o servidor
def connect_to_server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    return sock

# Enviar pacote de login
def send_login_packet(sock, version, account_name, account_pass):
    writer = TibiaPacketWriter()

    # Account Manager login opcode
    writer.write_byte(ProtocolCodes.C_LOGIN_ACCOUNT_MANAGER)

    # Client version
    writer.write_ushort(version)

    # Operating System (1 = Windows, 2 = Linux, 3 = macOS)
    writer.write_byte(1)

    # Account data
    writer.write_string(account_name)
    writer.write_string(account_pass)

    # Send packet
    sock.sendall(writer.get_data())

# Receber pacote de login
def receive_login_packet(sock, opcode_interpreter):
    data = sock.recv(1024)
    reader = TibiaPacketReader(data)

    # Opcode do pacote
    opcode = reader.read_byte()

    # Interpretar o opcode
    return opcode_interpreter.interpret(opcode, reader)


# Função principal
def main():
    # Conectar ao servidor
    sock = connect_to_server(HOST, PORT)

    # Instanciar o OpcodeInterpreter
    opcode_interpreter = OpcodeInterpreter(ProtocolCodes)

    # Enviar pacote de login
    send_login_packet(sock, VERSION, ACCOUNT_NAME, ACCOUNT_PASS)

    #
