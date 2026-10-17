import os
import sys
import unittest
import pygame

diretorio_atual = os.path.dirname(os.path.abspath(__file__))
diretorio_jogo = os.path.dirname(diretorio_atual)
if diretorio_jogo not in sys.path:
    sys.path.insert(0, diretorio_jogo)

pygame.init()
pygame.display.set_mode((1000, 800))

from Sistemas.Inventario import inventario_global, SistemaInventario, ItemBilhete
from Entidades.Personagem import Personagem
from Entidades.Inimigo import Inimigo
from Telas.TelaCombate import GerenciadorJogo
from Telas.TelaDescanco import GerenciadorPosLuta

class TestBilheteDormitorio(unittest.TestCase):
    def setUp(self):
        inventario_global.resetar()

    def test_inicio_com_um_bilhete(self):
        self.assertEqual(inventario_global.obter_bilhetes_dormitorio(), 1)
        self.assertEqual(inventario_global.bilhetes_dormitorio, 1)

        itens = inventario_global.itens_do_inventario()
        bilhetes = [i for i in itens if getattr(i, "tipo", None) == "bilhete" or i.nome == "Bilhete do Dormitório"]
        self.assertEqual(len(bilhetes), 1)
        self.assertEqual(bilhetes[0].quantidade, 1)

    def test_consumir_e_adicionar_bilhete(self):
        self.assertTrue(inventario_global.consumir_bilhete_dormitorio(1))
        self.assertEqual(inventario_global.obter_bilhetes_dormitorio(), 0)

        self.assertFalse(inventario_global.consumir_bilhete_dormitorio(1))
        self.assertEqual(inventario_global.obter_bilhetes_dormitorio(), 0)

        inventario_global.adicionar_bilhete_dormitorio(2)
        self.assertEqual(inventario_global.obter_bilhetes_dormitorio(), 2)
        self.assertTrue(inventario_global.consumir_bilhete_dormitorio(1))
        self.assertEqual(inventario_global.obter_bilhetes_dormitorio(), 1)

    def test_resetar_inventario_restaura_um_bilhete(self):
        inventario_global.consumir_bilhete_dormitorio(1)
        self.assertEqual(inventario_global.obter_bilhetes_dormitorio(), 0)
        inventario_global.resetar()
        self.assertEqual(inventario_global.obter_bilhetes_dormitorio(), 1)

    def test_chances_de_drop_por_forca(self):
        tela = pygame.Surface((1000, 800))
        combate = GerenciadorJogo(tela)

        fraco = Inimigo(0, 0, 25, "Maldicao1.png", nome="Zumbi", xp=25, tipo="fraco")
        medio = Inimigo(0, 0, 45, "Maldicao1.png", nome="Mutante", xp=50, tipo="medio")
        grande = Inimigo(0, 0, 70, "Maldicao1.png", nome="Aberração", xp=75, tipo="grande")
        chefe = Inimigo(0, 0, 160, "Sukuna1.png", nome="Sukuna", xp=350, tipo="chefe")

        chance_fraco = combate.calcular_chance_drop_bilhete(fraco)
        chance_medio = combate.calcular_chance_drop_bilhete(medio)
        chance_grande = combate.calcular_chance_drop_bilhete(grande)
        chance_chefe = combate.calcular_chance_drop_bilhete(chefe)

        self.assertLess(chance_fraco, chance_medio)
        self.assertLess(chance_medio, chance_grande)
        self.assertLess(chance_grande, chance_chefe)

        self.assertLessEqual(chance_chefe, 0.45)
        self.assertLessEqual(chance_fraco, 0.10)

    def test_recuperacao_dormir_gasta_bilhete(self):
        tela = pygame.Surface((1000, 800))
        combate = GerenciadorJogo(tela)
        p = combate.obter_jogadores()[0]

        p.hp = 10
        p.mp = 0
        inventario_global.resetar()

        combate.recuperar_apos_batalha(dormir=True)
        self.assertEqual(inventario_global.obter_bilhetes_dormitorio(), 0)
        self.assertGreater(p.hp, 10 + int(p.max_hp * 0.30))
        self.assertEqual(p.mp, 7)

    def test_recuperacao_dormir_sem_bilhete_bloqueado(self):
        tela = pygame.Surface((1000, 800))
        combate = GerenciadorJogo(tela)
        p = combate.obter_jogadores()[0]

        p.hp = 10
        p.mp = 0
        inventario_global.consumir_bilhete_dormitorio(1)
        self.assertEqual(inventario_global.obter_bilhetes_dormitorio(), 0)

        combate.recuperar_apos_batalha(dormir=True)
        self.assertEqual(inventario_global.obter_bilhetes_dormitorio(), 0)
        self.assertEqual(p.hp, 10 + int(p.max_hp * 0.30))
        self.assertEqual(p.mp, 3)

    def test_continuar_nao_gasta_bilhete(self):
        tela = pygame.Surface((1000, 800))
        combate = GerenciadorJogo(tela)
        p = combate.obter_jogadores()[0]

        p.hp = 10
        p.mp = 0
        inventario_global.resetar()

        combate.recuperar_apos_batalha(dormir=False)
        self.assertEqual(inventario_global.obter_bilhetes_dormitorio(), 1)
        self.assertEqual(p.hp, 10 + int(p.max_hp * 0.30))
        self.assertEqual(p.mp, 3)

    def test_tela_descanco_sem_opcao_dormir(self):
        tela = pygame.Surface((1000, 800))
        pos_luta = GerenciadorPosLuta(tela)

        self.assertFalse(hasattr(pos_luta, "btn_dormir"))

        pos_botao_continuar = (pos_luta.btn_continuar.rect.x + 5, pos_luta.btn_continuar.rect.y + 5)
        ev_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": pos_botao_continuar})
        ev_up = pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": 1, "pos": pos_botao_continuar})

        pos_luta.atualizar_eventos(ev_down, pos_botao_continuar)
        retorno = pos_luta.atualizar_eventos(ev_up, pos_botao_continuar)
        self.assertEqual(retorno, "continuar")

    def test_cura_automatica_fim_batalha_e_popup(self):
        tela = pygame.Surface((1000, 800))
        combate = GerenciadorJogo(tela)
        p = combate.obter_jogadores()[0]
        p.hp = 20
        p.mp = 1

        # Simula fim de batalha com vitoria
        combate.ordem_turnos = [p] # sem inimigos vivos
        combate.xp_calculado = False
        resultado = combate.atualizar((0, 0), (False, False, False))
        self.assertEqual(resultado, "vitoria")

        # Verifica se jogador foi curado automaticamente
        self.assertGreater(p.hp, 20)
        self.assertGreater(p.mp, 1)

        # Verifica informacoes salvas
        self.assertIsNotNone(combate.ultimo_resultado_batalha)
        self.assertIn("cura", combate.ultimo_resultado_batalha)
        self.assertIn("itens", combate.ultimo_resultado_batalha)

        # Testa popup na tela de descanso/inventario
        pos_luta = GerenciadorPosLuta(tela)
        pos_luta.definir_popup_notificacao(combate.ultimo_resultado_batalha)
        self.assertTrue(pos_luta.notificacao_visivel)
        self.assertIsNotNone(pos_luta.notificacao_popup)

        # Renderiza sem erros
        pos_luta.desenhar()

        # Testa fechar popup
        self.assertIsNotNone(pos_luta.btn_fechar_popup)
        ev_fechar = pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": 1, "pos": pos_luta.btn_fechar_popup.center})
        pos_luta.atualizar_eventos(ev_fechar, pos_luta.btn_fechar_popup.center)
        self.assertFalse(pos_luta.notificacao_visivel)

    def test_continuar_pos_luta_sem_recuperacao(self):
        import Main
        Main.personagem.hp = 15
        Main.personagem.mp = 2
        hp_antes = Main.personagem.hp
        mp_antes = Main.personagem.mp

        pos_botao_continuar = (Main.pos_luta_tela.btn_continuar.rect.x + 5, Main.pos_luta_tela.btn_continuar.rect.y + 5)
        ev_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": pos_botao_continuar})
        ev_up = pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": 1, "pos": pos_botao_continuar})

        Main.tratar_eventos_pos_luta(ev_down, pos_botao_continuar)
        res = Main.tratar_eventos_pos_luta(ev_up, pos_botao_continuar)
        self.assertEqual(res, "selecao_cenario")

        # Garante que continuar no menu de inventario NAO recuperou o personagem
        self.assertEqual(Main.personagem.hp, hp_antes)
        self.assertEqual(Main.personagem.mp, mp_antes)

if __name__ == "__main__":
    unittest.main()
