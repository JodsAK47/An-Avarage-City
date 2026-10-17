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

from Sistemas.Configuracoes import (
    GerenciadorConfiguracoes,
    RESOLUCOES_DISPONIVEIS,
    PADRAO_LARGURA,
    PADRAO_ALTURA,
    PADRAO_VOLUME_GERAL,
    PADRAO_VOLUME_MUSICA,
    PADRAO_VOLUME_SFX,
)
from Telas.TelaConfiguracoes import GerenciadorConfiguracoesTela
from Telas.TelaMenu import GerenciadorMenu
import Main

def testar_gerenciador_configuracoes():
    config = GerenciadorConfiguracoes()

    assert config.obter_resolucao() in [(r[0], r[1]) for r in RESOLUCOES_DISPONIVEIS]
    config.restaurar_padroes()
    assert config.obter_resolucao() == (PADRAO_LARGURA, PADRAO_ALTURA)
    assert config.obter_tela_cheia() is False
    assert config.obter_volume_geral() == PADRAO_VOLUME_GERAL
    assert config.obter_volume_musica() == PADRAO_VOLUME_MUSICA
    assert config.obter_volume_sfx() == PADRAO_VOLUME_SFX
    assert config.esta_mutado() is False
    print("✓ Padrões de fábrica verificados com sucesso!")

    config.definir_volume_geral(1.5)
    assert config.obter_volume_geral() == 1.0, "Volume não deve ultrapassar 1.0"
    config.definir_volume_geral(-0.5)
    assert config.obter_volume_geral() == 0.0, "Volume não deve ser negativo"
    config.definir_volume_geral(0.8)

    config.definir_volume_musica(0.5)
    assert config.obter_volume_musica_efetivo() == 0.4, f"Efetivo esperado 0.4, obtido {config.obter_volume_musica_efetivo()}"

    config.definir_mudo(True)
    assert config.obter_volume_musica_efetivo() == 0.0, "Volume efetivo deve ser 0 quando mutado"
    assert config.obter_volume_sfx_efetivo() == 0.0

    config.alternar_mudo()
    assert config.esta_mutado() is False
    assert config.obter_volume_musica_efetivo() == 0.4
    print("✓ Controle e cálculos de volumes e mudo verificados!")

    res_atual = config.obter_resolucao()
    prox_res = config.proxima_resolucao()
    assert prox_res != res_atual
    ant_res = config.resolucao_anterior()
    assert ant_res == res_atual

    config.definir_resolucao(1920, 1080)
    assert config.obter_resolucao() == (1920, 1080)
    assert "1920 x 1080" in config.obter_texto_resolucao_atual()

    assert config.obter_tela_cheia() is False
    config.alternar_tela_cheia()
    assert config.obter_tela_cheia() is True
    config.definir_tela_cheia(False)
    assert config.obter_tela_cheia() is False
    print("✓ Navegação e alteração de resoluções e tela cheia verificados!")

    config.salvar()
    novo_config = GerenciadorConfiguracoes()
    assert novo_config.obter_resolucao() == (1920, 1080)
    assert novo_config.obter_volume_geral() == 0.8

    config.restaurar_padroes()
    print("✓ Persistência em JSON e recarregamento testados com sucesso!")

def simular_clique(manipulador, pos):
    ev_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": pos})
    manipulador(ev_down, pos)
    ev_up = pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": 1, "pos": pos})
    return manipulador(ev_up, pos)

def testar_tela_configuracoes_e_eventos():
    tela = pygame.Surface((1000, 800))
    tela_config = GerenciadorConfiguracoesTela(tela)

    tela_config.atualizar((500, 400), (False, False, False))
    tela_config.desenhar()
    print("✓ Renderização e ciclo de atualização da tela de configurações passaram!")

    res_voltar = simular_clique(tela_config.atualizar_eventos, tela_config.btn_voltar.rect.center)
    assert res_voltar == "menu", "Clique no botão voltar deve retornar 'menu'"

    ev_esc = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})
    res_esc = tela_config.atualizar_eventos(ev_esc, (0, 0))
    assert res_esc == "menu", "Pressionar ESC deve retornar 'menu'"

    btn_hd = tela_config.botoes_res_rapida[1]
    simular_clique(tela_config.atualizar_eventos, btn_hd["btn"].rect.center)
    from Sistemas.Configuracoes import sistema_config
    assert sistema_config.obter_resolucao() == (1280, 720)

    res_aplicar = simular_clique(tela_config.atualizar_eventos, tela_config.btn_aplicar_video.rect.center)
    assert res_aplicar == "video_alterado", "Aplicar vídeo deve retornar 'video_alterado'"

    mudo_antes = sistema_config.esta_mutado()
    simular_clique(tela_config.atualizar_eventos, tela_config.btn_mudo.rect.center)
    assert sistema_config.esta_mutado() != mudo_antes

    ev_clique_barra = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (tela_config.rect_barra_musica.x + 140, tela_config.rect_barra_musica.centery)})
    tela_config.atualizar_eventos(ev_clique_barra, (tela_config.rect_barra_musica.x + 140, tela_config.rect_barra_musica.centery))
    assert 0.45 <= sistema_config.obter_volume_musica() <= 0.55

    sistema_config.restaurar_padroes()
    print("✓ Todos os eventos e interações da TelaConfiguracoes testados com sucesso!")

def testar_integracao_menu_e_main():
    tela = pygame.Surface((1000, 800))
    menu = GerenciadorMenu(tela)

    assert "config" in menu.botoes, "O menu principal deve conter o botão 'config'"
    btn_config = menu.botoes["config"]
    assert btn_config.texto == "OPÇÕES"

    novo_estado = simular_clique(Main.tratar_eventos_menu, btn_config.rect.center)
    assert novo_estado == "config", "Clicar no botão OPÇÕES deve transicionar para 'config'"
    print("✓ Integração do menu e máquina de estados em Main.py validada!")

if __name__ == "__main__":
    testar_gerenciador_configuracoes()
    testar_tela_configuracoes_e_eventos()
    testar_integracao_menu_e_main()
    print("\nTODOS OS TESTES DO SISTEMA DE CONFIGURAÇÕES PASSARAM COM SUCESSO!")
