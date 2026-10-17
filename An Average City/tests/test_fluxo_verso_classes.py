import os
import sys
from pathlib import Path

DIRETORIO_RAIZ = Path(__file__).resolve().parent.parent
if str(DIRETORIO_RAIZ) not in sys.path:
    sys.path.insert(0, str(DIRETORIO_RAIZ))

import pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1000, 800))

from Telas.TelaVerso import GerenciadorVerso
from Telas.TelaClasses import GerenciadorClasses
import Main

def testar_separacao_telas_e_fluxo_sem_repeticao():
    tela = pygame.Surface((1000, 800))
    evento_dummy = pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": 1, "pos": (0, 0)})

    Main.reiniciar_para_menu()
    Main.verso_menu_selecionado = None
    assert Main.jogo_tela.classe_atual == "Nenhuma"

    Main.menu_tela.botoes["classe"].pressionado = True
    resultado_menu_verso = Main.tratar_eventos_menu(evento_dummy, Main.menu_tela.botoes["classe"].rect.center)
    assert resultado_menu_verso == "verso", "Deve abrir a tela de verso ao clicar no menu"
    assert Main.verso_tela.modo == "menu", "Modo no menu deve ser 'menu' (para gastar pontos e melhorias)"

    Main.verso_tela.verso_atual = "Feiticeiro"
    Main.verso_tela.botao_selecionar.pressionado = True
    resultado_verso_menu = Main.tratar_eventos_verso(evento_dummy, Main.verso_tela.botao_selecionar.rect.center)
    assert resultado_verso_menu is None, "Selecionar verso no menu NÃO deve transicionar para tela de classes!"
    assert Main.verso_menu_selecionado == "Feiticeiro"
    assert Main.jogo_tela.classe_atual == "Feiticeiro"
    assert "definido como ativo" in Main.verso_tela.aviso

    Main.verso_tela.botao_voltar.pressionado = True
    resultado_voltar = Main.tratar_eventos_verso(evento_dummy, Main.verso_tela.botao_voltar.rect.center)
    assert resultado_voltar == "menu"

    Main.menu_tela.botoes["jogar"].pressionado = True
    resultado_jogar = Main.tratar_eventos_menu(evento_dummy, Main.menu_tela.botoes["jogar"].rect.center)
    assert resultado_jogar == "classes", "Tendo verso escolhido, deve ir direto para a tela de classes"
    assert Main.alvo_classes == 1

    Main.classes_tela.botao_selecionar.pressionado = True
    resultado_classe = Main.tratar_eventos_classes(evento_dummy, Main.classes_tela.botao_selecionar.rect.center)
    assert resultado_classe == "jogo", "A escolha de classe deve iniciar o jogo diretamente!"

    Main.reiniciar_para_menu()
    Main.verso_menu_selecionado = None
    assert Main.jogo_tela.classe_atual == "Nenhuma"

    Main.menu_tela.botoes["jogar"].pressionado = True
    resultado_jogar_sem_verso = Main.tratar_eventos_menu(evento_dummy, Main.menu_tela.botoes["jogar"].rect.center)
    assert resultado_jogar_sem_verso == "verso", "Sem verso prévio, deve abrir a tela de visualização de verso"
    assert Main.verso_tela.modo == "visualizacao", "Tela aberta deve ser apenas de visualização de verso"

    Main.verso_tela.habilidade_foco = {"id": "S1", "preco": 10, "req": [], "nome": "Teste"}
    Main.verso_tela.pontos = 100
    Main.verso_tela.botao_comprar.pressionado = True
    Main.verso_tela.atualizar_eventos(evento_dummy, Main.verso_tela.botao_comprar.rect.center)
    assert "S1" not in Main.verso_tela.habilidades_desbloqueadas, "Modo visualização não deve permitir compras!"

    Main.verso_tela.verso_atual = "Sobrevivente"
    Main.verso_tela.botao_selecionar.pressionado = True
    resultado_confirmar_verso = Main.tratar_eventos_verso(evento_dummy, Main.verso_tela.botao_selecionar.rect.center)
    assert resultado_confirmar_verso == "classes", "Confirmar verso na visualização deve avançar para classes"
    assert Main.alvo_classes == 1
    assert Main.jogo_tela.classe_atual == "Sobrevivente"

    Main.classes_tela.classe_atual = "Físico"
    Main.classes_tela.botao_selecionar.pressionado = True
    resultado_classe_final = Main.tratar_eventos_classes(evento_dummy, Main.classes_tela.botao_selecionar.rect.center)
    assert resultado_classe_final == "jogo", "Após escolher a classe, deve ir direto para o jogo sem repetição!"

    Main.reiniciar_para_menu()
    Main.verso_menu_selecionado = None
    Main.menu_tela.duas_pessoas = True

    Main.menu_tela.botoes["jogar"].pressionado = True
    res_2p_jogar = Main.tratar_eventos_menu(evento_dummy, Main.menu_tela.botoes["jogar"].rect.center)
    assert res_2p_jogar == "verso"
    assert Main.verso_tela.modo == "visualizacao"

    Main.verso_tela.verso_atual = "Agente"
    Main.verso_tela.botao_selecionar.pressionado = True
    res_2p_v = Main.tratar_eventos_verso(evento_dummy, Main.verso_tela.botao_selecionar.rect.center)
    assert res_2p_v == "classes"
    assert Main.alvo_classes == 1

    Main.classes_tela.classe_atual = "Distância"
    Main.classes_tela.botao_selecionar.pressionado = True
    res_2p_c1 = Main.tratar_eventos_classes(evento_dummy, Main.classes_tela.botao_selecionar.rect.center)
    assert res_2p_c1 is None, "Em 2P, após J1 deve esperar escolha de J2"
    assert Main.alvo_classes == 2

    Main.classes_tela.classe_atual = "Magia"
    Main.classes_tela.botao_selecionar.pressionado = True
    res_2p_c2 = Main.tratar_eventos_classes(evento_dummy, Main.classes_tela.botao_selecionar.rect.center)
    assert res_2p_c2 == "jogo", "Em 2P, após J2 deve iniciar o jogo diretamente!"

    print("[SUCESSO] Todos os testes de fluxo de verso e classes passaram com 100% de sucesso!")

def testar_equipamentos_iniciais_classes():
    from Sistemas.Inventario import inventario_global
    from Telas.TelaCombate import TABELA_EQUIPAMENTOS_INICIAIS, _obter_equipamento_inicial
    from Telas.TelaDescanco import GerenciadorPosLuta
    from Telas.TelaInventario import TelaInventario

    combinacoes = [
        ("Sobrevivente", "Físico", "Machado"),
        ("Sobrevivente", "Distância", "Estilingue"),
        ("Sobrevivente", "Magia", "Pedra Preciosa Multicor"),
        ("Agente", "Físico", "Faca de Confronto"),
        ("Agente", "Distância", "Vandal"),
        ("Agente", "Magia", "Rocha De Radianita"),
        ("Feiticeiro", "Físico", "Katana"),
        ("Feiticeiro", "Distância", "Amplificador de alcance"),
        ("Feiticeiro", "Magia", "Ferramenta Amaldiçoada"),
    ]

    tela = pygame.Surface((1000, 800))
    descanco = GerenciadorPosLuta(tela)
    inventario_tela = TelaInventario(tela)

    for verso, classe, item_esperado in combinacoes:
        inventario_global.resetar()
        assert inventario_global.equipamento_slot is None

        Main.jogo_tela.configurar_classe(verso, classe)
        assert inventario_global.equipamento_slot is not None, f"Equipamento deve estar presente para {verso} + {classe}"
        assert inventario_global.equipamento_slot.nome == item_esperado, f"Esperado {item_esperado}, obteve {inventario_global.equipamento_slot.nome}"

        # Teste de renderização sem erros
        descanco.desenhar()
        inventario_tela.desenhar()

        # Teste de clique no slot de equipamento em Descanso
        inventario, equipamentos = descanco._retangulos_slots()
        slot_eq = equipamentos[0]
        descanco.atualizar_eventos(pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": 1, "pos": slot_eq.center}), slot_eq.center)
        assert item_esperado in descanco.mensagem, f"A mensagem do slot clicado deve conter o nome do item {item_esperado}"

    # Teste através do fluxo real de telas em Main.py
    evento_dummy = pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": 1, "pos": (0, 0)})
    Main.reiniciar_para_menu()
    Main.verso_menu_selecionado = "Agente"
    Main.menu_tela.botoes["jogar"].pressionado = True
    Main.tratar_eventos_menu(evento_dummy, Main.menu_tela.botoes["jogar"].rect.center)
    Main.classes_tela.classe_atual = "Distância"
    Main.classes_tela.botao_selecionar.pressionado = True
    res = Main.tratar_eventos_classes(evento_dummy, Main.classes_tela.botao_selecionar.rect.center)
    assert res == "jogo"
    assert inventario_global.equipamento_slot is not None
    assert inventario_global.equipamento_slot.nome == "Vandal"

    print("[SUCESSO] Testes de equipamentos iniciais de classe concluídos com sucesso!")

if __name__ == "__main__":
    testar_separacao_telas_e_fluxo_sem_repeticao()
    testar_equipamentos_iniciais_classes()
