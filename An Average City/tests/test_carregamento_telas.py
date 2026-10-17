import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

DIRETORIO_RAIZ = Path(__file__).resolve().parent.parent
if str(DIRETORIO_RAIZ) not in sys.path:
    sys.path.insert(0, str(DIRETORIO_RAIZ))

import pygame
pygame.init()
pygame.mixer.init()
tela = pygame.display.set_mode((1000, 800))

from Telas import (
    GerenciadorMenu,
    GerenciadorJogo,
    GerenciadorGameOver,
    GerenciadorClasses,
    GerenciadorVerso,
    GerenciadorVitoria,
    GerenciadorConquistasTela,
    GerenciadorCheatsTela,
    GerenciadorSewerTela,
    GerenciadorSelecao,
    GerenciadorPosLuta,
    GerenciadorDialogo,
    TelaInventario,
    GerenciadorConfiguracoesTela,
    GerenciadorPosDialogo,
)
from Sistemas import save_global, sistema_conquistas, inventario_global, sistema_config
from Entidades import Personagem, Inimigo
from Gameplay import GeradorFase, carregar_habilidades_jogador

def testar_inicializacao_completa():
    save_global.resetar_tudo()
    sistema_conquistas.resetar_todas()
    tela = pygame.Surface((1000, 800))

    telas = {
        "menu": GerenciadorMenu(tela),
        "jogo": GerenciadorJogo(tela),
        "game_over": GerenciadorGameOver(tela),
        "classes": GerenciadorClasses(tela),
        "verso": GerenciadorVerso(tela),
        "vitoria": GerenciadorVitoria(tela),
        "conquistas": GerenciadorConquistasTela(tela),
        "cheats": GerenciadorCheatsTela(tela),
        "sewer": GerenciadorSewerTela(tela),
        "selecao": GerenciadorSelecao(tela),
        "pos_luta": GerenciadorPosLuta(tela),
        "dialogo": GerenciadorDialogo(tela),
        "inventario": TelaInventario(tela),
        "configuracoes": GerenciadorConfiguracoesTela(tela),
        "pos_dialogo": GerenciadorPosDialogo(tela),
    }

    assert len(telas) == 15, "Todas as 15 telas devem ser instanciadas com sucesso."
    print("✓ Todas as 15 telas instanciadas com sucesso!")

    assert save_global.obter_pontos() == 0, "Save inicial deve ter 0 pontos."
    assert not save_global.tem_member_card(), "Save inicial nao deve ter o member card."
    assert sistema_conquistas.total_desbloqueadas() == 0, "Nenhuma conquista desbloqueada inicialmente."
    print("✓ Estado limpo do SaveSystem e Conquistas confirmado!")

    p = Personagem(0, 0)
    assert p.hp == 100
    from Gameplay import banco_habilidades
    carregar_habilidades_jogador()
    assert len(banco_habilidades) > 0, "Habilidades do jogador devem ser carregadas em banco_habilidades."
    print("✓ Entidades e banco de habilidades carregados com sucesso!")

    print("\nTODOS OS TESTES DE INTEGRAÇÃO PASSARAM COM SUCESSO!")

if __name__ == "__main__":
    testar_inicializacao_completa()
