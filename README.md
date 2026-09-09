# Fanorona

## Apresentação do Projeto

Este trabalho apresenta a implementação do jogo Fanorona em Python, com interface gráfica desenvolvida em PySide6 e comunicação entre jogadores por meio de sockets TCP.

O objetivo principal do projeto foi desenvolver uma versão funcional do jogo que permita partidas em rede, com um jogador assumindo o papel de servidor e outro conectando-se por meio de um endereço IP.

## Objetivos

- Implementar a lógica do jogo Fanorona;
- criar uma interface gráfica interativa para o tabuleiro e ações do jogador;
- permitir partidas locais e em rede;
- disponibilizar uma forma prática de execução por meio de um executável.

## Tecnologias Utilizadas

- Python
- PySide6
- Socket TCP
- JSON para troca de mensagens
- PyInstaller para geração do executável

## Funcionalidades

- Criação de servidor pelo primeiro jogador;
- conexão de um segundo jogador por IP;
- chat integrado entre os jogadores;
- troca de turno;
- possibilidade de desfazer jogada, passar a vez e desistir;
- interface visual com tabuleiro, status e painel lateral.

## Estrutura do Projeto

- `main.py` — ponto de entrada do programa e seleção de modo de execução;
- `game_window.py` — interface principal do jogo;
- `game_server.py` — lógica do servidor e controle das partidas;
- `network_client.py` — cliente responsável pela conexão com o servidor;
- `board_widget.py` — desenho e interação com o tabuleiro.

## Como Executar

### Requisitos

- Python 3.10 ou superior
- PySide6
- PyInstaller (opcional, apenas para empacotar o jogo)

### Executar diretamente

```bash
py main.py
```

### Gerar o executável

```bash
pyinstaller --onefile --windowed --name Fanorona main.py
```

O executável será gerado na pasta `dist`.

## Modo de Jogo

### Primeiro jogador
1. Executa o programa;
2. Seleciona a opção `Criar servidor`;
3. Compartilha o IP exibido;
4. Depois, retorna ao menu e seleciona `Entrar em um servidor` para continuar no jogo como cliente local.

### Segundo jogador
1. Executa o programa;
2. Seleciona a opção `Entrar em um servidor`;
3. Digita o IP do primeiro jogador;
4. Inicia a partida na mesma rede local.

## Observações

- A aplicação foi desenvolvida para funcionar em rede local;
- a porta utilizada pelo servidor é a `5000`;
- o professor pode testar o jogo em duas máquinas na mesma rede ou em duas instâncias do programa no mesmo computador, utilizando o IP local.

## Conclusão

O projeto demonstra a aplicação prática de conceitos de programação orientada a objetos, interface gráfica, comunicação em rede e empacotamento de software. A versão entregue permite a execução do jogo Fanorona em ambiente local com interação entre dois jogadores, além de facilitar a apresentação e a avaliação do trabalho.

## Licença

Este projeto foi desenvolvido para fins acadêmicos e de estudo.
