import pygame
from Menu import Botao 

class GerenciadorClasses:
    def __init__(self, tela):
        self.tela = tela
        largura_tela = self.tela.get_width()
        
        self.fonte_titulo = pygame.font.SysFont(["consolas", "courier"], 60, bold=True)
        self.txt_titulo = self.fonte_titulo.render("SELECIONE SUA CLASSE", True, (255, 255, 255))
        self.x_titulo = (largura_tela - self.txt_titulo.get_width()) // 2
        
        self.fonte_aviso = pygame.font.SysFont(["consolas", "courier"], 24, bold=True)
        self.aviso = "Classe atual: NENHUMA" 
        
        largura_botao = 300
        altura_botao = 50
        x_botao = (largura_tela - largura_botao) // 2
        
        # 3 Classes Agora!
        self.botao_lutador = Botao(x_botao, 200, largura_botao, altura_botao, "LUTADOR", (150, 50, 50), (200, 80, 80), 310, 55, cor_texto=(255, 255, 255), fonte_tamanho=28)
        self.botao_manipulador = Botao(x_botao, 280, largura_botao, altura_botao, "MANIPULADOR", (50, 50, 150), (80, 80, 200), 310, 55, cor_texto=(255, 255, 255), fonte_tamanho=28)
        self.botao_arqueiro = Botao(x_botao, 360, largura_botao, altura_botao, "ARQUEIRO", (50, 150, 50), (80, 200, 80), 310, 55, cor_texto=(255, 255, 255), fonte_tamanho=28)
        
        self.botao_voltar = Botao(x_botao, 500, largura_botao, altura_botao, "VOLTAR AO MENU", (100, 100, 100), (150, 150, 150), 310, 55, cor_texto=(255, 255, 255), fonte_tamanho=24)

    def atualizar(self, mouse_pos, mouse_click):
        self.botao_lutador.atualizar(mouse_pos, mouse_click)
        self.botao_manipulador.atualizar(mouse_pos, mouse_click)
        self.botao_arqueiro.atualizar(mouse_pos, mouse_click)
        self.botao_voltar.atualizar(mouse_pos, mouse_click)

    def desenhar(self):
        self.tela.fill((20, 20, 30))
        self.tela.blit(self.txt_titulo, (self.x_titulo, 50))
        
        txt_aviso = self.fonte_aviso.render(self.aviso, True, (255, 255, 0))
        self.tela.blit(txt_aviso, ((self.tela.get_width() - txt_aviso.get_width()) // 2, 130))
        
        self.botao_lutador.desenhar(self.tela)
        self.botao_manipulador.desenhar(self.tela)
        self.botao_arqueiro.desenhar(self.tela)
        self.botao_voltar.desenhar(self.tela)