import socket
import threading
import json


class Client:

    # Classe responsável por conectar o cliente ao servidor,
    # enviar mensagens e receber respostas em segundo plano.
    def __init__(self, host, on_message=None):

        self.host = host
        self.port = 5000

        self.on_message = on_message

        self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        self.socket.connect(
            (self.host, self.port)
        )

        print("Conectado ao servidor!")

        self.receive_thread = threading.Thread(
            target=self.receive_messages
        )

        self.receive_thread.start()

    # Envia uma mensagem em formato JSON para o servidor,
    # acrescentando uma quebra de linha para facilitar o parsing.
    def send_message(self, data):

        message = json.dumps(data) + "\n"

        self.socket.sendall(
            message.encode("utf-8")
        )

    # Recebe mensagens do servidor em uma thread separada e
    # entrega os dados para o callback informado na inicialização.
    def receive_messages(self):

        buffer = ""

        while True:

            try:

                data = self.socket.recv(1024)

                if not data:
                    break

                buffer += data.decode("utf-8")

                while "\n" in buffer:

                    message, buffer = buffer.split(
                        "\n",
                        1
                    )

                    if not message:
                        continue

                    data = json.loads(message)

                    if self.on_message:
                        self.on_message(data)

            except ConnectionResetError:

                print("Servidor desconectado.")
                break

            except json.JSONDecodeError:

                print("Mensagem inválida recebida.")
                continue

    # Fecha o socket do cliente.
    def close(self):

        try:
            self.socket.close()

        except:
            pass