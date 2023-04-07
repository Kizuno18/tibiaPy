from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

def encrypt_rsa(data, rsa_key):
    rsa_key = RSA.construct((rsa_key, 65537))  # Adicionar o expoente público 65537
    cipher = PKCS1_OAEP.new(rsa_key)
    encrypted_data = b''

    # Dividir os dados em blocos e criptografar cada bloco
    for i in range(0, len(data), cipher.maximum_size - 42):
        block = data[i:i + cipher.maximum_size - 42]
        encrypted_data += cipher.encrypt(block)

    return encrypted_data
