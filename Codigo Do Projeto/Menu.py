import pygame
# Certifique-se de que o arquivo personagem.py está na mesma pasta
from Personagem import personagem, inimigo1, inimigo2, chefe

pygame.init()

LARGURA = 800
ALTURA = 600

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Menu RPG")

clock = pygame.time.Clock()

class Botao:

    def __init__(self, x, y, largura, altura, texto, cor_base,
                 cor_hover, largura_hover, altura_hover,
                 cor_texto=(0, 0, 0), fonte_tamanho=32): # Reduzi levemente o tamanho padrão para caber melhor

        self.x_centro = x + largura // 2
        self.y_centro = y + altura // 2

        self.largura_base = largura
        self.altura_base = altura

        self.largura_hover = largura_hover
        self.altura_hover = altura_hover

        self.largura_clique = largura - 10
        self.altura_clique = altura - 5

        self.rect = pygame.Rect(x, y, largura, altura)

        self.cor_base = cor_base
        self.cor_hover = cor_hover
        self.cor_atual = cor_base

        # --- MODIFICAÇÃO AQUI: Fonte pixelada/mono do sistema ---
        self.fonte = pygame.font.SysFont(["consolas", "courier"], fonte_tamanho, bold=True)

        self.txt_renderizado = self.fonte.render(
            texto,
            True,
            cor_texto
        )

        self.txt_rect = self.txt_renderizado.get_rect(
            center=self.rect.center
        )

    def atualizar(self, posicao_mouse, clique_mouse):

        if self.rect.collidepoint(posicao_mouse):
            self.cor_atual = self.cor_hover

            if clique_mouse[0]:
                self.rect.width = self.largura_clique
                self.rect.height = self.altura_clique
            else:
                self.rect.width = self.largura_hover
                self.rect.height = self.altura_hover
        else:
            self.cor_atual = self.cor_base
            self.rect.width = self.largura_base
            self.rect.height = self.altura_base

        self.rect.center = (self.x_centro, self.y_centro)
        self.txt_rect.center = self.rect.center

    def desenhar(self, superficie):
        pygame.draw.rect(
            superficie,
            self.cor_atual,
            self.rect
        )
        superficie.blit(
            self.txt_renderizado,
            self.txt_rect
        )

    def clicado(self, posicao_mouse):
        return self.rect.collidepoint(posicao_mouse)


# --- MODIFICAÇÃO AQUI: Título com fonte pixelada/mono ---
fonte_titulo = pygame.font.SysFont(["consolas", "courier"], 60, bold=True)

txt_titulo = fonte_titulo.render(
    "MENU",
    True,
    (255, 255, 255)
)

titulo_rect = pygame.Rect(
    250,
    50,
    300,
    80
)

# Instanciando botões (ajustei levemente o tamanho do texto interno se necessário)
botao_jogar = Botao(
    300, 200,
    190, 55,
    "JOGAR",
    (0, 200, 0),
    (0, 255, 0),
    200, 60
)

botao_creditos = Botao(
    300, 300,
    190, 55,
    "CLASSE",
    (200, 200, 0),
    (255, 255, 0),
    200, 60
)

botao_sair = Botao(
    300, 400,
    190, 55,
    "SAIR",
    (200, 0, 0),
    (255, 0, 0),
    200, 60,
    cor_texto=(255, 255, 255)
)

lista_botoes = [
    botao_jogar,
    botao_creditos,
    botao_sair
]

estado = "menu"
rodando = True

while rodando:

    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            rodando = False

        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:
                if botao_jogar.clicado(mouse_pos):
                    estado = "jogo"

                if botao_creditos.clicado(mouse_pos):
                    print("Creditos")

                if botao_sair.clicado(mouse_pos):
                    rodando = False

    if estado == "menu":
        tela.fill((30, 30, 40))

        pygame.draw.rect(
            tela,
            (80, 80, 200),
            titulo_rect
        )

        tela.blit(
            txt_titulo,
            txt_titulo.get_rect(
                center=titulo_rect.center
            )
        )

        # Atualização constante dos botões para o efeito Hover funcionar perfeitamente
        for botao in lista_botoes:
            botao.atualizar(mouse_pos, mouse_click)
            botao.desenhar(tela)

    elif estado == "jogo":
        tela.fill((20, 20, 20))
        personagem.desenhar(tela)
        inimigo1.desenhar(tela)
        inimigo2.desenhar(tela)
        chefe.desenhar(tela)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
