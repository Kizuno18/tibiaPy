from opcodes import ProtocolCodes

#Esta classe é responsável por interpretar os pacotes recebidos do servidor
# e enviar os pacotes de resposta apropriados
# Você pode adicionar mais handlers conforme necessário
# para lidar com outros pacotes do protocolo
# 

class OpCodeInterpreter:
    def __init__(self, protocol_codes):
        self.protocol_codes = protocol_codes
        self.character_list_received = False

    def interpret(self, opcode, reader):
        try:
            if opcode == self.protocol_codes.S_LOGIN_ERROR:
                return self.handle_login_error(reader)
            elif opcode == self.protocol_codes.S_LOGIN_SUCCESS:
                return self.handle_login_success(reader)
            elif opcode == self.protocol_codes.S_CHARACTER_LIST:
                if not self.character_list_received:
                    self.character_list_received = True
                    return self.handle_character_list(reader)
            elif opcode == 12:
                return self.handle_login(reader)

            else:
                print(f"Opcode não reconhecido: {opcode}")
        except Exception as e:
            print(f"Erro ao processar o opcode {opcode}: {e}")

    def handle_login(self, reader):
        player_id = reader.read_uint()
        server_beat = reader.read_ushort()
    
        # Supondo que você não precisa de informações de velocidade e outras configurações específicas do jogo
        # Pule os bytes relevantes se necessário, por exemplo:
        reader.skip_bytes(3)  # pula 3 bytes
        
        can_report_bugs = reader.read_byte()
    
        # Adicione aqui mais código para lidar com outras informações específicas do protocolo que você precisa
    
        print(f"Login bem-sucedido. ID do jogador: {player_id}, Server Beat: {server_beat}, Pode reportar bugs: {can_report_bugs}")


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
                  
    def handle_ping(self, reader):
        print("Ping recebido do servidor")
        return self.protocol_codes.C_PING
    
    def handle_ping_response(self, reader):        
        print("Ping respondido pelo servidor")
        return self.protocol_codes.C_PING_RESPONSE
    
    def handle_cancel_move(self, reader):
        print("Movimento cancelado")
        return self.protocol_codes.C_CANCEL_MOVE
    
    def handle_cancel_attack(self, reader):
        print("Ataque cancelado")
        return self.protocol_codes.C_CANCEL_ATTACK

