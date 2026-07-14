import pygame

class Inimigo:
    # ADICIONADO: O parâmetro 'ataques' (lista com os nomes dos golpes)
    def __init__(self, nome, hp, mp, forca, xp, x, y, cor, ataques):
        self.nome = nome
        self.xp = xp
        
        self.x = x
        self.y = y
        self.largura = 80
        self.altura = 80
        self.rect = pygame.Rect(self.x, self.y, self.largura, self.altura)

        self.max_hp = hp
        self.hp = self.max_hp
        self.max_mp = mp
        self.mp = self.max_mp
        self.congelado = False
        self.queimando = False
        self.envenenado = False
        self.cor = cor
        self.atributos = {"For": forca}
        
        # A lista de habilidades que o monstro sabe usar
        self.ataques = ataques 

    def receber_dano(self, dano):
        self.hp = max(0, self.hp - dano)

    def vivo(self):
        return self.hp > 0

    def desenhar(self, tela):
        pygame.draw.rect(tela, self.cor, self.rect)

# INIMIGOS AGORA RECEBEM SEUS ATAQUES OFICIAIS!
inimigo1 = Inimigo(nome="Geleia Amaldiçoada", hp=30, mp=6, forca=3, xp=10, x=650, y=150, cor=(0, 255, 0), ataques=["Mordida"])
inimigo2 = Inimigo(nome="Inimigo 2", hp=30, mp=6, forca=3, xp=10, x=800, y=300, cor=(0, 200, 0), ataques=["Mordida", "Soco"])
inimigo3 = Inimigo(nome="Inimigo 3", hp=30, mp=6, forca=3, xp=10, x=800, y=300, cor=(0, 200, 0), ataques=["Mordida", "Soco"])
inimigo4 = Inimigo(nome="Inimigo 4", hp=30, mp=6, forca=3, xp=10, x=800, y=300, cor=(0, 200, 0), ataques=["Mordida", "Soco"])
chefe    = Inimigo(nome="Grande Chefe", hp=80, mp=50, forca=8, xp=50, x=650, y=450, cor=(255, 0, 0), ataques=["Porrete do Chefe", "Soco"])
