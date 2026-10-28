import json
import os
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent / "An Average City"
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from Sistemas.Recursos import caminho_imagem, caminho_botao, caminho_cenario


class TestDados(unittest.TestCase):
    def test_inimigos_e_habilidades(self):
        caminho_inimigos = RAIZ / "Dados" / "inimigos.json"
        caminho_hab_ini = RAIZ / "Dados" / "habilidades_inimigos.json"

        with open(caminho_inimigos, "r", encoding="utf-8") as f:
            inimigos = json.load(f)

        with open(caminho_hab_ini, "r", encoding="utf-8") as f:
            hab_inimigos = json.load(f)

        for ini in inimigos:
            for atq in ini.get("ataques", []):
                self.assertIn(
                    atq, hab_inimigos,
                    f"Ataque '{atq}' do inimigo '{ini['nome']}' não existe em habilidades_inimigos.json"
                )

    def test_habilidades_bosses_em_inimigos_e_nao_jogador(self):
        caminho_hab_ini = RAIZ / "Dados" / "habilidades_inimigos.json"
        caminho_hab_jog = RAIZ / "Dados" / "habilidades_jogador.json"

        with open(caminho_hab_ini, "r", encoding="utf-8") as f:
            hab_inimigos = json.load(f)

        with open(caminho_hab_jog, "r", encoding="utf-8") as f:
            hab_jogador = json.load(f)

        # Boss skills must be in habilidades_inimigos.json
        self.assertIn("Santuário Malevolente", hab_inimigos)
        self.assertTrue(hab_inimigos["Santuário Malevolente"].get("is_ultimate"))
        self.assertEqual(hab_inimigos["Santuário Malevolente"].get("minion"), "Pequeno Santuário")

        self.assertIn("Plantar Spike", hab_inimigos)
        self.assertTrue(hab_inimigos["Plantar Spike"].get("is_ultimate"))

        self.assertIn("Spike", hab_inimigos)
        self.assertTrue(hab_inimigos["Spike"].get("is_ultimate"))

        # Boss skills must NOT be in habilidades_jogador.json
        self.assertNotIn("Plantar Spike", hab_jogador)
        self.assertNotIn("Spike", hab_jogador)
        self.assertNotIn("Santuário Malevolente", hab_jogador.get("habilidades", {}))
        self.assertNotIn("Feiticeiro|Sukuna", hab_jogador.get("ultimates", {}))

    def test_sprites_existem(self):
        caminho_inimigos = RAIZ / "Dados" / "inimigos.json"

        with open(caminho_inimigos, "r", encoding="utf-8") as f:
            inimigos = json.load(f)

        for ini in inimigos:
            img = ini.get("arquivo_imagem")
            if img:
                caminho_resolvido = caminho_imagem(img)
                self.assertTrue(
                    os.path.exists(caminho_resolvido),
                    f"Sprite '{img}' do inimigo '{ini['nome']}' não encontrada em {caminho_resolvido}"
                )

    def test_sprites_cenarios_reorganizados(self):
        """Verifica se cenários movidos para subpastas são encontrados corretamente."""
        cenarios_esperados = ["Menu.png", "Fight.png", "SewerAccess.png", "EsgotoTrancado.png", "EsgotoLivre.png", "GameOver Feiticeiro.png", "GameOver Agente.png"]
        for cen in cenarios_esperados:
            caminho_resolvido = caminho_imagem(cen)
            self.assertTrue(
                os.path.exists(caminho_resolvido),
                f"Cenário '{cen}' não encontrado em {caminho_resolvido}"
            )
            caminho_cen = caminho_cenario(cen)
            self.assertTrue(
                os.path.exists(caminho_cen),
                f"Cenário '{cen}' não encontrado via caminho_cenario em {caminho_cen}"
            )

    def test_sprites_botoes_e_debuffs(self):
        """Verifica se sprites de botões e debuffs são encontrados em suas respectivas subpastas."""
        self.assertTrue(os.path.exists(caminho_botao("BACK.png")))
        self.assertTrue(os.path.exists(caminho_botao("AGENTC.png")))
        self.assertTrue(os.path.exists(caminho_imagem("Atordoado.png")))
        self.assertTrue(os.path.exists(caminho_imagem("Fogo.png")))

    def test_conquistas_e_arvores(self):
        caminho_conquistas = RAIZ / "Dados" / "conquistas.json"
        caminho_arvores = RAIZ / "Dados" / "arvores.json"

        with open(caminho_conquistas, "r", encoding="utf-8") as f:
            conquistas = json.load(f)
        self.assertGreater(len(conquistas), 0)

        with open(caminho_arvores, "r", encoding="utf-8") as f:
            arvores = json.load(f)
        for verso in ("Sobrevivente", "Agente", "Feiticeiro"):
            self.assertIn(verso, arvores)


if __name__ == "__main__":
    unittest.main()
