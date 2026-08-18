# RPG Pygame - Jogo de Combate por Turnos em 2D ⚔️

Um jogo de RPG em 2D desenvolvido inteiramente em Python utilizando a biblioteca `pygame`. Este projeto apresenta um sistema clássico de combate por turnos, seleção de classes, progressão de atributos e uma mecânica interativa de esquiva de ataques.

## 🌟 Funcionalidades

* **Sistema de Batalha por Turnos:** Ordem de ataque definida dinamicamente pelo atributo de Agilidade (Iniciativa) das entidades.
* **Múltiplas Classes:** Escolha entre **Lutador** (foco em Força), **Manipulador** (foco em Inteligência/Magia) e **Arqueiro** (foco em Agilidade/Distância).
* **Progressão de Nível (RPG):** Ganha XP derrotando inimigos. Ao subir de nível, distribui pontos entre 5 atributos (Força, Agilidade, Constituição, Sabedoria, Intelecto) na tela de descanso.
* **Habilidades e Efeitos:** Diferentes habilidades com custo de PM (Mana), chance de acerto crítico e efeitos secundários, como *Congelamento* ou ataques *Em Área* (AoE).
* **Mecânica de Esquiva Interativa:** Durante o turno do inimigo, o jogador participa ativamente de um "Quick Time Event" (clicar no momento certo) para anular ou reduzir o dano recebido.
* **Múltiplos Cenários:** Escolha a dificuldade enfrentando diferentes grupos de monstros em fases variadas: *Floresta (Fácil)*, *Caverna (Médio)*, *Ruínas (Difícil)* e *Covil (Chefe)*.

## 📂 Estrutura do Projeto

Certifica-te de que o teu repositório tem a seguinte estrutura para que o jogo funcione corretamente (especialmente as pastas de *assets*):

```text
📁 Seu_Repositorio/
│
├── Main.py                # Ponto de entrada do jogo (Loop principal e Máquina de Estados)
├── Jogo.py                # Núcleo mecânico de combate e renderização da batalha
├── Menu.py                # Controlador do Menu Principal e classe base de Botões da UI
├── MenuClasses.py         # Tela de seleção de Arquétipo/Classe
├── Cenarios.py            # Tela de seleção de fases/dificuldades
├── Habilidades.py         # Banco de dados de ataques e magias
├── Descanço.py            # Tela de Status, XP e distribuição de Atributos
├── GameOver.py            # Tela de fim de jogo
│
├── 📁 Entidades/          # Lógica dos personagens do jogo
│   ├── Personagem.py      # Classe principal do Jogador
│   └── Inimigo.py         # Classe e gerador de inimigos por cenário
│
├── 📁 Sprites/            # [IMPORTANTE] Pasta para as imagens (.png)
│   ├── pixil.png          # Sprite do jogador
│   ├── Maldição1.png      # Sprite base dos inimigos
│   └── 📁 Botoes/         # Sprites de botões (base, hover, clique) - opcional
│
└── 📁 Ots's/              # [IMPORTANTE] Pasta para as músicas e sons (.mp3)
    ├── Menu.mp3
    ├── Combate.mp3
    ├── Boss.mp3
    └── GameOver.mp3
🚀 Como Executar o Jogo
Pré-requisitos
Precisarás de ter o Python instalado na sua máquina, bem como a biblioteca pygame.

Clone este repositório:

Bash
git clone [https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git](https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git)
Instala a dependência do Pygame:

Bash
pip install pygame
Executa o arquivo principal na pasta do projeto:

Bash
python Main.py
🎮 Controlos
Rato (Mouse): O jogo é inteiramente controlado via interface gráfica (Point and Click). Usa o clique esquerdo para interagir com menus, escolher habilidades, selecionar alvos, subir atributos e usar a barra de esquiva durante o combate.

🛠️ Modificações e Adições Próximas
[ ] Adicionar mais itens e sistema de inventário.

[ ] Melhorar as animações durante o uso de habilidades.

[ ] Adicionar mais músicas e efeitos sonoros (SFX) aos ataques.

Projeto desenvolvido como estudo de lógica de programação, orientação a objetos e desenvolvimento de jogos 2D utilizando Python e Pygame.

Este README Apresenta uma visão do projeto no dia 17 de agosto 2026.(ESTE DOCUMENTO FOI GERADO POR IA E VERIFICADO POR HUMANOS)
