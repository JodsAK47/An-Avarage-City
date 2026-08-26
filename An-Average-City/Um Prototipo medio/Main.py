import pygame
import os
from Menu import GerenciadorMenu
from Jogo import GerenciadorJogo
from GameOver import GerenciadorGameOver
from MenuClasses import GerenciadorClasses 
from Cenarios import GerenciadorSelecao
from Descanço import GerenciadorPosLuta
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
classes_tela = GerenciadorClasses(tela) 
pos_luta_tela = GerenciadorPosLuta(tela) # <-- INICIALIZANDO

# Estado para seleção de classes quando for necessário (player 1 ou 2)
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

    # Cálculo da escala para o redimensionamento
    largura_real, altura_real = tela_real.get_size()
    escala = min(largura_real / LARGURA, altura_real / ALTURA) if LARGURA > 0 and ALTURA > 0 else 1
    nova_largura = int(LARGURA * escala)
    nova_altura = int(ALTURA * escala)
    x_offset = (largura_real - nova_largura) // 2
    y_offset = (altura_real - nova_altura) // 2

    # Mapear o mouse real para a tela lógica
    if escala > 0:
        mx = int((posicao_mouse_real[0] - x_offset) / escala)
        my = int((posicao_mouse_real[1] - y_offset) / escala)
    else:
        mx, my = 0, 0
    posicao_mouse = (max(0, min(mx, LARGURA)), max(0, min(my, ALTURA)))

    # =========================================================
    # 1. EVENTOS 
    # =========================================================
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
                # Se modo 2P está ligado, forçar seleção de classes antes de iniciar
                if getattr(menu_tela, 'duas_pessoas', False):
                    classes_target = 1
                    classes_tela.aviso = "Escolha CLASSE para JOGADOR 1"
                    estado = "classes"
                else:
                    # Verifica se já há uma classe selecionada no jogo
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
            # Seleção de classe com suporte a 2 jogadores via classes_target
            escolha_classe = None
            if classes_tela.botao_lutador.checar_clique(evento, posicao_mouse):
                escolha_classe = "Lutador"
            elif classes_tela.botao_manipulador.checar_clique(evento, posicao_mouse):
                escolha_classe = "Manipulador"
            elif classes_tela.botao_arqueiro.checar_clique(evento, posicao_mouse):
                escolha_classe = "Arqueiro"
            elif classes_tela.botao_voltar.checar_clique(evento, posicao_mouse):
                classes_target = None
                estado = "menu"

            if escolha_classe:
                if classes_target == 1:
                    # configura jogador 1
                    jogo_tela.configurar_classe(escolha_classe)
                    player1_class = escolha_classe
                    classes_tela.aviso = f"Jogador 1: {escolha_classe}"
                    if getattr(menu_tela, 'duas_pessoas', False):
                        # pedir classe do jogador 2 agora
                        classes_target = 2
                        classes_tela.aviso = "Escolha CLASSE para JOGADOR 2"
                    else:
                        jogo_tela.duas_pessoas = False
                        jogo_tela.personagem2 = None
                        jogo_tela.classe_jogador2 = None
                        jogo_tela.reiniciar()
                        estado = "jogo"
                        tocar_musica("Combate.mp3")
                elif classes_target == 2:
                    player2_class = escolha_classe
                    classes_tela.aviso = f"Jogador 2: {escolha_classe}"
                    # aplicar classe 2 no gerenciador de jogo (cria personagem2 mais tarde)
                    jogo_tela.classe_jogador2 = escolha_classe
                    # ambos prontos -> iniciar
                    jogo_tela.duas_pessoas = True
                    jogo_tela.reiniciar()
                    estado = "jogo"
                    tocar_musica("Combate.mp3")

        elif estado == "game_over":
            if game_over_tela.botao_menu.checar_clique(evento, posicao_mouse):
                estado = "menu"
                tocar_musica("Menu.mp3")
                
        # --- NOVA LÓGICA DE TRANSIÇÃO: PÓS-LUTA ---
        elif estado == "pos_luta":
            if getattr(jogo_tela, 'duas_pessoas', False) and getattr(jogo_tela, 'personagem2', None) is not None:
                pos_luta_tela.jogadores = [personagem, jogo_tela.personagem2]
            else:
                pos_luta_tela.jogadores = [personagem]

            resultado_tela = pos_luta_tela.atualizar_eventos(evento, posicao_mouse)
            if resultado_tela == "continuar":
                selecao_tela.recarregar_opcoes()
                estado = "selecao_cenario"
                
        elif estado == "selecao_cenario":
            escolha_cenario = selecao_tela.atualizar_eventos(evento, posicao_mouse)
            if escolha_cenario:
                jogo_tela.configurar_cenario(escolha_cenario)
                jogo_tela.reiniciar()
                estado = "jogo"
                tocar_musica(jogo_tela.musica_luta)

    # =========================================================
    # 2. LÓGICA CONTÍNUA E HOVER
    # =========================================================
    if estado == "menu":
        menu_tela.atualizar(posicao_mouse, estado_clique_mouse)
    elif estado == "classes":
        classes_tela.atualizar(posicao_mouse, estado_clique_mouse)
    elif estado == "game_over":
        game_over_tela.atualizar(posicao_mouse, estado_clique_mouse)
    elif estado == "pos_luta":
        pos_luta_tela.atualizar(posicao_mouse, estado_clique_mouse)
    elif estado == "jogo":
        resultado_jogo = jogo_tela.atualizar(posicao_mouse, estado_clique_mouse)
        if resultado_jogo == "game_over":
            estado = "game_over"
            tocar_musica("GameOver.mp3")
        elif resultado_jogo == "vitoria": 
            estado = "pos_luta" # Vai para a tela de Status e Nível!
            tocar_musica("Menu.mp3") # Coloca uma música calma de vitória/menu
        elif resultado_jogo in ["fugiu", "batalha_encerrada"]:
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
        jogo_tela.desenhar(posicao_mouse)
    elif estado == "pos_luta":
        pos_luta_tela.desenhar() # Desenha a nova tela
    elif estado == "selecao_cenario":
        selecao_tela.desenhar(posicao_mouse)
    elif estado == "game_over":
        game_over_tela.desenhar()

    tela_redimensionada = pygame.transform.scale(tela, (nova_largura, nova_altura))
    tela_real.fill((0, 0, 0))
    tela_real.blit(tela_redimensionada, (x_offset, y_offset))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
