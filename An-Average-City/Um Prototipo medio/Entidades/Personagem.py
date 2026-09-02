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

    @property
    def vida_maxima(self): return self.max_hp
    @vida_maxima.setter
    def vida_maxima(self, valor): self.max_hp = valor

    @property
    def vida(self): return self.hp
    @vida.setter
    def vida(self, valor): self.hp = valor

    @property
    def pm_maximo(self): return self.max_mp
    @pm_maximo.setter
    def pm_maximo(self, valor): self.max_mp = valor

    @property
    def pm(self): return self.mp
    @pm.setter
    def pm(self, valor): self.mp = valor

    @property
    def experiencia(self): return self.xp
    @experiencia.setter
    def experiencia(self, valor): self.xp = valor

    @property
    def eh_jogador(self): return self.is_player
    @eh_jogador.setter
    def eh_jogador(self, valor): self.is_player = valor

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
personagem.eh_jogador = True
personagem.is_player = True
