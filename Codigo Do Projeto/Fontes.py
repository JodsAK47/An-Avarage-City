import pygame
import os

# Caminho para a sua fonte pixel art dentro da pasta Fonts
DIRETORIO_BASE = os.path.dirname(os.path.abspath(__file__))
CAMINHO_FONTE = os.path.join(DIRETORIO_BASE, "Fonts", "pixel_font.ttf") # Coloque o nome correto do seu arquivo .ttf

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