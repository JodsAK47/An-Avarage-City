import pygame
import os

class Personagem:
    # 1. ATRIBUTOS BÁSICOS
    def __init__(self, x, y):
        self.max_hp = 100
        self.hp = 100
        self.max_mp = 10
        self.mp = 10
 
        # 2. STATUS E ATAQUES
        self.nivel = 1
        self.xp = 0
        self.pontos_atributo = 0
        self.atributos = {"For": 1, "Agi": 1, "Con": 1, "Sab": 1, "Int": 1}
        self.ataques = [] 

        #3. ESTADOS DE COMBATE
        self.congelado = False
        self.bloqueando = False
        self.recuperando = False

        #4. Tentativa de ANIMAÇÃO 
        self.frames = []
        self.frame_atual = 0
        self.tempo_troca = 500  
        self.ultimo_tempo = pygame.time.get_ticks()

        self.carregar_sprites()


        if self.frames:
            self.rect = self.frames[0].get_rect(topleft=(x, y))
        else:
            self.rect = pygame.Rect(x, y, 100, 120)

    def carregar_sprites(self):
        diretorio_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pasta_sprites = os.path.join(diretorio_base, "Sprites")

        #Sprites
        nomes_arquivos = ["pixil.png", "Sukuna-Heian-Frame1-Direita.png"] 

        for arquivo in nomes_arquivos:
            caminho = os.path.join(pasta_sprites, arquivo)
            try:
                img = pygame.image.load(caminho)
                img = pygame.transform.scale(img, (100, 120))
                self.frames.append(img)
            except Exception as e:
                print(f"⚠️ Não encontrou sprite '{arquivo}' em {caminho}: {e}")


        if not self.frames:
            reserva = pygame.Surface((100, 120))
            reserva.fill((50, 100, 250))
            self.frames.append(reserva)

    def atualizar_animacao(self):
        agora = pygame.time.get_ticks()
        if agora - self.ultimo_tempo >= self.tempo_troca:
            self.ultimo_tempo = agora
            self.frame_atual = (self.frame_atual + 1) % len(self.frames)

    def desenhar(self, tela):
        if self.hp > 0:
            self.atualizar_animacao()
            imagem_atual = self.frames[self.frame_atual]
            tela.blit(imagem_atual, self.rect)

# Instância principal carregada e modificada durante o jogo
personagem = Personagem(150, 400)