import pygame
import os

# Caminho para a sua fonte pixel art dentro da pasta Fontes
DIRETORIO_BASE = os.path.dirname(os.path.abspath(__file__))
CAMINHO_FONTE = os.path.join(DIRETORIO_BASE, "Fontes", "PressStart2P.ttf") # Coloque o nome correto do seu arquivo .ttf

def obter_fonte(tamanho):
    """
    Retorna a fonte pixel art no tamanho desejado.
    Se o arquivo .ttf não for encontrado, usa a fonte do sistema como reserva.
    """
    try:
        return pygame.font.Font(CAMINHO_FONTE, tamanho)
    except Exception as e:
        # Reserva (Fallback) caso o arquivo da fonte falhe
        return pygame.font.SysFont(["consolas", "courier"], tamanho, bold=True)


def quebrar_texto(texto, fonte, largura_maxima):
    """Quebra `texto` em várias linhas para caber em `largura_maxima` pixels usando `fonte`.

    Retorna uma lista de strings (linhas).
    """
    palavras = texto.split()
    linhas = []
    linha_atual = ""

    for palavra in palavras:
        candidata = (linha_atual + " " + palavra).strip() if linha_atual else palavra
        largura, _ = fonte.size(candidata)
        if largura <= largura_maxima:
            linha_atual = candidata
        else:
            if linha_atual:
                linhas.append(linha_atual)
            # Palavra sozinha maior que largura_maxima? então cortamos
            if fonte.size(palavra)[0] > largura_maxima:
                # quebra a palavra em pedaços
                parte = ""
                for ch in palavra:
                    if fonte.size(parte + ch)[0] <= largura_maxima:
                        parte += ch
                    else:
                        if parte:
                            linhas.append(parte)
                        parte = ch
                if parte:
                    linha_atual = parte
                else:
                    linha_atual = ""
            else:
                linha_atual = palavra

    if linha_atual:
        linhas.append(linha_atual)

    return linhas
    