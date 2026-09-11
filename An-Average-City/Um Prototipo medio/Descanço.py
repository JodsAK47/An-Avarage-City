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
        self.btn_dormir = Botao(self.largura - 500, 715, 220, 48, "DORMIR",
                     (80, 110, 70), (110, 150, 90), 220, 48,
                     cor_texto=(255, 255, 255), fonte_tamanho=14)
        
        self.btn_melhorar_equip = Botao(68, 235, 205, 54, "MELHORAR",
                                        (59, 68, 88), (82, 94, 115), 205, 54,
                                        cor_texto=(255, 255, 255), fonte_tamanho=14)
        
        self.abas_jogadores = []

    def _retangulos_slots(self):
        inventario = [pygame.Rect(335 + coluna * 78, 218 + linha * 68, 62, 52)
                      for linha in range(4) for coluna in range(3)]
        equipamentos = [pygame.Rect(688 + coluna * 62, 535 + linha * 62, 52, 48)
                        for linha in range(2) for coluna in range(4)]
        return inventario, equipamentos

    def atualizar_eventos(self, evento, posicao_mouse):
        if self.btn_dormir.checar_clique(evento, posicao_mouse):
            return "dormir"
        if self.btn_continuar.checar_clique(evento, posicao_mouse):
            return "continuar"

        if self.btn_melhorar_equip.checar_clique(evento, posicao_mouse):
            from Inventario import inventario_global
            custo = inventario_global.custo_melhoria()
            if inventario_global.equipamento_slot and inventario_global.materiais_totais() >= custo:
                inventario_global.consumir_materiais(custo)
                inventario_global.equipamento_slot.melhorar()
                self.mensagem = "Equipamento melhorado!"
            else:
                self.mensagem = "Materiais insuficientes!"
            return None

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
                    self.mensagem = "Espaço vazio."
                    if indice < len(inventario):
                        from Inventario import inventario_global
                        if indice < len(inventario_global.consumiveis):
                            c = inventario_global.consumiveis[indice]
                            jogador = self.jogadores[self.jogador_selecionado] if self.jogadores else personagem
                            if c.quantidade > 0:
                                if c.rec_hp > 0: jogador.hp = min(jogador.max_hp, jogador.hp + c.rec_hp)
                                if c.rec_mp > 0: jogador.mp = min(jogador.max_mp, jogador.mp + c.rec_mp)
                                c.quantidade -= 1
                                self.mensagem = f"Usou {c.nome}!"
                                if c.quantidade <= 0:
                                    inventario_global.consumiveis.remove(c)
                    return None

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
        self.btn_dormir.atualizar(posicao_mouse, estado_clique_mouse)
        self.btn_continuar.atualizar(posicao_mouse, estado_clique_mouse)
        self.btn_melhorar_equip.atualizar(posicao_mouse, estado_clique_mouse)
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
        if self.jogador_selecionado >= len(self.jogadores):
            self.jogador_selecionado = 0
        jogador = self.jogadores[self.jogador_selecionado] if self.jogadores else personagem
        self.tela.blit(self.fonte_secao.render("STATUS", True, (235, 220, 170)), (68, 188))
        self.tela.blit(self.fonte_menor.render(
            f"HP: {int(jogador.hp)}/{int(jogador.max_hp)}    PM: {int(jogador.mp)}/{int(jogador.max_mp)}",
            True, (170, 220, 255)), (68, 210))
        from Inventario import inventario_global
        custo = inventario_global.custo_melhoria()
        mats = inventario_global.materiais_totais()
        
        if inventario_global.equipamento_slot:
            self.btn_melhorar_equip.texto = f"MELHORAR ({custo} MAT)"
            self.btn_melhorar_equip.desenhar(self.tela)
            eq = inventario_global.equipamento_slot
            self.tela.blit(self.fonte_menor.render(f"{eq.nome} +{eq.nivel-1}", True, (255, 215, 0)), (68, 300))
            y_attr = 320
            for k, v in eq.atributos_bonus.items():
                if v > 0:
                    self.tela.blit(self.fonte_menor.render(f"+{v} {k}", True, (150, 255, 150)), (68, y_attr))
                    y_attr += 20
        self.tela.blit(self.fonte_menor.render(f"Materiais disp.: {mats}", True, (200, 200, 200)), (68, y_attr + 20 if inventario_global.equipamento_slot else 300))
        self.tela.blit(self.fonte_menor.render("Em desenvolvimento", True, (150, 160, 175)), (68, 565))

        self.tela.blit(self.fonte_secao.render("INVENTARIO", True, (235, 220, 170)), (338, 132))
        self.tela.blit(self.fonte_menor.render("Itens carregados", True, (170, 180, 195)), (338, 163))
        inventario, equipamentos = self._retangulos_slots()
        for indice, slot in enumerate(inventario):
            cor = (76, 98, 122) if self.slot_selecionado == indice else (38, 46, 62)
            pygame.draw.rect(self.tela, cor, slot)
            pygame.draw.rect(self.tela, (91, 103, 126), slot, 1)
            
            from Inventario import inventario_global
            if indice < len(inventario_global.consumiveis):
                c = inventario_global.consumiveis[indice]
                nome = "HP" if c.rec_hp > 0 else "MP"
                cor_txt = (200, 255, 200) if nome=="HP" else (200, 200, 255)
                self.tela.blit(self.fonte_menor.render(f"{nome} x{c.quantidade}", True, cor_txt), (slot.x + 5, slot.y + 18))
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
            
            if indice == 0 and inventario_global.equipamento_slot:
                self.tela.blit(self.fonte_menor.render("EQP", True, (255, 215, 0)), (slot.x + 12, slot.y + 15))

        self.tela.blit(self.fonte_menor.render("+60% HP / +6 PM", True, (170, 200, 175)), (500, 690))
        self.tela.blit(self.fonte_menor.render("+30% HP / +3 PM", True, (180, 190, 205)), (740, 690))
        self.btn_dormir.desenhar(self.tela)
        self.btn_continuar.desenhar(self.tela)
