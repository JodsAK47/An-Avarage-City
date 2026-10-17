import os
import sys
import json
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

from Sistemas import GerenciadorSave, save_global, sistema_conquistas
from Sistemas.Recursos import caminho_saves

def testar_ciclo_save():
    save_global.resetar_tudo()
    sistema_conquistas.resetar_todas()

    assert save_global.obter_pontos() == 0
    assert not save_global.tem_member_card()
    assert sistema_conquistas.total_desbloqueadas() == 0

    save_global.coletar_member_card()
    assert save_global.tem_member_card()

    caminho_arq = caminho_saves("save.json")
    with open(caminho_arq, "r", encoding="utf-8") as f:
        dados_disco = json.load(f)
    assert dados_disco["member_card_coletado"] is False, "Nao deve persistir no disco sem save explicito!"

    save_global.adicionar_pontos(50)
    save_global.definir_progresso_verso("Sobrevivente", ["S1", "S2"])
    save_global.definir_progresso_verso("Agente", ["A1"])
    save_global.salvar()

    with open(caminho_arq, "r", encoding="utf-8") as f:
        dados_salvos = json.load(f)
    assert dados_salvos["member_card_coletado"] is True
    assert dados_salvos["pontos"] == 50
    assert dados_salvos["progresso_versos"] == {"Sobrevivente": ["S1", "S2"], "Agente": ["A1"]}

    novo_save = GerenciadorSave()
    assert novo_save.tem_member_card() is True
    assert novo_save.obter_pontos() == 50
    assert novo_save.obter_progresso_verso("Sobrevivente") == ["S1", "S2"]
    assert novo_save.obter_progresso_verso("Agente") == ["A1"]
    assert novo_save.obter_progresso_verso("Feiticeiro") == []

    novo_save.resetar_tudo()
    sistema_conquistas.resetar_todas()
    assert novo_save.tem_member_card() is False
    assert novo_save.obter_pontos() == 0
    assert novo_save.obter_progresso_versos() == {}

    with open(caminho_arq, "r", encoding="utf-8") as f:
        dados_resetados = json.load(f)
    assert dados_resetados["progresso_versos"] == {}

    print("✓ Ciclo de save, persistência em Saves/ e reset testados com sucesso!")

if __name__ == "__main__":
    testar_ciclo_save()
