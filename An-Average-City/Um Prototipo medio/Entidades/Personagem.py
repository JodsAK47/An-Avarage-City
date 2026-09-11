import pygame
from Recursos import caminho_imagem

class Personagem:
    def __init__(self, x, y, nome_imagem="pixil.png"):
        self.max_hp = 100
        self.hp = 100
        self.max_mp = 10
        self.mp = 10

        self.nivel = 1
        self.xp = 0
        self.pontos_atributo = 0
        self.atributos = {"For": 1, "Agi": 1, "Con": 1, "Sab": 1, "Int": 1}
        self.ataques = []

        self.congelado = False
        self.bloqueando = False
        self.recuperando = False
        self.is_player = True

        try:
            self.imagem_original = pygame.image.load(caminho_imagem(nome_imagem))
            self.imagem = pygame.transform.scale(self.imagem_original, (100, 120))
        except (pygame.error, FileNotFoundError) as e:
            print(f"⚠️ Erro ao carregar imagem: {e}")
            self.imagem = pygame.Surface((100, 120))
            self.imagem.fill((0, 200, 100))

        self.rect = self.imagem.get_rect(topleft=(x, y))
        self.convertida = False

    def resetar(self):
        self.__init__(self.rect.x, self.rect.y)

    def desenhar(self, tela):
        if not self.convertida:
            try:
                self.imagem = self.imagem.convert_alpha()
            except pygame.error:
                pass
            self.convertida = True

        tela.blit(self.imagem, self.rect)


personagem = Personagem(150, 350, "pixil.png")
personagem.is_player = True
