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
pygame.mixer.init()

from Sistemas.Constantes import Verso, MAPA_MUSICA_VERSO, obter_musica_combate
from Sistemas.Recursos import caminho_musica
from Sistemas.GerenciadorAudio import GerenciadorMusica, EstadoMusica, gerenciador_musica
from Sistemas.Configuracoes import sistema_config


class TestGerenciadorAudio(unittest.TestCase):
    def setUp(self):
        sistema_config.definir_mudo(False)
        sistema_config.definir_volume_geral(1.0)
        sistema_config.definir_volume_musica(1.0)
        gerenciador_musica.parar(fade_out_ms=0)

    def test_todas_osts_existem_no_disco(self):
        """Verifica se todos os arquivos referenciados existem no diretório OSTs."""
        arquivos_esperados = [
            "Menu.mp3",
            "GameOver.mp3",
            "Vitoria.mp3",
            "Sobrevivente Combate.mp3",
            "Sobrevivente Boss.mp3",
            "Agente Combate.mp3",
            "Agente Boss.mp3",
            "Feiticeiro Combate.mp3",
            "Feiticeiro Boss.mp3",
        ]
        for ost in arquivos_esperados:
            caminho = caminho_musica(ost)
            self.assertTrue(
                Path(caminho).exists(),
                f"OST não encontrada no disco: {ost} em {caminho}"
            )

    def test_mapeamento_musica_por_verso(self):
        """Verifica se cada verso retorna suas respectivas músicas de combate e boss."""
        casos = [
            ("Sobrevivente", False, "Sobrevivente Combate.mp3"),
            ("Sobrevivente", True, "Sobrevivente Boss.mp3"),
            ("Agente", False, "Agente Combate.mp3"),
            ("Agente", True, "Agente Boss.mp3"),
            ("Feiticeiro", False, "Feiticeiro Combate.mp3"),
            ("Feiticeiro", True, "Feiticeiro Boss.mp3"),
            # Variações de caixa e identificadores
            ("sobrevivente", False, "Sobrevivente Combate.mp3"),
            ("AGENTE", True, "Agente Boss.mp3"),
            ("feiticeiro", False, "Feiticeiro Combate.mp3"),
            (None, False, "Sobrevivente Combate.mp3"),
            ("Invalido", True, "Sobrevivente Boss.mp3"),
        ]
        for verso_input, eh_chefe, esperado in casos:
            resultado = obter_musica_combate(verso_input, eh_chefe=eh_chefe)
            self.assertEqual(resultado, esperado, f"Falha para verso={verso_input}, eh_chefe={eh_chefe}")

    def test_resolver_legados_combate_e_boss(self):
        """Testa se nomes genéricos legados são resolvidos para a trilha do verso ativo."""
        ger = GerenciadorMusica()
        ger.definir_verso("Feiticeiro")
        self.assertEqual(ger.resolver_nome_musica("Combate.mp3"), "Feiticeiro Combate.mp3")
        self.assertEqual(ger.resolver_nome_musica("Boss.mp3"), "Feiticeiro Boss.mp3")

        ger.definir_verso("Agente")
        self.assertEqual(ger.resolver_nome_musica("Combate.mp3"), "Agente Combate.mp3")
        self.assertEqual(ger.resolver_nome_musica("Boss.mp3"), "Agente Boss.mp3")

        ger.definir_verso("Sobrevivente")
        self.assertEqual(ger.resolver_nome_musica("Combate.mp3"), "Sobrevivente Combate.mp3")
        self.assertEqual(ger.resolver_nome_musica("Boss.mp3"), "Sobrevivente Boss.mp3")

    def test_transicao_fade_in_fade_out(self):
        """Testa o fluxo da máquina de estados de transição com fade out e fade in."""
        ger = GerenciadorMusica()
        # Iniciar primeira música com fade_in
        ger.tocar("Menu.mp3", fade_out_ms=0, fade_in_ms=400)
        self.assertEqual(ger.musica_atual, "Menu.mp3")
        self.assertEqual(ger.estado, EstadoMusica.FADING_IN)

        # Simular avanço no tempo para completar fade in
        ger.atualizar(dt=0.5)
        self.assertEqual(ger.estado, EstadoMusica.TOCANDO)
        self.assertAlmostEqual(ger.volume_atual, 1.0, places=1)

        # Transicionar para combate Sobrevivente
        ger.tocar("Sobrevivente Combate.mp3", fade_out_ms=300, fade_in_ms=400)
        self.assertEqual(ger.estado, EstadoMusica.FADING_OUT)
        self.assertEqual(ger.proxima_musica, "Sobrevivente Combate.mp3")

        # Avançar metade do fade out
        ger.atualizar(dt=0.15)
        self.assertEqual(ger.estado, EstadoMusica.FADING_OUT)
        self.assertTrue(0.0 < ger.volume_atual < 1.0)

        # Avançar o restante do fade out -> deve disparar a troca e iniciar fade in
        ger.atualizar(dt=0.2)
        self.assertEqual(ger.musica_atual, "Sobrevivente Combate.mp3")
        self.assertEqual(ger.estado, EstadoMusica.FADING_IN)

        # Avançar fade in até completar
        ger.atualizar(dt=0.5)
        self.assertEqual(ger.estado, EstadoMusica.TOCANDO)
        self.assertAlmostEqual(ger.volume_atual, 1.0, places=1)

    def test_continuidade_mesma_musica_sem_reinicio(self):
        """Garante que solicitar a mesma música que já está tocando não interrompe nem reinicia."""
        ger = GerenciadorMusica()
        ger.tocar("Menu.mp3", fade_out_ms=0, fade_in_ms=200)
        ger.atualizar(dt=0.3)
        self.assertEqual(ger.estado, EstadoMusica.TOCANDO)
        self.assertEqual(ger.musica_atual, "Menu.mp3")

        # Chama tocar na mesma música
        ger.tocar("Menu.mp3", fade_out_ms=500, fade_in_ms=500)
        # Deve permanecer TOCANDO, sem entrar em FADING_OUT
        self.assertEqual(ger.estado, EstadoMusica.TOCANDO)
        self.assertEqual(ger.musica_atual, "Menu.mp3")
        self.assertIsNone(ger.proxima_musica)


if __name__ == "__main__":
    unittest.main()
