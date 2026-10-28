import os
import sys
import time
import unittest
from pathlib import Path

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

RAIZ = Path(__file__).resolve().parent.parent / "An Average City"
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import pygame
pygame.init()
pygame.mixer.init()

from Telas.TelaGameOver import GerenciadorGameOver
from Telas.TelaCutscene import GerenciadorCutscene
from Sistemas.SistemaCutscene import sistema_cutscene, SistemaCutscene
from Sistemas.Recursos import caminho_cutscene, caminho_cenario


class TestTelaGameOver(unittest.TestCase):
    def setUp(self):
        self.superficie = pygame.Surface((1000, 800))
        self.tela_game_over = GerenciadorGameOver(self.superficie)

    def test_inicializacao_camada_transparencia(self):
        """Verifica se a tela de Game Over possui camada preta de transparência."""
        self.assertIsNotNone(self.tela_game_over.camada_escurecimento)
        self.assertEqual(self.tela_game_over.camada_escurecimento.get_size(), (1000, 800))
        self.assertTrue(self.tela_game_over.camada_escurecimento.get_flags() & pygame.SRCALPHA)
        # Amostra da cor: deve ser preta com transparência (0, 0, 0, alpha > 0)
        cor_pixel = self.tela_game_over.camada_escurecimento.get_at((100, 100))
        self.assertEqual(cor_pixel[0], 0)
        self.assertEqual(cor_pixel[1], 0)
        self.assertEqual(cor_pixel[2], 0)
        self.assertGreater(cor_pixel[3], 100)

    def test_definir_versos(self):
        """Verifica configuração para todos os versos (Feiticeiro, Sobrevivente, Agente)."""
        for verso in ["Feiticeiro", "Sobrevivente", "Agente"]:
            self.tela_game_over.definir_verso(verso)
            self.assertEqual(self.tela_game_over.verso, verso)
            self.assertIsNotNone(self.tela_game_over.superficie_fundo_atual)
            self.assertEqual(self.tela_game_over.superficie_fundo_atual.get_size(), (1000, 800))

    def test_botoes_game_over(self):
        """Verifica existência e botões reiniciar e menu."""
        self.assertIsNotNone(self.tela_game_over.botao_reiniciar)
        self.assertIsNotNone(self.tela_game_over.botao_menu)
        self.assertEqual(self.tela_game_over.botao_reiniciar.texto, "TENTAR NOVAMENTE")
        self.assertEqual(self.tela_game_over.botao_menu.texto, "MENU PRINCIPAL")

    def test_eventos_teclado_game_over(self):
        """Verifica se teclas de atalho 'R' e 'ESC' respondem adequadamente."""
        evento_r = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r)
        self.assertEqual(self.tela_game_over.atualizar_eventos(evento_r, (0, 0)), "reiniciar")

        evento_esc = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        self.assertEqual(self.tela_game_over.atualizar_eventos(evento_esc, (0, 0)), "menu")

    def test_desenho_sem_erros(self):
        """Garante que a renderização da tela de Game Over não gere exceções."""
        self.tela_game_over.definir_verso("Feiticeiro")
        self.tela_game_over.pontos = 1500
        self.tela_game_over.desenhar()

        self.tela_game_over.definir_verso("Sobrevivente")
        self.tela_game_over.desenhar()

        self.tela_game_over.definir_verso("Agente")
        self.tela_game_over.desenhar()


class TestTelaCutscene(unittest.TestCase):
    def setUp(self):
        self.superficie = pygame.Surface((1000, 800))
        self.cutscene = GerenciadorCutscene(self.superficie)

    def tearDown(self):
        self.cutscene.finalizar()

    def test_inicializacao(self):
        """Verifica que a cutscene inicia inativa."""
        self.assertFalse(self.cutscene.ativo)
        self.assertFalse(self.cutscene.em_cutscene)
        self.assertIsNone(self.cutscene.cap)

    def test_sistema_cutscene_identifica_estado_ativo(self):
        """Verifica que o sistema identifica com precisão quando o jogo está no meio de uma cutscene."""
        self.assertFalse(sistema_cutscene.esta_em_cutscene())
        self.assertFalse(self.cutscene.em_cutscene)

        self.cutscene.iniciar(boss_nome="Sukuna", verso="Feiticeiro")
        self.assertTrue(sistema_cutscene.esta_em_cutscene())
        self.assertTrue(self.cutscene.em_cutscene)
        self.assertTrue(self.cutscene.esta_em_cutscene())
        self.assertEqual(sistema_cutscene.chefe_atual, "Sukuna")
        self.assertEqual(sistema_cutscene.verso_atual, "Feiticeiro")

        self.cutscene.finalizar()
        self.assertFalse(sistema_cutscene.esta_em_cutscene())
        self.assertFalse(self.cutscene.em_cutscene)
        self.assertFalse(self.cutscene.esta_em_cutscene())

    def test_camada_pixel_art_gerada_e_sobreposta(self):
        """Verifica a geração e sobreposição da camada de Pixel Art sobre o vídeo."""
        self.cutscene.iniciar(boss_nome="Sukuna", verso="Feiticeiro")
        self.assertTrue(self.cutscene.filtro_pixel_art)
        self.assertIsNotNone(self.cutscene.camada_pixel_art)
        self.assertEqual(self.cutscene.camada_pixel_art.get_size(), self.cutscene.tam_frame)
        self.assertTrue(self.cutscene.camada_pixel_art.get_flags() & pygame.SRCALPHA)

        # Renderização com a camada de pixel art ativa
        self.cutscene.desenhar()

    def test_funcoes_pixel_art_sistema(self):
        """Verifica os métodos de criação de camada e pixelização do SistemaCutscene."""
        camada = sistema_cutscene.criar_camada_pixel_art(400, 300, tamanho_pixel=4)
        self.assertEqual(camada.get_size(), (400, 300))
        self.assertTrue(camada.get_flags() & pygame.SRCALPHA)

        surf_teste = pygame.Surface((200, 100))
        surf_teste.fill((100, 150, 200))
        pixelada = sistema_cutscene.pixelar_superficie(surf_teste, tamanho_pixel=4)
        self.assertEqual(pixelada.get_size(), (200, 100))

    def test_cutscene_sukuna_feiticeiro(self):
        """Verifica carregamento da cutscene do Sukuna (Feiticeiro)."""
        concluido = False
        def cb():
            nonlocal concluido
            concluido = True

        self.cutscene.iniciar(boss_nome="Sukuna", verso="Feiticeiro", callback_conclusao=cb)
        self.assertTrue(self.cutscene.ativo)
        self.cutscene.atualizar((0, 0), (False, False, False))
        self.cutscene.desenhar()

        # Pular com ESPAÇO
        evento = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        res = self.cutscene.atualizar_eventos(evento, (0, 0))
        self.assertEqual(res, "concluido")
        self.assertFalse(self.cutscene.ativo)
        self.assertTrue(concluido)

    def test_cutscene_charlie_sobrevivente(self):
        """Verifica carregamento da cutscene do Charlie (Sobrevivente)."""
        concluido = False
        def cb():
            nonlocal concluido
            concluido = True

        self.cutscene.iniciar(boss_nome="Charlie", verso="Sobrevivente", callback_conclusao=cb)
        self.assertTrue(self.cutscene.ativo)
        self.cutscene.atualizar((0, 0), (False, False, False))
        self.cutscene.desenhar()

        # Pular com ESCAPE
        evento = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        res = self.cutscene.atualizar_eventos(evento, (0, 0))
        self.assertEqual(res, "concluido")
        self.assertFalse(self.cutscene.ativo)
        self.assertTrue(concluido)

    def test_cutscene_agente_placeholder(self):
        """Verifica placeholder cinemático para o boss Estraga Prazeres / Verso Agente."""
        concluido = False
        def cb():
            nonlocal concluido
            concluido = True

        self.cutscene.iniciar(boss_nome="Estraga Prazeres", verso="Agente", callback_conclusao=cb)
        self.assertTrue(self.cutscene.ativo)
        self.assertTrue(self.cutscene.eh_placeholder)
        self.cutscene.atualizar((0, 0), (False, False, False))
        self.cutscene.desenhar()

        # Pular clicando no botão de skip
        btn_pos = self.cutscene.botao_pular.rect.center
        evento_mouse = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=btn_pos)
        res = self.cutscene.atualizar_eventos(evento_mouse, btn_pos)
        self.assertEqual(res, "concluido")
        self.assertFalse(self.cutscene.ativo)
        self.assertTrue(concluido)

    def test_botao_skip_some_apos_2_segundos_sem_mover_mouse(self):
        """Verifica que o botão de skip some após 2 segundos com o mouse parado."""
        self.cutscene.iniciar(boss_nome="Sukuna", verso="Feiticeiro")
        self.assertTrue(self.cutscene.botao_pular_visivel)

        # Simular mouse parado na mesma posição por mais de 2 segundos
        pos_fixa = (500, 300)
        self.cutscene.posicao_mouse_anterior = pos_fixa
        self.cutscene.tempo_ultimo_movimento_mouse = time.perf_counter() - 2.5

        # Atualizar múltiplos frames para o fade-out se completar
        for _ in range(20):
            self.cutscene.atualizar(pos_fixa, (False, False, False))

        self.assertFalse(self.cutscene.botao_pular_visivel)
        self.assertEqual(self.cutscene.alpha_botao, 0.0)

    def test_botao_skip_ressurge_ao_mover_mouse(self):
        """Verifica que o botão de skip ressurge imediatamente ao mover o mouse."""
        self.cutscene.iniciar(boss_nome="Sukuna", verso="Feiticeiro")

        # Forçar botão a sumir
        pos_fixa = (500, 300)
        self.cutscene.posicao_mouse_anterior = pos_fixa
        self.cutscene.tempo_ultimo_movimento_mouse = time.perf_counter() - 2.5
        for _ in range(20):
            self.cutscene.atualizar(pos_fixa, (False, False, False))
        self.assertFalse(self.cutscene.botao_pular_visivel)

        # Mexer o mouse (nova posição)
        nova_pos = (550, 320)
        self.cutscene.atualizar(nova_pos, (False, False, False))

        # O botão deve ressurgir imediatamente
        self.assertTrue(self.cutscene.botao_pular_visivel)
        self.assertGreater(self.cutscene.alpha_botao, 0.0)

    def test_botao_skip_ressurge_ao_disparar_mousemotion(self):
        """Verifica que o evento MOUSEMOTION faz o botão ressurgir."""
        self.cutscene.iniciar(boss_nome="Sukuna", verso="Feiticeiro")

        # Forçar botão a sumir
        self.cutscene.botao_pular_visivel = False
        self.cutscene.alpha_botao = 0.0
        self.cutscene.posicao_mouse_anterior = (100, 100)

        # Disparar MOUSEMOTION
        ev_motion = pygame.event.Event(pygame.MOUSEMOTION, pos=(150, 120), rel=(50, 20), buttons=(0, 0, 0))
        self.cutscene.atualizar_eventos(ev_motion, (150, 120))

        self.assertTrue(self.cutscene.botao_pular_visivel)
        self.assertEqual(self.cutscene.alpha_botao, 255.0)

    def test_liberacao_recursos(self):
        """Verifica liberação completa de VideoCapture e canais de áudio na finalização."""
        self.cutscene.iniciar(boss_nome="Sukuna", verso="Feiticeiro")
        self.assertTrue(self.cutscene.ativo)
        self.cutscene.finalizar()
        self.assertFalse(self.cutscene.ativo)
        self.assertIsNone(self.cutscene.cap)
        self.assertIsNone(self.cutscene.canal_audio)


if __name__ == "__main__":
    unittest.main()
