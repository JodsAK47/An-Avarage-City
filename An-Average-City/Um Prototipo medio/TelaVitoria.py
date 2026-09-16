import pygame
from Menu import Botao
from Fontes import obter_fonte

class GerenciadorVitoria:
    def __init__(self, tela):
        self.tela = tela
        self.botao_menu = Botao(400, 600, 200, 50, "VOLTAR AO MENU", (30, 100, 30), (50, 150, 50), 400, 600, cor_texto=(255, 255, 255))
        self.fonte_titulo = obter_fonte(40)
        self.fonte_texto = obter_fonte(20)

    def atualizar(self, posicao_mouse, estado_clique_mouse):
        self.botao_menu.atualizar(posicao_mouse, estado_clique_mouse)

    def desenhar(self):
        self.tela.fill((10, 40, 10))
        titulo = self.fonte_titulo.render("VITÓRIA!", True, (255, 215, 0))
        texto = self.fonte_texto.render("O Chefe foi derrotado e seu bolso está a salvo!", True, (200, 255, 200))
        
        self.tela.blit(titulo, (500 - titulo.get_width() // 2, 250))
        self.tela.blit(texto, (500 - texto.get_width() // 2, 350))
        
        self.botao_menu.desenhar(self.tela)
