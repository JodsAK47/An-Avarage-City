import os
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent / "An Average City"
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
pygame.init()
pygame.display.set_mode((1024, 768))

from Sistemas.Recursos import caminho_imagem, caminho_cenario
from Telas.TelaSewer import GerenciadorSewerTela


class TestTelaSewer(unittest.TestCase):
    def test_sprite_esgoto_trancado_existe(self):
        caminho_cen = caminho_cenario("EsgotoTrancado.png")
        self.assertTrue(os.path.exists(caminho_cen), f"EsgotoTrancado.png não existe em {caminho_cen}")
        caminho_img = caminho_imagem("EsgotoTrancado.png")
        self.assertTrue(os.path.exists(caminho_img), f"EsgotoTrancado.png não encontrado via caminho_imagem em {caminho_img}")

    def test_inicializacao_tela_sewer(self):
        tela_mock = pygame.Surface((1024, 768))
        sewer = GerenciadorSewerTela(tela_mock)
        self.assertIsNotNone(sewer.imagem_fundo, "A imagem de fundo do esgoto deveria ter sido carregada com sucesso.")
        self.assertGreater(sewer.imagem_fundo.get_width(), 0)
        self.assertGreater(sewer.imagem_fundo.get_height(), 0)
        self.assertIsNotNone(sewer.rect_saida)
        self.assertIsNotNone(sewer.rect_porta_restrita)
        self.assertIsNotNone(sewer.rect_card_chao)


if __name__ == "__main__":
    unittest.main()
