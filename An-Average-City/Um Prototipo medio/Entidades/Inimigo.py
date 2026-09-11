import pygame
from Fontes import obter_fonte
from Recursos import caminho_imagem
from Habilidades import Habilidade


_banco_habilidades_inimigos = {
    "Soco": Habilidade("Soco", "Físico", 4, 0, 0.90, "Um golpe direto.", verso="Inimigo"),
    "Mordida": Habilidade("Mordida", "Físico", 6, 0, 0.85, "Morde o alvo.", verso="Inimigo"),
    "Porrete do Chefe": Habilidade("Porrete do Chefe", "Físico", 12, 0, 0.75, "Um golpe pesado de porrete.", verso="Inimigo"),
    "Gelo": Habilidade("Gelo", "Magia", 8, 2, 0.80, "Dispara uma rajada de gelo.", efeito="Congelar", chance_efeito=0.20, verso="Inimigo"),
    "Fogo": Habilidade("Fogo", "Magia", 10, 3, 0.80, "Lança uma chama contra o alvo.", efeito="Queimar", chance_efeito=0.15, verso="Inimigo"),
    "Nevasca": Habilidade("Nevasca", "Magia", 9, 4, 0.70, "Uma tempestade de gelo atinge todos os alvos.", efeito="Congelar", chance_efeito=0.15, em_area=True, verso="Inimigo"),
    "Terremoto": Habilidade("Terremoto", "Magia", 14, 5, 0.65, "Abala o campo de batalha.", em_area=True, verso="Inimigo"),
}

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

    def obter_habilidade(self, nome):
        return _banco_habilidades_inimigos.get(nome, _banco_habilidades_inimigos["Soco"])

    def clone(self):
        novo_inimigo = Inimigo(
            self.rect.x,
            self.rect.y,
            self.max_hp,
            self.arquivo_imagem,
            self.nome,
            list(self.ataques),
            self.xp,
            dict(self.atributos),
        )
        novo_inimigo.hp = self.hp
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

