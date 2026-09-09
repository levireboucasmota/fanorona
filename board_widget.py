from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen, QBrush
from PySide6.QtCore import Qt, Signal


class BoardWidget(QWidget):

    # Sinal emitido quando o usuário clica em uma posição do tabuleiro.
    position_clicked = Signal(int, int)

    def __init__(self, parent=None):

        super().__init__(parent)

        self.rows = 5
        self.cols = 9

        # 0 = vazio
        # 1 = vermelho
        # 2 = preto

        self.board = self.create_board()

        self.selected_piece = None

        self.setMinimumSize(
            700,
            500
        )

    # Cria o estado inicial do tabuleiro do jogo.
    # 0 = vazio, 1 = peça vermelha, 2 = peça preta.
    def create_board(self):

        return [
            [2, 2, 2, 2, 2, 2, 2, 2, 2],
            [2, 2, 2, 2, 2, 2, 2, 2, 2],
            [2, 2, 2, 2, 0, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]

    # ==================================================
    # DESENHAR
    # ==================================================

    # Desenha todo o tabuleiro, linhas, diagonais, pontos e peças.
    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        width = self.width()
        height = self.height()

        # Margens
        margin_x = 60
        margin_y = 50

        board_width = width - (margin_x * 2)
        board_height = height - (margin_y * 2)

        cell_width = board_width / (self.cols - 1)
        cell_height = board_height / (self.rows - 1)

        # ==============================================
        # LINHAS DO TABULEIRO
        # ==============================================

        pen = QPen(
            Qt.white,
            3
        )

        painter.setPen(pen)

        # Linhas horizontais

        for row in range(self.rows):

            y = margin_y + (
                row * cell_height
            )

            painter.drawLine(
                int(margin_x),
                int(y),
                int(width - margin_x),
                int(y)
            )

        # Linhas verticais

        for col in range(self.cols):

            x = margin_x + (
                col * cell_width
            )

            painter.drawLine(
                int(x),
                int(margin_y),
                int(x),
                int(height - margin_y)
            )

        # ==============================================
        # DIAGONAIS
        # ==============================================

        for row in range(self.rows - 1):

            for col in range(self.cols - 1):

                x1 = margin_x + (
                    col * cell_width
                )

                y1 = margin_y + (
                    row * cell_height
                )

                x2 = margin_x + (
                    (col + 1) * cell_width
                )

                y2 = margin_y + (
                    (row + 1) * cell_height
                )

                painter.drawLine(
                    int(x1),
                    int(y1),
                    int(x2),
                    int(y2)
                )

                painter.drawLine(
                    int(x1),
                    int(y2),
                    int(x2),
                    int(y1)
                )

        # ==============================================
        # PONTOS E PEÇAS
        # ==============================================

        radius = 18

        for row in range(self.rows):

            for col in range(self.cols):

                x = margin_x + (
                    col * cell_width
                )

                y = margin_y + (
                    row * cell_height
                )

                # Ponto do tabuleiro

                painter.setBrush(
                    QBrush(Qt.black)
                )

                painter.drawEllipse(
                    int(x - 5),
                    int(y - 5),
                    10,
                    10
                )

                piece = self.board[row][col]

                # Peça selecionada

                if self.selected_piece == (
                    row,
                    col
                ):

                    painter.setPen(
                        QPen(
                            Qt.yellow,
                            4
                        )
                    )

                    painter.setBrush(
                        Qt.NoBrush
                    )

                    painter.drawEllipse(
                        int(x - radius - 5),
                        int(y - radius - 5),
                        (radius + 5) * 2,
                        (radius + 5) * 2
                    )

                # ======================================
                # PEÇA VERMELHA
                # ======================================

                if piece == 1:

                    painter.setPen(
                        QPen(
                            Qt.black,
                            2
                        )
                    )

                    painter.setBrush(
                        QBrush(Qt.red)
                    )

                    painter.drawEllipse(
                        int(x - radius),
                        int(y - radius),
                        radius * 2,
                        radius * 2
                    )

                # ======================================
                # PEÇA PRETA
                # ======================================

                elif piece == 2:

                    painter.setPen(
                        QPen(
                            Qt.gray,
                            2
                        )
                    )

                    painter.setBrush(
                        QBrush(Qt.black)
                    )

                    painter.drawEllipse(
                        int(x - radius),
                        int(y - radius),
                        radius * 2,
                        radius * 2
                    )

    # ==================================================
    # CLIQUE
    # ==================================================

    # Converte o clique do mouse em uma linha e coluna do tabuleiro,
    # enviando a posição clicada para a janela principal.
    def mousePressEvent(self, event):

        if event.button() != Qt.LeftButton:
            return

        width = self.width()
        height = self.height()

        margin_x = 60
        margin_y = 50

        board_width = width - (
            margin_x * 2
        )

        board_height = height - (
            margin_y * 2
        )

        cell_width = board_width / (
            self.cols - 1
        )

        cell_height = board_height / (
            self.rows - 1
        )

        col = round(
            (event.position().x() - margin_x)
            / cell_width
        )

        row = round(
            (event.position().y() - margin_y)
            / cell_height
        )

        # Fora do tabuleiro

        if row < 0 or row >= self.rows:
            return

        if col < 0 or col >= self.cols:
            return

        self.position_clicked.emit(
            row,
            col
        )