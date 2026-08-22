import random

import pygame
from Fontes import obter_fonte


class GerenciadorSelecao:
    def __init__(self, tela):
        self.tela = tela
        self.largura_tela = self.tela.get_width()
        self.retangulos = []
        self.clique_anterior = False

        self.fonte_titulo = obter_fonte(40)
        self.txt_titulo = self.fonte_titulo.render("ESCOLHA SEU PRÓXIMO DESAFIO", True, (255, 255, 255))

        self.cenarios_disponiveis = [
            ("evento_neutro_1", "TRILHA DA SURPRESA\n[EVENTO NEUTRO]"),
            ("evento_neutro_2", "ENTRADA DE TERRA\n[EVENTO NEUTRO]"),
            ("evento_neutro_3", "ROTA DA INSEGURANÇA\n[EVENTO NEUTRO]"),
            ("evento_neutro_4", "BATALHA IMPREVISÍVEL\n[EVENTO NEUTRO]"),
            ("fase_aleatoria", "FASE ALEATÓRIA\n[GERAÇÃO AUTOMÁTICA]"),
        ]

        self.recarregar_opcoes()

    def recarregar_opcoes(self):
        self.retangulos.clear()

        quantidade_opcoes = 3
        espacamento = max(12, self.largura_tela // 50)
        margem = max(20, self.largura_tela // 20)
        largura_rect = (self.largura_tela - (margem * 2) - (espacamento * (quantidade_opcoes - 1))) // quantidade_opcoes
        altura_rect = min(360, max(220, self.tela.get_height() - 300))
        y_rect = max(170, (self.tela.get_height() - altura_rect) // 2 + 30)
        x_inicial = (self.largura_tela - ((largura_rect * quantidade_opcoes) + (espacamento * (quantidade_opcoes - 1)))) // 2

        for i, (nome, label) in enumerate(random.sample(self.cenarios_disponiveis, quantidade_opcoes)):
            x = x_inicial + i * (largura_rect + espacamento)
            rect = pygame.Rect(x, y_rect, largura_rect, altura_rect)
            self.retangulos.append({
                "rect": rect,
                "nome": nome,
                "label": label,
            })

    def atualizar_eventos(self, evento, mouse_pos):
        if evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            for item in self.retangulos:
                if item["rect"].collidepoint(mouse_pos):
                    return item["nome"]
        return None

    def atualizar(self, mouse_pos, mouse_click):
        clique_agora = mouse_click[0]
        clicou = clique_agora and not self.clique_anterior
        self.clique_anterior = clique_agora
        
        if clicou:
            for item in self.retangulos:
                if item["rect"].collidepoint(mouse_pos):
                    return item["nome"] # Retorna "cenario_1", "cenario_2", etc.
        return None

    def desenhar(self):
        self.tela.fill((15, 15, 20))
        
        # Desenha o Título
        x_tit = (self.largura_tela - self.txt_titulo.get_width()) // 2
        self.tela.blit(self.txt_titulo, (x_tit, 80))
        
        mouse_pos = pygame.mouse.get_pos()
        fonte = obter_fonte(20)
        
        for item in self.retangulos:
            rect = item["rect"]
            pair_hover = rect.collidepoint(mouse_pos)
            
            # Cor de fundo (fica um pouco mais clara se passar o mouse)
            cor_fundo = (60, 60, 80) if pair_hover else (35, 35, 45)
            # Borda amarela se passar o mouse, branca se não
            cor_borda = (255, 220, 0) if pair_hover else (150, 150, 170)
            largura_borda = 4 if pair_hover else 2
            
            pygame.draw.rect(self.tela, cor_fundo, rect, border_radius=10)
            pygame.draw.rect(self.tela, cor_borda, rect, width=largura_borda, border_radius=10)
            
            linhas = []
            for linha in item["label"].split("\n"):
                if fonte.size(linha)[0] <= rect.width - 24:
                    linhas.append(linha)
                else:
                    palavras = linha.split()
                    linha_atual = ""
                    for palavra in palavras:
                        candidata = f"{linha_atual} {palavra}".strip()
                        if linha_atual and fonte.size(candidata)[0] > rect.width - 24:
                            linhas.append(linha_atual)
                            linha_atual = palavra
                        else:
                            linha_atual = candidata
                    if linha_atual:
                        linhas.append(linha_atual)

            altura_texto = len(linhas) * fonte.get_linesize()
            y_texto = rect.centery - altura_texto // 2
            for idx, linha in enumerate(linhas):
                cor_txt = (255, 220, 0) if pair_hover else (255, 255, 255)
                texto_surf = fonte.render(linha, True, cor_txt)
                x_txt = rect.x + (rect.width - texto_surf.get_width()) // 2
                y_txt = y_texto + (idx * fonte.get_linesize())
                self.tela.blit(texto_surf, (x_txt, y_txt))