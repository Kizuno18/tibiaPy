import time
from tibia_client import TibiaClient
from rsa import encrypt_rsa

HOST = "beta.king-baiak.net"
PORT = 7172
VERSION = 860
ACCOUNT_NAME = "1"
ACCOUNT_PASS = "1"
CHARACTER_NAME = "Account Manager"

OT_RSA = 109120132967399429278860960508995541528237502902798129123468757937266291492576446330739696001110603907230888610072655818825358503429057592827629436413108566029093628212635953836686562675849720620786279431090218017681061521755056710823876476444260558147179707119674283982419152118103759076030616683978566631413

class TibiaBot:
    def __init__(self, host, port):
        self.client = TibiaClient(host, port)
        self.client.handle_packet = self.handle_packet

    def connect(self):
        self.client.connect()

    def disconnect(self):
        self.client.disconnect()

    def login(self, account_name, account_password, character_name):
        self.client.perform_rsa_login(account_name, account_password, character_name, OT_RSA)

    def handle_packet(self, packet):
        packet_type = packet.get_uint8()

        if packet_type == TibiaClient.PACKET_PING:
            self.client.send_ping()
        elif packet_type == TibiaClient.PACKET_KEY:
            self.client.handle_key_packet(packet)
        else:
            pass
            # Implemente o tratamento de outros tipos de pacotes

if __name__ == "__main__":
    bot = TibiaBot(HOST, PORT)
    bot.connect()
    bot.login(ACCOUNT_NAME, ACCOUNT_PASS, CHARACTER_NAME)

    while True:
        bot.client.receive_packet()
        time.sleep(0.1)
