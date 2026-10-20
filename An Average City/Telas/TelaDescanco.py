import pygame
from Sistemas.SistemaUI import Botao
from Entidades.Personagem import personagem
from Sistemas.Fontes import obter_fonte
from Sistemas.Inventario import inventario_global
from Sistemas.Conquistas import sistema_conquistas

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
        for indice, atributo in enumerate(("For", "Agi", "Con", "Sab", "Int", "Sor")):
            botao = Botao(890, 195 + indice * 44, 36, 32, "+",
                          (35, 125, 75), (65, 190, 105), 36, 32,
                          cor_texto=(255, 255, 255), fonte_tamanho=14)
            botoes.append((botao, atributo))
        self.botoes_up = botoes
        self.btn_continuar = Botao(self.largura - 260, 715, 220, 48, "CONTINUAR",
                                   (70, 90, 115), (105, 130, 160), 220, 48,
                                   cor_texto=(255, 255, 255), fonte_tamanho=14)

        self.btn_melhorar_equip = Botao(68, 235, 205, 54, "MELHORAR",
                                        (59, 68, 88), (82, 94, 115), 205, 54,
                                        cor_texto=(255, 255, 255), fonte_tamanho=14)

        self.abas_jogadores = []
        self.notificacao_popup = None
        self.notificacao_visivel = False
        self.btn_fechar_popup = None

    def definir_popup_notificacao(self, dados_resultado):
        if not dados_resultado:
            self.notificacao_popup = None
            self.notificacao_visivel = False
            return

        cura = dados_resultado.get("cura", {})
        itens = dados_resultado.get("itens", [])

        contagem_itens = {}
        for item in itens:
            contagem_itens[item] = contagem_itens.get(item, 0) + 1

        lista_itens_formatada = []
        for nome_item, qtd in contagem_itens.items():
            if qtd > 1:
                lista_itens_formatada.append(f"{nome_item} x{qtd}")
            else:
                lista_itens_formatada.append(nome_item)

        hp_curado = cura.get("hp", 0)
        mp_curado = cura.get("mp", 0)

        if hp_curado > 0 or mp_curado > 0:
            texto_cura = f"+{hp_curado} HP  |  +{mp_curado} PM"
        else:
            texto_cura = "+30% HP  |  +3 PM (HP Máximo)"

        self.notificacao_popup = {
            "texto_cura": texto_cura,
            "itens": lista_itens_formatada,
            "hp_curado": hp_curado,
            "mp_curado": mp_curado,
        }
        self.notificacao_visivel = True

    def _retangulos_slots(self):
        inventario = [pygame.Rect(335 + coluna * 78, 218 + linha * 68, 62, 52)
                      for linha in range(4) for coluna in range(3)]
        equipamentos = [pygame.Rect(688 + coluna * 62, 535 + linha * 62, 52, 48)
                        for linha in range(2) for coluna in range(4)]
        return inventario, equipamentos

    def atualizar_eventos(self, evento, posicao_mouse):
        if self.notificacao_visivel and self.btn_fechar_popup and evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            if self.btn_fechar_popup.collidepoint(posicao_mouse):
                self.notificacao_visivel = False
                return None

        if self.btn_continuar.checar_clique(evento, posicao_mouse):
            self.notificacao_visivel = False
            return "continuar"

        if self.btn_melhorar_equip.checar_clique(evento, posicao_mouse):
            alvo_eq = inventario_global.obter_equipamento_alvo()
            custo = inventario_global.custo_melhoria(alvo_eq)
            if alvo_eq and inventario_global.materiais_totais() >= custo:
                inventario_global.consumir_materiais(custo)
                alvo_eq.melhorar()
                self.mensagem = f"{alvo_eq.nome} melhorado!"
                sistema_conquistas.desbloquear("ferreiro")
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
            itens_do_inventario = inventario_global.itens_do_inventario()
            for indice, slot in enumerate(inventario + equipamentos):
                if slot.collidepoint(posicao_mouse):
                    self.slot_selecionado = indice
                    self.mensagem = "Espaço vazio."
                    if indice < len(inventario):
                        if indice < len(itens_do_inventario):
                            item = itens_do_inventario[indice]
                            jogador = self.jogadores[self.jogador_selecionado] if self.jogadores else personagem
                            if getattr(item, "tipo", None) == "material":
                                self.mensagem = f"{item.nome} guardado no inventário para melhoria."
                            elif getattr(item, "tipo", None) == "bilhete" or item.nome == "Bilhete do Dormitório":
                                self.mensagem = f"Bilhete do Dormitório: possui {item.quantidade}. Gasta 1 para dormir."
                            elif getattr(item, "tipo", None) == "polidor" or item.nome == "Polidor de Itens":
                                alvo_eq = inventario_global.obter_equipamento_alvo()
                                if inventario_global.usar_polidor_itens(alvo_eq):
                                    nome_alvo = alvo_eq.nome if alvo_eq else "equipamento"
                                    self.mensagem = f"Usou {item.nome}! Efeito de {nome_alvo} dobrado!"
                                else:
                                    self.mensagem = "Nenhum equipamento para polir!"
                            elif getattr(item, "tipo", None) == "equipamento":
                                if inventario_global.equipar(item):
                                    self.mensagem = f"Equipou {item.nome}!"
                                else:
                                    self.mensagem = f"Não é possível equipar {item.nome} (máx. 3 amuletos sem repetir)!"
                            elif item.quantidade > 0:
                                item.usar(jogador)
                                self.mensagem = f"Usou {item.nome}!"
                                if item.quantidade <= 0:
                                    inventario_global.consumiveis.remove(item)
                    else:
                        eq_idx = indice - len(inventario)
                        slots_eq = inventario_global.obter_slots_equipamento()
                        if 0 <= eq_idx < len(slots_eq):
                            rotulo_slot, eq = slots_eq[eq_idx]
                            if eq is not None:
                                inventario_global.equipamento_selecionado = eq
                                bonus_str = ", ".join(f"+{v} {k}" for k, v in eq.atributos_bonus.items() if v > 0)
                                polido_str = " [Polido]" if getattr(eq, "polido", False) else ""
                                self.mensagem = f"{eq.nome} (+{eq.nivel - 1}){polido_str}" + (f": {bonus_str}" if bonus_str else "")
                            else:
                                self.mensagem = f"Slot {rotulo_slot} vazio."
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
        eq_alvo = inventario_global.obter_equipamento_alvo()
        custo = inventario_global.custo_melhoria(eq_alvo)
        mats = inventario_global.materiais_totais()

        y_attr = 320
        if eq_alvo:
            self.btn_melhorar_equip.texto = f"MELHORAR ({custo} MAT)"
            self.btn_melhorar_equip.desenhar(self.tela)
            sufixo_polido = " [Polido]" if getattr(eq_alvo, "polido", False) else ""
            self.tela.blit(self.fonte_menor.render(f"{eq_alvo.nome} +{eq_alvo.nivel-1}{sufixo_polido}", True, (255, 215, 0)), (68, 300))
            for k, v in eq_alvo.atributos_bonus.items():
                if v > 0:
                    self.tela.blit(self.fonte_menor.render(f"+{v} {k}", True, (150, 255, 150)), (68, y_attr))
                    y_attr += 20
        self.tela.blit(self.fonte_menor.render(f"Materiais disp.: {mats}", True, (200, 200, 200)), (68, y_attr + 15 if eq_alvo else 300))

        self.tela.blit(self.fonte_secao.render("INVENTARIO", True, (235, 220, 170)), (338, 132))
        self.tela.blit(self.fonte_menor.render("Itens carregados", True, (170, 180, 195)), (338, 163))
        inventario, equipamentos = self._retangulos_slots()
        itens_do_inventario = inventario_global.itens_do_inventario()
        for indice, slot in enumerate(inventario):
            cor = (76, 98, 122) if self.slot_selecionado == indice else (38, 46, 62)
            pygame.draw.rect(self.tela, cor, slot)
            pygame.draw.rect(self.tela, (91, 103, 126), slot, 1)

            if indice < len(itens_do_inventario):
                item = itens_do_inventario[indice]
                if getattr(item, "tipo", None) == "material":
                    texto = f"MAT x{item.quantidade}"
                    cor_txt = (255, 220, 130)
                elif getattr(item, "tipo", None) == "bilhete" or item.nome == "Bilhete do Dormitório":
                    texto = f"BILH x{item.quantidade}"
                    cor_txt = (255, 190, 80)
                elif getattr(item, "tipo", None) == "polidor" or item.nome == "Polidor de Itens":
                    texto = f"POL x{item.quantidade}"
                    cor_txt = (130, 235, 255)
                elif getattr(item, "tipo", None) == "equipamento":
                    texto = item.nome[:7]
                    cor_txt = (255, 215, 100)
                else:
                    nome = "HP" if item.rec_hp > 0 else "MP"
                    texto = f"{nome} x{item.quantidade}"
                    cor_txt = (200, 255, 200) if nome == "HP" else (200, 200, 255)
                self.tela.blit(self.fonte_menor.render(texto, True, cor_txt), (slot.x + 5, slot.y + 18))
        self.tela.blit(self.fonte_menor.render(self.mensagem, True, (170, 180, 195)), (338, 505))
        bilhetes = inventario_global.obter_bilhetes_dormitorio()
        self.tela.blit(self.fonte_menor.render(f"Bilhetes de Dormitório: {bilhetes}", True, (255, 215, 120)), (338, 535))

        if self.jogador_selecionado >= len(self.jogadores):
            self.jogador_selecionado = 0
        self.tela.blit(self.fonte_secao.render("ATRIBUTOS", True, (235, 220, 170)), (696, 132))
        self.tela.blit(self.fonte_menor.render(f"Nivel {getattr(jogador, 'nivel', 1)}", True, (180, 190, 205)), (696, 163))
        chaves = ["For", "Agi", "Con", "Sab", "Int", "Sor"]
        nomes = ["Forca", "Agilidade", "Constituicao", "Sabedoria", "Intelecto", "Sorte"]
        for indice, (chave, nome) in enumerate(zip(chaves, nomes)):
            y = 195 + indice * 44
            pygame.draw.rect(self.tela, (59, 68, 88), (696, y, 185, 32))
            valor_base = jogador.atributos.get(chave, 1)
            bonus_eq = inventario_global.obter_bonus_atributo(chave)
            texto_attr = f"{nome}: {valor_base + bonus_eq}" + (f" (+{bonus_eq})" if bonus_eq > 0 else "")
            self.tela.blit(self.fonte_menor.render(texto_attr, True, (235, 235, 235)), (708, y + 9))
            if getattr(jogador, 'pontos_atributo', 0) > 0:
                self.botoes_up[indice][0].desenhar(self.tela)
        pontos = getattr(jogador, 'pontos_atributo', 0)
        self.tela.blit(self.fonte_menor.render(f"Pontos disponiveis: {pontos}", True, (130, 230, 155)), (696, 468))
        self.tela.blit(self.fonte_secao.render("EQUIPAMENTOS", True, (235, 220, 170)), (696, 512))
        slots_eq = inventario_global.obter_slots_equipamento()
        for indice, slot in enumerate(equipamentos):
            slot_indice = len(inventario) + indice
            cor = (76, 98, 122) if self.slot_selecionado == slot_indice else (38, 46, 62)
            pygame.draw.rect(self.tela, cor, slot)
            pygame.draw.rect(self.tela, (91, 103, 126), slot, 1)

            if indice < len(slots_eq):
                rotulo_slot, eq = slots_eq[indice]
                if eq is not None:
                    nome_disp = eq.nome if len(eq.nome) <= 7 else eq.nome[:6] + "."
                    surf_nome = self.fonte_menor.render(nome_disp, True, (255, 215, 0))
                    self.tela.blit(surf_nome, (slot.x + max(2, (slot.width - surf_nome.get_width()) // 2), slot.y + 6))
                    surf_lvl = self.fonte_menor.render(f"+{eq.nivel - 1}", True, (150, 255, 150))
                    self.tela.blit(surf_lvl, (slot.x + max(2, (slot.width - surf_lvl.get_width()) // 2), slot.y + 26))
                else:
                    surf_rot = self.fonte_menor.render(rotulo_slot, True, (105, 115, 135))
                    self.tela.blit(surf_rot, (slot.x + max(2, (slot.width - surf_rot.get_width()) // 2), slot.y + 16))
        self.btn_continuar.desenhar(self.tela)

        if self.notificacao_visivel and self.notificacao_popup:
            self._desenhar_overlay_notificacao()

    def _desenhar_overlay_notificacao(self):
        dados = self.notificacao_popup
        if not dados:
            return

        itens = dados.get("itens", [])
        num_linhas_itens = max(1, len(itens))

        largura_popup = 285
        altura_popup = 74 + (num_linhas_itens * 18)

        x = self.largura - largura_popup - 24
        y = 16

        surf_popup = pygame.Surface((largura_popup, altura_popup), pygame.SRCALPHA)
        surf_popup.fill((22, 28, 42, 245))
        self.tela.blit(surf_popup, (x, y))

        pygame.draw.rect(self.tela, (76, 175, 120), (x, y, largura_popup, altura_popup), width=2, border_radius=8)
        pygame.draw.rect(self.tela, (40, 85, 60), (x + 2, y + 2, largura_popup - 4, 22), border_top_left_radius=6, border_top_right_radius=6)

        txt_titulo = self.fonte_menor.render("FIM DA BATALHA", True, (255, 220, 130))
        self.tela.blit(txt_titulo, (x + 10, y + 6))

        self.btn_fechar_popup = pygame.Rect(x + largura_popup - 22, y + 4, 18, 18)
        txt_x = self.fonte_menor.render("x", True, (210, 210, 210))
        self.tela.blit(txt_x, (self.btn_fechar_popup.x + 4, self.btn_fechar_popup.y + 1))

        txt_cura_label = self.fonte_menor.render("Cura obtida:", True, (160, 220, 180))
        self.tela.blit(txt_cura_label, (x + 10, y + 30))
        txt_cura_val = self.fonte_menor.render(dados.get("texto_cura", "+30% HP / +3 PM"), True, (130, 255, 160))
        self.tela.blit(txt_cura_val, (x + 100, y + 30))

        txt_itens_label = self.fonte_menor.render("Itens obtidos:", True, (255, 215, 120))
        self.tela.blit(txt_itens_label, (x + 10, y + 50))

        y_item = y + 68
        if itens:
            for item in itens:
                txt_item = self.fonte_menor.render(f"- {item}", True, (240, 240, 240))
                self.tela.blit(txt_item, (x + 20, y_item))
                y_item += 18
        else:
            txt_vazio = self.fonte_menor.render("- Nenhum item obtido", True, (170, 180, 195))
            self.tela.blit(txt_vazio, (x + 20, y_item))
