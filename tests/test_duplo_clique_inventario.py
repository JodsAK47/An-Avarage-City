import unittest
from unittest import mock
import os
import sys
import pygame

DIRETORIO_RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "An Average City"))
if DIRETORIO_RAIZ not in sys.path:
    sys.path.insert(0, DIRETORIO_RAIZ)

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1000, 800))

from Sistemas.Inventario import inventario_global, Equipamento
from Entidades.Personagem import personagem
from Telas import TelaDescanso


class TestDuploCliqueInventario(unittest.TestCase):
    def setUp(self):
        inventario_global.resetar()
        inventario_global.item_bilhete.quantidade = 0
        personagem.resetar()
        self.tela = pygame.Surface((1000, 800))
        self.descanso = TelaDescanso(self.tela)
        self.inventario_slots, self.equipamentos_slots = self.descanso._retangulos_slots()

    def _simular_clique(self, pos, tempo_ms):
        """Simula um clique de mouse com timestamp controlado."""
        with mock.patch("pygame.time.get_ticks", return_value=tempo_ms):
            ev_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos)
            self.descanso.atualizar_eventos(ev_down, pos)
            ev_up = pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=pos)
            self.descanso.atualizar_eventos(ev_up, pos)

    def _obter_pos_item_inventario(self, item):
        """Retorna as coordenadas centrais do slot onde o item se encontra na mochila."""
        idx = inventario_global.itens_do_inventario().index(item)
        slot = self.inventario_slots[idx]
        return (slot.centerx, slot.centery)

    def test_um_clique_consumivel_apenas_seleciona_e_mostra_descricao(self):
        """1 clique em poção apenas seleciona e exibe descrição, sem consumir o item nem curar."""
        personagem.hp = 40
        personagem.max_hp = 100
        inventario_global.adicionar_consumivel("Poção de Vida", "Restaura 30 HP.", rec_hp=30, rec_mp=0)
        pos = self._obter_pos_item_inventario(inventario_global.consumiveis[0])

        # 1 clique
        self._simular_clique(pos, tempo_ms=1000)

        # Não deve consumir nem curar
        self.assertEqual(len(inventario_global.consumiveis), 1)
        self.assertEqual(inventario_global.consumiveis[0].quantidade, 1)
        self.assertEqual(personagem.hp, 40)

        # Deve selecionar e exibir descrição
        self.assertEqual(self.descanso.slot_selecionado, 0)
        self.assertIn("Poção de Vida", self.descanso.mensagem)
        self.assertIn("Restaura 30 HP", self.descanso.mensagem)

    def test_dois_cliques_consome_item(self):
        """2 cliques rápidos em poção consome o item e aplica o efeito de cura."""
        personagem.hp = 40
        personagem.max_hp = 100
        inventario_global.adicionar_consumivel("Poção de Vida", "Restaura 30 HP.", rec_hp=30, rec_mp=0)
        pocao = inventario_global.consumiveis[0]
        pos = self._obter_pos_item_inventario(pocao)

        # 1º clique aos 1000ms
        self._simular_clique(pos, tempo_ms=1000)
        self.assertEqual(personagem.hp, 40)

        # 2º clique aos 1150ms (intervalo de 150ms <= 400ms -> duplo clique!)
        self._simular_clique(pos, tempo_ms=1150)

        # Agora sim deve consumir e curar!
        self.assertEqual(personagem.hp, 70)
        self.assertEqual(len(inventario_global.consumiveis), 0)
        self.assertIn("Usou Poção de Vida", self.descanso.mensagem)

    def test_um_clique_equipamento_mochila_apenas_seleciona(self):
        """1 clique em equipamento na mochila apenas seleciona para melhoria e exibe atributos."""
        katana = Equipamento("Katana", {"Agi": 3}, categoria="arma")
        inventario_global.adicionar_equipamento(katana, auto_equipar=False)
        pos = self._obter_pos_item_inventario(katana)

        # 1 clique
        self._simular_clique(pos, tempo_ms=1000)

        # Não deve equipar
        self.assertIsNone(inventario_global.equipamento_slot)
        self.assertIn(katana, inventario_global.equipamentos_inventario)

        # Deve selecionar
        self.assertEqual(inventario_global.equipamento_selecionado, katana)
        self.assertIn("Katana", self.descanso.mensagem)
        self.assertIn("+3 Agi", self.descanso.mensagem)

    def test_dois_cliques_equipamento_mochila_equipa_item(self):
        """2 cliques em equipamento na mochila equipa o item no slot correspondente."""
        katana = Equipamento("Katana", {"Agi": 3}, categoria="arma")
        inventario_global.adicionar_equipamento(katana, auto_equipar=False)
        pos = self._obter_pos_item_inventario(katana)

        # 1º clique aos 1000ms
        self._simular_clique(pos, tempo_ms=1000)
        self.assertIsNone(inventario_global.equipamento_slot)

        # 2º clique aos 1200ms (intervalo de 200ms -> duplo clique!)
        self._simular_clique(pos, tempo_ms=1200)

        # Item deve estar equipado no slot de arma!
        self.assertEqual(inventario_global.equipamento_slot, katana)
        self.assertNotIn(katana, inventario_global.equipamentos_inventario)
        self.assertIn("Equipou Katana", self.descanso.mensagem)

    def test_um_clique_equipamento_equipado_apenas_seleciona(self):
        """1 clique em equipamento equipado apenas seleciona e exibe descrição."""
        colete = Equipamento("Peitoral de Aço", {"Con": 3}, categoria="peitoral")
        inventario_global.equipar(colete)
        self.assertEqual(inventario_global.peitoral_slot, colete)

        # Slot de peitoral é o índice 2 nos equipamentos
        slot_peitoral = self.equipamentos_slots[2]
        pos = (slot_peitoral.centerx, slot_peitoral.centery)

        # 1 clique
        self._simular_clique(pos, tempo_ms=1000)

        # Deve continuar equipado
        self.assertEqual(inventario_global.peitoral_slot, colete)
        self.assertEqual(inventario_global.equipamento_selecionado, colete)
        self.assertIn("Peitoral de Aço", self.descanso.mensagem)
        self.assertIn("+3 Con", self.descanso.mensagem)

    def test_dois_cliques_equipamento_equipado_desequipa_item(self):
        """2 cliques em equipamento equipado desequipa o item e o move para a mochila."""
        colete = Equipamento("Peitoral de Aço", {"Con": 3}, categoria="peitoral")
        inventario_global.equipar(colete)
        self.assertEqual(inventario_global.peitoral_slot, colete)

        slot_peitoral = self.equipamentos_slots[2]
        pos = (slot_peitoral.centerx, slot_peitoral.centery)

        # 1º clique aos 1000ms
        self._simular_clique(pos, tempo_ms=1000)
        self.assertEqual(inventario_global.peitoral_slot, colete)

        # 2º clique aos 1180ms -> duplo clique!
        self._simular_clique(pos, tempo_ms=1180)

        # Deve desequipar!
        self.assertIsNone(inventario_global.peitoral_slot)
        self.assertIn(colete, inventario_global.equipamentos_inventario)
        self.assertIn("Desequipou Peitoral de Aço", self.descanso.mensagem)

    def test_clicar_em_slots_diferentes_rapidamente_nao_aciona_duplo_clique(self):
        """Clicar no slot A e depois rapidamente no slot B apenas seleciona B sem acionar duplo clique."""
        p1 = Equipamento("Faca", {"For": 1}, categoria="arma")
        p2 = Equipamento("Katana", {"Agi": 3}, categoria="arma")
        inventario_global.adicionar_equipamento(p1, auto_equipar=False)
        inventario_global.adicionar_equipamento(p2, auto_equipar=False)

        pos0 = self._obter_pos_item_inventario(p1)
        pos1 = self._obter_pos_item_inventario(p2)

        # Clica no slot 0
        self._simular_clique(pos0, tempo_ms=1000)
        self.assertIsNone(inventario_global.equipamento_slot)
        self.assertEqual(self.descanso.slot_selecionado, 0)
        self.assertEqual(inventario_global.equipamento_selecionado, p1)

        # Clica no slot 1 apenas 100ms depois
        self._simular_clique(pos1, tempo_ms=1100)
        # Não deve equipar p2, apenas selecionar slot 1
        self.assertIsNone(inventario_global.equipamento_slot)
        self.assertEqual(self.descanso.slot_selecionado, 1)
        self.assertEqual(inventario_global.equipamento_selecionado, p2)


if __name__ == "__main__":
    unittest.main()
