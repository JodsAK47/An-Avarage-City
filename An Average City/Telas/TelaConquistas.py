import pygame
from Sistemas.SistemaUI import Botao
from Sistemas.Fontes import obter_fonte
from Sistemas.Recursos import caminho_botao
from Sistemas.Conquistas import sistema_conquistas

FUNDO = (22, 26, 36)
PAINEL = (32, 38, 52)
PAINEL_DETALHES = (36, 44, 60)
CARD_DESBLOQUEADO = (42, 52, 70)
CARD_BLOQUEADO = (28, 33, 44)
BORDA_DESBLOQUEADA = (100, 130, 170)
BORDA_BLOQUEADA = (50, 56, 70)
BORDA_SELECIONADA = (255, 215, 60)
OURO = (245, 205, 55)
TEXTO_BRANCO = (240, 242, 245)
TEXTO_SECUNDARIO = (175, 185, 200)
TEXTO_BLOQUEADO = (120, 130, 145)
VERDE_STATUS = (70, 220, 120)
VERMELHO_STATUS = (210, 80, 80)


class GerenciadorConquistasTela:
    def __init__(self, tela):
        self.tela = tela
        self.fonte_titulo = obter_fonte(20)
        self.fonte_nome = obter_fonte(14)
        self.fonte_desc = obter_fonte(12)
        self.fonte_status = obter_fonte(11)

        self.scroll_y = 0.0
        self.scroll_alvo = 0.0
        self.voltar_clicado = False

        self.rect_lista = pygame.Rect(40, 90, 510, 670)
        self.rect_detalhes = pygame.Rect(570, 90, 390, 580)

        self.botao_voltar = Botao(
            720, 700, 240, 50, "VOLTAR", (55, 62, 78), (76, 98, 122), 250, 55,
            cor_texto=TEXTO_BRANCO, fonte_tamanho=14,
            sprite_base_path="BACK.png", sprite_hover_path="BACK.png", sprite_clique_path="BACK.png",
        )

        self.conquista_selecionada = None
        if sistema_conquistas.conquistas:
            self.conquista_selecionada = sistema_conquistas.conquistas[0]

    def _quebrar_texto(self, texto, fonte, largura_maxima):
        linhas = []
        for paragrafo in texto.split("\n"):
            palavras = paragrafo.split()
            if not palavras:
                linhas.append("")
                continue
            linha = ""
            for palavra in palavras:
                tentativa = f"{linha} {palavra}".strip()
                if fonte.size(tentativa)[0] <= largura_maxima:
                    linha = tentativa
                else:
                    if linha:
                        linhas.append(linha)
                    linha = palavra
            if linha:
                linhas.append(linha)
        return linhas

    def atualizar_eventos(self, evento, posicao_mouse):
        if self.botao_voltar.checar_clique(evento, posicao_mouse):
            self.voltar_clicado = True
            return "menu"

        # Rolagem suave do mouse
        if evento.type == pygame.MOUSEWHEEL:
            if self.rect_lista.collidepoint(posicao_mouse):
                self.scroll_alvo -= evento.y * 55

        # Clique nas conquistas dentro da lista
        if evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            if self.rect_lista.collidepoint(posicao_mouse):
                y_offset = self.rect_lista.y + 10 - int(self.scroll_y)
                card_w = self.rect_lista.width - 24
                card_h = 76
                espacamento = 10

                for c in sistema_conquistas.conquistas:
                    rect_item = pygame.Rect(self.rect_lista.x + 10, y_offset, card_w, card_h)
                    if rect_item.collidepoint(posicao_mouse):
                        self.conquista_selecionada = c
                        break
                    y_offset += card_h + espacamento

        return None

    def atualizar(self, posicao_mouse, estado_clique_mouse):
        self.botao_voltar.atualizar(posicao_mouse, estado_clique_mouse)

        # Atualiza limite do scroll
        total_itens = len(sistema_conquistas.conquistas)
        altura_conteudo = total_itens * (76 + 10) + 20
        max_scroll = max(0, altura_conteudo - self.rect_lista.height)

        self.scroll_alvo = max(0.0, min(self.scroll_alvo, float(max_scroll)))
        # Interpolação suave
        self.scroll_y += (self.scroll_alvo - self.scroll_y) * 0.35

    def desenhar(self):
        self.tela.fill(FUNDO)

        # Cabeçalho Superior
        pygame.draw.rect(self.tela, PAINEL, (40, 20, 920, 55), border_radius=8)
        pygame.draw.rect(self.tela, BORDA_DESBLOQUEADA, (40, 20, 920, 55), width=2, border_radius=8)

        txt_titulo = self.fonte_titulo.render("SALA DE CONQUISTAS", True, OURO)
        self.tela.blit(txt_titulo, (60, 32))

        desbloqueadas = sistema_conquistas.total_desbloqueadas()
        total = sistema_conquistas.total_conquistas()
        porcentagem = int((desbloqueadas / total) * 100) if total > 0 else 0
        txt_progresso = self.fonte_desc.render(f"Progresso: {desbloqueadas}/{total} ({porcentagem}%)", True, TEXTO_BRANCO)
        self.tela.blit(txt_progresso, (960 - 40 - txt_progresso.get_width(), 36))

        # -------------------------------------------------------------
        # 1. PAINEL SCROLÁVEL DA ESQUERDA (LISTA DE CONQUISTAS)
        # -------------------------------------------------------------
        pygame.draw.rect(self.tela, PAINEL, self.rect_lista, border_radius=8)
        pygame.draw.rect(self.tela, BORDA_DESBLOQUEADA, self.rect_lista, width=2, border_radius=8)

        # Superfície com clipping para recorte do scroll
        superficie_clip = self.tela.subsurface(self.rect_lista)

        card_w = self.rect_lista.width - 24
        card_h = 76
        espacamento = 10
        y_rel = 10 - int(self.scroll_y)

        for c in sistema_conquistas.conquistas:
            rect_card_local = pygame.Rect(10, y_rel, card_w, card_h)

            # Apenas desenha se estiver visível no viewport
            if rect_card_local.bottom >= 0 and rect_card_local.top <= self.rect_lista.height:
                esta_ativa = c.desbloqueada
                selecionada = (self.conquista_selecionada == c)

                cor_fundo_card = CARD_DESBLOQUEADO if esta_ativa else CARD_BLOQUEADO
                cor_borda = BORDA_SELECIONADA if selecionada else (BORDA_DESBLOQUEADA if esta_ativa else BORDA_BLOQUEADA)
                largura_borda = 3 if selecionada else 1

                pygame.draw.rect(superficie_clip, cor_fundo_card, rect_card_local, border_radius=8)
                pygame.draw.rect(superficie_clip, cor_borda, rect_card_local, width=largura_borda, border_radius=8)

                # Ícone (Colorido se desbloqueada, Preto e Branco se bloqueada)
                icone_surf = c.obter_icone(desbloqueada=esta_ativa, tamanho=(52, 52))
                superficie_clip.blit(icone_surf, (rect_card_local.x + 10, rect_card_local.y + 12))

                # Nome
                cor_texto_nome = TEXTO_BRANCO if esta_ativa else TEXTO_BLOQUEADO
                txt_nome = self.fonte_nome.render(c.nome, True, cor_texto_nome)
                superficie_clip.blit(txt_nome, (rect_card_local.x + 72, rect_card_local.y + 14))

                # Status Badge
                if esta_ativa:
                    txt_st = self.fonte_status.render("✓ DESBLOQUEADA", True, VERDE_STATUS)
                else:
                    txt_st = self.fonte_status.render("🔒 BLOQUEADA", True, TEXTO_BLOQUEADO)
                superficie_clip.blit(txt_st, (rect_card_local.x + 72, rect_card_local.y + 44))

            y_rel += card_h + espacamento

        # Barra de rolagem visual
        total_altura_conteudo = len(sistema_conquistas.conquistas) * (card_h + espacamento) + 20
        if total_altura_conteudo > self.rect_lista.height:
            trilho_h = self.rect_lista.height - 16
            proporcao = self.rect_lista.height / total_altura_conteudo
            polegar_h = max(24, int(trilho_h * proporcao))
            max_scroll = total_altura_conteudo - self.rect_lista.height
            pos_y_polegar = int((self.scroll_y / max_scroll) * (trilho_h - polegar_h))
            rect_polegar = pygame.Rect(self.rect_lista.right - 10, self.rect_lista.y + 8 + pos_y_polegar, 5, polegar_h)
            pygame.draw.rect(self.tela, OURO, rect_polegar, border_radius=3)

        # -------------------------------------------------------------
        # 2. PAINEL DE DETALHES DA DIREITA (ÍCONE, NOME E COMO LIBERAR)
        # -------------------------------------------------------------
        pygame.draw.rect(self.tela, PAINEL_DETALHES, self.rect_detalhes, border_radius=8)
        pygame.draw.rect(self.tela, BORDA_DESBLOQUEADA, self.rect_detalhes, width=2, border_radius=8)

        if self.conquista_selecionada:
            c = self.conquista_selecionada
            esta_ativa = c.desbloqueada

            # Moldura grande do ícone
            frame_icone = pygame.Rect(self.rect_detalhes.centerx - 70, self.rect_detalhes.y + 30, 140, 140)
            cor_moldura = OURO if esta_ativa else BORDA_BLOQUEADA
            pygame.draw.rect(self.tela, (20, 24, 32), frame_icone, border_radius=12)
            pygame.draw.rect(self.tela, cor_moldura, frame_icone, width=3, border_radius=12)

            # Ícone grande (Colorido se desbloqueada, Preto e Branco se bloqueada)
            icone_grande = c.obter_icone(desbloqueada=esta_ativa, tamanho=(110, 110))
            rect_icone_grande = icone_grande.get_rect(center=frame_icone.center)
            self.tela.blit(icone_grande, rect_icone_grande)

            # Badge de Estado abaixo do ícone
            if esta_ativa:
                txt_badge = self.fonte_nome.render("★ CONQUISTADA ★", True, OURO)
            else:
                txt_badge = self.fonte_nome.render("🔒 NÃO OBTIDA (P&B)", True, TEXTO_BLOQUEADO)
            self.tela.blit(txt_badge, txt_badge.get_rect(center=(self.rect_detalhes.centerx, frame_icone.bottom + 25)))

            # Linha divisória
            y_div = frame_icone.bottom + 50
            pygame.draw.line(self.tela, BORDA_BLOQUEADA, (self.rect_detalhes.x + 30, y_div), (self.rect_detalhes.right - 30, y_div), 2)

            # Nome da Conquista
            y_cursor = y_div + 20
            cor_nome = OURO if esta_ativa else TEXTO_BRANCO
            for linha in self._quebrar_texto(c.nome.upper(), self.fonte_titulo, self.rect_detalhes.width - 60):
                surf_l = self.fonte_titulo.render(linha, True, cor_nome)
                self.tela.blit(surf_l, surf_l.get_rect(centerx=self.rect_detalhes.centerx, top=y_cursor))
                y_cursor += 26

            # Seção: "COMO LIBERAR"
            y_cursor += 15
            txt_sec = self.fonte_status.render("COMO LIBERAR:", True, OURO)
            self.tela.blit(txt_sec, (self.rect_detalhes.x + 35, y_cursor))
            y_cursor += 22

            # Caixa com a descrição de como liberá-la
            rect_desc_box = pygame.Rect(self.rect_detalhes.x + 30, y_cursor, self.rect_detalhes.width - 60, 130)
            pygame.draw.rect(self.tela, (25, 30, 42), rect_desc_box, border_radius=6)
            pygame.draw.rect(self.tela, BORDA_BLOQUEADA, rect_desc_box, width=1, border_radius=6)

            y_texto_desc = rect_desc_box.y + 12
            for linha in self._quebrar_texto(c.como_liberar, self.fonte_desc, rect_desc_box.width - 24):
                surf_desc = self.fonte_desc.render(linha, True, TEXTO_BRANCO)
                self.tela.blit(surf_desc, (rect_desc_box.x + 12, y_texto_desc))
                y_texto_desc += 20

        # Botão Voltar
        self.botao_voltar.desenhar(self.tela)
