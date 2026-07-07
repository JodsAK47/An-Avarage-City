import pygame
import os # Importamos os para manipulação de caminhos
# Certifique-se de que o arquivo personagem.py está na mesma pasta
from Personagem import personagem, inimigo1, inimigo2, chefe

pygame.init()

LARGURA = 800
ALTURA = 600

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Menu RPG")

clock = pygame.time.Clock()

class Botao:

    # Atualizado para aceitar sprites específicos para cada estado, mantendo parâmetros inúteis
    def __init__(self, x, y, largura, altura, texto, cor_base,
                 cor_hover, largura_hover, altura_hover,
                 cor_texto=(0, 0, 0), fonte_tamanho=32,
                 sprite_base_path=None, sprite_hover_path=None, sprite_clique_path=None):

        self.x_centro = x + largura // 2
        self.y_centro = y + altura // 2

        self.largura_base = largura
        self.altura_base = altura

        self.largura_hover = largura_hover
        self.altura_hover = altura_hover

        self.largura_clique = largura - 10
        self.altura_clique = altura - 5

        # Define o tamanho fixo da colisão na tela
        self.rect = pygame.Rect(x, y, largura, altura)

        # Variáveis inúteis mantidas para compatibilidade
        self.cor_base = cor_base
        self.cor_hover = cor_hover
        self.cor_texto = cor_texto
        self.texto = texto
        self.cor_atual = cor_base # Ainda usada para inicialização, mas sobrescrita se houver sprites

        # --- CARREGAMENTO E REDIMENSIONAMENTO DOS SPRITES ---
        self.usar_sprites = sprite_base_path and sprite_hover_path and sprite_clique_path

        if self.usar_sprites:
            # ALTERAÇÃO: Removido o uso de diretórios fixos rígidos para evitar FileNotFoundError.
            # Os caminhos agora apontam diretamente para onde os arquivos de imagem estão localizados.
            # O dimensionamento usa (largura, altura) acompanhando o tamanho original do botão.
            sprite_base_temp = pygame.image.load(sprite_base_path).convert_alpha()
            self.sprite_base = pygame.transform.scale(sprite_base_temp, (largura, altura))
            
            sprite_hover_temp = pygame.image.load(sprite_hover_path).convert_alpha()
            self.sprite_hover = pygame.transform.scale(sprite_hover_temp, (largura, altura))
            
            sprite_clique_temp = pygame.image.load(sprite_clique_path).convert_alpha()
            self.sprite_clique = pygame.transform.scale(sprite_clique_temp, (largura, altura))
            
            self.sprite_atual = self.sprite_base
        else:
            self.sprite_base = None
            self.sprite_hover = None
            self.sprite_clique = None
            self.sprite_atual = None

        # --- MODIFICAÇÃO AQUI: Fonte pixelada/mono do sistema mantida para compatibilidade ---
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
        # Detecção de colisão baseada no rect fixo, sem alteração de tamanho
        if self.rect.collidepoint(posicao_mouse):
            self.cor_atual = self.cor_hover # Ainda atualizada para compatibilidade
            
            if clique_mouse[0]:
                if self.usar_sprites:
                    self.sprite_atual = self.sprite_clique
                # Tamanhos alterados para compatibilidade, mas não afetam sprites
                self.rect.width = self.largura_clique
                self.rect.height = self.altura_clique
            else:
                if self.usar_sprites:
                    self.sprite_atual = self.sprite_hover
                # Tamanhos alterados para compatibilidade, mas não afetam sprites
                self.rect.width = self.largura_hover
                self.rect.height = self.altura_hover
        else:
            if self.usar_sprites:
                self.sprite_atual = self.sprite_base
            self.cor_atual = self.cor_base
            self.rect.width = self.largura_base
            self.rect.height = self.altura_base

        self.rect.center = (self.x_centro, self.y_centro)
        self.txt_rect.center = self.rect.center

    def desenhar(self, superficie):
        if self.usar_sprites:
            # Desenha o sprite na posição do rect fixo
            superficie.blit(
                self.sprite_atual,
                self.rect
            )
        else:
            # Fallback para rect colorido e texto para compatibilidade
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

# ALTERAÇÃO: Removido o caminho estático "Pasta_do_projeto" que causava FileNotFoundError.
# Como os arquivos de imagens (BMM.png, BMG.png, BMP.png) estão na mesma pasta raiz do script,
# passamos apenas o nome direto do arquivo de imagem sem uma subpasta definida por enquanto.
sprite_jogar_base = "BMM.png"
sprite_jogar_hover = "BMG.png"
sprite_jogar_clique = "BMP.png"

sprite_creditos_base = "BMM.png" 
sprite_creditos_hover = "BMG.png"
sprite_creditos_clique = "BMP.png"

sprite_sair_base = "BMM.png"
sprite_sair_hover = "BMG.png"
sprite_sair_clique = "BMP.png"


# Instanciando botões (mantendo todos os parâmetros inúteis para compatibilidade)
# Passe os caminhos dos sprites para ativar o uso de imagens
botao_jogar = Botao(
    300, 200,
    190, 55,
    "JOGAR",
    (0, 200, 0),
    (0, 255, 0),
    200, 60,
    cor_texto=(0, 0, 0),
    fonte_tamanho=32,
    sprite_base_path=sprite_jogar_base,
    sprite_hover_path=sprite_jogar_hover,
    sprite_clique_path=sprite_jogar_clique
)

botao_creditos = Botao(
    300, 300,
    190, 55,
    "CLASSE",
    (200, 200, 0),
    (255, 255, 0),
    200, 60,
    cor_texto=(0, 0, 0),
    fonte_tamanho=32,
    sprite_base_path=sprite_creditos_base,
    sprite_hover_path=sprite_creditos_hover,
    sprite_clique_path=sprite_creditos_clique
)

botao_sair = Botao(
    300, 400,
    190, 55,
    "SAIR",
    (200, 0, 0),
    (255, 0, 0),
    200, 60,
    cor_texto=(255, 255, 255),
    fonte_tamanho=32,
    sprite_base_path=sprite_sair_base,
    sprite_hover_path=sprite_sair_hover,
    sprite_clique_path=sprite_sair_clique
)

lista_botoes = [
    botao_jogar,
    botao_creditos,
    botao_sair
]

# ==========================================================
# CONFIGURAÇÃO DA MÚSICA DO MENU
# ==========================================================
pygame.mixer.init() # Inicializa o sistema de som

# Substitua "musica_menu.mp3" pelo nome/caminho real do seu arquivo de música
# Dica: Arquivos .mp3 ou .ogg funcionam perfeitamente aqui.
try:
    pygame.mixer.music.load("Menu.mp3")
    pygame.mixer.music.set_volume(0.5) # Define o volume de 0.0 (mudo) a 1.0 (máximo)
    pygame.mixer.music.play(-1) # O -1 faz a música reiniciar automaticamente ao acabar
except pygame.error:
    print("Aviso: Arquivo de música não encontrado. O jogo continuará sem som.")

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
                
                # --- BOTÃO JOGAR ---
                if botao_jogar.clicado(mouse_pos):
                    pygame.mixer.music.stop() # PARA A MÚSICA AO ENTRAR NO JOGO
                    estado = "jogo"

                # --- BOTÃO CLASSE (CRÉDITOS) ---
                if botao_creditos.clicado(mouse_pos):
                    #pygame.mixer.music.stop() # PARA A MÚSICA SE QUISER PARAR AQUI TAMBÉM
                    print("Creditos")

                # --- BOTÃO SAIR ---
                if botao_sair.clicado(mouse_pos):
                    pygame.mixer.music.stop() # PARA A MÚSICA ANTES DE FECHAR
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