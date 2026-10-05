import math
import pygame
from Sistemas.Fontes import obter_fonte
from Sistemas.Recursos import caminho_botao, caminho_imagem
from Sistemas.SistemaUI import Botao, TelaBase, GerenciadorTelas
from Sistemas.SaveSystem import save_global


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
            self.escala_fundo = escala
        except (FileNotFoundError, pygame.error) as erro:
            self.imagem_fundo = None
            self.posicao_fundo = (0, 0)
            self.escala_fundo = 1.0
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
        self.titulo_surface = self.imagem_titulo if self.imagem_titulo is not None else self.txt_titulo
        
        sprite_jogar_base = "BVERDEM.png"
        sprite_jogar_hover = "BVERDG.png"
        sprite_jogar_clique = "BVERDEP.png"

        sprite_classe_base = "BYELLM.png"
        sprite_classe_hover = "BYELLG.png"
        sprite_classe_clique = "BYELLP.png"

        sprite_conquistas_base = "BAZULM.png"
        sprite_conquistas_hover = "BAZULG.png"
        sprite_conquistas_clique = "BAZULP.png"

        sprite_sair_base = "BREDM.png"
        sprite_sair_hover = "BREDG.png"
        sprite_sair_clique = "BREDP.png"

        largura_botao = 190
        altura_botao = 55
        x_botao = (largura_tela - largura_botao) // 2

        self.botoes = {
            "jogar": Botao(x_botao, 240, largura_botao, altura_botao, "JOGAR", (0, 200, 0), (0, 255, 0), 200, 60, cor_texto=(0, 0, 0), fonte_tamanho=24, sprite_base_path=sprite_jogar_base, sprite_hover_path=sprite_jogar_hover, sprite_clique_path=sprite_jogar_clique),
            "classe": Botao(x_botao, 330, largura_botao, altura_botao, "VERSO", (200, 200, 0), (255, 255, 0), 200, 60, cor_texto=(0, 0, 0), fonte_tamanho=24, sprite_base_path=sprite_classe_base, sprite_hover_path=sprite_classe_hover, sprite_clique_path=sprite_classe_clique),
            "conquistas": Botao(x_botao, 420, largura_botao, altura_botao, "CONQUISTAS", (0, 100, 220), (0, 150, 255), 200, 60, cor_texto=(255, 255, 255), fonte_tamanho=18, sprite_base_path=sprite_conquistas_base, sprite_hover_path=sprite_conquistas_hover, sprite_clique_path=sprite_conquistas_clique),
            "sair": Botao(x_botao, 510, largura_botao, altura_botao, "SAIR", (200, 0, 0), (255, 0, 0), 200, 60, cor_texto=(255, 255, 255), fonte_tamanho=24, sprite_base_path=sprite_sair_base, sprite_hover_path=sprite_sair_hover, sprite_clique_path=sprite_sair_clique),
        }
        self.botao_jogar = self.botoes["jogar"]
        self.botao_classe = self.botoes["classe"]
        self.botao_conquistas = self.botoes["conquistas"]
        self.botao_sair = self.botoes["sair"]
        self.lista_botoes = list(self.botoes.values())

        sw_w, sw_h = 80, 40
        sw_x = self.tela.get_width() - sw_w - 20
        sw_y = 20
        self.switch_2p = Botao(
            sw_x, sw_y, sw_w, sw_h, "",
            (120, 120, 120), (180, 180, 180), sw_w, sw_h,
            cor_texto=(255, 255, 255), fonte_tamanho=22,
            sprite_base_path="SON.png",
            sprite_hover_path="SON.png",
            sprite_clique_path="SOFF.png",
            alternado=True,
            ativo_inicial=False,
        )
        self.switch_2p.sem_texto = True
        self.duas_pessoas = False

        # Botões de Save e Reset manual no canto inferior esquerdo
        largura_sr = 100
        altura_sr = 40
        y_sr = self.tela.get_height() - altura_sr - 20  # y = 740

        self.botao_salvar = Botao(
            25, y_sr, largura_sr, altura_sr, "SALVAR", (30, 140, 70), (40, 180, 90), 104, 44,
            cor_texto=(255, 255, 255), fonte_tamanho=13,
            sprite_base_path="BVERDEM.png", sprite_hover_path="BVERDG.png", sprite_clique_path="BVERDEP.png"
        )
        self.botao_reset = Botao(
            135, y_sr, largura_sr, altura_sr, "RESET", (160, 40, 40), (200, 50, 50), 104, 44,
            cor_texto=(255, 255, 255), fonte_tamanho=13,
            sprite_base_path="BREDM.png", sprite_hover_path="BREDG.png", sprite_clique_path="BREDP.png"
        )

        self.fonte_feedback = obter_fonte(12)
        self.msg_feedback = ""
        self.cor_feedback = (100, 255, 140)
        self.timer_feedback = 0

        # Porta da Esquerda: Acesso ao Esgoto (SEWER ACCESS) onde o cartão é pego
        self.rect_porta_esgoto = pygame.Rect(
            self.posicao_fundo[0] + int(72 * self.escala_fundo),
            self.posicao_fundo[1] + int(375 * self.escala_fundo),
            int(143 * self.escala_fundo),
            int(490 * self.escala_fundo)
        )

        # Porta da Direita: Acesso aos Cheats (NO TRESPASSING / EXIT) - Requer Member Card
        self.rect_porta_cheats = pygame.Rect(
            self.posicao_fundo[0] + int(1045 * self.escala_fundo),
            self.posicao_fundo[1] + int(250 * self.escala_fundo),
            int(107 * self.escala_fundo),
            int(678 * self.escala_fundo)
        )
        self.rect_sewer_access = self.rect_porta_esgoto

    def checar_clique_esgoto(self, evento, posicao_mouse):
        """Verifica clique na porta da esquerda (Sewer Access) para entrar no esgoto."""
        if evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            if self.botao_salvar.rect.collidepoint(posicao_mouse) or self.botao_reset.rect.collidepoint(posicao_mouse):
                return False
            if self.rect_porta_esgoto.collidepoint(posicao_mouse):
                return True
        return False

    def checar_clique_porta_cheats(self, evento, posicao_mouse):
        """Verifica clique na porta da direita (No Trespassing). Abre cheats se tiver o Member Card."""
        if evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            if self.switch_2p.rect.collidepoint(posicao_mouse):
                return None
            if self.rect_porta_cheats.collidepoint(posicao_mouse):
                if save_global.tem_member_card():
                    return "cheats"
                else:
                    self.mostrar_feedback("🔒 NO TRESPASSING // Acesso Restrito! Requer o Member Card.", (255, 80, 80))
                    return "trancado"
        return None

    def checar_clique_sewer(self, evento, posicao_mouse):
        return self.checar_clique_esgoto(evento, posicao_mouse)

    def mostrar_feedback(self, texto, cor=(100, 255, 140)):
        self.msg_feedback = texto
        self.cor_feedback = cor
        self.timer_feedback = 180  # ~3 segundos a 60 FPS

    def buscar_botao(self, nome_botao):
        return self.botoes.get(nome_botao.lower())

    def atualizar(self, posicao_mouse, estado_clique_mouse):
        self.titulo_anim_tempo += 0.018

        for botao in self.lista_botoes:
            botao.atualizar(posicao_mouse, estado_clique_mouse)
        self.switch_2p.atualizar(posicao_mouse, estado_clique_mouse)
        self.botao_salvar.atualizar(posicao_mouse, estado_clique_mouse)
        self.botao_reset.atualizar(posicao_mouse, estado_clique_mouse)

        if self.timer_feedback > 0:
            self.timer_feedback -= 1

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
        self.switch_2p.desenhar(self.tela)

        # Desenha botões de Salvar e Reset no canto inferior esquerdo
        self.botao_salvar.desenhar(self.tela)
        self.botao_reset.desenhar(self.tela)

        # Mensagem de confirmação visual
        if self.timer_feedback > 0 and self.msg_feedback:
            txt_fb = self.fonte_feedback.render(self.msg_feedback, True, self.cor_feedback)
            # Fundo suave para legibilidade
            bg_rect = pygame.Rect(23, 715, txt_fb.get_width() + 8, txt_fb.get_height() + 4)
            pygame.draw.rect(self.tela, (15, 20, 28), bg_rect, border_radius=4)
            self.tela.blit(txt_fb, (27, 717))
