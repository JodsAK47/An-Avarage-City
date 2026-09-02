import pygame
from Menu import Botao 
from Fontes import obter_fonte

ARVORES = {
    "Sobrevivente": [
        {"id": "L1", "nome": "Soco Forte", "desc": "Ataque basico corpo a corpo\nCusto 10", "preco": 10, "pos": (500, 600), "req": []},
        {"id": "L2", "nome": "Pele de Pedra", "desc": "Aumenta defesa passiva\nCusto 20", "preco": 20, "pos": (500, 480), "req": ["L1"]},
        {"id": "L3", "nome": "Terremoto", "desc": "Ataque em area\nCusto 50", "preco": 50, "pos": (500, 360), "req": ["L2"]},
        {"id": "L4", "nome": "Furia", "desc": "Critico garantido\nCusto 100", "preco": 100, "pos": (420, 240), "req": ["L3"]},
        {"id": "L5", "nome": "Regeneracao", "desc": "Cura a cada turno\nCusto 100", "preco": 100, "pos": (580, 240), "req": ["L3"]},
    ],
    "Agente": [
        {"id": "A1", "nome": "One Tap", "desc": "Tiro preciso e poderoso\nCusto 10", "preco": 10, "pos": (500, 600), "req": []},
        {"id": "A2", "nome": "Spray", "desc": "Rajada em área\nCusto 20", "preco": 20, "pos": (500, 480), "req": ["A1"]},
        {"id": "A3", "nome": "Tiro de Fuga", "desc": "Foco e mobilidade\nCusto 50", "preco": 50, "pos": (500, 360), "req": ["A2"]},
        {"id": "A4", "nome": "Precisao", "desc": "Aumenta chance de acerto\nCusto 100", "preco": 100, "pos": (420, 240), "req": ["A3"]},
        {"id": "A5", "nome": "Disparo Rápido", "desc": "Ataque de suporte ágil\nCusto 100", "preco": 100, "pos": (580, 240), "req": ["A3"]},
    ],
    "Feiticeiro": [
        {"id": "M1", "nome": "Gelo", "desc": "Lança uma estaca gelada\nCusto 10", "preco": 10, "pos": (500, 600), "req": []},
        {"id": "M2", "nome": "Nevasca", "desc": "Congela todos na tela\nCusto 20", "preco": 20, "pos": (500, 480), "req": ["M1"]},
        {"id": "M3", "nome": "Fogo", "desc": "Explosão elemental em área\nCusto 50", "preco": 50, "pos": (500, 360), "req": ["M2"]},
        {"id": "M4", "nome": "Campo Arcano", "desc": "Aumenta a potência mágica\nCusto 100", "preco": 100, "pos": (420, 240), "req": ["M3"]},
        {"id": "M5", "nome": "Fluxo Mágico", "desc": "Recupera mana e pressiona\nCusto 100", "preco": 100, "pos": (580, 240), "req": ["M3"]},
    ]
}

FUNDO = (25, 30, 42)
PAINEL = (38, 46, 62)
PAINEL_CLARO = (48, 57, 75)
BORDA = (91, 103, 126)
TEXTO = (235, 235, 235)
TEXTO_SECUNDARIO = (180, 190, 205)
AZUL_DESTAQUE = (76, 98, 122)

CORES_CLASSES = {
    "Sobrevivente": (189, 118, 52),
    "Agente": (186, 52, 52),
    "Feiticeiro": (128, 78, 168)
}

class GerenciadorClasses:
    def __init__(self, tela):
        self.tela = tela
        
        self.fonte_titulo = obter_fonte(16)
        self.fonte_desc = obter_fonte(12)
        
        self.aviso = ""
        self.voltar_clicado = False
        
        self.pontos = 0
        self.classe_atual = "Sobrevivente"
        self.habilidades_desbloqueadas = {"Sobrevivente": [], "Agente": [], "Feiticeiro": []}
        self.habilidade_foco = None
        
        self.botao_voltar = Botao(720, 700, 240, 50, "VOLTAR", (55, 62, 78), AZUL_DESTAQUE, 250, 55, cor_texto=TEXTO, fonte_tamanho=14)
        self.botao_selecionar = Botao(720, 630, 240, 50, "ESCOLHER CLASSE", AZUL_DESTAQUE, (95, 120, 145), 250, 55, cor_texto=TEXTO, fonte_tamanho=14)
        self.botao_comprar = Botao(720, 560, 240, 50, "DESBLOQUEAR", (65, 75, 92), (95, 110, 130), 250, 55, cor_texto=TEXTO, fonte_tamanho=14)
        
        self.esferas_rects = {
            "Sobrevivente": pygame.Rect(70, 410, 80, 80),
            "Agente": pygame.Rect(190, 410, 80, 80),
            "Feiticeiro": pygame.Rect(130, 545, 80, 80)
        }

    def atualizar_eventos(self, evento, posicao_mouse):
        if self.botao_voltar.checar_clique(evento, posicao_mouse):
            self.voltar_clicado = True
            return None
            
        if self.botao_selecionar.checar_clique(evento, posicao_mouse):
            return self.classe_atual
            
        if self.botao_comprar.checar_clique(evento, posicao_mouse):
            if self.habilidade_foco:
                if self.habilidade_foco["id"] not in self.habilidades_desbloqueadas[self.classe_atual]:
                    pode_comprar = True
                    for req in self.habilidade_foco["req"]:
                        if req not in self.habilidades_desbloqueadas[self.classe_atual]:
                            pode_comprar = False
                    if pode_comprar and self.pontos >= self.habilidade_foco["preco"]:
                        self.pontos -= self.habilidade_foco["preco"]
                        self.habilidades_desbloqueadas[self.classe_atual].append(self.habilidade_foco["id"])
            return None
            
        if evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            for nome, rect in self.esferas_rects.items():
                if rect.collidepoint(posicao_mouse):
                    self.classe_atual = nome
                    self.habilidade_foco = None
                    return None
            
            for hab in ARVORES[self.classe_atual]:
                x, y = hab["pos"]
                rect_hab = pygame.Rect(x - 35, y - 35, 70, 70)
                if rect_hab.collidepoint(posicao_mouse):
                    self.habilidade_foco = hab
                    return None

        return None

    def atualizar(self, posicao_mouse, estado_clique_mouse):
        self.botao_voltar.atualizar(posicao_mouse, estado_clique_mouse)
        self.botao_selecionar.atualizar(posicao_mouse, estado_clique_mouse)
        self.botao_comprar.atualizar(posicao_mouse, estado_clique_mouse)

    def _quebrar_texto(self, texto, fonte, largura_maxima):
        linhas = []
        for paragrafo in texto.split("\n"):
            palavras = paragrafo.split()
            linha = ""
            for palavra in palavras:
                tentativa = f"{linha} {palavra}".strip()
                if fonte.size(tentativa)[0] <= largura_maxima:
                    linha = tentativa
                else:
                    if linha:
                        linhas.append(linha)
                    linha = palavra
            linhas.append(linha)
        return linhas

    def desenhar(self):
        self.tela.fill(FUNDO)
        
        pygame.draw.rect(self.tela, PAINEL_CLARO, (40, 40, 260, 260))
        txt_carac = self.fonte_desc.render("CLASSE", True, TEXTO)
        self.tela.blit(txt_carac, (170 - txt_carac.get_width()//2, 50))

        pygame.draw.circle(self.tela, CORES_CLASSES[self.classe_atual], (170, 180), 60)
        pygame.draw.circle(self.tela, (200, 255, 50), (170, 180), 60, 5)

        nome_classe = self.classe_atual.upper()
        txt_nome_classe = self.fonte_desc.render(nome_classe, True, TEXTO)
        self.tela.blit(txt_nome_classe, (170 - txt_nome_classe.get_width()//2, 260))
        
        pygame.draw.rect(self.tela, PAINEL_CLARO, (40, 320, 260, 440))
        txt_arvores = self.fonte_desc.render("Arvores de Habilidades", True, TEXTO)
        self.tela.blit(txt_arvores, (170 - txt_arvores.get_width()//2, 340))
        
        destaque_por_classe = {
            "Sobrevivente": (255, 191, 122),
            "Agente": (255, 120, 120),
            "Feiticeiro": (196, 147, 255)
        }

        for nome, rect in self.esferas_rects.items():
            borda = 5 if nome == self.classe_atual else 0
            pygame.draw.circle(self.tela, CORES_CLASSES[nome], rect.center, 40)
            if borda:
                pygame.draw.circle(self.tela, destaque_por_classe[nome], rect.center, 40, 5)
        
        pygame.draw.rect(self.tela, PAINEL, (320, 40, 360, 720))
        
        for hab in ARVORES[self.classe_atual]:
            for req_id in hab["req"]:
                for h in ARVORES[self.classe_atual]:
                    if h["id"] == req_id:
                        cor_linha = AZUL_DESTAQUE if (hab["id"] in self.habilidades_desbloqueadas[self.classe_atual]) else BORDA
                        pygame.draw.line(self.tela, cor_linha, h["pos"], hab["pos"], 4)
        
        for hab in ARVORES[self.classe_atual]:
            cor = (75, 82, 95)
            if hab["id"] in self.habilidades_desbloqueadas[self.classe_atual]:
                cor = (95, 125, 155)
            else:
                pode = True
                for req in hab["req"]:
                    if req not in self.habilidades_desbloqueadas[self.classe_atual]:
                        pode = False
                if pode:
                    cor = (110, 125, 145)
            
            x, y = hab["pos"]
            pygame.draw.circle(self.tela, cor, (x, y), 35)
            if self.habilidade_foco == hab:
                pygame.draw.circle(self.tela, TEXTO, (x, y), 38, 3)
                
        if self.aviso:
            txt_aviso = self.fonte_titulo.render(self.aviso, True, TEXTO)
            self.tela.blit(txt_aviso, (500 - txt_aviso.get_width()//2, 60))
            
        pygame.draw.rect(self.tela, PAINEL_CLARO, (700, 40, 280, 500), border_radius=8)
        pygame.draw.rect(self.tela, BORDA, (700, 40, 280, 500), width=3, border_radius=8)
        
        if self.habilidade_foco:
            txt_nome = self.fonte_titulo.render(self.habilidade_foco["nome"].upper(), True, TEXTO)
            self.tela.blit(txt_nome, txt_nome.get_rect(centerx=840, top=62))
            
            y_offset = 120
            for linha in self._quebrar_texto(self.habilidade_foco["desc"], self.fonte_desc, 240):
                txt_desc = self.fonte_desc.render(linha, True, TEXTO_SECUNDARIO)
                self.tela.blit(txt_desc, txt_desc.get_rect(centerx=840, top=y_offset))
                y_offset += 22
                
            estado_txt = "BLOQUEADO"
            if self.habilidade_foco["id"] in self.habilidades_desbloqueadas[self.classe_atual]:
                estado_txt = "DESBLOQUEADO"
            txt_estado = self.fonte_desc.render(estado_txt, True, AZUL_DESTAQUE)
            self.tela.blit(txt_estado, txt_estado.get_rect(centerx=840, top=y_offset + 18))
            
        else:
            txt_nada = self.fonte_desc.render("Selecione um poder", True, TEXTO_SECUNDARIO)
            self.tela.blit(txt_nada, txt_nada.get_rect(centerx=840, top=62))
            
        pygame.draw.rect(self.tela, FUNDO, (712, 470, 256, 40))
        txt_pontos = self.fonte_titulo.render(f"PONTOS: {self.pontos}", True, TEXTO)
        self.tela.blit(txt_pontos, txt_pontos.get_rect(center=(840, 490)))
            
        self.botao_comprar.desenhar(self.tela)
        self.botao_selecionar.desenhar(self.tela)
        self.botao_voltar.desenhar(self.tela)