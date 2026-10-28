import os
import sys
import unittest
from pathlib import Path

# Headless pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"

RAIZ = Path(__file__).resolve().parent.parent / "An Average City"
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import pygame
pygame.init()
pygame.display.set_mode((1000, 780))

from Telas.TelaVerso import GerenciadorVerso
from Sistemas.SaveSystem import save_global
from Entidades.Personagem import personagem
import Main


class TestTelaVerso(unittest.TestCase):
    def setUp(self):
        self.tela = pygame.display.get_surface()
        save_global.resetar_tudo()
        self.verso = GerenciadorVerso(self.tela)
        self.verso.sincronizar_habilidades_ativas()

    def _clicar_botao(self, btn):
        pos = (btn.rect.centerx, btn.rect.centery)
        evt_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": pos})
        self.verso.atualizar_eventos(evt_down, pos)
        evt_up = pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": 1, "pos": pos})
        return self.verso.atualizar_eventos(evt_up, pos)

    def test_identificacao_visual_orbes(self):
        """Testa se as cores das orbes seguem: Verde (liberado), Vermelho (desabilitado),
        Amarelo (sem dinheiro), Cinza (requer anterior)."""
        save_global.definir_pontos(0)
        self.verso.verso_atual = "Sobrevivente"
        self.verso.sincronizar_habilidades_ativas()
        arvore = self.verso.obter_arvore_ativa()

        hab_s1 = next(h for h in arvore if h["id"] == "S1")
        hab_s2 = next(h for h in arvore if h["id"] == "S2")

        # Teste S1 (Sem dinheiro o bastante -> Amarelo)
        req_ok_s1 = all(req in self.verso.habilidades_desbloqueadas for req in hab_s1["req"])
        self.assertTrue(req_ok_s1)
        self.assertNotIn("S1", self.verso.habilidades_desbloqueadas)
        self.assertLess(self.verso.pontos, hab_s1["preco"])

        # Teste S2 (Requer anterior -> Cinza)
        req_ok_s2 = all(req in self.verso.habilidades_desbloqueadas for req in hab_s2["req"])
        self.assertFalse(req_ok_s2)

        # Desbloqueia S1 -> Deve ficar Verde (Liberado)
        save_global.definir_progresso_verso("Sobrevivente", ["S1"])
        self.verso.sincronizar_habilidades_ativas()
        self.assertIn("S1", self.verso.habilidades_desbloqueadas)
        self.assertNotIn("S1", self.verso.habilidades_desabilitadas.get("Sobrevivente", set()))

        # Desabilita S1 -> Deve ficar Vermelho (Desabilitado)
        self.verso.habilidade_foco = hab_s1
        self.verso.alternar_habilidade_foco()
        self.assertIn("S1", self.verso.habilidades_desabilitadas["Sobrevivente"])
        self.assertNotIn("S1", personagem.talentos)

    def test_botao_habilitar_desabilitar_menu(self):
        """Testa o botão substituir 'escolher verso' por 'habilitar/desabilitar habilidade' no modo menu."""
        self.verso.modo = "menu"
        save_global.definir_progresso_verso("Sobrevivente", ["S1"])
        self.verso.sincronizar_habilidades_ativas()
        hab_s1 = next(h for h in self.verso.obter_arvore_ativa() if h["id"] == "S1")

        # Foca S1 habilitada
        self.verso.habilidade_foco = hab_s1
        self.verso.atualizar((0, 0), (False, False, False))
        self.assertEqual(self.verso.botao_selecionar.texto, "DESABILITAR HABILIDADE")

        # Clica para desabilitar
        self._clicar_botao(self.verso.botao_selecionar)

        # Agora deve estar desabilitada e botão deve oferecer HABILITAR
        self.assertIn("S1", self.verso.habilidades_desabilitadas["Sobrevivente"])
        self.assertNotIn("S1", personagem.talentos)
        self.verso.atualizar((0, 0), (False, False, False))
        self.assertEqual(self.verso.botao_selecionar.texto, "HABILITAR HABILIDADE")

        # Clica novamente para reabilitar
        self._clicar_botao(self.verso.botao_selecionar)
        self.assertNotIn("S1", self.verso.habilidades_desabilitadas["Sobrevivente"])
        self.assertIn("S1", personagem.talentos)

    def test_modo_visualizacao_mantem_confirmar_verso(self):
        """Garante que na tela de início de jogo (modo visualizacao), o botão continua sendo CONFIRMAR VERSO."""
        self.verso.modo = "visualizacao"
        self.verso.verso_atual = "Feiticeiro"
        self.verso.atualizar((0, 0), (False, False, False))
        self.assertEqual(self.verso.botao_selecionar.texto, "CONFIRMAR VERSO")

        resultado = self._clicar_botao(self.verso.botao_selecionar)
        self.assertEqual(resultado, "Feiticeiro")

    def test_desabilitar_ultimate_bloqueia_uso(self):
        """Verifica se desabilitar a habilidade de ultimate (ex: S4) remove o uso da ultimate do personagem."""
        save_global.definir_progresso_verso("Sobrevivente", ["S1", "S2", "S3", "S4"])
        self.verso.verso_atual = "Sobrevivente"
        self.verso.sincronizar_habilidades_ativas()

        self.assertIn("Sobrevivente", personagem.ultimates_desbloqueadas)

        hab_s4 = next(h for h in self.verso.obter_arvore_ativa() if h["id"] == "S4")
        self.verso.habilidade_foco = hab_s4
        self.verso.alternar_habilidade_foco()

        self.assertNotIn("Sobrevivente", personagem.ultimates_desbloqueadas)
        self.assertNotIn("S4", personagem.talentos)

        # Reabilita
        self.verso.alternar_habilidade_foco()
        self.assertIn("Sobrevivente", personagem.ultimates_desbloqueadas)
        self.assertIn("S4", personagem.talentos)

    def test_reset_jogo_limpa_desabilitadas(self):
        """Verifica se o reset do jogo restaura as habilidades desabilitadas."""
        self.verso.verso_atual = "Agente"
        self.verso.habilidades_desbloqueadas = ["A1"]
        self.verso.habilidades_desabilitadas["Agente"] = {"A1"}
        save_global.definir_habilidades_desabilitadas("Agente", ["A1"])
        save_global.salvar()

        Main.resetar_jogo()

        self.assertEqual(len(Main.verso_tela.habilidades_desabilitadas.get("Agente", set())), 0)
        self.assertEqual(len(save_global.obter_habilidades_desabilitadas("Agente")), 0)


    def test_fluxo_escolha_versos_2_jogadores(self):
        """Verifica o fluxo completo de escolha de versos e classes para Player 1 e Player 2."""
        Main.reiniciar_para_menu()
        Main.menu_tela.duas_pessoas = True

        # 1. Menu -> J1 escolhe Verso
        btn_jogar = Main.menu_tela.botoes["jogar"]
        pos_jogar = (btn_jogar.rect.centerx, btn_jogar.rect.centery)
        ev_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": pos_jogar})
        Main.tratar_eventos_menu(ev_down, pos_jogar)
        ev_up = pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": 1, "pos": pos_jogar})
        estado = Main.tratar_eventos_menu(ev_up, pos_jogar)
        self.assertEqual(estado, "verso")
        self.assertEqual(Main.alvo_classes, 1)
        self.assertEqual(Main.verso_tela.aviso, "Escolha o Verso para JOGADOR 1")

        # 2. J1 escolhe Feiticeiro
        Main.verso_tela.verso_atual = "Feiticeiro"
        btn_conf_verso = Main.verso_tela.botao_selecionar
        pos_conf_v = (btn_conf_verso.rect.centerx, btn_conf_verso.rect.centery)
        ev_down_v = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": pos_conf_v})
        Main.tratar_eventos_verso(ev_down_v, pos_conf_v)
        ev_up_v = pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": 1, "pos": pos_conf_v})
        estado = Main.tratar_eventos_verso(ev_up_v, pos_conf_v)
        self.assertEqual(estado, "classes")
        self.assertEqual(Main.verso_jogador1, "Feiticeiro")
        self.assertIn("J1: Feiticeiro", Main.classes_tela.aviso)

        # 3. J1 escolhe Magia -> Transiciona para J2 escolher Verso
        Main.classes_tela.classe_atual = "Magia"
        btn_conf_classe = Main.classes_tela.botao_selecionar
        pos_conf_c = (btn_conf_classe.rect.centerx, btn_conf_classe.rect.centery)
        ev_down_c = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": pos_conf_c})
        Main.tratar_eventos_classes(ev_down_c, pos_conf_c)
        ev_up_c = pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": 1, "pos": pos_conf_c})
        estado = Main.tratar_eventos_classes(ev_up_c, pos_conf_c)
        self.assertEqual(estado, "verso")
        self.assertEqual(Main.alvo_classes, 2)
        self.assertEqual(Main.verso_tela.aviso, "Escolha o Verso para JOGADOR 2")

        # 4. J2 escolhe Agente
        Main.verso_tela.verso_atual = "Agente"
        Main.tratar_eventos_verso(ev_down_v, pos_conf_v)
        estado = Main.tratar_eventos_verso(ev_up_v, pos_conf_v)
        self.assertEqual(estado, "classes")
        self.assertEqual(Main.verso_jogador2, "Agente")
        self.assertIn("J2: Agente", Main.classes_tela.aviso)

        # 5. J2 escolhe Distância -> Inicia o Jogo!
        Main.classes_tela.classe_atual = "Distância"
        Main.tratar_eventos_classes(ev_down_c, pos_conf_c)
        estado = Main.tratar_eventos_classes(ev_up_c, pos_conf_c)
        self.assertEqual(estado, "jogo")

        # Validação final das configurações de combate
        self.assertEqual(Main.jogo_tela.classe_atual, "Feiticeiro")
        self.assertEqual(Main.jogo_tela.classe_dano_atual, "Magia")
        self.assertEqual(Main.jogo_tela.classe_jogador2, "Agente")
        self.assertEqual(Main.jogo_tela.classe_jogador2_tipo, "Distância")
        self.assertTrue(Main.jogo_tela.duas_pessoas)
        self.assertIsNotNone(Main.jogo_tela.personagem2)

    def test_fluxo_voltar_navegacao_2_jogadores(self):
        """Verifica a navegação para trás entre as telas com 2 jogadores."""
        Main.reiniciar_para_menu()
        Main.menu_tela.duas_pessoas = True
        Main.verso_jogador1 = "Feiticeiro"
        Main.verso_jogador2 = "Agente"

        # Simula J2 na tela de classe clicando em VOLTAR -> deve voltar para J2 Verso
        Main.alvo_classes = 2
        Main.classes_tela.voltar_clicado = True
        estado = Main.tratar_eventos_classes(pygame.event.Event(pygame.NOEVENT), (0, 0))
        self.assertEqual(estado, "verso")
        self.assertEqual(Main.alvo_classes, 2)
        self.assertEqual(Main.verso_tela.aviso, "Escolha o Verso para JOGADOR 2")

        # Simula J2 na tela de verso clicando em VOLTAR -> deve voltar para J1 Classe
        Main.verso_tela.voltar_clicado = True
        estado = Main.tratar_eventos_verso(pygame.event.Event(pygame.NOEVENT), (0, 0))
        self.assertEqual(estado, "classes")
        self.assertEqual(Main.alvo_classes, 1)

        # Simula J1 na tela de classe clicando em VOLTAR -> deve voltar para J1 Verso
        Main.classes_tela.voltar_clicado = True
        estado = Main.tratar_eventos_classes(pygame.event.Event(pygame.NOEVENT), (0, 0))
        self.assertEqual(estado, "verso")
        self.assertEqual(Main.alvo_classes, 1)

        # Simula J1 na tela de verso clicando em VOLTAR -> deve voltar para Menu
        Main.verso_tela.voltar_clicado = True
        estado = Main.tratar_eventos_verso(pygame.event.Event(pygame.NOEVENT), (0, 0))
        self.assertEqual(estado, "menu")
        self.assertIsNone(Main.alvo_classes)


if __name__ == "__main__":
    unittest.main()
