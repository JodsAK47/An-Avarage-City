import math

import pygame
from Fontes import obter_fonte
from Recursos import caminho_botao, caminho_imagem

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
                caminho_base = caminho_botao(sprite_base_path)
                caminho_hover = caminho_botao(sprite_hover_path)
                caminho_clique = caminho_botao(sprite_clique_path)

                sprite_base_temp = pygame.image.load(caminho_base).convert_alpha()
                self.sprite_base = pygame.transform.scale(sprite_base_temp, (largura, altura))
                
                sprite_hover_temp = pygame.image.load(caminho_hover).convert_alpha()
                self.sprite_hover = pygame.transform.scale(sprite_hover_temp, (largura, altura))
                
                sprite_clique_temp = pygame.image.load(caminho_clique).convert_alpha()
                self.sprite_clique = pygame.transform.scale(sprite_clique_temp, (largura, altura))
                
                self.sprite_atual = self.sprite_base

            except FileNotFoundError as erro:
                print(f"⚠️ Aviso: Não foi possível carregar os sprites do botão '{texto}'.")
                print(f"Caminho procurado: {erro.filename}")
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

        self.fonte = obter_fonte(fonte_tamanho)
        self.txt_renderizado = self.fonte.render(texto, True, cor_texto)
        self.txt_rect = self.txt_renderizado.get_rect(center=self.rect.center)

    def checar_clique(self, evento, posicao_mouse):
        """Verifica se o botão foi pressionado e solto sobre ele"""
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(posicao_mouse):
                self.pressionado = True
        
        if evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            if self.pressionado and self.rect.collidepoint(posicao_mouse):
                self.pressionado = False
                return True
            self.pressionado = False
            
        return False

    def atualizar(self, posicao_mouse, estado_clique_mouse):
        if self.rect.collidepoint(posicao_mouse):
            self.cor_atual = self.cor_hover
            if estado_clique_mouse[0]:
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
            superficie.blit(self.txt_renderizado, self.txt_rect)
        else:
            pygame.draw.rect(superficie, self.cor_atual, self.rect)
            superficie.blit(self.txt_renderizado, self.txt_rect)

    def clicado(self, posicao_mouse):
        return self.rect.collidepoint(posicao_mouse)


class GerenciadorMenu:
    def __init__(self, tela):
        self.tela = tela
        
        largura_tela = self.tela.get_width()
        altura_tela = self.tela.get_height()

        caminho_fundo = caminho_imagem("Menu.png")
        try:
            imagem_fundo = pygame.image.load(caminho_fundo).convert()
            escala = max(largura_tela / imagem_fundo.get_width(), altura_tela / imagem_fundo.get_height())
            tamanho_fundo = (int(imagem_fundo.get_width() * escala), int(imagem_fundo.get_height() * escala))
            imagem_fundo = pygame.transform.scale(imagem_fundo, tamanho_fundo)
            x_fundo = (largura_tela - tamanho_fundo[0]) // 2
            y_fundo = (altura_tela - tamanho_fundo[1]) // 2
            self.imagem_fundo = imagem_fundo
            self.posicao_fundo = (x_fundo, y_fundo)
        except (FileNotFoundError, pygame.error) as erro:
            self.imagem_fundo = None
            self.posicao_fundo = (0, 0)
            print(f"Aviso: nao foi possivel carregar o fundo do menu: {erro}")
        
        self.fonte_titulo = obter_fonte(60)
        self.txt_titulo = self.fonte_titulo.render("MENU", True, (255, 255, 255))

        largura_titulo = 600
        altura_titulo = 160
        x_titulo = (largura_tela - largura_titulo) // 2
        self.titulo_rect = pygame.Rect(x_titulo, 100, largura_titulo, altura_titulo)
        self.titulo_anim_rect = self.titulo_rect.copy()
        self.titulo_anim_tempo = 0.0

        self.imagem_titulo = None
        self.posicao_titulo = self.titulo_rect.topleft
        for nome_titulo in ("Titulo.png", "Titulo(1).png"):
            try:
                imagem_titulo = pygame.image.load(caminho_imagem(nome_titulo)).convert_alpha()
                self.imagem_titulo = pygame.transform.scale(imagem_titulo, (largura_titulo + 120, altura_titulo + 30))
                self.posicao_titulo = (x_titulo - 60, 70)
                self.titulo_anim_rect = pygame.Rect(self.posicao_titulo, self.imagem_titulo.get_size())
                break
            except (FileNotFoundError, pygame.error):
                continue
        
        sprite_jogar_base = "BPM.png"
        sprite_jogar_hover = "BPG.png"
        sprite_jogar_clique = "BPP.png"

        sprite_classe_base = "BCM.png" 
        sprite_classe_hover = "BCG.png"
        sprite_classe_clique = "BCP.png"

        sprite_sair_base = "BSM.png"
        sprite_sair_hover = "BSG.png"
        sprite_sair_clique = "BSP.png"

        largura_botao = 190
        altura_botao = 55
        x_botao = (largura_tela - largura_botao) // 2
        
        self.botao_jogar = Botao(x_botao, 250, largura_botao, altura_botao, "JOGAR", (0, 200, 0), (0, 255, 0), 200, 60, cor_texto=(0, 0, 0), fonte_tamanho=24, sprite_base_path=sprite_jogar_base, sprite_hover_path=sprite_jogar_hover, sprite_clique_path=sprite_jogar_clique)
        self.botao_classe = Botao(x_botao, 350, largura_botao, altura_botao, "VERSO", (200, 200, 0), (255, 255, 0), 200, 60, cor_texto=(0, 0, 0), fonte_tamanho=24, sprite_base_path=sprite_classe_base, sprite_hover_path=sprite_classe_hover, sprite_clique_path=sprite_classe_clique)
        self.botao_sair = Botao(x_botao, 450, largura_botao, altura_botao, "SAIR", (200, 0, 0), (255, 0, 0), 200, 60, cor_texto=(255, 255, 255), fonte_tamanho=24, sprite_base_path=sprite_sair_base, sprite_hover_path=sprite_sair_hover, sprite_clique_path=sprite_sair_clique)

        self.lista_botoes = [self.botao_jogar, self.botao_classe, self.botao_sair]
        sw_w, sw_h = 80, 40
        sw_x = self.tela.get_width() - sw_w - 20
        sw_y = 20
        self.switch_2p = Botao(sw_x, sw_y, sw_w, sw_h, "2P", (120,120,120), (180,180,180), sw_w, sw_h, cor_texto=(255,255,255), fonte_tamanho=22)
        self.duas_pessoas = False
        self.txt_switch_2p = self.switch_2p.fonte.render("2P", True, (255, 255, 255))
    def atualizar(self, posicao_mouse, estado_clique_mouse):
        self.titulo_anim_tempo += 0.018

        for botao in self.lista_botoes:
            botao.atualizar(posicao_mouse, estado_clique_mouse)
        self.switch_2p.atualizar(posicao_mouse, estado_clique_mouse)

        if self.imagem_titulo is not None:
            angulo = math.sin(self.titulo_anim_tempo * 1.4) * 4
            escala = 1.0 + (math.sin(self.titulo_anim_tempo * 2.4) * 0.025)
            imagem_animada = pygame.transform.rotozoom(self.imagem_titulo, angulo, escala)
            self.titulo_anim_rect = imagem_animada.get_rect(center=self.titulo_rect.center)
            self.titulo_anim_rect.y += int(math.sin(self.titulo_anim_tempo * 1.4) * 6)
            self.titulo_surface = imagem_animada
        else:
            pulsacao = 1.0 + math.sin(self.titulo_anim_tempo * 2.2) * 0.025
            titulo_base = pygame.transform.scale(self.txt_titulo, (
                int(self.txt_titulo.get_width() * pulsacao),
                int(self.txt_titulo.get_height() * pulsacao)
            ))
            self.titulo_surface = titulo_base
            self.titulo_anim_rect = titulo_base.get_rect(center=self.titulo_rect.center)
            self.titulo_anim_rect.x += int(math.sin(self.titulo_anim_tempo * 1.2) * 8)

    def desenhar(self):
        if self.imagem_fundo is not None:
            self.tela.blit(self.imagem_fundo, self.posicao_fundo)
        else:
            self.tela.fill((30, 30, 40))

        if self.imagem_titulo is not None:
            self.tela.blit(self.titulo_surface, self.titulo_anim_rect)
        else:
            pygame.draw.rect(self.tela, (80, 80, 200), self.titulo_rect)
            self.tela.blit(self.titulo_surface, self.titulo_anim_rect)
        
        for botao in self.lista_botoes:
            botao.desenhar(self.tela)
        cor = (0,180,0) if self.duas_pessoas else (120,120,120)
        pygame.draw.rect(self.tela, cor, self.switch_2p.rect, border_radius=6)
        self.tela.blit(self.txt_switch_2p, self.txt_switch_2p.get_rect(center=self.switch_2p.rect.center))