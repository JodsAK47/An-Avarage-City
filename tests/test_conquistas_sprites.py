import json
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

from Sistemas.Recursos import caminho_imagem, caminho_conquista
from Sistemas.Conquistas import sistema_conquistas, Conquista
from Telas.TelaConquistas import GerenciadorConquistasTela


class TestConquistasSprites(unittest.TestCase):
    def setUp(self):
        sistema_conquistas.carregar()

    def test_sprites_conquistas_arquivos_existem(self):
        """Verifica se todos os 12 sprites de conquistas existem na pasta Sprites/Conquistas."""
        sprites_esperados = [
            "Acontece Com Todos.png",
            "Agente Radiante.png",
            "Alquimia.png",
            "Esgotado.png",
            "Esquiva tatica.png",
            "Feiticeiro Supremo.png",
            "Ferreiro.png",
            "Lenda.png",
            "Moda Em Primeiro Lugar.png",
            "Mão Amiga.png",
            "Posso Fazer Isso O Dia Todo.png",
            "Primeiro Abate.png",
            "Primeiro Talento.png",
            "Que Critico.png",
            "Quem Precisa De Dominio.png",
            "Ultimate Pronta.png"
        ]
        for nome in sprites_esperados:
            p_conq = caminho_conquista(nome)
            self.assertTrue(os.path.exists(p_conq), f"Sprite de conquista '{nome}' não encontrado em {p_conq}")
            p_img = caminho_imagem(nome)
            self.assertTrue(os.path.exists(p_img), f"Sprite de conquista '{nome}' não encontrado via caminho_imagem em {p_img}")

    def test_conquistas_usam_seus_sprites_especificos(self):
        """Garante que as quatro conquistas apontam para os ícones correspondentes."""
        icones_esperados = {
            "Feiticeiro Supremo": "Feiticeiro Supremo.png",
            "Golpe Preciso": "Que Critico.png",
            "Reflexos de Aço": "Esquiva tatica.png",
            "Lenda dos Versos": "Lenda.png",
        }
        icones_por_nome = {
            item["nome"]: item["icone"]
            for item in json.loads((RAIZ / "Dados" / "conquistas.json").read_text(encoding="utf-8"))
        }
        for nome, icone in icones_esperados.items():
            self.assertEqual(icones_por_nome[nome], icone)
            self.assertTrue(os.path.exists(caminho_conquista(icone)))

    def test_todos_icones_do_json_existem(self):
        """Garante que todos os ícones apontados em Dados/conquistas.json existem fisicamente no disco."""
        caminho_json = RAIZ / "Dados" / "conquistas.json"
        with open(caminho_json, "r", encoding="utf-8") as f:
            dados = json.load(f)

        for c in dados:
            icone = c.get("icone")
            self.assertIsNotNone(icone, f"Conquista '{c.get('nome')}' não possui o campo 'icone'.")
            caminho_resolvido = caminho_conquista(icone)
            if not os.path.exists(caminho_resolvido):
                caminho_resolvido = caminho_imagem(icone)
            self.assertTrue(os.path.exists(caminho_resolvido), f"Ícone '{icone}' da conquista '{c.get('nome')}' não encontrado!")

    def test_carregamento_e_escala_icones(self):
        """Verifica se os ícones carregam como superfícies válidas (colorida e P&B)."""
        for c in sistema_conquistas.conquistas:
            c.carregar_icones()
            self.assertIsNotNone(c._superficie_colorida, f"Falha ao carregar superfície colorida de {c.nome}")
            self.assertIsNotNone(c._superficie_cinza, f"Falha ao carregar superfície cinza de {c.nome}")

            # Testa obtenção do ícone em diferentes resoluções (HUD, card e detalhes)
            icone_hud = c.obter_icone(desbloqueada=True, tamanho=(40, 40))
            self.assertEqual(icone_hud.get_size(), (40, 40))

            icone_card = c.obter_icone(desbloqueada=False, tamanho=(52, 52))
            self.assertEqual(icone_card.get_size(), (52, 52))

            icone_grande = c.obter_icone(desbloqueada=True, tamanho=(110, 110))
            self.assertEqual(icone_grande.get_size(), (110, 110))

    def test_renderizacao_tela_conquistas(self):
        """Verifica se a tela de conquistas desenha todos os cards e o painel de detalhes sem exceções."""
        superficie = pygame.Surface((1024, 768))
        tela_conq = GerenciadorConquistasTela(superficie)
        tela_conq.atualizar((200, 200), (False, False, False))
        tela_conq.desenhar()
        # Seleciona diferentes conquistas e desenha
        if len(sistema_conquistas.conquistas) > 1:
            tela_conq.conquista_selecionada = sistema_conquistas.conquistas[1]
            tela_conq.desenhar()


if __name__ == "__main__":
    unittest.main()
