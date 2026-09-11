import pygame
from Menu import Botao 
from Fontes import obter_fonte

ARVORE_GERAL = [
    {"id": "G1", "nome": "Saúde de Ferro", "desc": "Aumenta o HP máximo\nCusto 10", "preco": 10, "pos": (500, 600), "req": []},
    {"id": "G2", "nome": "Foco Mental", "desc": "Aumenta MP máximo\nCusto 20", "preco": 20, "pos": (500, 480), "req": ["G1"]},
    {"id": "G3", "nome": "Golpe Pesado", "desc": "Aumenta o dano causado\nCusto 50", "preco": 50, "pos": (500, 360), "req": ["G2"]},
    {"id": "G4", "nome": "Instinto", "desc": "Aumenta a defesa geral\nCusto 100", "preco": 100, "pos": (420, 240), "req": ["G3"]},
    {"id": "G5", "nome": "Recuperação", "desc": "Regenera vida aos poucos\nCusto 100", "preco": 100, "pos": (580, 240), "req": ["G3"]},
]

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
        self.caminho_atual = "Físico"
        self.habilidades_desbloqueadas = []
        self.habilidade_foco = None
        
        self.botao_voltar = Botao(720, 700, 240, 50, "VOLTAR", (55, 62, 78), AZUL_DESTAQUE, 250, 55, cor_texto=TEXTO, fonte_tamanho=14)
        self.botao_selecionar = Botao(720, 630, 240, 50, "ESCOLHER CLASSE", AZUL_DESTAQUE, (95, 120, 145), 250, 55, cor_texto=TEXTO, fonte_tamanho=14)
        self.botao_comprar = Botao(720, 560, 240, 50, "DESBLOQUEAR", (65, 75, 92), (95, 110, 130), 250, 55, cor_texto=TEXTO, fonte_tamanho=14)
        
        self.botoes_caminho = {
            "Físico": Botao(320, 670, 110, 40, "FÍSICO", (189, 118, 52), (209, 138, 72), 120, 50, cor_texto=TEXTO, fonte_tamanho=12),
            "Distância": Botao(445, 670, 110, 40, "DISTÂNCIA", (186, 52, 52), (206, 72, 72), 120, 50, cor_texto=TEXTO, fonte_tamanho=12),
            "Magia": Botao(570, 670, 110, 40, "MAGIA", (128, 78, 168), (148, 98, 188), 120, 50, cor_texto=TEXTO, fonte_tamanho=12)
        }

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
            return (self.classe_atual, self.caminho_atual)
            
        if self.botao_comprar.checar_clique(evento, posicao_mouse):
            if self.habilidade_foco:
                if self.habilidade_foco["id"] not in self.habilidades_desbloqueadas:
                    pode_comprar = True
                    for req in self.habilidade_foco["req"]:
                        if req not in self.habilidades_desbloqueadas:
                            pode_comprar = False
                    if pode_comprar and self.pontos >= self.habilidade_foco["preco"]:
                        self.pontos -= self.habilidade_foco["preco"]
                        self.habilidades_desbloqueadas.append(self.habilidade_foco["id"])
            return None

        for nome_caminho, botao in self.botoes_caminho.items():
            if botao.checar_clique(evento, posicao_mouse):
                self.caminho_atual = nome_caminho
                self.habilidade_foco = None
                return None
            
        if evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            for nome, rect in self.esferas_rects.items():
                if rect.collidepoint(posicao_mouse):
                    self.classe_atual = nome
                    self.habilidade_foco = None
                    return None
            
            for hab in ARVORE_GERAL:
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
        for botao in self.botoes_caminho.values():
            botao.atualizar(posicao_mouse, estado_clique_mouse)

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
        
        for hab in ARVORE_GERAL:
            for req_id in hab["req"]:
                for h in ARVORE_GERAL:
                    if h["id"] == req_id:
                        cor_linha = AZUL_DESTAQUE if (hab["id"] in self.habilidades_desbloqueadas) else BORDA
                        pygame.draw.line(self.tela, cor_linha, h["pos"], hab["pos"], 4)
        
        for hab in ARVORE_GERAL:
            cor = (75, 82, 95)
            if hab["id"] in self.habilidades_desbloqueadas:
                cor = (95, 125, 155)
            else:
                pode = True
                for req in hab["req"]:
                    if req not in self.habilidades_desbloqueadas:
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
            if self.habilidade_foco["id"] in self.habilidades_desbloqueadas:
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
        for nome_caminho, botao in self.botoes_caminho.items():
            botao.desenhar(self.tela)
            if nome_caminho == self.caminho_atual:
                pygame.draw.rect(self.tela, (255, 255, 100), botao.rect, 3, border_radius=4)