import pygame
from Menu import Botao
from Entidades.Personagem import personagem
from Fontes import obter_fonte
class GerenciadorPosLuta:
    def __init__(self, tela):
        self.tela = tela
        self.largura = tela.get_width()
        self.altura = tela.get_height()
        self.jogadores = [personagem]
        self.jogador_selecionado = 0
        self.slot_selecionado = None
        self.mensagem = "Selecione um espaco."

        self.fonte_titulo = obter_fonte(28)
        self.fonte_secao = obter_fonte(16)
        self.fonte_texto = obter_fonte(14)
        self.fonte_menor = obter_fonte(10)

        botoes = []
        for indice, atributo in enumerate(("For", "Agi", "Con", "Sab", "Int")):
            botao = Botao(925, 210 + indice * 52, 36, 36, "+",
                          (35, 125, 75), (65, 190, 105), 36, 36,
                          cor_texto=(255, 255, 255), fonte_tamanho=14)
            botoes.append((botao, atributo))
        self.botoes_up = botoes
        self.btn_continuar = Botao(self.largura - 260, 715, 220, 48, "CONTINUAR",
                                   (70, 90, 115), (105, 130, 160), 220, 48,
                                   cor_texto=(255, 255, 255), fonte_tamanho=14)
        self.abas_jogadores = []

    def _retangulos_slots(self):
        inventario = [pygame.Rect(335 + coluna * 78, 218 + linha * 68, 62, 52)
                      for linha in range(4) for coluna in range(3)]
        equipamentos = [pygame.Rect(688 + coluna * 62, 535 + linha * 62, 52, 48)
                        for linha in range(2) for coluna in range(4)]
        return inventario, equipamentos

    def atualizar_eventos(self, evento, posicao_mouse):
        if self.btn_continuar.checar_clique(evento, posicao_mouse):
            return "continuar"

        if evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            for indice, aba in enumerate(self.abas_jogadores):
                if aba.collidepoint(posicao_mouse):
                    self.jogador_selecionado = indice
                    self.slot_selecionado = None
                    self.mensagem = "Jogador selecionado."
                    return None
            inventario, equipamentos = self._retangulos_slots()
            for indice, slot in enumerate(inventario + equipamentos):
                if slot.collidepoint(posicao_mouse):
                    self.slot_selecionado = indice
                    self.mensagem = "Espaco vazio."
                    return None

        # Proteção contra índice fora do range (ex: saindo do modo 2P)
        if self.jogador_selecionado >= len(self.jogadores):
            self.jogador_selecionado = 0

        jogador = self.jogadores[self.jogador_selecionado] if self.jogadores else personagem
        if getattr(jogador, 'pontos_atributo', 0) > 0:
            for botao_atributo, atributo in self.botoes_up:
                if botao_atributo.checar_clique(evento, posicao_mouse):
                    jogador.atributos[atributo] += 1
                    jogador.pontos_atributo -= 1

                    if atributo == "Con":
                        jogador.max_hp += 10
                        jogador.hp += 10
                    elif atributo == "Sab":
                        jogador.max_mp += 2
                        jogador.mp += 2
                    self.mensagem = f"{atributo} aumentado."
        return None

    def atualizar(self, posicao_mouse, estado_clique_mouse):
        self.btn_continuar.atualizar(posicao_mouse, estado_clique_mouse)
        for botao_atributo, atributo in self.botoes_up:
            botao_atributo.atualizar(posicao_mouse, estado_clique_mouse)

    def desenhar(self):
        self.tela.fill((25, 30, 42))
        pygame.draw.rect(self.tela, (38, 46, 62), (24, 24, self.largura - 48, self.altura - 48))
        self.tela.blit(self.fonte_titulo.render("DESCANSO", True, (240, 220, 150)), (48, 42))

        self.abas_jogadores = []
        for indice, jogador in enumerate(self.jogadores):
            rect = pygame.Rect(300 + indice * 135, 38, 120, 34)
            self.abas_jogadores.append(rect)
            cor = (75, 110, 145) if indice == self.jogador_selecionado else (55, 62, 78)
            pygame.draw.rect(self.tela, cor, rect)
            texto = self.fonte_menor.render(f"JOGADOR {indice + 1}", True, (235, 235, 235))
            self.tela.blit(texto, texto.get_rect(center=rect.center))

        paineis = (pygame.Rect(48, 110, 245, 565), pygame.Rect(315, 110, 335, 565), pygame.Rect(672, 110, 280, 565))
        for painel in paineis:
            pygame.draw.rect(self.tela, (48, 57, 75), painel)
            pygame.draw.rect(self.tela, (91, 103, 126), painel, 2)

        self.tela.blit(self.fonte_secao.render("CRIACAO", True, (235, 220, 170)), (68, 132))
        self.tela.blit(self.fonte_menor.render("Receitas e materiais", True, (170, 180, 195)), (68, 163))
        for indice in range(4):
            rect = pygame.Rect(68, 205 + indice * 82, 205, 58)
            pygame.draw.rect(self.tela, (59, 68, 88), rect)
            pygame.draw.rect(self.tela, (82, 94, 115), rect, 1)
            self.tela.blit(self.fonte_menor.render(f"RECEITA {indice + 1}", True, (185, 190, 205)), (82, rect.y + 12))
            self.tela.blit(self.fonte_menor.render("em breve", True, (125, 135, 150)), (82, rect.y + 34))
        self.tela.blit(self.fonte_menor.render("Em desenvolvimento", True, (150, 160, 175)), (68, 585))

        self.tela.blit(self.fonte_secao.render("INVENTARIO", True, (235, 220, 170)), (338, 132))
        self.tela.blit(self.fonte_menor.render("Itens carregados", True, (170, 180, 195)), (338, 163))
        inventario, equipamentos = self._retangulos_slots()
        for indice, slot in enumerate(inventario):
            cor = (76, 98, 122) if self.slot_selecionado == indice else (38, 46, 62)
            pygame.draw.rect(self.tela, cor, slot)
            pygame.draw.rect(self.tela, (91, 103, 126), slot, 1)
        self.tela.blit(self.fonte_menor.render(self.mensagem, True, (170, 180, 195)), (338, 505))

        if self.jogador_selecionado >= len(self.jogadores):
            self.jogador_selecionado = 0
        jogador = self.jogadores[self.jogador_selecionado] if self.jogadores else personagem
        self.tela.blit(self.fonte_secao.render("ATRIBUTOS", True, (235, 220, 170)), (696, 132))
        self.tela.blit(self.fonte_menor.render(f"Nivel {getattr(jogador, 'nivel', 1)}", True, (180, 190, 205)), (696, 163))
        chaves = ["For", "Agi", "Con", "Sab", "Int"]
        nomes = ["Forca", "Agilidade", "Constituicao", "Sabedoria", "Intelecto"]
        for indice, (chave, nome) in enumerate(zip(chaves, nomes)):
            y = 210 + indice * 52
            pygame.draw.rect(self.tela, (59, 68, 88), (696, y, 185, 36))
            valor = jogador.atributos.get(chave, 1)
            self.tela.blit(self.fonte_menor.render(f"{nome}: {valor}", True, (235, 235, 235)), (708, y + 11))
            if getattr(jogador, 'pontos_atributo', 0) > 0:
                self.botoes_up[indice][0].desenhar(self.tela)
        pontos = getattr(jogador, 'pontos_atributo', 0)
        self.tela.blit(self.fonte_menor.render(f"Pontos disponiveis: {pontos}", True, (130, 230, 155)), (696, 480))
        self.tela.blit(self.fonte_secao.render("EQUIPAMENTOS", True, (235, 220, 170)), (696, 512))
        for indice, slot in enumerate(equipamentos):
            slot_indice = len(inventario) + indice
            cor = (76, 98, 122) if self.slot_selecionado == slot_indice else (38, 46, 62)
            pygame.draw.rect(self.tela, cor, slot)
            pygame.draw.rect(self.tela, (91, 103, 126), slot, 1)

        self.btn_continuar.desenhar(self.tela)
