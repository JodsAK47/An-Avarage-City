import pygame
import os
from Menu import GerenciadorMenu
from Jogo import GerenciadorJogo
from GameOver import GerenciadorGameOver
from MenuClasses import GerenciadorClasses 
from Cenarios import GerenciadorSelecao
from Descanço import GerenciadorPosLuta # <-- NOVA TELA IMPORTADA

pygame.init()
pygame.mixer.init()

LARGURA = 1000
ALTURA = 800
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Menu RPG")
clock = pygame.time.Clock()

menu_tela = GerenciadorMenu(tela)
jogo_tela = GerenciadorJogo(tela)
game_over_tela = GerenciadorGameOver(tela)
selecao_tela = GerenciadorSelecao(tela)
classes_tela = GerenciadorClasses(tela) 
pos_luta_tela = GerenciadorPosLuta(tela) # <-- INICIALIZANDO

def tocar_musica(nome_arquivo):
    pygame.mixer.music.stop()
    try:
        caminho_musica = os.path.join("Ots's", nome_arquivo)
        pygame.mixer.music.load(caminho_musica)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    except pygame.error as erro:
        print(f"⚠️ Aviso: Não foi possível tocar '{nome_arquivo}'.")

tocar_musica("Menu.mp3")

estado = "menu"
rodando = True

while rodando:
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()

    # =========================================================
    # 1. EVENTOS 
    # =========================================================
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        if estado == "menu":
            if menu_tela.botao_jogar.checar_clique(evento, mouse_pos):
                jogo_tela.reiniciar()
                estado = "jogo"
                tocar_musica("Combate.mp3")
            elif menu_tela.botao_classe.checar_clique(evento, mouse_pos):
                estado = "classes"
            elif menu_tela.botao_sair.checar_clique(evento, mouse_pos):
                rodando = False

        elif estado == "classes":
            if classes_tela.botao_lutador.checar_clique(evento, mouse_pos):
                jogo_tela.configurar_classe("Lutador")
                classes_tela.aviso = "Classe: LUTADOR"
            elif classes_tela.botao_manipulador.checar_clique(evento, mouse_pos):
                jogo_tela.configurar_classe("Manipulador")
                classes_tela.aviso = "Classe: MANIPULADOR"
            elif classes_tela.botao_arqueiro.checar_clique(evento, mouse_pos):
                jogo_tela.configurar_classe("Arqueiro")
                classes_tela.aviso = "Classe: ARQUEIRO"
            elif classes_tela.botao_voltar.checar_clique(evento, mouse_pos):
                estado = "menu"

        elif estado == "game_over":
            if game_over_tela.botao_tentar_novamente.checar_clique(evento, mouse_pos):
                jogo_tela.reiniciar()
                estado = "jogo"
                tocar_musica(jogo_tela.musica_luta)
            elif game_over_tela.botao_menu.checar_clique(evento, mouse_pos):
                estado = "menu"
                tocar_musica("Menu.mp3")
                
        # --- NOVA LÓGICA DE TRANSIÇÃO: PÓS-LUTA ---
        elif estado == "pos_luta":
            resultado = pos_luta_tela.atualizar_eventos(evento, mouse_pos)
            if resultado == "continuar":
                estado = "selecao_cenario" # Avança para escolher a fase
                
        elif estado == "selecao_cenario":
            escolha = selecao_tela.atualizar_eventos(evento, mouse_pos)
            if escolha:
                jogo_tela.configurar_cenario(escolha)
                jogo_tela.reiniciar()
                estado = "jogo"
                tocar_musica(jogo_tela.musica_luta)

    # =========================================================
    # 2. LÓGICA CONTÍNUA E HOVER
    # =========================================================
    if estado == "menu":
        menu_tela.atualizar(mouse_pos, mouse_click)
    elif estado == "classes":
        classes_tela.atualizar(mouse_pos, mouse_click)
    elif estado == "game_over":
        game_over_tela.atualizar(mouse_pos, mouse_click)
    elif estado == "pos_luta":
        pos_luta_tela.atualizar(mouse_pos, mouse_click)
    elif estado == "jogo":
        resultado = jogo_tela.atualizar(mouse_pos, mouse_click)
        if resultado == "game_over":
            estado = "game_over"
            tocar_musica("GameOver.mp3")
        elif resultado == "vitoria": 
            estado = "pos_luta" # Vai para a tela de Status e Nível!
            tocar_musica("Menu.mp3") # Coloca uma música calma de vitória/menu
        elif resultado in ["fugiu", "batalha_encerrada"]:
            estado = "selecao_cenario"

    # =========================================================
    # 3. DESENHO 
    # =========================================================
    tela.fill((0, 0, 0))
    if estado == "menu":
        menu_tela.desenhar()
    elif estado == "classes":
        classes_tela.desenhar()
    elif estado == "jogo":
        jogo_tela.desenhar()
    elif estado == "pos_luta":
        pos_luta_tela.desenhar() # Desenha a nova tela
    elif estado == "selecao_cenario":
        selecao_tela.desenhar()
    elif estado == "game_over":
        game_over_tela.desenhar()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()