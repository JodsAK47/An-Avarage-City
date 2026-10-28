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

from Telas.TelaCheats import GerenciadorCheatsTela
from Gameplay.GeracaoFases import BANCO_INIMIGOS
from Entidades.Santuario import Santuario
import Main


class TestCheatsBatalha(unittest.TestCase):
    def setUp(self):
        self.tela = pygame.display.get_surface()
        self.cheats = GerenciadorCheatsTela(self.tela)

    def _clicar_botao(self, btn):
        pos = (btn.rect.centerx, btn.rect.centery)
        evt_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": pos})
        self.cheats.atualizar_eventos(evt_down, pos)
        evt_up = pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": 1, "pos": pos})
        return self.cheats.atualizar_eventos(evt_up, pos)

    def test_cheats_modo_e_transicao(self):
        self.assertEqual(self.cheats.modo, "cheats")
        # Simula clique no botão de batalha personalizada
        resultado = self._clicar_botao(self.cheats.btn_batalha_custom)
        self.assertIsNone(resultado)
        self.assertEqual(self.cheats.modo, "seletor_batalha")

        # Simula ESC para voltar
        evento_esc = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})
        self.cheats.atualizar_eventos(evento_esc, (0, 0))
        self.assertEqual(self.cheats.modo, "cheats")

    def test_seletor_adicionar_e_limitar_inimigos(self):
        self.cheats.modo = "seletor_batalha"
        self.assertEqual(len(self.cheats.equipe_selecionada), 0)

        tmpl_confinamento = next((t for t in BANCO_INIMIGOS if t.get("nome") == "Confinamento"), None)
        self.assertIsNotNone(tmpl_confinamento)

        for _ in range(6):
            if len(self.cheats.equipe_selecionada) < 4:
                self.cheats.equipe_selecionada.append(tmpl_confinamento)
        self.assertEqual(len(self.cheats.equipe_selecionada), 4)

        self.cheats.equipe_selecionada.pop(0)
        self.assertEqual(len(self.cheats.equipe_selecionada), 3)

        self.cheats.equipe_selecionada.clear()
        self.assertEqual(len(self.cheats.equipe_selecionada), 0)

    def test_iniciar_batalha_customizada_vazia(self):
        self.cheats.modo = "seletor_batalha"
        self.cheats.equipe_selecionada.clear()
        resultado = self._clicar_botao(self.cheats.btn_iniciar_batalha_custom)
        self.assertIsNone(resultado)

    def test_iniciar_batalha_customizada_com_selecao(self):
        self.cheats.modo = "seletor_batalha"
        self.cheats.equipe_selecionada.clear()
        tmpl = BANCO_INIMIGOS[0]
        self.cheats.equipe_selecionada.append(tmpl)
        self.cheats.equipe_selecionada.append(tmpl)

        # Clicar em iniciar
        resultado = self._clicar_botao(self.cheats.btn_iniciar_batalha_custom)
        self.assertIsInstance(resultado, tuple)
        self.assertEqual(resultado[0], "batalhar_custom")
        self.assertEqual(len(resultado[1]), 2)

        # Testar tecla ENTER
        evt_enter = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RETURN})
        res_enter = self.cheats.atualizar_eventos(evt_enter, (0, 0))
        self.assertIsInstance(res_enter, tuple)
        self.assertEqual(res_enter[0], "batalhar_custom")

    def test_iniciar_batalha_customizada_duplicatas_e_posicoes(self):
        equipe_nomes = ["Confinamento", "Confinamento", "Sukuna", "Torreta"]
        resultado = Main.iniciar_batalha_customizada(equipe_nomes)
        self.assertEqual(resultado, "jogo")

        inimigos_em_combate = [e for e in Main.jogo_tela.ordem_turnos if Main.jogo_tela.eh_inimigo(e)]
        self.assertEqual(len(inimigos_em_combate), 4)

        nomes_em_combate = [e.nome for e in inimigos_em_combate]
        self.assertIn("Confinamento #1", nomes_em_combate)
        self.assertIn("Confinamento #2", nomes_em_combate)
        self.assertIn("Sukuna", nomes_em_combate)
        self.assertIn("Torreta", nomes_em_combate)

        # Checa se os confinamentos receberam a mecânica de carga
        confinamentos = [e for e in inimigos_em_combate if "confinamento" in e.nome.lower()]
        self.assertEqual(len(confinamentos), 2)
        for conf in confinamentos:
            self.assertTrue(getattr(conf, "eh_confinamento", False))
            self.assertEqual(getattr(conf, "carga_confinamento", 0), 0)
            self.assertEqual(getattr(conf, "max_carga_confinamento", 5), 5)

        # Como Sukuna é chefe, música de chefe deve ser ativada
        self.assertEqual(Main.jogo_tela.musica_luta, "Feiticeiro Boss.mp3")

    def test_iniciar_batalha_sukuna_invocacao_santuario(self):
        """Garante que a batalha contra Sukuna e a invocação do Santuário ocorram sem erros de atributo."""
        resultado = Main.iniciar_batalha_customizada(["Sukuna"])
        self.assertEqual(resultado, "jogo")

        sukunas = [e for e in Main.jogo_tela.ordem_turnos if "sukuna" in e.nome.lower()]
        self.assertEqual(len(sukunas), 1)
        sukuna = sukunas[0]

        # Invoca Santuário pelo Sukuna
        santuario = Main.jogo_tela.invocar_santuario(dono=sukuna)
        self.assertIsNotNone(santuario)
        self.assertEqual(santuario.hp, 100)
        self.assertEqual(santuario.golpes_restantes(), 4)

        # Atualiza tela de combate sem erros
        Main.jogo_tela.atualizar((0, 0), (False, False, False))
        Main.desenhar_estado_atual((0, 0))


    def test_cheats_tela_resetar(self):
        """Testa se o método resetar da tela de cheats restaura o estado padrão."""
        self.cheats.modo = "seletor_batalha"
        self.cheats.equipe_selecionada.append(BANCO_INIMIGOS[0])
        self.cheats.filtro_verso = "Feiticeiro"
        Main.personagem.god_mode = True
        Main.personagem.max_hp = 999
        Main.personagem.hp = 999
        Main.personagem.trocar_skin("Sukuna1.png")
        self.cheats.btn_godmode.texto = "GOD MODE: ATIVADO (ON)"

        self.cheats.resetar()

        self.assertEqual(self.cheats.modo, "cheats")
        self.assertEqual(len(self.cheats.equipe_selecionada), 0)
        self.assertEqual(self.cheats.filtro_verso, "TODOS")
        self.assertFalse(Main.personagem.god_mode)
        self.assertEqual(Main.personagem.hp, 100)
        self.assertEqual(Main.personagem.max_hp, 100)
        self.assertEqual(Main.personagem.nome_imagem, "pixil.png")
        self.assertEqual(self.cheats.btn_godmode.texto, "GOD MODE: DESATIVADO")

    def test_reset_jogo_reseta_menu_cheats_e_efeitos(self):
        """Garante que o reset do jogo (menu principal) reseta também o menu de cheats."""
        # Configura trapaças ativas
        Main.save_global.coletar_member_card()
        Main.save_global.adicionar_pontos(999999)
        Main.personagem.god_mode = True
        Main.personagem.max_hp = 999
        Main.personagem.hp = 999
        Main.personagem.trocar_skin("Cyborg Skin.png")
        Main.cheats_tela.modo = "seletor_batalha"
        Main.cheats_tela.equipe_selecionada.append(BANCO_INIMIGOS[0])
        Main.cheats_tela.filtro_verso = "Agente"

        # Simula o clique no botão de RESET do menu principal
        pos = (Main.menu_tela.botao_reset.rect.centerx, Main.menu_tela.botao_reset.rect.centery)
        evt_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": pos})
        Main.tratar_eventos_menu(evt_down, pos)
        evt_up = pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": 1, "pos": pos})
        Main.tratar_eventos_menu(evt_up, pos)

        # Checa se o menu de cheats foi resetado junto com o jogo
        self.assertEqual(Main.cheats_tela.modo, "cheats")
        self.assertEqual(len(Main.cheats_tela.equipe_selecionada), 0)
        self.assertEqual(Main.cheats_tela.filtro_verso, "TODOS")
        self.assertEqual(Main.cheats_tela.btn_godmode.texto, "GOD MODE: DESATIVADO")
        self.assertFalse(Main.personagem.god_mode)
        self.assertEqual(Main.personagem.nome_imagem, "pixil.png")
        self.assertFalse(Main.save_global.tem_member_card())
        self.assertEqual(Main.save_global.obter_pontos(), 0)


if __name__ == "__main__":
    unittest.main()
