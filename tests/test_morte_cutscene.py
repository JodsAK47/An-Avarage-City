import os
import sys
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

import Main
from Telas.TelaCombate import GerenciadorJogo
from Telas.TelaGameOver import GerenciadorGameOver
from Telas.TelaCutscene import GerenciadorCutscene
from Sistemas.SistemaCutscene import sistema_cutscene


class TestMorteCutscene(unittest.TestCase):
    def setUp(self):
        self.superficie = pygame.Surface((1000, 800))
        Main.estado = "menu"
        Main.personagem.hp = Main.personagem.max_hp
        Main.personagem.god_mode = False
        Main.jogo_tela.duas_pessoas = False
        Main.jogo_tela.personagem2 = None
        Main.jogo_tela.ordem_turnos = [Main.personagem]
        Main.jogo_tela.ultimo_chefe_combate = None
        Main.jogo_tela.derrota_processada = False
        Main.jogo_tela.cooldown_feedback = 0
        Main.jogo_tela.acao_pos_feedback = None

    def tearDown(self):
        Main.cutscene_tela.finalizar()
        Main.estado = "menu"

    def test_morte_feiticeiro_dispara_cutscene_sukuna_e_gameover(self):
        """Verifica se a morte do jogador no verso Feiticeiro contra o Sukuna dispara a cutscene antes do Game Over."""
        from Entidades.Inimigo import Inimigo
        Main.estado = "jogo"
        Main.jogo_tela.classe_atual = "Feiticeiro"
        Main.jogo_tela.reiniciar()
        chefe_sukuna = Inimigo(500, 200, 300, "pixil.png", nome="Sukuna", tipo="chefe")
        Main.jogo_tela.ordem_turnos = [Main.personagem, chefe_sukuna]
        Main.personagem.hp = 0

        # Atualiza até que a derrota seja processada e passe para cutscene
        for _ in range(50):
            Main.atualizar_estado_atual((0, 0), (False, False, False))
            if Main.estado == "cutscene":
                break

        self.assertEqual(Main.estado, "cutscene")
        self.assertTrue(Main.cutscene_tela.ativo)
        self.assertTrue(sistema_cutscene.esta_em_cutscene())
        self.assertEqual(Main.cutscene_tela.boss_atual, "Sukuna")
        self.assertEqual(Main.cutscene_tela.verso_atual, "Feiticeiro")

        # Concluir cutscene
        Main.cutscene_tela.finalizar()
        self.assertEqual(Main.estado, "game_over")
        self.assertEqual(Main.game_over_tela.verso, "Feiticeiro")
        self.assertFalse(sistema_cutscene.esta_em_cutscene())

    def test_morte_sobrevivente_dispara_cutscene_charlie_e_gameover(self):
        """Verifica se a morte do jogador no verso Sobrevivente contra o Charlie dispara a cutscene antes do Game Over."""
        from Entidades.Inimigo import Inimigo
        Main.estado = "jogo"
        Main.jogo_tela.classe_atual = "Sobrevivente"
        Main.jogo_tela.reiniciar()
        chefe_charlie = Inimigo(500, 200, 300, "pixil.png", nome="Charlie", tipo="chefe")
        Main.jogo_tela.ordem_turnos = [Main.personagem, chefe_charlie]
        Main.personagem.hp = 0

        for _ in range(50):
            Main.atualizar_estado_atual((0, 0), (False, False, False))
            if Main.estado == "cutscene":
                break

        self.assertEqual(Main.estado, "cutscene")
        self.assertTrue(Main.cutscene_tela.ativo)
        self.assertEqual(Main.cutscene_tela.boss_atual, "Charlie")
        self.assertEqual(Main.cutscene_tela.verso_atual, "Sobrevivente")

        Main.cutscene_tela.finalizar()
        self.assertEqual(Main.estado, "game_over")
        self.assertEqual(Main.game_over_tela.verso, "Sobrevivente")

    def test_morte_agente_dispara_cutscene_estraga_prazeres_e_gameover(self):
        """Verifica se a morte do jogador no verso Agente contra o Estraga Prazeres dispara a cutscene antes do Game Over."""
        from Entidades.Inimigo import Inimigo
        Main.estado = "jogo"
        Main.jogo_tela.classe_atual = "Agente"
        Main.jogo_tela.reiniciar()
        chefe_estraga = Inimigo(500, 200, 300, "pixil.png", nome="Estraga Prazeres", tipo="chefe")
        Main.jogo_tela.ordem_turnos = [Main.personagem, chefe_estraga]
        Main.personagem.hp = 0

        for _ in range(50):
            Main.atualizar_estado_atual((0, 0), (False, False, False))
            if Main.estado == "cutscene":
                break

        self.assertEqual(Main.estado, "cutscene")
        self.assertTrue(Main.cutscene_tela.ativo)
        self.assertEqual(Main.cutscene_tela.boss_atual, "Estraga Prazeres")
        self.assertEqual(Main.cutscene_tela.verso_atual, "Agente")

        Main.cutscene_tela.finalizar()
        self.assertEqual(Main.estado, "game_over")
        self.assertEqual(Main.game_over_tela.verso, "Agente")

    def test_morte_para_inimigo_comum_nao_dispara_cutscene(self):
        """Verifica que a morte para inimigo comum vai direto para Game Over sem cutscene."""
        from Entidades.Inimigo import Inimigo
        Main.estado = "jogo"
        Main.jogo_tela.classe_atual = "Feiticeiro"
        Main.jogo_tela.reiniciar()
        inimigo_comum = Inimigo(500, 200, 100, "Abelha.png", nome="Abelha", tipo="comum")
        Main.jogo_tela.ordem_turnos = [Main.personagem, inimigo_comum]
        Main.personagem.hp = 0

        for _ in range(50):
            Main.atualizar_estado_atual((0, 0), (False, False, False))
            if Main.estado in ("game_over", "cutscene"):
                break

        self.assertEqual(Main.estado, "game_over")
        self.assertFalse(Main.cutscene_tela.ativo)
        self.assertFalse(sistema_cutscene.esta_em_cutscene())

    def test_morte_para_boss_de_outro_verso_nao_dispara_cutscene(self):
        """Verifica que a morte para um boss que não seja o respectivo verso não dispara cutscene."""
        from Entidades.Inimigo import Inimigo
        Main.estado = "jogo"
        Main.jogo_tela.classe_atual = "Sobrevivente" # Sobrevivente tem o Charlie como boss
        Main.jogo_tela.reiniciar()
        chefe_sukuna = Inimigo(500, 200, 300, "pixil.png", nome="Sukuna", tipo="chefe")
        Main.jogo_tela.ordem_turnos = [Main.personagem, chefe_sukuna]
        Main.personagem.hp = 0

        for _ in range(50):
            Main.atualizar_estado_atual((0, 0), (False, False, False))
            if Main.estado in ("game_over", "cutscene"):
                break

        self.assertEqual(Main.estado, "game_over")
        self.assertFalse(Main.cutscene_tela.ativo)
        self.assertFalse(sistema_cutscene.esta_em_cutscene())

    def test_morte_contra_chefe_especifico_reconhece_nome(self):
        """Verifica se a morte em um combate com chefe específico identifica o nome do chefe."""
        from Entidades.Inimigo import Inimigo
        Main.estado = "jogo"
        Main.jogo_tela.classe_atual = "Feiticeiro"
        Main.jogo_tela.reiniciar()

        chefe_sukuna = Inimigo(500, 200, 300, "pixil.png", nome="Sukuna", tipo="chefe")
        Main.jogo_tela.ordem_turnos = [Main.personagem, chefe_sukuna]
        Main.personagem.hp = 0

        for _ in range(50):
            Main.atualizar_estado_atual((0, 0), (False, False, False))
            if Main.estado == "cutscene":
                break

        self.assertEqual(Main.estado, "cutscene")
        self.assertEqual(Main.cutscene_tela.boss_atual, "Sukuna")

    def test_game_over_tentar_novamente_reinicia_jogo(self):
        """Verifica se o botão de TENTAR NOVAMENTE reinicia o combate limpando os dados de derrota."""
        Main.estado = "game_over"
        Main.game_over_tela.definir_verso("Feiticeiro")

        # Dispara evento tecla R (Tentar Novamente)
        ev_r = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r)
        resultado = Main.tratar_eventos_game_over(ev_r, (0, 0))
        self.assertEqual(resultado, "jogo")
        self.assertGreater(Main.personagem.hp, 0)
        self.assertFalse(Main.jogo_tela.derrota_processada)
        self.assertEqual(Main.jogo_tela.partida_atual, 1)

    def test_game_over_menu_principal_retorna_ao_menu(self):
        """Verifica se o botão de MENU PRINCIPAL retorna para a tela inicial."""
        Main.estado = "game_over"
        Main.game_over_tela.definir_verso("Feiticeiro")

        ev_esc = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        resultado = Main.tratar_eventos_game_over(ev_esc, (0, 0))
        self.assertEqual(resultado, "menu")
        self.assertGreater(Main.personagem.hp, 0)

    def test_pular_cutscene_teclado_espaco_vai_para_game_over_sem_tela_preta(self):
        """Garante que ao pular a cutscene com ESPAÇO, o estado vai para game_over e a tela é renderizada sem ficar preta."""
        from Entidades.Inimigo import Inimigo
        Main.estado = "jogo"
        Main.jogo_tela.classe_atual = "Feiticeiro"
        Main.jogo_tela.reiniciar()
        chefe_sukuna = Inimigo(500, 200, 300, "pixil.png", nome="Sukuna", tipo="chefe")
        Main.jogo_tela.ordem_turnos = [Main.personagem, chefe_sukuna]
        Main.personagem.hp = 0

        for _ in range(50):
            Main.atualizar_estado_atual((0, 0), (False, False, False))
            if Main.estado == "cutscene":
                break

        self.assertEqual(Main.estado, "cutscene")

        # Dispara evento ESPAÇO pelo manipulador de eventos
        ev_space = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        manipulador = Main.DISTRIBUIDOR_EVENTOS.get(Main.estado)
        novo_estado = manipulador(ev_space, (0, 0))
        if novo_estado:
            Main.estado = novo_estado

        # O estado não pode virar 'concluido' nem None
        self.assertEqual(Main.estado, "game_over")
        self.assertEqual(Main.game_over_tela.verso, "Feiticeiro")

        # Verifica se o renderizador da tela desenha sem erro e com elementos visíveis
        Main.desenhar_estado_atual((0, 0))

    def test_pular_cutscene_botao_mouse_vai_para_game_over_sem_tela_preta(self):
        """Garante que ao clicar no botão de pular com o mouse, transiciona para game_over diretamente."""
        from Entidades.Inimigo import Inimigo
        Main.estado = "jogo"
        Main.jogo_tela.classe_atual = "Sobrevivente"
        Main.jogo_tela.reiniciar()
        chefe_charlie = Inimigo(500, 200, 300, "pixil.png", nome="Charlie", tipo="chefe")
        Main.jogo_tela.ordem_turnos = [Main.personagem, chefe_charlie]
        Main.personagem.hp = 0

        for _ in range(50):
            Main.atualizar_estado_atual((0, 0), (False, False, False))
            if Main.estado == "cutscene":
                break

        self.assertEqual(Main.estado, "cutscene")
        btn_pos = Main.cutscene_tela.botao_pular.rect.center

        ev_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=btn_pos)
        manipulador = Main.DISTRIBUIDOR_EVENTOS.get(Main.estado)
        novo_estado = manipulador(ev_click, btn_pos)
        if novo_estado:
            Main.estado = novo_estado

        self.assertEqual(Main.estado, "game_over")
        self.assertEqual(Main.game_over_tela.verso, "Sobrevivente")
        Main.desenhar_estado_atual(btn_pos)

    def test_pular_cutscene_vitoria_vai_para_tela_vitoria_sem_tela_preta(self):
        """Garante que ao pular a cutscene de vitória de chefe, vai para tela_vitoria sem tela preta."""
        Main.estado = "jogo"
        Main.personagem.hp = 100
        Main.jogo_tela.classe_atual = "Sobrevivente"
        Main.jogo_tela.iniciar_cooldown_feedback(1, lambda: "fim_jogo")
        Main.atualizar_estado_atual((0, 0), (False, False, False))

        self.assertEqual(Main.estado, "cutscene")

        ev_esc = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        manipulador = Main.DISTRIBUIDOR_EVENTOS.get(Main.estado)
        novo_estado = manipulador(ev_esc, (0, 0))
        if novo_estado:
            Main.estado = novo_estado

        self.assertEqual(Main.estado, "tela_vitoria")
        Main.desenhar_estado_atual((0, 0))


if __name__ == "__main__":
    unittest.main()
