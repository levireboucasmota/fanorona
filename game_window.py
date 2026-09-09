import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QLineEdit,
    QFrame,
    QInputDialog,
    QMessageBox
)

from PySide6.QtCore import Qt, Signal, QObject

from network_client import Client
from board_widget import BoardWidget

class MessageBridge(QObject):

    # Ponte simples para encaminhar mensagens do cliente
    # até a janela principal via sinal Qt.
    message_received = Signal(dict)


class FanoronaGUI(QMainWindow):

    # Inicializa a interface do jogo.
    # O parâmetro host é opcional e usado quando o programa já
    # conhece o endereço do servidor ao abrir.
    def __init__(self, host=None):

        super().__init__()

        self.bridge = MessageBridge()

        self.bridge.message_received.connect(
            self.receive_message
        )

        self.client = None

        # =========================
        # CONFIGURAÇÃO DA JANELA
        # =========================

        self.setWindowTitle("Fanorona")

        self.setFixedSize(1200, 750)

        # =========================
        # ESTADO DO JOGO
        # =========================

        self.player_number = None

        self.current_player = 1

        self.game_started = False

        self.selected_piece = None

        self.history = []

        # =========================
        # WIDGET CENTRAL
        # =========================

        central_widget = QWidget()

        self.setCentralWidget(
            central_widget
        )

        # Layout principal
        main_layout = QHBoxLayout()

        main_layout.setContentsMargins(
            25,
            25,
            25,
            25
        )

        main_layout.setSpacing(25)

        central_widget.setLayout(
            main_layout
        )

        # =========================
        # ÁREA DO TABULEIRO
        # =========================

        board_container = QFrame()

        board_container.setFrameShape(
            QFrame.StyledPanel
        )

        board_layout = QVBoxLayout()

        board_container.setLayout(
            board_layout
        )

        main_layout.addWidget(
            board_container,
            stretch=3
        )

        # Título

        title = QLabel("FANORONA")

        title.setAlignment(
            Qt.AlignCenter
        )

        title.setObjectName(
            "title"
        )

        board_layout.addWidget(
            title
        )

        self.turn_banner = QLabel(
            "Aguardando início da partida"
        )

        self.turn_banner.setAlignment(
            Qt.AlignCenter
        )

        self.turn_banner.setObjectName(
            "turn_banner"
        )

        self.turn_banner.setMinimumHeight(
            52
        )

        board_layout.addWidget(
            self.turn_banner
        )

        # Área temporária do tabuleiro

        self.board_widget = BoardWidget()

        board_layout.addWidget(
            self.board_widget
        )

        self.board_widget.position_clicked.connect(
            self.on_board_click
        )

        # =========================
        # PAINEL LATERAL
        # =========================

        side_container = QFrame()

        side_layout = QVBoxLayout()

        side_container.setLayout(
            side_layout
        )

        main_layout.addWidget(
            side_container,
            stretch=1
        )

        # =========================
        # JOGADORES
        # =========================

        self.player_label = QLabel(
            "Jogador 1 🔴  |  Jogador 2 ⚫"
        )

        self.player_label.setAlignment(
            Qt.AlignCenter
        )

        side_layout.addWidget(
            self.player_label
        )

        # =========================
        # STATUS
        # =========================

        self.status_label = QLabel(
            "Partida não iniciada"
        )

        self.status_label.setAlignment(
            Qt.AlignCenter
        )

        self.status_label.setObjectName(
            "status"
        )

        side_layout.addWidget(
            self.status_label
        )

        # =========================
        # CHAT
        # =========================

        chat_title = QLabel("CHAT")

        chat_title.setObjectName(
            "section_title"
        )

        side_layout.addWidget(
            chat_title
        )

        self.chat_area = QTextEdit()

        self.chat_area.setReadOnly(
            True
        )

        side_layout.addWidget(
            self.chat_area
        )

        # =========================
        # CAMPO DE CHAT
        # =========================

        chat_input_layout = QHBoxLayout()

        self.message_entry = QLineEdit()

        self.message_entry.setPlaceholderText(
            "Digite sua mensagem..."
        )

        self.send_button = QPushButton(
            "Enviar"
        )

        chat_input_layout.addWidget(
            self.message_entry
        )

        chat_input_layout.addWidget(
            self.send_button
        )

        side_layout.addLayout(
            chat_input_layout
        )

        # =========================
        # BOTÕES
        # =========================

        self.start_button = QPushButton(
            "▶  Iniciar partida"
        )

        self.undo_button = QPushButton(
            "↶  Voltar jogada"
        )

        self.pass_button = QPushButton(
            "→  Passar jogada"
        )

        self.surrender_button = QPushButton(
            "⚑  Desistir"
        )

        self.message_entry.returnPressed.connect(
            self.send_chat
        )

        self.send_button.clicked.connect(
            self.send_chat
        )

        self.start_button.clicked.connect(
            self.start_game
        )

        self.undo_button.clicked.connect(
            self.undo_move
        )

        self.pass_button.clicked.connect(
            self.pass_turn
        )

        self.surrender_button.clicked.connect(
            self.surrender
        )

        side_layout.addWidget(
            self.start_button
        )

        side_layout.addWidget(
            self.undo_button
        )

        side_layout.addWidget(
            self.pass_button
        )

        side_layout.addWidget(
            self.surrender_button
        )

        # =========================
        # ESTADO INICIAL DOS BOTÕES
        # =========================

        self.undo_button.setEnabled(
            False
        )

        self.pass_button.setEnabled(
            False
        )

        self.surrender_button.setEnabled(
            False
        )

        # =========================
        # ESTILO
        # =========================

        self.setStyleSheet("""

            QMainWindow {
                background-color: #111827;
            }

            QFrame {
                background-color: #1f2937;
                border-radius: 12px;
            }

            QLabel {
                color: #f9fafb;
                font-size: 14px;
            }

            QLabel#title {
                font-size: 28px;
                font-weight: bold;
                padding: 10px;
            }

            QLabel#status {
                font-size: 16px;
                font-weight: bold;
                padding: 12px;
            }

            QLabel#turn_banner {
                background-color: #374151;
                color: #d1d5db;
                border-radius: 8px;
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
            }

            QLabel#section_title {
                font-size: 18px;
                font-weight: bold;
                padding: 8px;
            }

            QLabel#board {
                background-color: #e5d0a8;
                color: #374151;
                border-radius: 10px;
                font-size: 24px;
            }

            QTextEdit {
                background-color: #111827;
                color: #f9fafb;
                border: none;
                border-radius: 8px;
                padding: 8px;
            }

            QLineEdit {
                background-color: #111827;
                color: #f9fafb;
                border: none;
                border-radius: 8px;
                padding: 10px;
            }

            QPushButton {
                background-color: #374151;
                color: #f9fafb;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }

            QPushButton:hover {
                background-color: #4b5563;
            }

            QPushButton:disabled {
                background-color: #1f2937;
                color: #6b7280;
            }

        """)

        self.connect_to_server(host)

    # Tenta conectar o cliente ao servidor informado.
    # Se nenhum IP for passado, pede ao usuário para digitar.
    def connect_to_server(self, host=None):

        if host:
            ip = host

        else:

            ip, ok = QInputDialog.getText(
                self,
                "Conectar ao servidor",
                "Digite o IP do servidor:"
            )

            if not ok or not ip:
                self.close()
                return

        try:

            self.client = Client(
                ip,
                self.bridge.message_received.emit
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Erro de conexão",
                f"Não foi possível conectar ao servidor:\n\n{e}"
            )

            self.close()

    # Trata o clique do usuário no tabuleiro.
    # Primeiro clique seleciona a peça; segundo clique envia a jogada.
    def on_board_click(self, row, col):

        print(
            f"Clique no tabuleiro: "
            f"linha={row}, coluna={col}"
        )

        if not self.game_started:
            return

        if self.current_player != self.player_number:
            return

        # ==================================
        # PRIMEIRO CLIQUE
        # ==================================

        if self.selected_piece is None:

            # Só pode selecionar uma posição
            # que tenha uma peça

            if self.board_widget.board[row][col] != 0:

                self.selected_piece = (
                    row,
                    col
                )

                self.board_widget.selected_piece = (
                    row,
                    col
                )

                self.board_widget.update()

        # ==================================
        # SEGUNDO CLIQUE
        # ==================================

        else:

            old_row, old_col = self.selected_piece

            self.client.send_message(
                {
                    "type": "move",

                    "from": [
                        old_row,
                        old_col
                    ],

                    "to": [
                        row,
                        col
                    ]
                }
            )

            self.selected_piece = None

            self.board_widget.selected_piece = None

            self.board_widget.update()

    # Atualiza visualmente o tabuleiro após uma movimentação recebida
    # do servidor e registra o estado anterior para permitir desfazer.
    def receive_move(self, data):

        old_row, old_col = data["from"]

        new_row, new_col = data["to"]

        # Salva o estado anterior
        self.history.append(
            [
                line[:]
                for line in self.board_widget.board
            ]
        )

        # Move a peça
        self.board_widget.board[new_row][new_col] = (
            self.board_widget.board[old_row][old_col]
        )

        self.board_widget.board[old_row][old_col] = 0

        # Limpa seleção
        self.selected_piece = None

        self.board_widget.selected_piece = None

        # Atualiza visualmente
        self.board_widget.update()

        self.undo_button.setEnabled(
            self.current_player == self.player_number
            and bool(self.history)
        )

    # Processa mensagens vindas do servidor.
    # Cada tipo de mensagem altera o estado do jogo e a interface.
    def receive_message(self, data):

        message_type = data.get("type")

        if message_type == "player_assigned":

            self.player_number = data["player"]
            self.add_chat_message(
                f"Você é o Jogador {self.player_number}."
            )

        elif message_type == "chat":

            self.add_chat_message(
                f"Jogador {data['player']}: {data['message']}"
            )

        elif message_type == "game_started":

            self.game_started_received(
                data["starting_player"]
            )

        elif message_type == "move":

            self.receive_move(data)

        elif message_type == "undo_move":

            self.undo_move_received()

        elif message_type == "turn_changed":

            self.turn_changed_received(
                data["current_player"]
            )

        elif message_type == "game_over":

            self.game_over_received(
                data["winner"],
                data["reason"]
            )

    # Adiciona uma mensagem no painel de chat da interface.
    def add_chat_message(self, message):

        self.chat_area.append(message)

    # Envia uma mensagem do chat para o servidor.
    def send_chat(self):

        message = self.message_entry.text().strip()

        if not message or self.client is None:
            return

        self.client.send_message(
            {
                "type": "chat",
                "message": message
            }
        )

        self.add_chat_message(
            f"Você: {message}"
        )

        self.message_entry.clear()

    # Solicita ao servidor que inicie uma nova partida.
    def start_game(self):

        if self.game_started or self.client is None:
            return

        self.client.send_message(
            {
                "type": "start_game"
            }
        )

    # Atualiza a interface quando a partida começa.
    def game_started_received(self, starting_player):

        self.game_started = True
        self.current_player = starting_player
        self.history.clear()
        self.board_widget.board = self.board_widget.create_board()
        self.board_widget.selected_piece = None

        self.start_button.setEnabled(False)
        self.start_button.setText(
            "▶  Iniciar partida"
        )
        self.surrender_button.setEnabled(True)

        self.turn_changed_received(starting_player)

        self.add_chat_message(
            f"Partida iniciada! Jogador {starting_player} começa."
        )

    # Envia a ação de passar a vez para o servidor.
    def pass_turn(self):

        if not self.game_started:
            return

        if self.current_player != self.player_number:
            return

        self.client.send_message(
            {
                "type": "pass_turn"
            }
        )

    # Atualiza a interface para refletir o jogador da vez.
    def turn_changed_received(self, current_player):

        self.current_player = current_player
        self.selected_piece = None
        self.board_widget.selected_piece = None

        self.status_label.setText(
            f"Turno: Jogador {current_player}"
        )

        is_my_turn = current_player == self.player_number

        if is_my_turn:

            self.turn_banner.setText(
                "SEU TURNO"
            )

            self.turn_banner.setStyleSheet(
                "background-color: #facc15; color: #111827;"
            )

        else:

            self.turn_banner.setText(
                f"Turno do Jogador {current_player}"
            )

            self.turn_banner.setStyleSheet(
                "background-color: #2563eb; color: white;"
            )

        self.pass_button.setEnabled(is_my_turn)
        self.undo_button.setEnabled(
            is_my_turn and bool(self.history)
        )

        self.board_widget.update()

    # Solicita ao servidor que reverta a última jogada.
    def undo_move(self):

        if not self.game_started:
            return

        if not self.history:
            return

        self.client.send_message(
            {
                "type": "undo_move"
            }
        )

        self.add_chat_message(
            "Última jogada desfeita."
        )

    # Solicita o encerramento da partida por desistência.
    def surrender(self):

        if not self.game_started or self.client is None:
            return

        self.client.send_message(
            {
                "type": "surrender"
            }
        )

    # Finaliza a partida na interface e mostra o resultado.
    def game_over_received(self, winner, reason):

        self.game_started = False
        self.current_player = None
        self.selected_piece = None
        self.board_widget.selected_piece = None

        self.pass_button.setEnabled(False)
        self.undo_button.setEnabled(False)
        self.surrender_button.setEnabled(False)
        self.start_button.setEnabled(True)
        self.start_button.setText(
            "↻  Revanche"
        )

        if winner == self.player_number:
            message = "Você venceu!"

            self.turn_banner.setText(
                "VOCÊ GANHOU"
            )

            self.turn_banner.setStyleSheet(
                "background-color: #facc15; color: #111827;"
            )

        else:
            message = "Você perdeu!"

            self.turn_banner.setText(
                "VOCÊ PERDEU"
            )

            self.turn_banner.setStyleSheet(
                "background-color: #2563eb; color: white;"
            )

        self.status_label.setText(message)
        self.add_chat_message(message)


    # Reaplica o estado anterior do tabuleiro quando a jogada é desfeita.
    def undo_move_received(self):

        if not self.history:
            return

        self.board_widget.board = self.history.pop()

        self.selected_piece = None

        self.board_widget.selected_piece = None

        self.board_widget.update()

        self.undo_button.setEnabled(
            self.current_player == self.player_number
            and bool(self.history)
        )


# =====================================================
# EXECUÇÃO
# =====================================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = FanoronaGUI()

    window.show()

    sys.exit(
        app.exec()
    )