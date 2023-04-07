import socket
import struct

# Constantes
HOST = "4.228.215.116"
PORT = 7172
VERSION = 860
ACCOUNT_NAME = "1"
ACCOUNT_PASS = "1"
CHARACTER_NAME = "Account Manager"

# Protocolos
XTEA = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
RSA = (int(
    '1321277432058722840622950990822933849527763264961655079678763618'
    '837281649846495476509300616736131876052563205881939193366830614'
    '212421932944149689976097724565456087960039698194213991819836648'
    '01566009366126326707689705577660294323306890374355365061003108'
    '13977124614488542822123142555655169162528459184485355152496547'
    '74930312859777566304059213796086762263679608183735330401275654'
    '70421948576681879296070989133195984994101232788635295334951519'
    '56381421534169042199931120162373086365260331817350'), int(65537))

def xtea_decrypt(key, data):
    rounds = 32
    delta = 0x9E3779B9
    data = bytearray(data)

    # Preenche os dados com zeros para garantir que seja múltiplo de 8
    if len(data) % 8 != 0:
        data.extend(b'\x00' * (8 - len(data) % 8))
        
    n = len(data)
    sum = delta * rounds
    key = struct.unpack("<4I", key)

    for _ in range(rounds):
        e = (sum >> 2) & 3

        for offset in range(n - 4, -4, -8):
            z = data[offset + 4:offset + 8]
            z = struct.unpack("<I", z)[0]
            z -= (((data[offset] << 4) ^ (data[offset + 3] >> 5)) + data[offset + 3]) ^ (sum + key[(sum >> 11) & 3])
            z &= 0xFFFFFFFF
            data[offset + 4:offset + 8] = struct.pack("<I", z)

        sum -= delta

        for offset in range(0, n, 8):
            x = data[offset:offset + 4]
            x = struct.unpack("<I", x)[0]
            x -= (((data[offset + 5] << 4) ^ (data[offset + 2] >> 5)) + data[offset + 2]) ^ (sum + key[sum & 3])
            x &= 0xFFFFFFFF
            data[offset:offset + 4] = struct.pack("<I", x)

    return bytes(data)




def rsa_decrypt(n, e, data):
    number = int.from_bytes(data, byteorder='big', signed=False)
    decrypted = pow(number, e, n)
    decrypted_bytes = decrypted.to_bytes((decrypted.bit_length() + 7) // 8, byteorder='big', signed=False)
    return decrypted_bytes.rjust(len(data), b'\x00')


def create_socket():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        return s
    except socket.error as err:
        print(f"Erro ao criar o socket: {err}")
        return None

def send_login_packet(socket, account_name, account_pass, character_name):
    packet = bytearray()
    packet.extend(struct.pack(">H", 6))  # Adiciona o tamanho do pacote
    packet.extend(b'\x01')  # Adiciona o código do protocolo

    # Adiciona a versão do cliente
    packet.extend(struct.pack(">H", VERSION))

    # Adiciona informações de conta e senha
    packet.extend(struct.pack(">I", len(account_name) + len(account_pass) + 2))
    packet.extend(struct.pack(">B", len(account_name)))
    packet.extend(account_name.encode())
    packet.extend(struct.pack(">B", len(account_pass)))
    packet.extend(account_pass.encode())

    # Adiciona o nome do personagem
    packet.extend(struct.pack(">B", len(character_name)))
    packet.extend(character_name.encode())

    # Adiciona chave XTEA
    packet.extend(XTEA)

    # Criptografa o pacote com RSA
    encrypted_packet = rsa_decrypt(*RSA, packet[8:])  # Altere o índice de 7 para 8
    packet[8:] = encrypted_packet[:len(packet) - 8]  # Altere o índice de 7 para 8

    # Envia o pacote
    socket.sendall(packet)

def main():
    # Cria o socket e se conecta ao servidor
    s = create_socket()
    if not s:
        return

    # Envia o pacote de login
    send_login_packet(s, ACCOUNT_NAME, ACCOUNT_PASS, CHARACTER_NAME)

    # Recebe a resposta do servidor
    data = s.recv(1024)
    decrypted_data = xtea_decrypt(XTEA, data[6:])

    # Exibe a resposta
    print(f"Resposta do servidor (criptografada): {data[6:]}")
    print(f"Resposta do servidor (descriptografada): {decrypted_data}")

    # Fecha o socket
    s.close()


if __name__ == "__main__":
    main()
