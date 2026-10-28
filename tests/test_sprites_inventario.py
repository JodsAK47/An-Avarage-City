import unittest
import os
import sys
import pygame

DIRETORIO_RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "An Average City"))
if DIRETORIO_RAIZ not in sys.path:
    sys.path.insert(0, DIRETORIO_RAIZ)

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1000, 800))

from Sistemas.Recursos import caminho_imagem, reindexar_sprites
from Sistemas.Inventario import (
    carregar_sprite_item,
    obter_arquivo_imagem_item,
    eh_arte_placeholder,
    limpar_cache_sprites_itens,
    carregar_dados_itens,
    obter_todos_itens_catalogo,
    inventario_global,
    Consumivel,
    Material,
    ItemBilhete,
    ItemPolidor,
    Equipamento,
    MAPA_SPRITES_ITENS,
    ARTES_OFICIAIS_INVENTARIO,
)
from Telas import TelaDescanso


class TestSpritesInventario(unittest.TestCase):
    def setUp(self):
        reindexar_sprites()
        limpar_cache_sprites_itens()
        self.tela = pygame.Surface((1000, 800))

    def test_existencia_artes_oficiais(self):
        """Verifica se todas as 19 artes oficiais na pasta Sprites/Inventario existem e podem ser carregadas."""
        for arq in ARTES_OFICIAIS_INVENTARIO:
            caminho = caminho_imagem(arq)
            self.assertTrue(os.path.exists(caminho), f"Arquivo de sprite oficial não encontrado: {arq} (caminho: {caminho})")
            img = pygame.image.load(caminho)
            self.assertGreater(img.get_width(), 0)
            self.assertGreater(img.get_height(), 0)

    def test_existencia_placeholders(self):
        """Verifica se os arquivos de placeholder existem e são superfícies válidas."""
        placeholders = [
            "Placeholder.png",
            "Placeholder_Arma.png",
            "Placeholder_Armadura.png",
            "Placeholder_Acessorio.png",
        ]
        for ph in placeholders:
            caminho = caminho_imagem(ph)
            self.assertTrue(os.path.exists(caminho), f"Placeholder não encontrado: {ph} (caminho: {caminho})")
            img = pygame.image.load(caminho)
            self.assertEqual(img.get_size(), (32, 32))

    def test_mapeamento_itens_com_arte_propria(self):
        """Verifica se itens que possuem artes oficiais retornam seus respectivos sprites."""
        casos = [
            ("Poção de Vida", "Pocao Cura.png"),
            ("Poção de Mana", "Pocao Mana.png"),
            ("Chá de Mana Concentrado", "Cha.png"),
            ("Café Expresso Revigorante", "Cafe.png"),
            ("Marmita Nutritiva Especial", "Marmita.png"),
            ("Sucata", "Sucata.png"),
            ("Bilhete do Dormitório", "TIcket.png"),
            ("Polidor de Itens", "Polidor.png"),
            ("Machado", "Lucy O Machado.png"),
            ("Estilingue", "Estilingue.png"),
            ("Pedra Preciosa Multicor", "Gema.png"),
            ("Flauta de Pã", "Flauta.png"),
            ("Faca de Confronto", "Faca.png"),
            ("Vandal", "Vandal.png"),
            ("Rocha De Radianita", "Radianita.png"),
            ("Bracelete de Comando", "Bracelete.png"),
            ("Katana", "Katana.png"),
            ("Amplificador de alcance", "Megafone.png"),
            ("Ferramenta Amaldiçoada", "Ferramenta Amaldicoada.png"),
            ("Amuleto das Dez Sombras", "Amuleto Sombrio.png"),
        ]
        for nome_item, arquivo_esperado in casos:
            res = obter_arquivo_imagem_item(nome_item)
            self.assertEqual(res, arquivo_esperado, f"Item '{nome_item}' deveria mapear para '{arquivo_esperado}', mas retornou '{res}'")
            self.assertFalse(eh_arte_placeholder(nome_item), f"Item '{nome_item}' deveria ser considerado arte oficial, não placeholder")

    def test_mapeamento_itens_sem_arte_usam_placeholder(self):
        """Verifica se itens sem arte oficial usam placeholders e são sinalizados corretamente."""
        casos_placeholder = [
            ("Capacete de Ferro", "Placeholder_Armadura.png"),
            ("Peitoral de Aço", "Placeholder_Armadura.png"),
            ("Calça Reforçada", "Placeholder_Armadura.png"),
            ("Botas de Combate", "Placeholder_Armadura.png"),
            ("Amuleto do Mago", "Placeholder_Acessorio.png"),
            ("Arma Contrabandeada", "Placeholder_Arma.png"),
            ("Equipamento Misterioso Clandestino", "Placeholder.png"),
            ("Item Inexistente Qualquer", "Placeholder.png"),
        ]
        for nome_item, arquivo_esperado in casos_placeholder:
            res = obter_arquivo_imagem_item(nome_item)
            self.assertEqual(res, arquivo_esperado, f"Item '{nome_item}' deveria mapear para '{arquivo_esperado}', mas retornou '{res}'")
            self.assertTrue(eh_arte_placeholder(nome_item), f"Item '{nome_item}' deveria ser identificado como placeholder")

    def test_carregar_sprite_item_e_cache(self):
        """Verifica se carregar_sprite_item retorna superfície válida e faz cache adequado."""
        surf1 = carregar_sprite_item("Katana", tamanho=(34, 34))
        self.assertIsInstance(surf1, pygame.Surface)
        self.assertEqual(surf1.get_size(), (34, 34))

        # Segunda chamada deve retornar o mesmo objeto do cache
        surf2 = carregar_sprite_item("Katana", tamanho=(34, 34))
        self.assertIs(surf1, surf2)

        # Placeholder também deve gerar superfície no tamanho pedido
        surf_ph = carregar_sprite_item("Capacete de Ferro", tamanho=(28, 28))
        self.assertEqual(surf_ph.get_size(), (28, 28))

    def test_catalogo_itens_json_sprites_validos(self):
        """Verifica se todos os itens cadastrados no itens.json apontam para imagens existentes no disco."""
        todos = obter_todos_itens_catalogo()
        self.assertGreater(len(todos), 0, "Catálogo de itens não pode estar vazio")

        for item in todos:
            img = item.get("arquivo_imagem")
            self.assertTrue(bool(img), f"Item {item.get('id')} ({item.get('nome')}) deve possuir arquivo_imagem definido")
            caminho = caminho_imagem(img)
            self.assertTrue(os.path.exists(caminho), f"Sprite '{img}' do item {item.get('id')} não foi encontrado no disco (caminho: {caminho})")

    def test_tela_descanso_renderizacao_com_sprites_e_tooltips(self):
        """Verifica que a TelaDescanso renderiza slots com sprites de itens reais e placeholders sem erros."""
        inventario_global.resetar()
        # Adiciona itens variados (com artes oficiais e com placeholders)
        inventario_global.adicionar_consumivel("Poção de Vida", "Cura 30 HP", 30, 0)
        inventario_global.adicionar_consumivel("Café Expresso Revigorante", "Cura 35 HP e 10 MP", 35, 10)
        inventario_global.adicionar_material("Sucata", "Material de melhoria")
        inventario_global.adicionar_bilhete_dormitorio(2)
        inventario_global.adicionar_polidor_itens(1)

        # Equipamento com arte oficial
        eq_katana = Equipamento("Katana", {"Agi": 3}, categoria="arma")
        inventario_global.equipar(eq_katana)

        # Equipamento com placeholder
        eq_capacete = Equipamento("Capacete de Ferro", {"Con": 2}, categoria="capacete")
        inventario_global.equipar(eq_capacete)

        tela_descanso = TelaDescanso(self.tela)

        # Executa atualização e renderização
        tela_descanso.atualizar((400, 300), (False, False, False))
        tela_descanso.desenhar((400, 300))

        # Testa tooltip para item com arte oficial
        tela_descanso._desenhar_tooltip_item(eq_katana, (400, 300))

        # Testa tooltip para item com placeholder
        tela_descanso._desenhar_tooltip_item(eq_capacete, (400, 300))


if __name__ == "__main__":
    unittest.main()
