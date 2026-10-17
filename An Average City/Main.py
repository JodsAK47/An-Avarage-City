import os
import sys
from pathlib import Path

DIRETORIO_RAIZ = Path(__file__).resolve().parent
if str(DIRETORIO_RAIZ) not in sys.path:
    sys.path.insert(0, str(DIRETORIO_RAIZ))

import pygame
from Telas import (
    GerenciadorMenu,
    GerenciadorJogo,
    GerenciadorGameOver,
    GerenciadorClasses,
    GerenciadorVerso,
    GerenciadorVitoria,
    GerenciadorConquistasTela,
    GerenciadorCheatsTela,
    GerenciadorSewerTela,
    GerenciadorSelecao,
    GerenciadorPosLuta,
    GerenciadorDialogo,
    TelaInventario,
    GerenciadorConfiguracoesTela,
    GerenciadorPosDialogo,
)
from Sistemas import (
    save_global,
    sistema_conquistas,
    inventario_global,
    caminho_musica,
    sistema_config,
)
from Entidades import personagem
from Gameplay import obter_dialogo_evento

pygame.init()
pygame.mixer.init()

LARGURA = 1000
ALTURA = 800
tela = pygame.Surface((LARGURA, ALTURA))
tela_cheia = sistema_config.obter_tela_cheia()
tela_real = sistema_config.aplicar_video()
if tela_real is None:
    tela_real = pygame.display.set_mode((LARGURA, ALTURA), pygame.RESIZABLE)
pygame.display.set_caption("Menu RPG")
relogio = pygame.time.Clock()

menu_tela = GerenciadorMenu(tela)
jogo_tela = GerenciadorJogo(tela)
game_over_tela = GerenciadorGameOver(tela)
selecao_tela = GerenciadorSelecao(tela)
conquistas_tela = GerenciadorConquistasTela(tela)
cheats_tela = GerenciadorCheatsTela(tela)
sewer_tela = GerenciadorSewerTela(tela)
classes_tela = GerenciadorClasses(tela)
verso_tela = GerenciadorVerso(tela)
pos_luta_tela = GerenciadorPosLuta(tela)
dialogo_tela = GerenciadorDialogo(tela)
pos_dialogo_tela = GerenciadorPosDialogo(tela)
vitoria_tela = GerenciadorVitoria(tela)
inventario_tela = TelaInventario(tela)
config_tela = GerenciadorConfiguracoesTela(tela)

classe_jogador1 = None
classe_jogador2 = None
alvo_classes = None
verso_menu_selecionado = None

def tocar_musica(nome_arquivo):
    pygame.mixer.music.stop()
    try:
        pygame.mixer.music.load(caminho_musica(nome_arquivo))
        pygame.mixer.music.set_volume(sistema_config.obter_volume_musica_efetivo())
        pygame.mixer.music.play(-1)
    except pygame.error as erro:
        print(f"⚠️ Aviso: Não foi possível tocar '{nome_arquivo}'.")

tocar_musica("Menu.mp3")

estado = "menu"
rodando = True

def reiniciar_para_menu():
    global alvo_classes
    alvo_classes = None
    from Sistemas.Inventario import inventario_global
    inventario_global.resetar()
    personagem.resetar()
    jogo_tela.partida_atual = 1
    jogo_tela.pontos_jogo = max(0, jogo_tela.pontos_jogo)
    jogo_tela.classe_atual = "Nenhuma"
    jogo_tela.duas_pessoas = False
    jogo_tela.personagem2 = None
    jogo_tela.classe_jogador2 = None
    menu_tela.duas_pessoas = False
    menu_tela.switch_2p.ativo = False
    tocar_musica("Menu.mp3")
    return "menu"

def registrar_pontos_partida():
    pontos_partida = max(0, int(jogo_tela.pontos_jogo))
    if not getattr(jogo_tela, 'pontos_salvos_na_partida', False):
        save_global.registrar_partida(pontos_partida)
        jogo_tela.pontos_salvos_na_partida = True
    return pontos_partida

def tratar_eventos_menu(evento, posicao_mouse):
    global estado, rodando, alvo_classes, verso_menu_selecionado
    botoes_menu = menu_tela.botoes

    if botoes_menu["jogar"].checar_clique(evento, posicao_mouse):
        verso_escolhido_anteriormente = verso_menu_selecionado or (
            jogo_tela.classe_atual if getattr(jogo_tela, 'classe_atual', 'Nenhuma') != 'Nenhuma' else None
        )
        if getattr(menu_tela, 'duas_pessoas', False):
            if verso_escolhido_anteriormente:
                jogo_tela.classe_atual = verso_escolhido_anteriormente
                alvo_classes = 1
                classes_tela.aviso = f"J1: {verso_escolhido_anteriormente} | Escolha CLASSE para JOGADOR 1"
                return "classes"
            alvo_classes = 1
            verso_tela.modo = "visualizacao"
            verso_tela.verso_atual = "Sobrevivente"
            verso_tela.aviso = "Escolha o Verso para JOGADOR 1"
            return "verso"
        else:
            if verso_escolhido_anteriormente:
                jogo_tela.classe_atual = verso_escolhido_anteriormente
                alvo_classes = 1
                classes_tela.aviso = f"Verso: {verso_escolhido_anteriormente} | Escolha SUA CLASSE"
                return "classes"
            alvo_classes = 1
            verso_tela.modo = "visualizacao"
            verso_tela.verso_atual = "Sobrevivente"
            verso_tela.aviso = "Escolha seu Verso"
            return "verso"

    if botoes_menu["classe"].checar_clique(evento, posicao_mouse):
        verso_tela.modo = "menu"
        verso_ativo = verso_menu_selecionado or (
            jogo_tela.classe_atual if getattr(jogo_tela, 'classe_atual', 'Nenhuma') != 'Nenhuma' else None
        )
        verso_tela.verso_ativo = verso_ativo
        verso_tela.verso_atual = verso_ativo if verso_ativo else "Sobrevivente"
        verso_tela.pontos = save_global.obter_pontos()
        verso_tela.sincronizar_habilidades_ativas()
        verso_tela.aviso = ""
        return "verso"

    if botoes_menu["conquistas"].checar_clique(evento, posicao_mouse):
        return "conquistas"

    if "config" in botoes_menu and botoes_menu["config"].checar_clique(evento, posicao_mouse):
        return "config"

    if menu_tela.botao_salvar.checar_clique(evento, posicao_mouse):
        save_global.salvar()
        sistema_conquistas.salvar()
        menu_tela.mostrar_feedback("✓ JOGO SALVO COM SUCESSO!", (100, 255, 140))
        return None

    if menu_tela.botao_reset.checar_clique(evento, posicao_mouse):
        save_global.resetar_tudo()
        sistema_conquistas.resetar_todas()
        verso_menu_selecionado = None
        verso_tela.verso_ativo = None
        verso_tela.progresso_por_verso = {verso: [] for verso in verso_tela.versos}
        verso_tela.pontos = save_global.obter_pontos()
        verso_tela.sincronizar_habilidades_ativas()
        personagem.resetar()
        personagem.talentos = set()
        personagem.ultimates_desbloqueadas = set()
        menu_tela.mostrar_feedback("⚠️ SAVE RESETADO COM SUCESSO!", (255, 100, 100))
        return None

    if menu_tela.checar_clique_esgoto(evento, posicao_mouse):
        return "sewer"

    if (destino_porta := menu_tela.checar_clique_porta_cheats(evento, posicao_mouse)):
        if destino_porta == "cheats":
            return "cheats"

    if menu_tela.switch_2p.checar_clique(evento, posicao_mouse):
        menu_tela.duas_pessoas = menu_tela.switch_2p.ativo
        if menu_tela.duas_pessoas:
            sistema_conquistas.desbloquear("cooperativo")
        else:
            jogo_tela.duas_pessoas = False
            jogo_tela.personagem2 = None
            jogo_tela.classe_jogador2 = None
        return None

    if botoes_menu["sair"].checar_clique(evento, posicao_mouse):
        rodando = False
        return None

    return None

def tratar_eventos_classes(evento, posicao_mouse):
    global alvo_classes, classe_jogador1, classe_jogador2
    escolha_classe = classes_tela.atualizar_eventos(evento, posicao_mouse)

    if classes_tela.voltar_clicado:
        alvo_classes = None
        classes_tela.voltar_clicado = False
        return "menu"

    if escolha_classe:
        if isinstance(escolha_classe, tuple):
            verso_escolhido, classe_escolhida = escolha_classe
        else:
            classe_escolhida = escolha_classe
            verso_escolhido = getattr(jogo_tela, 'classe_atual', getattr(verso_tela, 'verso_atual', 'Sobrevivente'))
            if verso_escolhido == "Nenhuma":
                verso_escolhido = getattr(verso_tela, 'verso_atual', 'Sobrevivente')

        target = alvo_classes if alvo_classes is not None else 1
        if target == 1:
            from Sistemas.Inventario import inventario_global
            inventario_global.resetar()
            jogo_tela.configurar_classe(verso_escolhido, classe_escolhida)
            classe_jogador1 = verso_escolhido
            classes_tela.aviso = f"J1: {verso_escolhido} - {classe_escolhida}"
            verso_tela.aplicar_talentos_ao_personagem(personagem, verso=verso_escolhido)
            if getattr(menu_tela, 'duas_pessoas', False):
                alvo_classes = 2
                classes_tela.aviso = "Escolha CLASSE para JOGADOR 2"
                return None
            else:
                jogo_tela.duas_pessoas = False
                jogo_tela.personagem2 = None
                jogo_tela.classe_jogador2 = None
                jogo_tela.classe_jogador2_tipo = None
                jogo_tela.reiniciar()
                tocar_musica("Combate.mp3")
                return "jogo"
        elif target == 2:
            classe_jogador2 = verso_escolhido
            classes_tela.aviso = f"J2: {verso_escolhido} - {classe_escolhida}"
            jogo_tela.classe_jogador2 = verso_escolhido
            jogo_tela.classe_jogador2_tipo = classe_escolhida
            jogo_tela.duas_pessoas = True
            if jogo_tela.personagem2 is not None:
                verso_tela.aplicar_talentos_ao_personagem(jogo_tela.personagem2, verso=verso_escolhido)
            jogo_tela.reiniciar()
            tocar_musica("Combate.mp3")
            return "jogo"
        else:
            from Sistemas.Inventario import inventario_global
            inventario_global.resetar()
            jogo_tela.configurar_classe(verso_escolhido, classe_escolhida)
            verso_tela.aplicar_talentos_ao_personagem(personagem, verso=verso_escolhido)
            jogo_tela.reiniciar()
            tocar_musica("Combate.mp3")
            return "jogo"
    return None

def tratar_eventos_verso(evento, posicao_mouse):
    global alvo_classes, verso_menu_selecionado
    escolha_verso = verso_tela.atualizar_eventos(evento, posicao_mouse)

    if verso_tela.voltar_clicado:
        verso_tela.voltar_clicado = False
        alvo_classes = None
        return "menu"

    if escolha_verso:
        if getattr(verso_tela, "modo", "menu") == "visualizacao":
            verso_tela.aviso = f"Verso selecionado: {escolha_verso}"
            jogo_tela.classe_atual = escolha_verso
            verso_tela.aplicar_talentos_ao_personagem(personagem, verso=escolha_verso)
            alvo_classes = 1
            if getattr(menu_tela, 'duas_pessoas', False):
                classes_tela.aviso = f"J1: {escolha_verso} | Escolha CLASSE para JOGADOR 1"
            else:
                classes_tela.aviso = f"Verso: {escolha_verso} | Escolha SUA CLASSE"
            return "classes"
        else:
            verso_menu_selecionado = escolha_verso
            jogo_tela.classe_atual = escolha_verso
            verso_tela.verso_ativo = escolha_verso
            verso_tela.aplicar_talentos_ao_personagem(personagem, verso=escolha_verso)
            verso_tela.aviso = f"Verso {escolha_verso} definido como ativo!"
            save_global.salvar()
            return None
    return None

def tratar_eventos_pos_luta(evento, posicao_mouse):
    if getattr(jogo_tela, 'duas_pessoas', False) and getattr(jogo_tela, 'personagem2', None) is not None:
        pos_luta_tela.jogadores = [personagem, jogo_tela.personagem2]
    else:
        pos_luta_tela.jogadores = [personagem]

    resultado_tela = pos_luta_tela.atualizar_eventos(evento, posicao_mouse)
    if resultado_tela == "continuar":
        selecao_tela.recarregar_opcoes()
        return "selecao_cenario"
    return None

def tratar_eventos_selecao_cenario(evento, posicao_mouse):
    escolha_cenario = selecao_tela.atualizar_eventos(evento, posicao_mouse)
    if escolha_cenario == "dormir":
        jogo_tela.recuperar_apos_batalha(dormir=True)
        jogo_tela.configurar_cenario("dormir")
        jogo_tela.reiniciar()
        tocar_musica(jogo_tela.musica_luta)
        return "jogo"
    elif escolha_cenario:
        if "evento" in escolha_cenario:
            dados_dialogo = obter_dialogo_evento(escolha_cenario)
            dialogo_tela.iniciar(dados_dialogo)
            return "dialogo"
        else:
            jogo_tela.configurar_cenario(escolha_cenario)
            jogo_tela.reiniciar()
            tocar_musica(jogo_tela.musica_luta)
            return "jogo"
    return None

def tratar_eventos_dialogo(evento, posicao_mouse):
    resultado_dialogo = dialogo_tela.atualizar_eventos(evento, posicao_mouse)
    if resultado_dialogo == "cancelar_evento":
        jogo_tela.configurar_cenario("ignorar_evento")
        jogo_tela.reiniciar()
        tocar_musica(jogo_tela.musica_luta)
        return "jogo"
    elif resultado_dialogo:
        dados_efeito = jogo_tela.configurar_cenario(resultado_dialogo)
        if dados_efeito and isinstance(dados_efeito, dict):
            pos_dialogo_tela.configurar(dados_efeito)
            return "pos_dialogo"
        jogo_tela.reiniciar()
        tocar_musica(jogo_tela.musica_luta)
        return "jogo"
    return None

def tratar_eventos_pos_dialogo(evento, posicao_mouse):
    resultado_pos = pos_dialogo_tela.atualizar_eventos(evento, posicao_mouse)
    if resultado_pos == "continuar":
        jogo_tela.reiniciar()
        tocar_musica(jogo_tela.musica_luta)
        return "jogo"
    return None

def tratar_eventos_conquistas(evento, posicao_mouse):
    resultado_conquistas = conquistas_tela.atualizar_eventos(evento, posicao_mouse)
    if resultado_conquistas == "menu" or conquistas_tela.voltar_clicado:
        conquistas_tela.voltar_clicado = False
        return "menu"
    return None

def tratar_eventos_sewer(evento, posicao_mouse):
    resultado_sewer = sewer_tela.atualizar_eventos(evento, posicao_mouse)
    if resultado_sewer == "menu":
        return "menu"
    return None

def tratar_eventos_cheats(evento, posicao_mouse):
    resultado_cheats = cheats_tela.atualizar_eventos(evento, posicao_mouse)
    if resultado_cheats in ("menu", "sewer") or cheats_tela.voltar_clicado:
        cheats_tela.voltar_clicado = False
        return "menu"
    return None

def tratar_eventos_config(evento, posicao_mouse):
    global tela_real, tela_cheia
    resultado_config = config_tela.atualizar_eventos(evento, posicao_mouse)
    if resultado_config == "menu" or config_tela.voltar_clicado:
        config_tela.voltar_clicado = False
        return "menu"
    elif resultado_config == "video_alterado":
        nova_tela = pygame.display.get_surface()
        if nova_tela is not None:
            tela_real = nova_tela
        tela_cheia = sistema_config.obter_tela_cheia()
        return None
    return None

DISTRIBUIDOR_EVENTOS = {
    "menu": tratar_eventos_menu,
    "classes": tratar_eventos_classes,
    "verso": tratar_eventos_verso,
    "game_over": lambda ev, pos: reiniciar_para_menu() if game_over_tela.botao_menu.checar_clique(ev, pos) else None,
    "tela_vitoria": lambda ev, pos: reiniciar_para_menu() if vitoria_tela.botao_menu.checar_clique(ev, pos) else None,
    "pos_luta": tratar_eventos_pos_luta,
    "selecao_cenario": tratar_eventos_selecao_cenario,
    "dialogo": tratar_eventos_dialogo,
    "pos_dialogo": tratar_eventos_pos_dialogo,
    "conquistas": tratar_eventos_conquistas,
    "config": tratar_eventos_config,
    "sewer": tratar_eventos_sewer,
    "cheats": tratar_eventos_cheats,
}

def atualizar_estado_atual(posicao_mouse, estado_clique_mouse):
    global estado
    if estado == "jogo":
        resultado_jogo = jogo_tela.atualizar(posicao_mouse, estado_clique_mouse)
        if resultado_jogo == "game_over":
            game_over_tela.pontos = registrar_pontos_partida()
            tocar_musica("GameOver.mp3")
            estado = "game_over"
        elif resultado_jogo == "vitoria":
            registrar_pontos_partida()
            tocar_musica("Menu.mp3")
            if hasattr(jogo_tela, 'ultimo_resultado_batalha') and jogo_tela.ultimo_resultado_batalha:
                pos_luta_tela.definir_popup_notificacao(jogo_tela.ultimo_resultado_batalha)
            estado = "pos_luta"
        elif resultado_jogo == "fim_jogo":
            registrar_pontos_partida()
            tocar_musica("Vitoria.mp3")
            estado = "tela_vitoria"
        elif resultado_jogo == "fugiu":
            if getattr(jogo_tela, 'duas_pessoas', False) and getattr(jogo_tela, 'personagem2', None) is not None:
                pos_luta_tela.jogadores = [personagem, jogo_tela.personagem2]
            else:
                pos_luta_tela.jogadores = [personagem]
            if hasattr(jogo_tela, 'ultimo_resultado_batalha') and jogo_tela.ultimo_resultado_batalha:
                pos_luta_tela.definir_popup_notificacao(jogo_tela.ultimo_resultado_batalha)
            tocar_musica("Menu.mp3")
            estado = "pos_luta"
        elif resultado_jogo == "batalha_encerrada":
            estado = "selecao_cenario"
        return

    telas_atualizacao = {
        "menu": menu_tela,
        "classes": classes_tela,
        "verso": verso_tela,
        "conquistas": conquistas_tela,
        "config": config_tela,
        "sewer": sewer_tela,
        "cheats": cheats_tela,
        "game_over": game_over_tela,
        "tela_vitoria": vitoria_tela,
        "pos_luta": pos_luta_tela,
        "selecao_cenario": selecao_tela,
        "pos_dialogo": pos_dialogo_tela,
    }
    if tela_alvo := telas_atualizacao.get(estado):
        tela_alvo.atualizar(posicao_mouse, estado_clique_mouse)

def desenhar_estado_atual(posicao_mouse):
    telas_desenho = {
        "menu": menu_tela.desenhar,
        "classes": classes_tela.desenhar,
        "verso": verso_tela.desenhar,
        "conquistas": conquistas_tela.desenhar,
        "config": config_tela.desenhar,
        "sewer": sewer_tela.desenhar,
        "cheats": cheats_tela.desenhar,
        "jogo": lambda: jogo_tela.desenhar(posicao_mouse),
        "pos_luta": pos_luta_tela.desenhar,
        "selecao_cenario": lambda: selecao_tela.desenhar(posicao_mouse),
        "dialogo": lambda: (selecao_tela.desenhar(posicao_mouse), dialogo_tela.desenhar()),
        "pos_dialogo": lambda: (selecao_tela.desenhar(posicao_mouse), pos_dialogo_tela.desenhar(posicao_mouse)),
        "game_over": game_over_tela.desenhar,
        "tela_vitoria": vitoria_tela.desenhar,
    }
    tela.fill((0, 0, 0))
    if renderizador := telas_desenho.get(estado):
        renderizador()

def loop_principal():
    global rodando, estado, tela_real, tela, tela_cheia
    while rodando:
        posicao_mouse_real = pygame.mouse.get_pos()
        estado_clique_mouse = pygame.mouse.get_pressed()

        largura_real, altura_real = tela_real.get_size()
        escala = min(largura_real / LARGURA, altura_real / ALTURA) if LARGURA > 0 and ALTURA > 0 else 1
        nova_largura = int(LARGURA * escala)
        nova_altura = int(ALTURA * escala)
        deslocamento_x = (largura_real - nova_largura) // 2
        deslocamento_y = (altura_real - nova_altura) // 2

        if escala > 0:
            mx = int((posicao_mouse_real[0] - deslocamento_x) / escala)
            my = int((posicao_mouse_real[1] - deslocamento_y) / escala)
        else:
            mx, my = 0, 0
        posicao_mouse = (max(0, min(mx, LARGURA)), max(0, min(my, ALTURA)))

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_F11:
                    tela_cheia = not tela_cheia
                    sistema_config.definir_tela_cheia(tela_cheia)
                    sistema_config.salvar()
                    nova_tela = sistema_config.aplicar_video()
                    if nova_tela is not None:
                        tela_real = nova_tela
            if manipulador := DISTRIBUIDOR_EVENTOS.get(estado):
                novo_estado = manipulador(evento, posicao_mouse)
                if novo_estado:
                    estado = novo_estado

        atualizar_estado_atual(posicao_mouse, estado_clique_mouse)
        desenhar_estado_atual(posicao_mouse)

        sistema_conquistas.atualizar_notificacoes()
        sistema_conquistas.desenhar_notificacao(tela)

        tela_redimensionada = pygame.transform.scale(tela, (nova_largura, nova_altura))
        tela_real.fill((0, 0, 0))
        tela_real.blit(tela_redimensionada, (deslocamento_x, deslocamento_y))
        pygame.display.flip()
        relogio.tick(60)

    pygame.quit()

if __name__ == "__main__":
    loop_principal()
