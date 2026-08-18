import pygame
import os

class Personagem:
    def __init__(self, x, y, nome_imagem="pixil.png"):
        # 1. ATRIBUTOS BÁSICOS
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
        
        # 3. ESTADOS DE COMBATE
        self.congelado = False
        self.bloqueando = False
        self.recuperando = False

        # 4. CARREGANDO A SPRITE 
        diretorio_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        caminho_imagem = os.path.join(diretorio_base, "Sprites", nome_imagem)

        try:
            self.imagem_original = pygame.image.load(caminho_imagem)
            self.imagem = pygame.transform.scale(self.imagem_original, (100, 120))
        except Exception as e:
            # Caso a imagem não seja encontrada na pasta Sprites, cria um retângulo reserva
            print(f"⚠️ Erro ao carregar imagem: {e}")
            self.imagem = pygame.Surface((100, 120))
            self.imagem.fill((0, 200, 100))

        self.rect = self.imagem.get_rect(topleft=(x, y))
        self.convertida = False

    def desenhar(self, tela):
        if not self.convertida:
            try:
                self.imagem = self.imagem.convert_alpha()
            except Exception:
                pass
            self.convertida = True

        tela.blit(self.imagem, self.rect)


# Personagem
personagem = Personagem(150, 350, "pixil.png")
