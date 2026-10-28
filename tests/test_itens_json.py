import os
import sys
import json
import unittest
from pathlib import Path

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

RAIZ = Path(__file__).resolve().parent.parent / "An Average City"
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from Sistemas.Recursos import caminho_dados
from Sistemas.Inventario import (
    inventario_global,
    carregar_dados_itens,
    obter_catalogo_equipamentos,
    obter_todos_itens_catalogo,
    obter_item_por_id_ou_nome,
    obter_itens_por_tipo,
    obter_itens_por_categoria,
    Consumivel,
    Material,
    Equipamento,
)


class TestItensJSON(unittest.TestCase):
    def setUp(self):
        self.caminho_json = caminho_dados("itens.json")
        self.assertTrue(os.path.exists(self.caminho_json), "O arquivo itens.json deve existir em Dados/")
        with open(self.caminho_json, "r", encoding="utf-8") as f:
            self.dados = json.load(f)

    def test_estrutura_categorias_raiz(self):
        """Verifica se o JSON possui as categorias principais estruturadas."""
        chaves_esperadas = {"consumiveis", "materiais", "especiais", "equipamentos", "itens"}
        for chave in chaves_esperadas:
            self.assertIn(chave, self.dados)
            self.assertIsInstance(self.dados[chave], list)
            self.assertGreater(len(self.dados[chave]), 0)

    def test_todos_itens_possuem_campos_obrigatorios(self):
        """Garante que todos os itens possuem os campos essenciais de identificação e narrativa."""
        campos_obrigatorios = ["id", "nome", "tipo", "categoria", "descricao"]
        for item in self.dados["itens"]:
            for campo in campos_obrigatorios:
                self.assertIn(campo, item, f"Item {item.get('nome')} deve possuir o campo '{campo}'")
                self.assertTrue(str(item[campo]).strip(), f"Campo '{campo}' do item {item.get('nome')} não pode ser vazio")

    def test_consumiveis_possuem_recuperacao(self):
        """Verifica se todos os consumíveis definem restauração de vida ou mana."""
        for c in self.dados["consumiveis"]:
            self.assertEqual(c["tipo"], "consumivel")
            self.assertIn("rec_hp", c)
            self.assertIn("rec_mp", c)
            self.assertTrue(c["rec_hp"] > 0 or c["rec_mp"] > 0, f"Consumível {c['nome']} deve recuperar HP ou MP")

    def test_equipamentos_possuem_categorias_validas(self):
        """Verifica se os equipamentos possuem categorias e bônus de atributos válidos."""
        categorias_validas = {"arma", "capacete", "peitoral", "calca", "bota", "amuleto"}
        for eq in self.dados["equipamentos"]:
            self.assertEqual(eq["tipo"], "equipamento")
            self.assertIn(eq["categoria"], categorias_validas, f"Equipamento {eq['nome']} com categoria inválida: {eq['categoria']}")
            self.assertIsInstance(eq.get("atributos_bonus"), dict)
            self.assertGreater(len(eq["atributos_bonus"]), 0, f"Equipamento {eq['nome']} deve possuir atributos_bonus")

    def test_funcoes_acesso_inventario(self):
        """Verifica se as funções utilitárias em Inventario.py carregam e filtram itens do JSON."""
        todos = obter_todos_itens_catalogo()
        self.assertGreaterEqual(len(todos), 40)

        # Busca por ID
        pocao = obter_item_por_id_ou_nome("pocao_vida")
        self.assertIsNotNone(pocao)
        self.assertEqual(pocao["nome"], "Poção de Vida")
        self.assertEqual(pocao["rec_hp"], 30)

        # Busca por Nome
        machado = obter_item_por_id_ou_nome("Machado")
        self.assertIsNotNone(machado)
        self.assertEqual(machado["categoria"], "arma")

        # Filtro por Tipo
        consumiveis = obter_itens_por_tipo("consumivel")
        self.assertGreaterEqual(len(consumiveis), 6)

        # Filtro por Categoria
        amuletos = obter_itens_por_categoria("amuleto")
        self.assertGreaterEqual(len(amuletos), 7)

    def test_adicionar_item_por_id_ao_inventario(self):
        """Testa o método adicionar_item_por_id do inventario_global com itens do JSON."""
        inventario_global.resetar()

        # Adiciona poção de vida
        sucesso_pocao = inventario_global.adicionar_item_por_id("pocao_vida", 3)
        self.assertTrue(sucesso_pocao)
        self.assertEqual(len(inventario_global.consumiveis), 1)
        self.assertEqual(inventario_global.consumiveis[0].quantidade, 3)

        # Adiciona sucata
        sucesso_sucata = inventario_global.adicionar_item_por_id("sucata", 5)
        self.assertTrue(sucesso_sucata)
        self.assertEqual(inventario_global.materiais_totais(), 5)

        # Adiciona bilhete do dormitório
        sucesso_bilhete = inventario_global.adicionar_item_por_id("bilhete_dormitorio", 2)
        self.assertTrue(sucesso_bilhete)
        # Iniciou com 1 no reset + 2 adicionados = 3
        self.assertEqual(inventario_global.bilhetes_dormitorio, 3)

        # Adiciona polidor de itens
        sucesso_polidor = inventario_global.adicionar_item_por_id("polidor_itens", 2)
        self.assertTrue(sucesso_polidor)
        self.assertEqual(inventario_global.polidores_itens, 2)

        # Adiciona equipamento
        sucesso_arma = inventario_global.adicionar_item_por_id("machado", 1)
        self.assertTrue(sucesso_arma)
        self.assertEqual(len(inventario_global.equipamentos_inventario), 1)
        self.assertEqual(inventario_global.equipamentos_inventario[0].nome, "Machado")


if __name__ == "__main__":
    unittest.main()
