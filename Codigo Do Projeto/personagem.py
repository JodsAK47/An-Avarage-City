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
personagem = Personagem(
    nome="naotem",
    x=100,
    y=250
)
