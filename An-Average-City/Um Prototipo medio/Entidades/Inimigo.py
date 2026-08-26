import pygame
import os
from Fontes import obter_fonte

class Inimigo:
    # Adicionamos xp e atributos ao __init__
    def __init__(self, x, y, vida_maxima, nome_imagem, nome="Inimigo", ataques=None, xp=0, atributos=None):
        self.nome = nome
        self.arquivo_imagem = nome_imagem
        self.vida_maxima = vida_maxima
        self.vida = vida_maxima
        self.pm_maximo = 0
        self.pm = 0

        self.max_hp = self.vida_maxima
        self.hp = self.vida
        self.max_mp = self.pm_maximo
        self.mp = self.pm

        self.congelado = False
        self.experiencia = xp
        self.xp = self.experiencia

        # Garante que o inimigo nasça com os atributos para não dar erro
        self.atributos = atributos if atributos is not None else {"For": 1, "Agi": 1, "Int": 1}
        self.eh_jogador = False
        self.is_player = False
        
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
        self.fonte_nome = obter_fonte(16)  # Criada uma vez, reutilizada a cada frame

    def clone(self):
        novo_inimigo = Inimigo(
            self.rect.x,
            self.rect.y,
            self.vida_maxima,
            self.arquivo_imagem,
            self.nome,
            list(self.ataques),
            self.experiencia,
            dict(self.atributos),
        )
        novo_inimigo.vida = self.vida
        novo_inimigo.hp = self.hp
        novo_inimigo.pm = self.pm
        novo_inimigo.mp = self.mp
        novo_inimigo.congelado = self.congelado
        return novo_inimigo

    def desenhar(self, tela):
        if self.hp > 0:
            if not self.convertida:
                try:
                    self.imagem = self.imagem.convert_alpha()
                except Exception:
                    pass
                self.convertida = True

            tela.blit(self.imagem, self.rect)
             
            # Opcional: Desenha o nome em cima da sprite
            txt = self.fonte_nome.render(self.nome, True, (255, 255, 255))
            tela.blit(txt, (self.rect.centerx - txt.get_width()//2, self.rect.y - 20))

