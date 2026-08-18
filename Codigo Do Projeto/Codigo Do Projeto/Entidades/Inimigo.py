import pygame
import os
from Fontes import obter_fonte

class Inimigo:
    # Adicionamos xp e atributos ao __init__
    def __init__(self, x, y, max_hp, nome_imagem, nome="Inimigo", ataques=None, xp=0, atributos=None):
        self.nome = nome
        self.max_hp = max_hp
        self.hp = max_hp
        self.max_mp = 0 
        self.mp = 0
        self.congelado = False
        self.xp = xp
        
        # Garante que o inimigo nasça com os atributos para não dar erro
        self.atributos = atributos if atributos is not None else {"For": 1, "Agi": 1, "Int": 1}
        
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
            
            # Opcional: Desenha o nome em cima da sprite
            fonte = obter_fonte(24)
            txt = fonte.render(self.nome, True, (255, 255, 255))
            tela.blit(txt, (self.rect.centerx - txt.get_width()//2, self.rect.y - 20))

# ==========================================================
# BANCO DE DADOS DE INIMIGOS (SEPARADOS POR CENÁRIO)
# ==========================================================
def obter_inimigos_por_cenario(id_cenario):
    """
    Retorna uma lista de inimigos configurados com seus status, imagens e atributos.
    OBS: As posições (x,y) podem ser 0 pois o Jogo.py as ajusta dinamicamente no combate.
    """
    if id_cenario == "cenario_1":
        return [
            Inimigo(0, 0, 25, "Maldição1.png", "Goblin Verde", ["Mordida", "Soco"], 30, {"For": 2, "Agi": 3, "Int": 0}),
            Inimigo(0, 0, 20, "Maldição1.png", "Goblin Corredor", ["Mordida"], 20, {"For": 1, "Agi": 5, "Int": 0})
        ]
        
    elif id_cenario == "cenario_2":
        return [
            Inimigo(0, 0, 35, "Maldição1.png", "Morcego Gigante", ["Mordida"], 40, {"For": 3, "Agi": 4, "Int": 0}),
            Inimigo(0, 0, 50, "Maldição1.png", "Troll da Caverna", ["Porrete do Chefe", "Soco"], 60, {"For": 6, "Agi": 1, "Int": 0})
        ]
        
    elif id_cenario == "cenario_3":
        return [
            Inimigo(0, 0, 40, "Maldição1.png", "Arqueiro Esqueleto", ["Flechada Letal"], 50, {"For": 1, "Agi": 6, "Int": 0}),
            Inimigo(0, 0, 35, "Maldição1.png", "Mago Sombrio", ["Gelo", "Soco"], 50, {"For": 1, "Agi": 2, "Int": 5})
        ]
        
    elif id_cenario == "cenario_4":
        return [
            Inimigo(0, 0, 120, "Sukuna1.png", "Senhor da Guerra", ["Porrete do Chefe", "Soco", "Flechada Letal"], 200, {"For": 8, "Agi": 4, "Int": 2})
        ]
        
    return []
