import pygame
class Jogo:

    def __init__(self):

        pygame.init()

        self.largura = 800
        self.altura = 600

        self.tela = pygame.display.set_mode(
            (self.largura,self.altura)
        )

        pygame.display.set_caption("An-Avarage-City")
