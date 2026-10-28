import unittest
from unittest.mock import MagicMock, patch
import pygame
import os
import sys

DIRETORIO_RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "An Average City"))
if DIRETORIO_RAIZ not in sys.path:
    sys.path.insert(0, DIRETORIO_RAIZ)

# Ensure pygame display is initialized headless
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1000, 800))

from Telas import GerenciadorPausa, TelaPausa, GerenciadorJogo, TelaDescanso
import Main


def simular_clique(handler, pos):
    """Simula o ciclo completo de clique do mouse (DOWN e UP)."""
    ev_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos)
    handler(ev_down, pos)
    ev_up = pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=pos)
    return handler(ev_up, pos)


class TestMenuPausa(unittest.TestCase):
    def setUp(self):
        self.tela = pygame.Surface((1000, 800))
        self.pausa = GerenciadorPausa(self.tela)

    def test_instanciacao_e_botoes(self):
        """Verifica se os componentes e botões essenciais da tela de pausa foram instanciados."""
        self.assertIsNotNone(self.pausa.btn_continuar)
        self.assertIsNotNone(self.pausa.btn_config)
        self.assertIsNotNone(self.pausa.btn_menu)
        self.assertEqual(len(self.pausa.botoes), 3)

        # Verifica congelamento de estado
        self.pausa.abrir(estado_anterior="jogo")
        self.assertEqual(self.pausa.estado_anterior, "jogo")
        self.assertIsNotNone(self.pausa.superficie_fundo)

        self.pausa.fechar()
        self.assertIsNone(self.pausa.superficie_fundo)

    def test_teclas_atalho_continuar(self):
        """Pressionar ESC ou P deve retornar 'continuar'."""
        evento_esc = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        self.assertEqual(self.pausa.atualizar_eventos(evento_esc, (0, 0)), "continuar")

        evento_p = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p)
        self.assertEqual(self.pausa.atualizar_eventos(evento_p, (0, 0)), "continuar")

    def test_clique_botoes_pausa(self):
        """Testa o clique nos botões Continuar, Configurações e Menu."""
        # Clique em Continuar
        pos_continuar = (self.pausa.btn_continuar.rect.centerx, self.pausa.btn_continuar.rect.centery)
        resultado_continuar = simular_clique(self.pausa.atualizar_eventos, pos_continuar)
        self.assertEqual(resultado_continuar, "continuar")

        # Clique em Configurações
        pos_config = (self.pausa.btn_config.rect.centerx, self.pausa.btn_config.rect.centery)
        resultado_config = simular_clique(self.pausa.atualizar_eventos, pos_config)
        self.assertEqual(resultado_config, "config")

        # Clique em Tela de Título
        pos_menu = (self.pausa.btn_menu.rect.centerx, self.pausa.btn_menu.rect.centery)
        resultado_menu = simular_clique(self.pausa.atualizar_eventos, pos_menu)
        self.assertEqual(resultado_menu, "menu")

    def test_botao_pausa_combate(self):
        """Verifica que TelaCombate possui o botão de pausa no HUD e responde a cliques."""
        jogo_tela = GerenciadorJogo(self.tela)
        self.assertTrue(hasattr(jogo_tela, "btn_pausa"))
        self.assertEqual(jogo_tela.btn_pausa.texto, "⏸ MENU")

        # Teste de clique no botão de pausa durante combate via atualizar()
        pos_pausa = (jogo_tela.btn_pausa.rect.centerx, jogo_tela.btn_pausa.rect.centery)
        jogo_tela.clique_anterior = True
        resultado = jogo_tela.atualizar(pos_pausa, (False, False, False))
        self.assertEqual(resultado, "pausa")

        # Teste via tratar_eventos_jogo
        Main.jogo_tela = jogo_tela
        res_evento = simular_clique(Main.tratar_eventos_jogo, pos_pausa)
        self.assertEqual(res_evento, "pausa")

    def test_botao_pausa_descanso_inventario(self):
        """Verifica que TelaDescanso possui o botão de pausa e responde a ESC e clique."""
        descanso_tela = TelaDescanso(self.tela)
        self.assertTrue(hasattr(descanso_tela, "btn_pausa"))

        # Atalho ESC
        evento_esc = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        self.assertEqual(descanso_tela.atualizar_eventos(evento_esc, (0, 0)), "pausa")

        # Atalho P
        evento_p = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p)
        self.assertEqual(descanso_tela.atualizar_eventos(evento_p, (0, 0)), "pausa")

        # Clique no botão do HUD de descanso
        pos_pausa = (descanso_tela.btn_pausa.rect.centerx, descanso_tela.btn_pausa.rect.centery)
        resultado = simular_clique(descanso_tela.atualizar_eventos, pos_pausa)
        self.assertEqual(resultado, "pausa")

    def test_transicao_config_e_retorno_para_pausa(self):
        """Verifica que acessar Configurações a partir da Pausa retorna para Pausa ao sair."""
        Main.estado = "pausa"
        Main.pausa_tela.abrir("jogo")

        # Clica em Configurações no menu de pausa
        pos_config = (Main.pausa_tela.btn_config.rect.centerx, Main.pausa_tela.btn_config.rect.centery)
        novo_estado = simular_clique(Main.tratar_eventos_pausa, pos_config)
        self.assertEqual(novo_estado, "config")
        self.assertEqual(Main.estado_anterior_config, "pausa")

        # No menu de configurações, ao clicar em voltar ou ESC, deve retornar para 'pausa'
        evento_voltar = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        estado_retorno = Main.tratar_eventos_config(evento_voltar, (0, 0))
        self.assertEqual(estado_retorno, "pausa")

        # Ao continuar da pausa, deve retornar ao estado de origem ('jogo')
        evento_continuar = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        estado_final = Main.tratar_eventos_pausa(evento_continuar, (0, 0))
        self.assertEqual(estado_final, "jogo")

    def test_transicao_config_do_menu_principal(self):
        """Verifica que acessar Configurações pelo Menu Principal retorna para 'menu'."""
        Main.estado_anterior_config = "menu"
        evento_voltar = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        estado_retorno = Main.tratar_eventos_config(evento_voltar, (0, 0))
        self.assertEqual(estado_retorno, "menu")

    def test_retornar_ao_menu_principal_reseta_partida(self):
        """Verifica que escolher 'Tela de Título' reseta o estado da partida e volta ao menu."""
        Main.pausa_tela.abrir("jogo")
        Main.jogo_tela.partida_atual = 5
        Main.jogo_tela.pontos_jogo = 120

        pos_menu = (Main.pausa_tela.btn_menu.rect.centerx, Main.pausa_tela.btn_menu.rect.centery)
        resultado = simular_clique(Main.tratar_eventos_pausa, pos_menu)

        self.assertEqual(resultado, "menu")
        self.assertEqual(Main.jogo_tela.partida_atual, 1)
        self.assertIsNone(Main.pausa_tela.superficie_fundo)


    def test_switch_2p_sprites_on_off(self):
        """Verifica se o switch 2P usa SOFF.png quando desligado e SON.png quando ligado."""
        from Telas.TelaMenu import GerenciadorMenu
        menu = GerenciadorMenu(self.tela)

        # Estado inicial: Desligado (ativo=False) -> deve usar sprite_base (SOFF.png)
        self.assertFalse(menu.switch_2p.ativo)
        menu.switch_2p.atualizar((0, 0), (0, 0, 0))
        self.assertIs(menu.switch_2p.sprite_atual, menu.switch_2p.sprite_base)

        # Simula ligar o switch: Ligado (ativo=True) -> deve usar sprite_clique (SON.png)
        menu.switch_2p.ativo = True
        menu.switch_2p.atualizar((0, 0), (0, 0, 0))
        self.assertIs(menu.switch_2p.sprite_atual, menu.switch_2p.sprite_clique)

        # Garante que os sprites base e clique são distintos
        self.assertIsNot(menu.switch_2p.sprite_base, menu.switch_2p.sprite_clique)

if __name__ == "__main__":
    unittest.main()
