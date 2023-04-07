import socket
import threading
from packety import Packet

class TibiaClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.socket.connect((self.host, self.port))
        self.receive_thread = threading.Thread(target=self.receive_data)
        self.receive_thread.start()

    def disconnect(self):
        self.socket.close()

    def send_packet(self, packet):
        data = packet.get_data()
        length = len(data) + 4
        self.socket.send(struct.pack('<I', length) + data)

    def receive_data(self):
        while True:
            try:
                header = self.socket.recv(4)
                if not header:
                    break
                length = struct.unpack('<I', header)[0] - 4
                data = self.socket.recv(length)
                packet = Packet(data)
                self.handle_packet(packet)
            except Exception as e:
                print(f"Error: {e}")
                break

    def handle_packet(self, packet):
        # Implementar o tratamento dos pacotes recebidos aqui
        pass
