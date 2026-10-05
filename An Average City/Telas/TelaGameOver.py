import pygame
from Sistemas.SistemaUI import TelaBase, Botao
from Sistemas.Fontes import obter_fonte


class GerenciadorGameOver(TelaBase):
    def __init__(self, tela):
        super().__init__(tela, nome="game_over")
        self.cor_fundo = (15, 5, 5)
        self.pontos = 0
        
        self.fonte_titulo = obter_fonte(50)
        self.fonte_pontos = obter_fonte(28)
        self.txt_titulo = self.fonte_titulo.render("GAME OVER", True, (255, 50, 50))
        
        self.x_titulo = (self.largura - self.txt_titulo.get_width()) // 2
        self.y_titulo = 200
        
        largura_botao = 280
        altura_botao = 60
        x_botao = (self.largura - largura_botao) // 2
        self.botao_menu = self.criar_botao(
            x_botao, 480, largura_botao, altura_botao, "MENU",
            cor_base=(100, 100, 100), cor_hover=(150, 150, 150),
            cor_texto=(255, 255, 255), fonte_tamanho=18,
            acao=lambda: "menu"
        )

    def desenhar_conteudo(self):
        self.tela.blit(self.txt_titulo, (self.x_titulo, self.y_titulo))
        txt_pontos = self.fonte_pontos.render(f"Pontos: {self.pontos}", True, (255, 210, 70))
        self.tela.blit(txt_pontos, txt_pontos.get_rect(center=(self.largura // 2, 290)))
