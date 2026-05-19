import pygame
import sys
class Jogo:

    def __init__(self):

        pygame.init()

        self.largura = 800
        self.altura = 600

        self.tela = pygame.display.set_mode(
            (self.largura,self.altura)
        )
        self.rodador = True 
        pygame.display.set_caption("An-Avarage-City")
    def executar(self):
        while self.rodando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.rodando = False
            self.tela.fill((0, 0, 0))
            pygame.display.flip()
        pygame.quit()
        sys.exit()
        
