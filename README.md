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

Este README resume o estado atual do projeto."(Gerado com Inteligencia artificial.)"
