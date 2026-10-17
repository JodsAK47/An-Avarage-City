import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

DIRETORIO_RAIZ = Path(__file__).resolve().parent.parent
if str(DIRETORIO_RAIZ) not in sys.path:
    sys.path.insert(0, str(DIRETORIO_RAIZ))

import pygame
pygame.init()
pygame.display.set_mode((1000, 800))

from Telas.TelaCombate import GerenciadorJogo
from Telas.TelaVerso import GerenciadorVerso
from Entidades.Personagem import personagem
from Sistemas.SaveSystem import save_global

def test_desbloqueio_ultimates_por_verso():
    tela = pygame.display.get_surface()
    gerenciador_combate = GerenciadorJogo(tela)
    gerenciador_verso = GerenciadorVerso(tela)

    save_global.resetar_tudo()
    personagem.resetar()
    personagem.talentos = set()
    personagem.ultimates_desbloqueadas = set()

    gerenciador_combate.configurar_classe("Sobrevivente", "Físico")
    assert "Ultimate do Sobrevivente: Fúria Brutal" not in personagem.ataques, (
        f"Ultimate não deveria aparecer sem S4: {personagem.ataques}"
    )
    assert len(personagem.ataques) == 2, f"Deveria ter apenas 2 ataques básicos: {personagem.ataques}"

    gerenciador_combate.configurar_classe("Agente", "Distância")
    assert "Ultimate do Agente: Apagão" not in personagem.ataques, (
        f"Ultimate do Agente não deveria aparecer sem A4: {personagem.ataques}"
    )

    gerenciador_combate.configurar_classe("Feiticeiro", "Magia")
    assert "Ultimate do Feiticeiro: Eclipse Sombrio" not in personagem.ataques, (
        f"Ultimate do Feiticeiro não deveria aparecer sem F4: {personagem.ataques}"
    )

    save_global.adicionar_pontos(200)
    gerenciador_verso.verso_atual = "Sobrevivente"
    gerenciador_verso.progresso_por_verso["Sobrevivente"] = ["S1", "S2", "S3", "S4"]
    save_global.definir_progresso_verso("Sobrevivente", ["S1", "S2", "S3", "S4"])
    gerenciador_verso.sincronizar_habilidades_ativas()

    gerenciador_combate.configurar_classe("Sobrevivente", "Físico")
    assert "Ultimate do Sobrevivente: Fúria Brutal" in personagem.ataques, (
        f"Ultimate deveria estar presente após desbloquear S4: {personagem.ataques}"
    )

    gerenciador_combate.configurar_classe("Agente", "Físico")
    assert "Ultimate do Agente: Golpe Final" not in personagem.ataques, (
        f"Ultimate do Agente NÃO deve aparecer só porque Sobrevivente desbloqueou a sua: {personagem.ataques}"
    )

    gerenciador_verso.verso_atual = "Agente"
    gerenciador_verso.progresso_por_verso["Agente"] = ["A1", "A2", "A3", "A4"]
    save_global.definir_progresso_verso("Agente", ["A1", "A2", "A3", "A4"])
    gerenciador_verso.sincronizar_habilidades_ativas()

    gerenciador_combate.configurar_classe("Agente", "Físico")
    assert "Ultimate do Agente: Golpe Final" in personagem.ataques, (
        f"Ultimate do Agente deveria estar presente após desbloquear A4: {personagem.ataques}"
    )

    gerenciador_combate.configurar_classe("Feiticeiro", "Físico")
    assert "Ultimate do Feiticeiro: Fúria Arcana" not in personagem.ataques, (
        f"Ultimate do Feiticeiro não deve aparecer sem F4: {personagem.ataques}"
    )

    save_global.salvar()
    verso_recarregado = GerenciadorVerso(tela)
    assert verso_recarregado.progresso_por_verso["Sobrevivente"] == ["S1", "S2", "S3", "S4"]
    assert verso_recarregado.progresso_por_verso["Agente"] == ["A1", "A2", "A3", "A4"]
    assert verso_recarregado.progresso_por_verso["Feiticeiro"] == []

    save_global.resetar_tudo()
    personagem.resetar()
    print("✓ Testes de desbloqueio de ultimate por verso e persistência da skill tree passaram com 100% de sucesso!")

if __name__ == "__main__":
    test_desbloqueio_ultimates_por_verso()
