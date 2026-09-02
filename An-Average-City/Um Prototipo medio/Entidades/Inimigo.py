import pygame
from Fontes import obter_fonte
from Recursos import caminho_imagem

class Inimigo:
    def __init__(self, x, y, vida_maxima, nome_imagem, nome="Inimigo", ataques=None, xp=0, atributos=None):
        self.nome = nome
        self.arquivo_imagem = nome_imagem
        self.max_hp = vida_maxima
        self.hp = vida_maxima
        self.max_mp = 0
        self.mp = 0

        self.congelado = False
        self.xp = xp

        self.atributos = atributos if atributos is not None else {"For": 1, "Agi": 1, "Int": 1}
        self.is_player = False
        
        self.ataques = ataques if ataques is not None else ["Soco"]
        
        try:
            self.imagem_original = pygame.image.load(caminho_imagem(nome_imagem))
            self.imagem = pygame.transform.scale(self.imagem_original, (100, 120))
        except (pygame.error, FileNotFoundError) as e:
            print(f"⚠️ Erro ao carregar imagem do inimigo ({nome_imagem}): {e}")
            self.imagem = pygame.Surface((100, 120))
            self.imagem.fill((200, 50, 50))

        self.rect = self.imagem.get_rect(topleft=(x, y))
        self.convertida = False
        self.fonte_nome = obter_fonte(16)

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
                except pygame.error:
                    pass
                self.convertida = True

            tela.blit(self.imagem, self.rect)
             
            txt = self.fonte_nome.render(self.nome, True, (255, 255, 255))
            tela.blit(txt, (self.rect.centerx - txt.get_width()//2, self.rect.y - 20))

