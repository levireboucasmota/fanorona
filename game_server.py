import json
import socket
import threading

HOST = "0.0.0.0"
PORT = 5000


# Classe que encapsula o servidor TCP do jogo.
# Ela aceita conexões, atribui o número do jogador e
# controla o estado do tabuleiro e das mensagens do jogo.
class FanoronaServer:

    # Inicializa o socket do servidor, o estado do jogo e
    # os dados necessários para controlar as conexões.
    def __init__(self, host=HOST, port=PORT):

        self.host = host
        self.port = port

        self.server = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        self.server.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        self.server.bind((self.host, self.port))
        self.server.listen(2)

        self.running = False
        self.accept_thread = None

        self.players = []
        self.game_lock = threading.Lock()
        self.game_started = False

        self.board_template = self.build_initial_board()
        self.board = self.reset_board()
        self.history = []

    # Define a formação inicial do tabuleiro da Fanorona.
    def build_initial_board(self):

        return [
            [2, 2, 2, 2, 2, 2, 2, 2, 2],
            [2, 2, 2, 2, 2, 2, 2, 2, 2],
            [2, 2, 2, 2, 0, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]

    # Cria uma cópia do tabuleiro inicial para reiniciar a partida.
    def reset_board(self):

        return [line[:] for line in self.board_template]

    # Serializa um dicionário em JSON e envia para o cliente.
    def send_message(self, sock, data):

        message = json.dumps(data) + "\n"

        sock.sendall(
            message.encode("utf-8")
        )

    # Envia uma mensagem para todos os jogadores, exceto o remetente.
    def broadcast(self, sender_socket, data):

        for player in self.players:

            if player != sender_socket:

                try:
                    self.send_message(
                        player,
                        data
                    )

                except Exception:
                    pass

    # Envia uma mensagem para todos os clientes conectados.
    def broadcast_all(self, data):

        for player in self.players:

            try:
                self.send_message(
                    player,
                    data
                )

            except Exception:
                pass

    # Processa as mensagens recebidas de um jogador específico.
    # Aqui ficam as regras de chat, start_game, movimentos, undo, turnos
    # e desistência.
    def handle_client(self, client_socket, player_number):

        print(
            f"Thread do Jogador "
            f"{player_number} iniciada."
        )

        buffer = ""

        while True:

            try:

                data = client_socket.recv(1024)

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

                    print(
                        f"Jogador {player_number}: "
                        f"{data}"
                    )

                    if data["type"] == "chat":

                        self.broadcast(
                            client_socket,
                            {
                                "type": "chat",
                                "player": player_number,
                                "message": data["message"]
                            }
                        )

                    elif data["type"] == "start_game":

                        with self.game_lock:
                            self.board = self.reset_board()
                            self.history.clear()
                            self.game_started = True

                        self.broadcast_all(
                            {
                                "type": "game_started",
                                "starting_player": player_number
                            }
                        )

                    elif data["type"] == "move":

                        old_row, old_col = data["from"]
                        new_row, new_col = data["to"]

                        with self.game_lock:

                            if not self.game_started:
                                continue

                            if not all(
                                0 <= position < 5
                                for position in (old_row, new_row)
                            ) or not all(
                                0 <= position < 9
                                for position in (old_col, new_col)
                            ):
                                continue

                            if self.board[old_row][old_col] == 0:
                                continue

                            self.history.append(
                                [line[:] for line in self.board]
                            )

                            self.board[new_row][new_col] = self.board[old_row][old_col]
                            self.board[old_row][old_col] = 0

                            player_one_has_pieces = any(
                                1 in line
                                for line in self.board
                            )

                            player_two_has_pieces = any(
                                2 in line
                                for line in self.board
                            )

                        self.broadcast_all(
                            {
                                "type": "move",
                                "player": player_number,
                                "from": data["from"],
                                "to": data["to"]
                            }
                        )

                        if not player_one_has_pieces or not player_two_has_pieces:

                            with self.game_lock:
                                self.game_started = False

                            winner = 1 if player_one_has_pieces else 2

                            self.broadcast_all(
                                {
                                    "type": "game_over",
                                    "winner": winner,
                                    "reason": "no_pieces"
                                }
                            )

                    elif data["type"] == "undo_move":

                        with self.game_lock:

                            if not self.history:
                                continue

                            self.board = self.history.pop()

                        self.broadcast_all(
                            {
                                "type": "undo_move"
                            }
                        )

                    elif data["type"] == "pass_turn":

                        if player_number == 1:
                            next_player = 2
                        else:
                            next_player = 1

                        self.broadcast_all(
                            {
                                "type": "turn_changed",
                                "current_player": next_player
                            }
                        )

                    elif data["type"] == "surrender":

                        if player_number == 1:
                            winner = 2
                        else:
                            winner = 1

                        self.broadcast_all(
                            {
                                "type": "game_over",
                                "winner": winner,
                                "reason": "surrender"
                            }
                        )

                        with self.game_lock:
                            self.game_started = False

            except ConnectionResetError:
                break

            except json.JSONDecodeError:
                print("Mensagem JSON inválida.")

        if client_socket in self.players:
            self.players.remove(client_socket)

        client_socket.close()

        print(
            f"Jogador {player_number} "
            f"desconectou."
        )

    # Loop que aceita conexões novas e cria uma thread para cada jogador.
    def _accept_clients(self):

        print(
            f"Servidor esperando conexões "
            f"na porta {self.port}..."
        )

        while self.running:

            try:
                client_socket, address = self.server.accept()

            except OSError:
                break

            if len(self.players) >= 2:
                self.send_message(
                    client_socket,
                    {
                        "type": "server_full",
                        "message": "Servidor já está cheio."
                    }
                )

                client_socket.close()
                continue

            player_number = len(self.players) + 1
            self.players.append(client_socket)

            self.send_message(
                client_socket,
                {
                    "type": "player_assigned",
                    "player": player_number
                }
            )

            print(
                f"Jogador {player_number} conectado: "
                f"{address}"
            )

            thread = threading.Thread(
                target=self.handle_client,
                args=(
                    client_socket,
                    player_number
                ),
                daemon=True
            )

            thread.start()

        print("Servidor encerrado.")

    # Inicia o servidor em background para receber jogadores.
    def start(self):

        if self.running:
            return self

        self.running = True
        self.accept_thread = threading.Thread(
            target=self._accept_clients,
            daemon=True
        )
        self.accept_thread.start()

        return self

    # Para o servidor e fecha as conexões ativas.
    def stop(self):

        self.running = False

        try:
            self.server.close()

        except Exception:
            pass

        for player in list(self.players):

            try:
                player.close()

            except Exception:
                pass

        self.players.clear()


if __name__ == "__main__":

    server = FanoronaServer()
    server.start()

    try:
        while True:
            pass

    except KeyboardInterrupt:
        server.stop()
