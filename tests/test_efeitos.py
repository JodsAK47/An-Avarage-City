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
pygame.display.set_mode((1000, 800))

from Entidades.Personagem import Personagem, personagem
from Entidades.Inimigo import Inimigo
from Entidades.Minion import Minion
from Sistemas.SistemaEfeitos import (
    CONFIG_EFEITOS,
    obter_efeitos_ativos,
    carregar_icone_efeito,
    desenhar_icones_entidade,
    desenhar_tooltip_efeito,
)
from Telas.TelaCombate import GerenciadorJogo


class TestSistemaEfeitos(unittest.TestCase):
    def setUp(self):
        self.tela = pygame.Surface((1000, 800))
        self.p1 = Personagem(150, 350, "pixil.png")
        self.inimigo = Inimigo(
            x=700, y=350, vida_maxima=80, nome_imagem="Maldicao1.png",
            nome="Maldição Teste", ataques=[], xp=20,
            atributos={"For": 2, "Agi": 2, "Int": 1, "Sor": 1}
        )
        self.minion = Minion(x=250, y=400, nome="Abelha", vida_maxima=30, nome_imagem="Abelha.png", dono=self.p1)

    def test_icones_existem_e_carregam(self):
        """Testa se os ícones da pasta De_Buffs são carregados e redimensionados corretamente."""
        for chave, cfg in CONFIG_EFEITOS.items():
            arquivo = cfg["arquivo"]
            icone = carregar_icone_efeito(arquivo, tamanho=20)
            self.assertIsNotNone(icone)
            self.assertEqual(icone.get_size(), (20, 20))

    def test_obter_efeitos_ativos_personagem(self):
        """Verifica se efeitos positivos e negativos no Personagem são detectados."""
        # Sem efeitos
        self.assertEqual(obter_efeitos_ativos(self.p1), [])

        # Aplica Congelado
        self.p1.congelado = True
        efeitos = obter_efeitos_ativos(self.p1)
        self.assertEqual(len(efeitos), 1)
        self.assertEqual(efeitos[0]["id"], "congelado")
        self.assertEqual(efeitos[0]["tipo"], "debuff")

        # Aplica Bloqueio (Buff)
        self.p1.bloqueando = True
        efeitos = obter_efeitos_ativos(self.p1)
        ids = [e["id"] for e in efeitos]
        self.assertIn("congelado", ids)
        self.assertIn("bloqueio", ids)

        # Aplica Queimando e Recuperando
        self.p1.queimando = True
        self.p1.recuperando = True
        efeitos = obter_efeitos_ativos(self.p1)
        ids = [e["id"] for e in efeitos]
        self.assertIn("fogo", ids)
        self.assertIn("recuperando", ids)

    def test_obter_efeitos_ativos_inimigo(self):
        """Verifica se efeitos em inimigos (incluindo Confinamento) são detectados."""
        self.inimigo.atordoado = True
        self.inimigo.envenenado = True
        efeitos = obter_efeitos_ativos(self.inimigo)
        ids = [e["id"] for e in efeitos]
        self.assertIn("atordoado", ids)
        self.assertIn("veneno", ids)

        # Inimigo Confinamento com cargas
        self.inimigo.eh_confinamento = True
        self.inimigo.carga_confinamento = 3
        efeitos = obter_efeitos_ativos(self.inimigo)
        ids = [e["id"] for e in efeitos]
        self.assertIn("confinamento", ids)

    def test_obter_efeitos_ativos_minion(self):
        """Verifica se efeitos aplicados ao Minion são detectados."""
        self.minion.congelado = True
        self.minion.queimando = True
        efeitos = obter_efeitos_ativos(self.minion)
        ids = [e["id"] for e in efeitos]
        self.assertIn("congelado", ids)
        self.assertIn("fogo", ids)

    def test_desenhar_icones_e_hover_tooltip(self):
        """Testa o desenho de ícones e a detecção de passar o mouse por cima (hover)."""
        self.inimigo.congelado = True
        x_alvo = 500
        y_alvo = 300

        # Mouse longe dos ícones
        hovered_longe = desenhar_icones_entidade(
            self.tela, self.inimigo, x=x_alvo, y=y_alvo,
            tamanho=20, posicao_mouse=(0, 0)
        )
        self.assertIsNone(hovered_longe)

        # Mouse em cima do ícone centralizado (x_alvo - 10, y_alvo)
        hovered_em_cima = desenhar_icones_entidade(
            self.tela, self.inimigo, x=x_alvo, y=y_alvo,
            tamanho=20, posicao_mouse=(x_alvo, y_alvo + 5)
        )
        self.assertIsNotNone(hovered_em_cima)
        self.assertEqual(hovered_em_cima["id"], "congelado")

    def test_desenhar_tooltip_sem_erros(self):
        """Testa a renderização da tooltip do efeito sem exceções de tela."""
        info = CONFIG_EFEITOS["fogo"]
        # Desenha na tela em várias posições (centro, canto direito, canto inferior)
        desenhar_tooltip_efeito(self.tela, info, (100, 100))
        desenhar_tooltip_efeito(self.tela, info, (980, 780)) # teste de clamp na borda
        desenhar_tooltip_efeito(self.tela, info, (0, 0))

    def test_combate_aplicar_e_processar_efeitos(self):
        """Testa aplicação de Queimar, Veneno, Congelar e Atordoar no combate."""
        jogo = GerenciadorJogo(self.tela)
        jogo.ordem_turnos = [self.p1, self.inimigo]

        # Aplicar efeitos de controle
        res_gelo = jogo.aplicar_efeito_controle(self.inimigo, "Congelar")
        self.assertEqual(res_gelo, "CONGELOU!")
        self.assertTrue(self.inimigo.congelado)

        res_fogo = jogo.aplicar_efeito_controle(self.inimigo, "Queimar")
        self.assertEqual(res_fogo, "EM CHAMAS!")
        self.assertTrue(self.inimigo.queimando)

        res_veneno = jogo.aplicar_efeito_controle(self.inimigo, "Veneno")
        self.assertEqual(res_veneno, "ENVENENOU!")
        self.assertTrue(self.inimigo.envenenado)

        # Testar processar fim da rodada (dano contínuo de fogo e veneno)
        hp_antes = self.inimigo.hp
        jogo.processar_fim_rodada()
        self.assertLess(self.inimigo.hp, hp_antes)


if __name__ == "__main__":
    unittest.main()
