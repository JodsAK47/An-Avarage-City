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
            fonte = obter_fonte(24)
            txt = fonte.render(self.nome, True, (255, 255, 255))
            tela.blit(txt, (self.rect.centerx - txt.get_width()//2, self.rect.y - 20))

# ==========================================================
# BANCO DE DADOS DE INIMIGOS (TEMPLATES)
# ==========================================================
# Agora usamos dicionários (templates) em vez de instanciar `Inimigo` no
# momento do import. Isso evita carregamento irregular de sprites e permite
# criar instâncias apenas quando necessário (ao gerar a fase).
BANCOS_INIMIGOS = {
    "cenario_1": [
        {"max_hp": 25, "arquivo_imagem": "Maldição1.png", "nome": "Goblin Verde", "ataques": ["Mordida", "Soco"], "xp": 30, "atributos": {"For": 2, "Agi": 3, "Int": 0}},
        {"max_hp": 20, "arquivo_imagem": "Maldição1.png", "nome": "Goblin Corredor", "ataques": ["Mordida"], "xp": 20, "atributos": {"For": 1, "Agi": 5, "Int": 0}},
    ],
    "cenario_2": [
        {"max_hp": 35, "arquivo_imagem": "Maldição1.png", "nome": "Morcego Gigante", "ataques": ["Mordida"], "xp": 40, "atributos": {"For": 3, "Agi": 4, "Int": 0}},
        {"max_hp": 50, "arquivo_imagem": "Maldição1.png", "nome": "Troll da Caverna", "ataques": ["Porrete do Chefe", "Soco"], "xp": 60, "atributos": {"For": 6, "Agi": 1, "Int": 0}},
    ],
    "cenario_3": [
        {"max_hp": 40, "arquivo_imagem": "Maldição1.png", "nome": "Arqueiro Esqueleto", "ataques": ["Flechada Letal"], "xp": 50, "atributos": {"For": 1, "Agi": 6, "Int": 0}},
        {"max_hp": 35, "arquivo_imagem": "Maldição1.png", "nome": "Mago Sombrio", "ataques": ["Gelo", "Soco"], "xp": 50, "atributos": {"For": 1, "Agi": 2, "Int": 5}},
    ],
    "cenario_4": [
        {"max_hp": 120, "arquivo_imagem": "Sukuna1.png", "nome": "Senhor da Guerra", "ataques": ["Porrete do Chefe", "Soco", "Flechada Letal"], "xp": 200, "atributos": {"For": 8, "Agi": 4, "Int": 2}},
    ],
}


def _criar_inimigo_a_partir_template(template, x=0, y=0):
    return Inimigo(
        x,
        y,
        template.get("max_hp", 20),
        template.get("arquivo_imagem", "Maldição1.png"),
        template.get("nome", "Inimigo"),
        list(template.get("ataques", ["Soco"])),
        template.get("xp", 0),
        dict(template.get("atributos", {"For": 1, "Agi": 1, "Int": 1})),
    )


def listar_inimigos_disponiveis():
    """Retorna instâncias novas para todos os templates de inimigos."""
    inimigos = []
    for lista in BANCOS_INIMIGOS.values():
        for tpl in lista:
            inimigos.append(_criar_inimigo_a_partir_template(tpl))
    return inimigos


def obter_inimigos_por_cenario(id_cenario):
    """Cria novas instâncias de inimigos para o cenário pedido.

    As posições (x,y) ficam em 0; o `Jogo.py` ajusta dinamicamente as posições
    durante o combate.
    """
    return [_criar_inimigo_a_partir_template(tpl) for tpl in BANCOS_INIMIGOS.get(id_cenario, [])]
