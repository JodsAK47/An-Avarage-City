import os
import sys
import unittest

import pygame

sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "An-Average-City", "Um Prototipo medio"),
)

from Menu import GerenciadorMenu
from MenuClasses import GerenciadorClasses
from TelaVerso import GerenciadorVerso
from Jogo import GerenciadorJogo
from Habilidades import obter_ultimate
from Entidades.Personagem import Personagem


class TestMenuPadrao(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((100, 100))

    def test_menu_agrupa_botoes_em_um_dicionario(self):
        tela = pygame.Surface((1000, 800))
        menu = GerenciadorMenu(tela)

        self.assertIn("jogar", menu.botoes)
        self.assertIn("classe", menu.botoes)
        self.assertIn("sair", menu.botoes)
        self.assertIs(menu.buscar_botao("jogar"), menu.botao_jogar)
        self.assertIs(menu.buscar_botao("classe"), menu.botao_classe)
        self.assertIs(menu.buscar_botao("sair"), menu.botao_sair)
        self.assertIsNone(menu.buscar_botao("botao_inexistente"))

    def test_arvore_de_habilidades_centralizada_por_classe(self):
        tela = pygame.Surface((1000, 800))
        classes = GerenciadorClasses(tela)

        self.assertIn("Sobrevivente", classes.arvores_por_classe)
        self.assertIn("Agente", classes.arvores_por_classe)
        self.assertIn("Feiticeiro", classes.arvores_por_classe)
        self.assertEqual(classes.obter_arvore_ativa(), classes.arvores_por_classe["Sobrevivente"])

        classes.classe_atual = "Agente"
        self.assertEqual(classes.obter_arvore_ativa(), classes.arvores_por_classe["Agente"])

    def test_tela_verso_exibe_opcoes_esperadas(self):
        tela = pygame.Surface((1000, 800))
        verso_tela = GerenciadorVerso(tela)

        self.assertEqual(verso_tela.versos, ["Sobrevivente", "Agente", "Feiticeiro"])
        self.assertIn("verso_atual", verso_tela.__dict__)
        self.assertTrue(hasattr(verso_tela, "botao_confirmar"))

    def test_arvore_por_verso_diferente_e_progresso_independente(self):
        tela = pygame.Surface((1000, 800))
        verso_tela = GerenciadorVerso(tela)

        self.assertNotEqual(verso_tela.arvores_por_verso["Sobrevivente"], verso_tela.arvores_por_verso["Agente"])
        self.assertNotEqual(verso_tela.arvores_por_verso["Agente"], verso_tela.arvores_por_verso["Feiticeiro"])

        verso_tela.progresso_por_verso["Sobrevivente"] = ["S1"]
        verso_tela.verso_atual = "Sobrevivente"
        verso_tela.sincronizar_habilidades_ativas()
        self.assertEqual(verso_tela.habilidades_desbloqueadas, ["S1"])

        verso_tela.verso_atual = "Agente"
        verso_tela.sincronizar_habilidades_ativas()
        self.assertEqual(verso_tela.habilidades_desbloqueadas, [])

    def test_jogador_2_sobe_de_nivel_mesmo_morto_apos_vitoria(self):
        tela = pygame.Surface((1000, 800))
        jogo = GerenciadorJogo(tela)

        jogador1 = Personagem(0, 0)
        jogador2 = Personagem(0, 0)
        inimigo = Personagem(0, 0)
        inimigo.is_player = False

        jogador1.is_player = True
        jogador2.is_player = True
        jogador1.hp = 50
        jogador2.hp = 0
        jogador1.xp = 0
        jogador2.xp = 0
        jogador1.nivel = 1
        jogador2.nivel = 1
        inimigo.xp = 150
        inimigo.hp = 0

        jogo.personagem2 = jogador2
        jogo.ordem_turnos = [jogador1, jogador2, inimigo]
        jogo.partida_atual = 1
        jogo.total_partidas = 2

        resultado = jogo.atualizar((0, 0), (False, False))

        self.assertEqual(resultado, "vitoria")
        self.assertEqual(jogador2.nivel, 2)
        self.assertEqual(jogador1.nivel, 2)

    def test_pontos_de_desempenho_considera_kills_dano_e_dificuldade(self):
        tela = pygame.Surface((1000, 800))
        jogo = GerenciadorJogo(tela)

        pontos_base = jogo.calcular_pontos_desempenho(
            xp_ganho=0,
            dano_causado=120,
            inimigos_eliminados=2,
            dificuldade_total=300,
        )
        pontos_vazios = jogo.calcular_pontos_desempenho()

        self.assertGreater(pontos_base, pontos_vazios)
        self.assertGreater(pontos_base, 0)

    def test_ultimate_do_ultimo_nivel_custa_100_porcento_da_mana(self):
        habilidade = obter_ultimate("Sobrevivente", "Físico")
        jogador = Personagem(0, 0)
        jogador.max_mp = 42
        jogador.mp = 42

        self.assertIsNotNone(habilidade)
        self.assertEqual(habilidade.custo_para(jogador), jogador.max_mp)
        self.assertTrue(habilidade.nome.lower().startswith("ultimate") or "ultimate" in habilidade.nome.lower())


if __name__ == "__main__":
    unittest.main()
