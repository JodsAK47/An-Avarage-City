import pygame

class Personagem:
    def __init__(self, nome, x, y,ataques):
        self.nome = nome
        self.nivel = 1
        self.xp = 0
        
        # --- POSIÇÃO E COLISÃO (NOVO) ---
        self.x = x
        self.y = y
        self.largura = 80
        self.altura = 80
        self.rect = pygame.Rect(self.x, self.y, self.largura, self.altura)

        #STATUS

        self.max_hp = 60
        self.hp = self.max_hp

        self.max_mp = 6
        self.mp = self.max_mp

        self.ataques = ataques

        self.congelado = False
        self.queimando = False
        self.envenenado = False

        self.cor = (255, 0, 255)
        self.atributos = {
            "For": 1,
            "Agi": 1,
            "Con": 1,
            "Sab": 1,
            "Int": 1
        }

    def receber_dano(self, dano):
        self.hp = max(0, self.hp - dano)

    def vivo(self):
        return self.hp > 0

    def desenhar(self, tela):
        # Agora desenha usando o rect oficial
        pygame.draw.rect( tela, self.cor, self.rect)

personagem = Personagem(nome="Herói", x=200, y=300, ataques = ["Gelo","Fogo"])
subpersonagem = Personagem(nome="Herói", x=200, y=300, ataques = ["Gelo","Fogo"])
