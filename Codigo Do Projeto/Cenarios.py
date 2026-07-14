import pygame

class GerenciadorSelecao:
    def __init__(self, tela):
        self.tela = tela
        self.largura_tela = self.tela.get_width()
        self.retangulos = []
        self.clique_anterior = False
        
        # Título da tela
        self.fonte_titulo = pygame.font.SysFont(["consolas", "courier"], 40, bold=True)
        self.txt_titulo = self.fonte_titulo.render("ESCOLHA SEU PRÓXIMO DESAFIO", True, (255, 255, 255))
        
        # Textos explicativos dos cenários
        nomes_cenarios = [
            "1. FLORESTA\n(Fácil)", 
            "2. CAVERNA\n(Médio)", 
            "3. RUÍNAS\n(Difícil)", 
            "4. COVIL\n(Chefe)"
        ]
        
        # Criando os 4 retângulos verticais centralizados
        espacamento = 20
        largura_rect = 180
        altura_rect = 400
        x_inicial = (self.largura_tela - ((largura_rect * 4) + (espacamento * 3))) // 2
        
        for i in range(4):
            x = x_inicial + i * (largura_rect + espacamento)
            rect = pygame.Rect(x, 200, largura_rect, altura_rect)
            self.retangulos.append({
                "rect": rect, 
                "nome": f"cenario_{i+1}", 
                "label": nomes_cenarios[i]
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
        fonte = pygame.font.SysFont(["consolas", "courier"], 22, bold=True)
        
        # Desenha os 4 Retângulos
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
            
            # Desenha o texto dentro do retângulo (suporta quebra de linha com \n)
            linhas = item["label"].split("\n")
            for idx, linha in enumerate(linhas):
                cor_txt = (255, 220, 0) if pair_hover else (255, 255, 255)
                texto_surf = fonte.render(linha, True, cor_txt)
                x_txt = rect.x + (rect.width - texto_surf.get_width()) // 2
                y_txt = rect.y + 160 + (idx * 30)
                self.tela.blit(texto_surf, (x_txt, y_txt))