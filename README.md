# An Average City — RPG 2D em Pygame ⚔️🏙️

**An Average City** (Um Protótipo Médio) é um jogo de RPG 2D tático em turnos desenvolvido inteiramente em Python com a biblioteca **Pygame**. O projeto combina elementos de RPG clássico, ambientação urbana/cyberpunk contemporânea, combate estratégico, árvores de habilidades por arquétipos ("Versos"), minigames de esquiva em tempo real, modo cooperativo local e áreas secretas exploráveis.

---

## 🌟 Principais Funcionalidades

### ⚔️ 1. Sistema de Combate Tático por Turnos
- **Iniciativa Dinâmica:** A ordem de ação de jogadores e inimigos é calculada com base no atributo de Agilidade.
- **Habilidades & Ultimates:** Habilidades físicas, mágicas e de distância com custo de MP, precisão, efeitos de status (*Congelamento*, *Bloqueio*, etc.) e ataques em área (*AoE*).
- **Ataques Especiais (Ultimates):** Golpes devastadores únicos para cada combinação de Verso e Classe que consomem todo o MP do personagem.
- **Mecânica de Esquiva Interativa (QTE):** Durante o turno inimigo, uma barra de precisão em tempo real permite ao jogador sincronizar o clique para aparar, reduzir ou esquivar totalmente do dano.
- **Modo 2 Jogadores (Co-op Local):** Ative a chave de 2 Jogadores no menu para jogar com dois heróis em turnos cooperativos contra hordas de monstros e chefes.

### 🎭 2. Arquétipos (Versos) e Classes
- **Versos (Origens):**
  - 🛡️ **Sobrevivente:** Especialista em resistência, combate rústico e sustentabilidade.
  - 🕶️ **Agente:** Tático e furtivo, mestre em ataques críticos e armamentos precisos.
  - 🔮 **Feiticeiro:** Manipulador arcano focado em feitiços de alto dano e controle elemental.
- **Classes de Combate:** *Físico* (Força), *Distância* (Agilidade) e *Magia* (Intelecto).
- **Árvores de Talentos:** Desbloqueio progressivo de habilidades passivas e ativas com visualização em nós interativos.

### 📦 3. Inventário, Descanso e Progressão
- **Progressão por Atributos:** Ganho de XP e níveis para distribuição de pontos em 5 atributos centrais:
  - `For` (Força) — Dano físico corpo a corpo.
  - `Agi` (Agilidade) — Iniciativa de turnos e dano à distância.
  - `Con` (Constituição) — Aumento de Vida Máxima (HP).
  - `Sab` (Sabedoria) — Aumento de Mana Máxima (MP).
  - `Int` (Intelecto) — Poder mágico e eficácia de feitiços.
- **Sistema de Inventário:** Consumíveis (Poções de HP/MP) e Materiais (Sucata).
- **Forja e Melhoria:** Aprimoramento contínuo de armas e equipamentos consumindo sucata na tela de descanso.

### 🚪 4. Segredos, Esgoto e Terminal Hacker (Cheats)
- **Porta do Esgoto (*Sewer Access*):** Interaja com a porta da esquerda no menu para descer aos esgotos da cidade e encontrar o lendário *Member Card*.
- **Porta Restrita (*No Trespassing*):** Acesso trancado que só pode ser aberto com o *Member Card*, revelando o **Terminal Secreto de Cheats**.
- **Terminal de Cheats:** Funções de debug e testes (pontos infinitos, god mode, desbloqueio total de talentos, alteração de skins e níveis).

### 🏆 5. Sistema de Conquistas e Persistência
- **Galeria de Conquistas:** Painel dedicado com visualização de ícones em escala de cinza/coloridos e metas de desbloqueio.
- **Notificações Animadas (*Toasts*):** Avisos visuais em tempo real quando uma nova conquista é atingida.
- **Save Global:** Persistência automática em JSON (`Dados/save.json`), guardando recorde de pontuação, pontos acumulados, estado do cartão e conquistas liberadas.

---

## 📂 Arquitetura e Estrutura do Projeto

O código-fonte é organizado de forma modular, desacoplada e escalável:

```
Um Prototipo medio/
│
├── Main.py                     # Ponto de entrada do jogo (Loop principal e orquestrador)
│
├── Telas/                      # Carregadores e gerenciadores de telas (Screen Loaders)
│   ├── __init__.py             # Exporta todos os gerenciadores de telas
│   ├── TelaMenu.py             # Menu principal e portas interativas
│   ├── TelaCombate.py          # Gerenciador de batalha, turnos e combate
│   ├── TelaClasses.py          # Seleção de classes (Físico, Distância, Magia)
│   ├── TelaVerso.py            # Árvore de talentos e arquétipos
│   ├── TelaCenarios.py         # Seleção de desafios e rotas
│   ├── TelaDescanco.py         # Tela pós-luta, distribuição de atributos e forja
│   ├── TelaDialogo.py          # Sobreposição de diálogos narrativos
│   ├── TelaInventario.py       # Interface visual do inventário e consumíveis
│   ├── TelaCheats.py           # Terminal de trapaças / painel hacker
│   ├── TelaConquistas.py       # Galeria de conquistas
│   ├── TelaSewer.py            # Exploração do esgoto e coleta do Member Card
│   ├── TelaGameOver.py         # Tela de derrota e registro de pontuação
│   └── TelaVitoria.py          # Tela de vitória contra o chefe
│
├── Sistemas/                   # Motores centrais, persistência e utilitários
│   ├── __init__.py             # Exporta sistemas e componentes
│   ├── Recursos.py             # Resolução dinâmica da raiz do projeto e caminhos universais
│   ├── Fontes.py               # Tipografia e utilitário de quebra de texto
│   ├── SaveSystem.py           # Persistência de dados (Dados/save.json)
│   ├── Conquistas.py           # Lógica e registro de conquistas (Dados/conquistas.json)
│   ├── Inventario.py           # Lógica de itens, equipamentos e consumíveis
│   └── SistemaUI.py            # Framework de UI (Botao, TelaBase, GerenciadorTelas)
│
├── Gameplay/                   # Regras de gameplay e geração procedural
│   ├── __init__.py             # Exporta habilidades e gerador de fases
│   ├── GeracaoFases.py         # Gerador de encontros e inimigos procedurais
│   └── Habilidades.py          # Carregador de habilidades e Ultimates
│
├── Entidades/                  # Modelos de personagens e inimigos
│   ├── __init__.py             # Exporta Personagem e Inimigo
│   ├── Personagem.py           # Entidade do jogador e atributos globais
│   └── Inimigo.py              # Entidade dos monstros e chefes
│
├── Dados/                      # Base de dados estruturada em JSON
│   ├── arvores.json            # Nós e talentos dos Versos
│   ├── conquistas.json         # Metas e dados de conquistas
│   ├── eventos.json            # Eventos neutros de fases
│   ├── habilidades_jogador.json# Lista de habilidades e ultimates dos heróis
│   ├── habilidades_inimigos.json# Habilidades e golpes dos monstros
│   ├── inimigos.json           # Templates de inimigos e chefes
│   └── save.json               # Save game persistente
│
├── Sprites/                    # Texturas, planos de fundo e botões (.png)
├── Fontes/                     # Fontes tipográficas (.ttf)
└── OSTs/                       # Trilhas sonoras originais (.mp3)
```

---

## 🚀 Como Executar o Jogo

### Pré-requisitos
- **Python 3.10 ou superior** instalado.
- Biblioteca **Pygame**.

### 1. Clonar o Repositório
```bash
git clone https://github.com/JodsAK47/An-Avarage-City.git
```

### 2. Acessar a pasta do projeto
```bash
cd "An-Avarage-City/Um Prototipo medio"
```

### 3. Instalar as Dependências
```bash
pip install pygame
```

### 4. Iniciar o Jogo
```bash
python Main.py
```
*(ou `py Main.py` no Windows)*

---

## 🎮 Controles

| Ação | Controle |
| :--- | :--- |
| **Navegação nos Menus** | Botão Esquerdo do Mouse |
| **Ações de Combate** | Clique sobre as habilidades / alvos |
| **Minigame de Esquiva (QTE)** | Clique no momento exato em que o ponteiro atingir a área destacada |
| **Diálogos** | Clique na tela, `Enter` ou setas `▲ / ▼` do teclado |
| **Ativar 2 Jogadores** | Clique no botão alternador no topo superior direito do Menu Principal |
| **Segredos no Menu** | Clique na porta da esquerda (Esgoto) ou na porta da direita (Cheats com cartão) |

---

## 🛠️ Tecnologias e Padrões de Projeto

- **Linguagem:** Python 3.13
- **Engine Gráfica / Áudio:** Pygame 2.6
- **Padrões de Arquitetura:**
  - *State Pattern* / Máquina de Estados para gerenciamento de telas.
  - *Data-Driven Design* com JSON para habilidades, inimigos, eventos e árvores de talentos.
  - *Factory & Encapsulation* no framework de interface gráfica (`SistemaUI.py`).
  - *Dynamic Root Resolution* para execução transparente independente do diretório de chamada.

---

## 📄 Licença

Este projeto é desenvolvido para fins educacionais e estudo de desenvolvimento de jogos 2D, lógica de programação e arquitetura de software orientada a objetos.
