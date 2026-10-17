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
from Telas.TelaCenarios import GerenciadorSelecao
from Telas.TelaDescanco import GerenciadorPosLuta
from Entidades.Personagem import personagem
from Sistemas.Inventario import inventario_global, Equipamento
from Gameplay.GeracaoFases import (
    BANCO_EVENTOS,
    obter_evento_por_nome,
    obter_dialogo_evento,
    executar_efeito_evento,
)
import Main

NOMES_ESPERADOS = [
    "Um Estranho te convida para beber",
    "A porta do achados e perdidos ficou aberta",
    "Comprar com o perigo",
    "Alguem na entrada do bar te chama",
    "Duelar até cair",
    "Uma Pausa para comprar mantimentos",
]

def testar_carregamento_eventos_json():
    assert len(BANCO_EVENTOS) == 6
    nomes_carregados = [ev["nome"] for ev in BANCO_EVENTOS]
    for nome_esperado in NOMES_ESPERADOS:
        assert nome_esperado in nomes_carregados
        raw_evento = next(ev for ev in BANCO_EVENTOS if ev["nome"] == nome_esperado)
        assert "vitoria" in raw_evento
        assert "derrota" in raw_evento
        assert "resumo" in raw_evento["vitoria"]
        assert "narrativa" in raw_evento["vitoria"]
        assert "efeitos" in raw_evento["vitoria"]
        assert "mensagem" in raw_evento["vitoria"]
        assert "resumo" in raw_evento["derrota"]
        assert "narrativa" in raw_evento["derrota"]
        assert "efeitos" in raw_evento["derrota"]
        assert "mensagem" in raw_evento["derrota"]

        evento_obj = obter_evento_por_nome(nome_esperado)
        assert evento_obj.nome == nome_esperado
        assert len(evento_obj.descricao) > 0
        assert evento_obj.atributo_chave in ("For", "Agi", "Con", "Sab", "Int", "Sor")
        assert evento_obj.dificuldade > 0
        assert evento_obj.vitoria is not None and len(evento_obj.vitoria) > 0
        assert evento_obj.derrota is not None and len(evento_obj.derrota) > 0

def testar_selecao_cenarios_duas_escolhas():
    tela = pygame.display.get_surface()
    selecao = GerenciadorSelecao(tela)
    eventos_opcoes = [op for op in selecao.retangulos if op["nome"].startswith("evento_neutro_")]
    assert len(eventos_opcoes) == 3
    assert len(selecao.retangulos) == 3
    for op in eventos_opcoes:
        assert ":" in op["nome"]
        nome_extraido = op["nome"].split(":", 1)[1]
        assert nome_extraido in NOMES_ESPERADOS
        dados_dialogo = obter_dialogo_evento(op["nome"])
        assert len(dados_dialogo) == 1
        opcoes_dialogo = dados_dialogo[0]["opcoes"]
        assert len(opcoes_dialogo) == 2
        assert opcoes_dialogo[0]["retorno"].startswith("evento_acao:tentar:")
        assert opcoes_dialogo[1]["retorno"] == "cancelar_evento"

def testar_sucesso_e_falha_todos_eventos():
    tela = pygame.display.get_surface()
    jogo = GerenciadorJogo(tela)

    personagem.resetar()
    jogo.configurar_classe("Sobrevivente", "Físico")
    personagem.hp = 50
    personagem.mp = 2
    sab_antes = personagem.atributos["Sab"]
    con_antes = personagem.atributos["Con"]
    res_bom_1 = executar_efeito_evento("evento_acao:tentar:Um Estranho te convida para beber", jogo_tela=jogo, rolagem_forcada=15)
    assert res_bom_1["sucesso"] is True
    assert res_bom_1["total_teste"] == 15 + sab_antes
    assert personagem.hp == 85
    assert personagem.mp == 10
    assert personagem.atributos["Sab"] == sab_antes + 1
    assert personagem.atributos["Con"] == con_antes + 1

    personagem.resetar()
    personagem.hp = 60
    personagem.mp = 8
    res_ruim_1 = executar_efeito_evento("evento_acao:tentar:Um Estranho te convida para beber", jogo_tela=jogo, rolagem_forcada=2)
    assert res_ruim_1["sucesso"] is False
    assert personagem.hp == 40
    assert personagem.mp == 3

    inventario_global.resetar()
    personagem.resetar()
    jogo.configurar_classe("Sobrevivente", "Físico")
    for_antes = personagem.atributos["For"]
    res_bom_2 = executar_efeito_evento("evento_acao:tentar:A porta do achados e perdidos ficou aberta", jogo_tela=jogo, rolagem_forcada=15)
    assert res_bom_2["sucesso"] is True
    assert personagem.atributos["For"] == for_antes + 1
    assert inventario_global.materiais_totais() == 2
    assert sum(c.quantidade for c in inventario_global.consumiveis) == 1
    assert inventario_global.bilhetes_dormitorio == 2

    personagem.resetar()
    personagem.hp = 60
    res_ruim_2 = executar_efeito_evento("evento_acao:tentar:A porta do achados e perdidos ficou aberta", jogo_tela=jogo, rolagem_forcada=1)
    assert res_ruim_2["sucesso"] is False
    assert personagem.hp == 45
    assert res_ruim_2["quantidade_inimigos"] == 3
    assert res_ruim_2["multiplicador_forca"] > 1.0

    inventario_global.resetar()
    personagem.resetar()
    jogo.configurar_classe("Sobrevivente", "Físico")
    for_antes_3 = personagem.atributos["For"]
    sor_antes_3 = personagem.atributos["Sor"]
    nivel_eq_antes = inventario_global.equipamento_slot.nivel
    res_bom_3 = executar_efeito_evento("evento_acao:tentar:Comprar com o perigo", jogo_tela=jogo, rolagem_forcada=14)
    assert res_bom_3["sucesso"] is True
    assert personagem.atributos["For"] == for_antes_3 + 1
    assert personagem.atributos["Sor"] == sor_antes_3 + 1
    assert inventario_global.equipamento_slot.nivel == nivel_eq_antes + 1

    personagem.resetar()
    personagem.hp = 70
    inventario_global.resetar()
    inventario_global.adicionar_material("Sucata", "Melhora equips.")
    res_ruim_3 = executar_efeito_evento("evento_acao:tentar:Comprar com o perigo", jogo_tela=jogo, rolagem_forcada=1)
    assert res_ruim_3["sucesso"] is False
    assert personagem.hp == 50
    assert inventario_global.materiais_totais() == 0

    personagem.resetar()
    jogo.configurar_classe("Sobrevivente", "Físico")
    personagem.hp = 60
    for_antes_4 = personagem.atributos["For"]
    pts_antes_4 = personagem.pontos_atributo
    xp_antes_4 = personagem.xp
    res_bom_4 = executar_efeito_evento("evento_acao:tentar:Alguem na entrada do bar te chama", jogo_tela=jogo, rolagem_forcada=16)
    assert res_bom_4["sucesso"] is True
    assert personagem.atributos["For"] == for_antes_4 + 1
    assert personagem.pontos_atributo == pts_antes_4 + 1
    assert personagem.hp == 80
    assert personagem.xp == xp_antes_4 + 40
    assert res_bom_4["quantidade_inimigos"] == 1

    personagem.resetar()
    personagem.hp = 60
    personagem.mp = 8
    res_ruim_4 = executar_efeito_evento("evento_acao:tentar:Alguem na entrada do bar te chama", jogo_tela=jogo, rolagem_forcada=1)
    assert res_ruim_4["sucesso"] is False
    assert personagem.hp == 45
    assert personagem.mp == 3
    assert res_ruim_4["quantidade_inimigos"] == 3

    personagem.resetar()
    jogo.configurar_classe("Sobrevivente", "Físico")
    jogo.partida_atual = 2
    for_antes_5 = personagem.atributos["For"]
    jogo.configurar_cenario("evento_acao:tentar:Duelar até cair", rolagem_forcada=18)
    assert jogo.evento_neutro.nome == "Duelar até cair"
    assert jogo.multiplicador_recompensa == 2.0
    assert personagem.atributos["For"] == for_antes_5 + 1
    inimigos_duelo = [e for e in jogo.ordem_turnos if not getattr(e, "is_player", False)]
    assert len(inimigos_duelo) == 1

    xp_inimigo = inimigos_duelo[0].xp
    xp_jogador_antes = personagem.xp
    inimigos_duelo[0].hp = 0
    jogo.xp_calculado = False
    resultado_luta = jogo.atualizar((0, 0), (0, 0, 0))
    assert resultado_luta == "vitoria"
    assert personagem.xp == xp_jogador_antes + (xp_inimigo * 2)

    personagem.resetar()
    personagem.hp = 70
    jogo.partida_atual = 2
    jogo.configurar_cenario("evento_acao:tentar:Duelar até cair", rolagem_forcada=1)
    assert jogo.multiplicador_recompensa == 1.0
    assert personagem.hp == 50

    inventario_global.resetar()
    personagem.resetar()
    jogo.configurar_classe("Sobrevivente", "Físico")
    personagem.hp = 50
    for_antes_6 = personagem.atributos["For"]
    res_bom_6 = executar_efeito_evento("evento_acao:tentar:Uma Pausa para comprar mantimentos", jogo_tela=jogo, rolagem_forcada=15)
    assert res_bom_6["sucesso"] is True
    assert personagem.hp == 85
    assert personagem.atributos["For"] == for_antes_6 + 1
    assert inventario_global.materiais_totais() == 1
    assert sum(c.quantidade for c in inventario_global.consumiveis) == 1

    personagem.resetar()
    personagem.hp = 60
    res_ruim_6 = executar_efeito_evento("evento_acao:tentar:Uma Pausa para comprar mantimentos", jogo_tela=jogo, rolagem_forcada=1)
    assert res_ruim_6["sucesso"] is False
    assert personagem.hp == 45

def testar_fluxo_tentar_e_ignorar_main():
    Main.reiniciar_para_menu()
    Main.jogo_tela.configurar_classe("Sobrevivente", "Físico")
    Main.selecao_tela.recarregar_opcoes()

    cartao_evento = Main.selecao_tela.retangulos[0]
    pos_cartao = cartao_evento["rect"].center
    evento_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": pos_cartao})
    evento_up = pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": 1, "pos": pos_cartao})

    Main.tratar_eventos_selecao_cenario(evento_down, pos_cartao)
    novo_estado = Main.tratar_eventos_selecao_cenario(evento_up, pos_cartao)
    assert novo_estado == "dialogo"
    assert Main.dialogo_tela.ativo
    assert len(Main.dialogo_tela.opcoes_retangulos) == 2

    rect_tentar = Main.dialogo_tela.opcoes_retangulos[0]
    pos_tentar = rect_tentar.center
    Main.tratar_eventos_dialogo(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": pos_tentar}), pos_tentar)
    estado_pos_tentar = Main.tratar_eventos_dialogo(pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": 1, "pos": pos_tentar}), pos_tentar)
    assert estado_pos_tentar == "pos_dialogo"
    assert Main.pos_dialogo_tela.titulo in ("SUCESSO!", "FALHA!")
    assert len(Main.pos_dialogo_tela.narrativa) > 0
    assert len(Main.pos_dialogo_tela.efeitos) > 0
    assert "1d20" not in Main.pos_dialogo_tela.narrativa
    assert "dificuldade" not in Main.pos_dialogo_tela.narrativa.lower()

    pos_avancar = Main.pos_dialogo_tela.btn_continuar.rect.center
    Main.tratar_eventos_pos_dialogo(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": pos_avancar}), pos_avancar)
    estado_jogo = Main.tratar_eventos_pos_dialogo(pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": 1, "pos": pos_avancar}), pos_avancar)
    assert estado_jogo == "jogo"
    assert Main.jogo_tela.evento_neutro is not None
    assert "🎲" in Main.jogo_tela.mensagem_log

    Main.selecao_tela.recarregar_opcoes()
    cartao_evento_2 = Main.selecao_tela.retangulos[0]
    pos_cartao_2 = cartao_evento_2["rect"].center
    Main.tratar_eventos_selecao_cenario(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": pos_cartao_2}), pos_cartao_2)
    Main.tratar_eventos_selecao_cenario(pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": 1, "pos": pos_cartao_2}), pos_cartao_2)

    personagem.resetar()
    Main.jogo_tela.configurar_classe("Sobrevivente", "Físico")
    hp_antes_ignorar = personagem.hp
    rect_ignorar = Main.dialogo_tela.opcoes_retangulos[1]
    pos_ignorar = rect_ignorar.center
    Main.tratar_eventos_dialogo(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": pos_ignorar}), pos_ignorar)
    estado_pos_ignorar = Main.tratar_eventos_dialogo(pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": 1, "pos": pos_ignorar}), pos_ignorar)
    assert estado_pos_ignorar == "jogo"
    assert Main.jogo_tela.evento_neutro is None
    assert personagem.hp == hp_antes_ignorar
    inimigos_batalha = [e for e in Main.jogo_tela.ordem_turnos if not getattr(e, "is_player", False)]
    assert len(inimigos_batalha) >= 1

def testar_atributo_sorte_e_critico():
    personagem.resetar()
    assert "Sor" in personagem.atributos
    assert personagem.atributos["Sor"] == 1

    tela = pygame.display.get_surface()
    pos_luta = GerenciadorPosLuta(tela)
    pos_luta.jogadores = [personagem]
    personagem.pontos_atributo = 2

    botao_sor = next(b for b, attr in pos_luta.botoes_up if attr == "Sor")
    evento_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": botao_sor.rect.center})
    evento_up = pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": 1, "pos": botao_sor.rect.center})
    pos_luta.atualizar_eventos(evento_down, botao_sor.rect.center)
    pos_luta.atualizar_eventos(evento_up, botao_sor.rect.center)
    assert personagem.atributos["Sor"] == 2
    assert personagem.pontos_atributo == 1

    from Entidades.Inimigo import Inimigo
    inimigo = Inimigo(0, 0, 50, "Maldicao1.png")
    assert "Sor" in inimigo.atributos
    assert inimigo.atributos["Sor"] >= 1

def testar_dormir_na_tela_cenarios():
    tela = pygame.display.get_surface()
    selecao = GerenciadorSelecao(tela)
    inventario_global.resetar()
    assert hasattr(selecao, "btn_dormir")
    assert inventario_global.bilhetes_dormitorio == 1

    pos_dormir = selecao.btn_dormir.rect.center
    evento_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": pos_dormir})
    evento_up = pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": 1, "pos": pos_dormir})

    selecao.atualizar_eventos(evento_down, pos_dormir)
    resultado = selecao.atualizar_eventos(evento_up, pos_dormir)
    assert resultado == "dormir"

    inventario_global.consumir_bilhete_dormitorio(1)
    assert inventario_global.bilhetes_dormitorio == 0
    selecao.atualizar_eventos(evento_down, pos_dormir)
    resultado_sem_bilhete = selecao.atualizar_eventos(evento_up, pos_dormir)
    assert resultado_sem_bilhete is None
    assert "Bilhete do Dormitório" in selecao.mensagem

    inventario_global.adicionar_bilhete_dormitorio(1)
    personagem.resetar()
    Main.jogo_tela.configurar_classe("Sobrevivente", "Físico")
    personagem.hp = 20
    personagem.mp = 1
    fase_antes = Main.jogo_tela.fase_numero

    Main.tratar_eventos_selecao_cenario(evento_down, pos_dormir)
    estado_jogo = Main.tratar_eventos_selecao_cenario(evento_up, pos_dormir)
    assert estado_jogo == "jogo"
    assert inventario_global.bilhetes_dormitorio == 0
    assert personagem.hp > 20
    assert personagem.mp > 1
    assert Main.jogo_tela.evento_neutro is None
    assert Main.jogo_tela.fase_numero == fase_antes + 1
    assert "dormitório" in Main.jogo_tela.mensagem_log.lower()

if __name__ == "__main__":
    testar_carregamento_eventos_json()
    testar_selecao_cenarios_duas_escolhas()
    testar_sucesso_e_falha_todos_eventos()
    testar_fluxo_tentar_e_ignorar_main()
    testar_atributo_sorte_e_critico()
    testar_dormir_na_tela_cenarios()
    print("[SUCESSO] Testes de rolagem 1d20 + atributo, resultados bons/ruins, ignorar para próxima batalha, dormir e Sorte concluídos!")
