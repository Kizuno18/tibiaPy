from bot import TibiaBot
from opcodeInterpreter import OpCodeInterpreter
from opcodes import ProtocolCodes

# Esse é o arquivo principal do seu bot. Ele é responsável por instanciar a classe TibiaBot e chamar os métodos necessários para que o bot funcione.
# Você pode adicionar mais código aqui para fazer o seu bot fazer mais coisas, como por exemplo, enviar pacotes de movimento para o servidor
# ou enviar pacotes de ataque para o servidor.

HOST = "beta.king-baiak.net"  # Coloque o endereço do servidor aqui
PORT = 7172  # Coloque a porta do servidor aqui
VERSION = 860  # Coloque a versão do cliente aqui
ACCOUNT_NAME = "1"  # Coloque o nome da sua conta aqui
ACCOUNT_PASS = "1"  # Coloque a senha da sua conta aqui
CHARACTER_NAME = "Account Manager" # Coloque o nome do seu personagem aqui

# Essa é a função principal do seu programa. Ela é responsável por instanciar a classe TibiaBot e chamar os métodos necessários para que o bot funcione.
def main():
    bot = TibiaBot(HOST, PORT, VERSION, ACCOUNT_NAME, ACCOUNT_PASS)
    bot.connect_to_server()
    bot.send_login_packet()

    opcode_interpreter = OpCodeInterpreter(ProtocolCodes)

    while True:
        opcode, reader = bot.receive_packet()
        response_opcode = opcode_interpreter.interpret(opcode, reader)

        if response_opcode == ProtocolCodes.C_PING:
            bot.send_ping_response()


# Esse é o ponto de entrada do seu programa. Ele chama a função main() que é responsável por instanciar a classe TibiaBot e chamar os métodos necessários para que o bot funcione.

if __name__ == "__main__":
    main()