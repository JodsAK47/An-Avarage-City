import pygame
from Menu import Botao
from Fontes import obter_fonte
from Entidades.Personagem import personagem

ARVORE_SOBREVIVENTE = [
    {"id": "S1", "nome": "Resiliência", "desc": "Aumenta o HP máximo\nCusto 10", "preco": 10, "pos": (500, 150), "req": []},
    {"id": "S2", "nome": "Foco de Sobrevivência", "desc": "Aumenta MP máximo\nCusto 20", "preco": 20, "pos": (500, 270), "req": ["S1"]},
    {"id": "S3", "nome": "Golpe de Ferro", "desc": "Aumenta o dano físico\nCusto 50", "preco": 50, "pos": (500, 390), "req": ["S2"]},
    {"id": "S4", "nome": "Instinto de Sobrevivente", "desc": "Desbloqueia a ultimate do verso\nCusto 100", "preco": 100, "pos": (500, 510), "req": ["S3"]},
]

ARVORE_AGENTE = [
    {"id": "A1", "nome": "Precisão Mortal", "desc": "Aumenta a precisão\nCusto 10", "preco": 10, "pos": (500, 150), "req": []},
    {"id": "A2", "nome": "Mira Rápida", "desc": "Aumenta a agilidade\nCusto 20", "preco": 20, "pos": (500, 270), "req": ["A1"]},
    {"id": "A3", "nome": "Exploit de Posição", "desc": "Aumenta o dano de ataque\nCusto 50", "preco": 50, "pos": (500, 390), "req": ["A2"]},
    {"id": "A4", "nome": "Golpe Final", "desc": "Desbloqueia a ultimate do verso\nCusto 100", "preco": 100, "pos": (500, 510), "req": ["A3"]},
]

ARVORE_FEITICEIRO = [
    {"id": "F1", "nome": "Arcano Inicial", "desc": "Aumenta o MP máximo\nCusto 10", "preco": 10, "pos": (500, 150), "req": []},
    {"id": "F2", "nome": "Concentração Mística", "desc": "Aumenta o dano mágico\nCusto 20", "preco": 20, "pos": (500, 270), "req": ["F1"]},
    {"id": "F3", "nome": "Fluxo Arcano", "desc": "Melhora a precisão e controle\nCusto 50", "preco": 50, "pos": (500, 390), "req": ["F2"]},
    {"id": "F4", "nome": "Eclipse Sombrio", "desc": "Desbloqueia a ultimate do verso\nCusto 100", "preco": 100, "pos": (500, 510), "req": ["F3"]},
]

ARVORE_POR_VERSO = {
    "Sobrevivente": ARVORE_SOBREVIVENTE,
    "Agente": ARVORE_AGENTE,
    "Feiticeiro": ARVORE_FEITICEIRO,
}

FUNDO = (25, 30, 42)
PAINEL = (38, 46, 62)
PAINEL_CLARO = (48, 57, 75)
BORDA = (91, 103, 126)
TEXTO = (235, 235, 235)
TEXTO_SECUNDARIO = (180, 190, 205)
AZUL_DESTAQUE = (76, 98, 122)

CORES_VERSO = {
    "Sobrevivente": (189, 118, 52),
    "Agente": (186, 52, 52),
    "Feiticeiro": (128, 78, 168),
}


class GerenciadorVerso:
    def __init__(self, tela):
        self.tela = tela

        self.fonte_titulo = obter_fonte(16)
        self.fonte_desc = obter_fonte(12)

        self.aviso = ""
        self.voltar_clicado = False

        self.pontos = 0
        self.verso_atual = "Sobrevivente"
        self.habilidades_desbloqueadas = []
        self.habilidade_foco = None
        self.arvores_por_verso = {verso: arvore[:] for verso, arvore in ARVORE_POR_VERSO.items()}
        self.versos = ["Sobrevivente", "Agente", "Feiticeiro"]
        self.progresso_por_verso = {verso: [] for verso in self.versos}
        self.sincronizar_habilidades_ativas()

        self.botao_voltar = Botao(720, 700, 240, 50, "VOLTAR", (55, 62, 78), AZUL_DESTAQUE, 250, 55, cor_texto=TEXTO, fonte_tamanho=14)
        self.botao_selecionar = Botao(720, 630, 240, 50, "ESCOLHER VERSO", AZUL_DESTAQUE, (95, 120, 145), 250, 55, cor_texto=TEXTO, fonte_tamanho=14)
        self.botao_confirmar = self.botao_selecionar
        self.botao_comprar = Botao(720, 560, 240, 50, "DESBLOQUEAR", (65, 75, 92), (95, 110, 130), 250, 55, cor_texto=TEXTO, fonte_tamanho=14)

        self.esferas_rects = {
            "Sobrevivente": pygame.Rect(70, 410, 80, 80),
            "Agente": pygame.Rect(190, 410, 80, 80),
            "Feiticeiro": pygame.Rect(130, 545, 80, 80),
        }

    def sincronizar_habilidades_ativas(self):
        self.progresso_por_verso.setdefault(self.verso_atual, [])
        self.habilidades_desbloqueadas = list(self.progresso_por_verso.get(self.verso_atual, []))

    def obter_arvore_ativa(self):
        return self.arvores_por_verso.get(self.verso_atual, self.arvores_por_verso["Sobrevivente"])

    def atualizar_eventos(self, evento, posicao_mouse):
        if self.botao_voltar.checar_clique(evento, posicao_mouse):
            self.voltar_clicado = True
            return None

        if self.botao_selecionar.checar_clique(evento, posicao_mouse):
            return self.verso_atual

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
                        self.progresso_por_verso[self.verso_atual] = list(self.habilidades_desbloqueadas)
                        if self.habilidade_foco["id"] in {"S4", "A4", "F4"}:
                            personagem.ultimates_desbloqueadas = set(getattr(personagem, "ultimates_desbloqueadas", set()))
                            for classe in ["Físico", "Distância", "Magia"]:
                                personagem.ultimates_desbloqueadas.add((self.verso_atual, classe))
                            self.aviso = f"Ultimate desbloqueada para {self.verso_atual}!"
            return None

        if evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            for nome, rect in self.esferas_rects.items():
                if rect.collidepoint(posicao_mouse):
                    self.verso_atual = nome
                    self.sincronizar_habilidades_ativas()
                    self.habilidade_foco = None
                    return None

            for hab in self.obter_arvore_ativa():
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
        txt_carac = self.fonte_desc.render("VERSO", True, TEXTO)
        self.tela.blit(txt_carac, (170 - txt_carac.get_width()//2, 50))

        pygame.draw.circle(self.tela, CORES_VERSO[self.verso_atual], (170, 180), 60)
        pygame.draw.circle(self.tela, (200, 255, 50), (170, 180), 60, 5)

        nome_verso = self.verso_atual.upper()
        txt_nome_verso = self.fonte_desc.render(nome_verso, True, TEXTO)
        self.tela.blit(txt_nome_verso, (170 - txt_nome_verso.get_width()//2, 260))

        pygame.draw.rect(self.tela, PAINEL_CLARO, (40, 320, 260, 440))
        txt_arvores = self.fonte_desc.render("Arvores de Habilidades", True, TEXTO)
        self.tela.blit(txt_arvores, (170 - txt_arvores.get_width()//2, 340))

        destaque_por_verso = {
            "Sobrevivente": (255, 191, 122),
            "Agente": (255, 120, 120),
            "Feiticeiro": (196, 147, 255),
        }

        for nome, rect in self.esferas_rects.items():
            borda = 5 if nome == self.verso_atual else 0
            pygame.draw.circle(self.tela, CORES_VERSO[nome], rect.center, 40)
            if borda:
                pygame.draw.circle(self.tela, destaque_por_verso[nome], rect.center, 40, 5)

        pygame.draw.rect(self.tela, PAINEL, (320, 40, 360, 720))

        arvore_ativa = self.obter_arvore_ativa()

        for hab in arvore_ativa:
            for req_id in hab["req"]:
                for h in arvore_ativa:
                    if h["id"] == req_id:
                        cor_linha = AZUL_DESTAQUE if (hab["id"] in self.habilidades_desbloqueadas) else BORDA
                        pygame.draw.line(self.tela, cor_linha, h["pos"], hab["pos"], 4)

        for hab in arvore_ativa:
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
