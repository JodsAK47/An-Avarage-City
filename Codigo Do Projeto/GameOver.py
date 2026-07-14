import pygame
from Menu import Botao 

class GerenciadorGameOver:
    def __init__(self, tela):
        self.tela = tela
        largura_tela = self.tela.get_width()
        
        # --- TÍTULO ---
        self.fonte_titulo = pygame.font.SysFont(["consolas", "courier"], 80, bold=True)
        self.txt_titulo = self.fonte_titulo.render("GAME OVER", True, (255, 50, 50))
        
        largura_titulo = self.txt_titulo.get_width()
        self.x_titulo = (largura_tela - largura_titulo) // 2
        self.y_titulo = 200
        
        # --- BOTÕES ---
        largura_botao = 280
        altura_botao = 60
        x_botao = (largura_tela - largura_botao) // 2
        
        self.botao_tentar_novamente = Botao(x_botao, 380, largura_botao, altura_botao, "TENTAR DE NOVO", (200, 100, 0), (255, 150, 0), 290, 65, cor_texto=(255, 255, 255), fonte_tamanho=26)
        self.botao_menu = Botao(x_botao, 480, largura_botao, altura_botao, "MENU", (100, 100, 100), (150, 150, 150), 290, 65, cor_texto=(255, 255, 255), fonte_tamanho=26)

    def atualizar(self, mouse_pos, mouse_click):
        """Atualiza o estado visual de animação dos botões (Hover)"""
        self.botao_tentar_novamente.atualizar(mouse_pos, mouse_click)
        self.botao_menu.atualizar(mouse_pos, mouse_click)

    def desenhar(self):
        self.tela.fill((15, 5, 5)) # Fundo escuro avermelhado temático
        self.tela.blit(self.txt_titulo, (self.x_titulo, self.y_titulo))
        
        self.botao_tentar_novamente.desenhar(self.tela)
        self.botao_menu.desenhar(self.tela)
