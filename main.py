import socket
import sys

from PySide6.QtWidgets import QApplication, QInputDialog, QMessageBox

from game_server import FanoronaServer
from game_window import FanoronaGUI


# Retorna o IP local do computador para que o outro jogador
# consiga se conectar ao servidor criado pela primeira máquina.
def get_local_ip():

    try:

        local_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        local_socket.connect(("8.8.8.8", 80))
        ip = local_socket.getsockname()[0]
        local_socket.close()

        return ip

    except Exception:
        return "127.0.0.1"


if __name__ == "__main__":

    # Cria a aplicação Qt e mantém o controle do servidor
    # para que o jogador 1 possa criar o host e depois entrar
    # como cliente usando o mesmo programa.
    application = QApplication(sys.argv)
    server = None

    while True:

        # Menu inicial do jogo: criar servidor, entrar em um servidor
        # ou sair do programa.
        mode, ok = QInputDialog.getItem(
            None,
            "Fanorona",
            "Escolha o modo:",
            ["Criar servidor", "Entrar em um servidor", "Sair"],
            0,
            False
        )

        if not ok or mode == "Sair":
            sys.exit(0)

        if mode == "Criar servidor":

            # Garante que apenas uma instância do servidor seja criada.
            if server is None:
                server = FanoronaServer()
                server.start()

            local_ip = get_local_ip()

            QMessageBox.information(
                None,
                "Servidor criado",
                f"Compartilhe este IP com o segundo jogador:\n\n{local_ip}\n\n"
                f"Depois escolha 'Entrar em um servidor' e digite este IP."
            )

            continue

        # O segundo jogador entra com o IP do primeiro jogador.
        ip, ok = QInputDialog.getText(
            None,
            "Conectar ao servidor",
            "Digite o IP do primeiro jogador:"
        )

        if not ok or not ip:
            continue

        # Cria a janela do jogo já conectada ao servidor informado.
        window = FanoronaGUI(host=ip)

        if server is not None:
            window.server = server

        window.show()

        sys.exit(
            application.exec()
        )
