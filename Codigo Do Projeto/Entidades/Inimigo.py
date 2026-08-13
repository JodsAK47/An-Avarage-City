import pygame
import os

class Inimigo:
    def __init__(self, x, y, max_hp, nome_imagem, nome="Inimigo", ataques=None):
        self.nome = nome
        self.max_hp = max_hp
        self.hp = max_hp
        self.congelado = False
        
        # Atributo sorteia os golpes 
        self.ataques = ataques if ataques is not None else ["Soco"]
        
        # CARREGAMENTO DA SPRITE
        diretorio_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        caminho_imagem = os.path.join(diretorio_base, "Sprites", nome_imagem)

        try:
            self.imagem_original = pygame.image.load(caminho_imagem)
            self.imagem = pygame.transform.scale(self.imagem_original, (100, 120))
        except Exception as e:
            print(f"⚠️ Erro ao carregar imagem do inimigo ({nome_imagem}): {e}")
            self.imagem = pygame.Surface((100, 120))
            self.imagem.fill((200, 50, 50))

        self.rect = self.imagem.get_rect(topleft=(x, y))
        self.convertida = False

    def desenhar(self, tela):
        if self.hp > 0:
            if not self.convertida:
                try:
                    self.imagem = self.imagem.convert_alpha()
                except Exception:
                    pass
                self.convertida = True

            tela.blit(self.imagem, self.rect)
#inimigos
inimigo1 = Inimigo(500, 350, 30, "Maldição1.png", nome="Maldição", ataques=["Soco"])
inimigo2 = Inimigo(650, 350, 30, "Maldição1.png", nome="Maldiçao", ataques=["Soco"])
chefe = Inimigo(600, 300, 150, "Maldição1.png", nome="Maldição_Martinino", ataques=["Soco", "Nevasca"])
