import pygame
import os

class Botao:
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
        self.rect = pygame.Rect(x, y, largura, altura)
        self.pressionado = False
        self.cor_base = cor_base
        self.cor_hover = cor_hover
        self.cor_texto = cor_texto
        self.texto = texto
        self.cor_atual = cor_base

        self.usar_sprites = sprite_base_path and sprite_hover_path and sprite_clique_path

        if self.usar_sprites:
            try:
                caminho_base = os.path.join("Sprites", "Botoes", sprite_base_path)
                caminho_hover = os.path.join("Sprites", "Botoes", sprite_hover_path)
                caminho_clique = os.path.join("Sprites", "Botoes", sprite_clique_path)

                sprite_base_temp = pygame.image.load(caminho_base).convert_alpha()
                self.sprite_base = pygame.transform.scale(sprite_base_temp, (largura, altura))
                
                sprite_hover_temp = pygame.image.load(caminho_hover).convert_alpha()
                self.sprite_hover = pygame.transform.scale(sprite_hover_temp, (largura, altura))
                
                sprite_clique_temp = pygame.image.load(caminho_clique).convert_alpha()
                self.sprite_clique = pygame.transform.scale(sprite_clique_temp, (largura, altura))
                
                self.sprite_atual = self.sprite_base

            except FileNotFoundError as erro:
                print(f"⚠️ Aviso: Não foi possível carregar os sprites do botão '{texto}'.")
                print(f"Erro detalhado: {erro}")
                self.usar_sprites = False
                self.sprite_base = None
                self.sprite_hover = None
                self.sprite_clique = None
                self.sprite_atual = None
        else:
            self.sprite_base = None
            self.sprite_hover = None
            self.sprite_clique = None
            self.sprite_atual = None

        self.fonte = pygame.font.SysFont(["consolas", "courier"], fonte_tamanho, bold=True)
        self.txt_renderizado = self.fonte.render(texto, True, cor_texto)
        self.txt_rect = self.txt_renderizado.get_rect(center=self.rect.center)

    def clicado(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    # ---> ADICIONE ESTA FUNÇÃO INTEIRA AQUI: <---
    def checar_clique(self, evento, mouse_pos):
        """Verifica se o botão foi pressionado e solto sobre ele"""
        # Se apertou o botão esquerdo do mouse
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(mouse_pos):
                self.pressionado = True
        
        # Se soltou o botão esquerdo do mouse
        if evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            if self.pressionado and self.rect.collidepoint(mouse_pos):
                self.pressionado = False
                return True # Retorna True só quando a ação de clique termina!
            self.pressionado = False
            
        return False

    def atualizar(self, posicao_mouse, clique_mouse):
        if self.rect.collidepoint(posicao_mouse):
            self.cor_atual = self.cor_hover
            if clique_mouse[0]:
                if self.usar_sprites:
                    self.sprite_atual = self.sprite_clique
                self.rect.width = self.largura_clique
                self.rect.height = self.altura_clique
            else:
                if self.usar_sprites:
                    self.sprite_atual = self.sprite_hover
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
            superficie.blit(self.sprite_atual, self.rect)
        else:
            pygame.draw.rect(superficie, self.cor_atual, self.rect)
            superficie.blit(self.txt_renderizado, self.txt_rect)

    def clicado(self, posicao_mouse):
        return self.rect.collidepoint(posicao_mouse)


class GerenciadorMenu:
    def __init__(self, tela):
        self.tela = tela
        
        # Pega a largura e altura atuais da tela (agora 1000x800)
        largura_tela = self.tela.get_width()
        altura_tela = self.tela.get_height()
        
        # --- CENTRALIZANDO O TÍTULO ---
        self.fonte_titulo = pygame.font.SysFont(["consolas", "courier"], 60, bold=True)
        self.txt_titulo = self.fonte_titulo.render("MENU", True, (255, 255, 255))
        
        largura_titulo = 300
        altura_titulo = 80
        x_titulo = (largura_tela - largura_titulo) // 2 # Calcula o meio da tela
        self.titulo_rect = pygame.Rect(x_titulo, 100, largura_titulo, altura_titulo) # Y descido para 100
        
        # Caminhos dos sprites
        sprite_jogar_base = "BPM.png"
        sprite_jogar_hover = "BPG.png"
        sprite_jogar_clique = "BPP.png"

        sprite_classe_base = "BCM.png" 
        sprite_classe_hover = "BCG.png"
        sprite_classe_clique = "BCP.png"

        sprite_sair_base = "BSM.png"
        sprite_sair_hover = "BSG.png"
        sprite_sair_clique = "BSP.png"

        # --- CENTRALIZANDO OS BOTÕES ---
        largura_botao = 190
        altura_botao = 55
        x_botao = (largura_tela - largura_botao) // 2 # Calcula o meio da tela para os botões
        
        # Aumentei o espaçamento no eixo Y (250, 350, 450) para ficar harmonioso na tela de 800 de altura
        self.botao_jogar = Botao(x_botao, 250, largura_botao, altura_botao, "JOGAR", (0, 200, 0), (0, 255, 0), 200, 60, cor_texto=(0, 0, 0), fonte_tamanho=32, sprite_base_path=sprite_jogar_base, sprite_hover_path=sprite_jogar_hover, sprite_clique_path=sprite_jogar_clique)
        self.botao_classe = Botao(x_botao, 350, largura_botao, altura_botao, "CLASSE", (200, 200, 0), (255, 255, 0), 200, 60, cor_texto=(0, 0, 0), fonte_tamanho=32, sprite_base_path=sprite_classe_base, sprite_hover_path=sprite_classe_hover, sprite_clique_path=sprite_classe_clique)
        self.botao_sair = Botao(x_botao, 450, largura_botao, altura_botao, "SAIR", (200, 0, 0), (255, 0, 0), 200, 60, cor_texto=(255, 255, 255), fonte_tamanho=32, sprite_base_path=sprite_sair_base, sprite_hover_path=sprite_sair_hover, sprite_clique_path=sprite_sair_clique)

        self.lista_botoes = [self.botao_jogar, self.botao_classe, self.botao_sair]
    def atualizar(self, mouse_pos, mouse_click):
        for botao in self.lista_botoes:
            botao.atualizar(mouse_pos, mouse_click)

    def desenhar(self):
        self.tela.fill((30, 30, 40))
        pygame.draw.rect(self.tela, (80, 80, 200), self.titulo_rect)
        self.tela.blit(self.txt_titulo, self.txt_titulo.get_rect(center=self.titulo_rect.center))
        
        for botao in self.lista_botoes:
            botao.desenhar(self.tela)
