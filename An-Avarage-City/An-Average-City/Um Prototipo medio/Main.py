import pygame
import os
import sys
from Menu import GerenciadorMenu
from Jogo import GerenciadorJogo
from GameOver import GerenciadorGameOver
from MenuClasses import GerenciadorClasses 
from TelaVitoria import GerenciadorVitoria
from Cenarios import GerenciadorSelecao
from Descanço import GerenciadorPosLuta
from Dialogo import GerenciadorDialogo
from Entidades.Personagem import personagem
from Recursos import caminho_musica

pygame.init()
pygame.mixer.init()

LARGURA = 1000
ALTURA = 800
tela_real = pygame.display.set_mode((LARGURA, ALTURA), pygame.RESIZABLE)
tela = pygame.Surface((LARGURA, ALTURA))
pygame.display.set_caption("Menu RPG")
clock = pygame.time.Clock()
tela_cheia = False

menu_tela = GerenciadorMenu(tela)
jogo_tela = GerenciadorJogo(tela)
game_over_tela = GerenciadorGameOver(tela)
selecao_tela = GerenciadorSelecao(tela)
from Inventario import TelaInventario

classes_tela = GerenciadorClasses(tela) 
pos_luta_tela = GerenciadorPosLuta(tela)
dialogo_tela = GerenciadorDialogo(tela)
vitoria_tela = GerenciadorVitoria(tela)
inventario_tela = TelaInventario(tela)

player1_class = None
player2_class = None
classes_target = None

def tocar_musica(nome_arquivo):
    pygame.mixer.music.stop()
    try:
        pygame.mixer.music.load(caminho_musica(nome_arquivo))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    except pygame.error as erro:
        print(f"⚠️ Aviso: Não foi possível tocar '{nome_arquivo}'.")

tocar_musica("Menu.mp3")

estado = "menu"
rodando = True

while rodando:
    posicao_mouse_real = pygame.mouse.get_pos()
    estado_clique_mouse = pygame.mouse.get_pressed()

    largura_real, altura_real = tela_real.get_size()
    escala = min(largura_real / LARGURA, altura_real / ALTURA) if LARGURA > 0 and ALTURA > 0 else 1
    nova_largura = int(LARGURA * escala)
    nova_altura = int(ALTURA * escala)
    x_offset = (largura_real - nova_largura) // 2
    y_offset = (altura_real - nova_altura) // 2

    if escala > 0:
        mx = int((posicao_mouse_real[0] - x_offset) / escala)
        my = int((posicao_mouse_real[1] - y_offset) / escala)
    else:
        mx, my = 0, 0
    posicao_mouse = (max(0, min(mx, LARGURA)), max(0, min(my, ALTURA)))

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_F11:
                tela_cheia = not tela_cheia
                if tela_cheia:
                    tela_real = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    tela_real = pygame.display.set_mode((LARGURA, ALTURA), pygame.RESIZABLE)

        if estado == "menu":
            if menu_tela.botao_jogar.checar_clique(evento, posicao_mouse):
                if getattr(menu_tela, 'duas_pessoas', False):
                    classes_target = 1
                    classes_tela.aviso = "Escolha CLASSE para JOGADOR 1"
                    estado = "classes"
                else:
                    if jogo_tela.classe_atual == "Nenhuma":
                        classes_target = 1
                        classes_tela.aviso = "Escolha SUA CLASSE"
                        estado = "classes"
                    else:
                        jogo_tela.duas_pessoas = getattr(menu_tela, 'duas_pessoas', False)
                        jogo_tela.reiniciar()
                        estado = "jogo"
                        tocar_musica("Combate.mp3")
            elif menu_tela.botao_classe.checar_clique(evento, posicao_mouse):
                classes_tela.aviso = "Gerencie as Habilidades"
                estado = "classes"
            elif menu_tela.switch_2p.checar_clique(evento, posicao_mouse):
                menu_tela.duas_pessoas = not menu_tela.duas_pessoas
                if not menu_tela.duas_pessoas:
                    jogo_tela.duas_pessoas = False
                    jogo_tela.personagem2 = None
                    jogo_tela.classe_jogador2 = None
            elif menu_tela.botao_sair.checar_clique(evento, posicao_mouse):
                rodando = False

        elif estado == "classes":
            escolha_classe = classes_tela.atualizar_eventos(evento, posicao_mouse)
            
            if classes_tela.voltar_clicado:
                classes_target = None
                estado = "menu"
                classes_tela.voltar_clicado = False

            if escolha_classe:
                verso_escolhido, classe_escolhida = escolha_classe
                if classes_target == 1:
                    jogo_tela.configurar_classe(verso_escolhido, classe_escolhida)
                    player1_class = verso_escolhido
                    classes_tela.aviso = f"J1: {verso_escolhido} - {classe_escolhida}"
                    if getattr(menu_tela, 'duas_pessoas', False):
                        classes_target = 2
                        classes_tela.aviso = "Escolha CLASSE para JOGADOR 2"
                    else:
                        jogo_tela.duas_pessoas = False
                        jogo_tela.personagem2 = None
                        jogo_tela.classe_jogador2 = None
                        jogo_tela.classe_jogador2_tipo = None
                        jogo_tela.reiniciar()
                        estado = "jogo"
                        tocar_musica("Combate.mp3")
                elif classes_target == 2:
                    player2_class = verso_escolhido
                    classes_tela.aviso = f"J2: {verso_escolhido} - {classe_escolhida}"
                    jogo_tela.classe_jogador2 = verso_escolhido
                    jogo_tela.classe_jogador2_tipo = classe_escolhida
                    jogo_tela.duas_pessoas = True
                    jogo_tela.reiniciar()
                    estado = "jogo"
                    tocar_musica("Combate.mp3")

        elif estado == "game_over":
            if game_over_tela.botao_menu.checar_clique(evento, posicao_mouse):
                from Inventario import inventario_global
                inventario_global.resetar()
                personagem.resetar()
                jogo_tela.partida_atual = 1
                jogo_tela.pontos_jogo = max(0, jogo_tela.pontos_jogo)
                jogo_tela.classe_atual = "Nenhuma"
                jogo_tela.duas_pessoas = False
                jogo_tela.personagem2 = None
                jogo_tela.classe_jogador2 = None
                estado = "menu"
                tocar_musica("Menu.mp3")

        elif estado == "tela_vitoria":
            if vitoria_tela.botao_menu.checar_clique(evento, posicao_mouse):
                from Inventario import inventario_global
                inventario_global.resetar()
                personagem.resetar()
                jogo_tela.partida_atual = 1
                jogo_tela.pontos_jogo = max(0, jogo_tela.pontos_jogo)
                jogo_tela.classe_atual = "Nenhuma"
                jogo_tela.duas_pessoas = False
                jogo_tela.personagem2 = None
                jogo_tela.classe_jogador2 = None
                estado = "menu"
                tocar_musica("Menu.mp3")
                
        elif estado == "pos_luta":
            if getattr(jogo_tela, 'duas_pessoas', False) and getattr(jogo_tela, 'personagem2', None) is not None:
                pos_luta_tela.jogadores = [personagem, jogo_tela.personagem2]
            else:
                pos_luta_tela.jogadores = [personagem]

            resultado_tela = pos_luta_tela.atualizar_eventos(evento, posicao_mouse)
            if resultado_tela in ("continuar", "dormir"):
                jogo_tela.recuperar_apos_batalha(dormir=resultado_tela == "dormir")
                selecao_tela.recarregar_opcoes()
                estado = "selecao_cenario"
                
        elif estado == "selecao_cenario":
            escolha_cenario = selecao_tela.atualizar_eventos(evento, posicao_mouse)
            if escolha_cenario:
                if "evento" in escolha_cenario:
                    dados_dialogo = [
                        {
                            "nome": "Andarilho Misterioso",
                            "texto": "Você encontrou um evento misterioso pelo caminho.\nO que deseja fazer a seguir?",
                            "opcoes": [
                                {"texto": "Explorar o local", "retorno": escolha_cenario},
                                {"texto": "Ignorar e seguir em frente", "retorno": "cancelar_evento"}
                            ]
                        }
                    ]
                    dialogo_tela.iniciar(dados_dialogo)
                    estado = "dialogo"
                else:
                    jogo_tela.configurar_cenario(escolha_cenario)
                    jogo_tela.reiniciar()
                    estado = "jogo"
                    tocar_musica(jogo_tela.musica_luta)

        elif estado == "dialogo":
            resultado_dialogo = dialogo_tela.atualizar_eventos(evento, posicao_mouse)
            if resultado_dialogo == "cancelar_evento":
                jogo_tela.configurar_cenario("fase_aleatoria")
                jogo_tela.reiniciar()
                estado = "jogo"
                tocar_musica("Combate.mp3")
            elif resultado_dialogo:
                jogo_tela.configurar_cenario(resultado_dialogo)
                jogo_tela.reiniciar()
                estado = "jogo"
                tocar_musica("Combate.mp3")

    if estado == "menu":
        menu_tela.atualizar(posicao_mouse, estado_clique_mouse)
    elif estado == "classes":
        classes_tela.atualizar(posicao_mouse, estado_clique_mouse)
    elif estado == "game_over":
        game_over_tela.atualizar(posicao_mouse, estado_clique_mouse)
    elif estado == "tela_vitoria":
        vitoria_tela.atualizar(posicao_mouse, estado_clique_mouse)
    elif estado == "pos_luta":
        pos_luta_tela.atualizar(posicao_mouse, estado_clique_mouse)
    elif estado == "jogo":
        resultado_jogo = jogo_tela.atualizar(posicao_mouse, estado_clique_mouse)
        if resultado_jogo == "game_over":
            estado = "game_over"
            tocar_musica("GameOver.mp3")
        elif resultado_jogo == "vitoria": 
            estado = "pos_luta"
            tocar_musica("Menu.mp3")
        elif resultado_jogo == "fim_jogo":
            estado = "tela_vitoria"
            tocar_musica("Vitoria.mp3")
        elif resultado_jogo == "fugiu":
            if getattr(jogo_tela, 'duas_pessoas', False) and getattr(jogo_tela, 'personagem2', None) is not None:
                pos_luta_tela.jogadores = [personagem, jogo_tela.personagem2]
            else:
                pos_luta_tela.jogadores = [personagem]
            estado = "pos_luta"
            tocar_musica("Menu.mp3")
        elif resultado_jogo == "batalha_encerrada":
            estado = "selecao_cenario"

    tela.fill((0, 0, 0))
    if estado == "menu":
        menu_tela.desenhar()
    elif estado == "classes":
        classes_tela.desenhar()
    elif estado == "jogo":
        jogo_tela.desenhar(posicao_mouse)
    elif estado == "pos_luta":
        pos_luta_tela.desenhar()
    elif estado == "selecao_cenario":
        selecao_tela.desenhar(posicao_mouse)
    elif estado == "dialogo":
        selecao_tela.desenhar(posicao_mouse)
        dialogo_tela.desenhar()
    elif estado == "game_over":
        game_over_tela.desenhar()
    elif estado == "tela_vitoria":
        vitoria_tela.desenhar()

    tela_redimensionada = pygame.transform.scale(tela, (nova_largura, nova_altura))
    tela_real.fill((0, 0, 0))
    tela_real.blit(tela_redimensionada, (x_offset, y_offset))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
