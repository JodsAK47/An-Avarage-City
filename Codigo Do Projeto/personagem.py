import pygame

# ==========================
# CLASSE PERSONAGEM
# ==========================

class Personagem:

    def __init__(self, nome, x, y):

        self.nome = nome
        self.x = x
        self.y = y

        self.nivel = 1
        self.xp = 0

        self.vida_max = 30
        self.vida = self.vida_max

        self.mana_max = 10
        self.mana = self.mana_max

        self.cor = (255, 0, 255)

        self.atributos = {
            "For": 5,
            "Agi": 3,
            "Con": 4,
            "Sab": 2
        }

    def atacar(self):
        return self.atributos["For"]

    def receber_dano(self, dano):

        self.vida -= dano

        if self.vida < 0:
            self.vida = 0

    def vivo(self):
        return self.vida > 0

    def desenhar(self, tela):

        pygame.draw.rect(
            tela,
            self.cor,
            (self.x, self.y, 80, 80)
        )


class Inimigo:

    def __init__(self, nome, vida, forca, xp, x, y, cor):

        self.nome = nome

        self.vida_max = vida
        self.vida = vida
        self.xp = xp

        self.x = x
        self.y = y

        self.cor = cor

        self.atributos = {
            "For": forca
        }

    def atacar(self):
        return self.atributos["For"]

    def receber_dano(self, dano):

        self.vida -= dano

        if self.vida < 0:
            self.vida = 0

    def vivo(self):
        return self.vida > 0

    def desenhar(self, tela):

        pygame.draw.rect(
            tela,
            self.cor,
            (self.x, self.y, 80, 80)
        )

personagem = Personagem(
    nome="naotem",
    x=100,
    y=250
)


inimigo1 = Inimigo(
    nome="Inimigo 1",
    vida=15,
    forca=3,
    xp=10,
    x=550,
    y=150,
    cor=(0, 255, 0)
)


inimigo2 = Inimigo(
    nome="Inimigo 2",
    vida=25,
    forca=5,
    xp=20,
    x=550,
    y=250,
    cor=(255, 255, 0)
)

chefe = Inimigo(
    nome="Chefe",
    vida=80,
    forca=10,
    xp=100,
    x=550,
    y=350,
    cor=(255, 0, 0)
)
