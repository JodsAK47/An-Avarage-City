import pygame
from Sistemas.SistemaUI import Botao
from Sistemas.Fontes import obter_fonte
from Sistemas.Recursos import caminho_imagem
from Sistemas.SaveSystem import save_global
from Sistemas.Conquistas import sistema_conquistas
from Entidades.Personagem import personagem

# Cores tema Hacker / Esgoto Neon
FUNDO = (14, 18, 22)
PAINEL = (22, 28, 36)
PAINEL_CARD = (30, 38, 48)
VERDE_NEON = (0, 255, 140)
VERDE_ESCURO = (15, 60, 35)
CIANO = (50, 220, 255)
ROXO_NEON = (180, 80, 255)
VERMELHO_ALERTA = (255, 70, 70)
AMARELO_OURO = (255, 215, 60)
TEXTO_CLARO = (240, 245, 250)
TEXTO_CINZA = (150, 165, 180)
BORDA_PAINEL = (45, 60, 75)


class GerenciadorCheatsTela:
    def __init__(self, tela):
        self.tela = tela
        self.fonte_titulo = obter_fonte(20)
        self.fonte_sub = obter_fonte(12)
        self.fonte_botao = obter_fonte(14)
        self.fonte_status = obter_fonte(13)
        self.fonte_mini = obter_fonte(11)

        self.voltar_clicado = False
        self.msg_feedback = "Terminal pronto. Selecione uma função."
        self.cor_feedback = VERDE_NEON

        # Botões principais de Cheats
        self.btn_pontos = Botao(
            60, 140, 390, 50, "+999.999 PONTOS INFINITOS",
            (25, 55, 45), (35, 85, 65), 395, 54,
            cor_texto=VERDE_NEON, fonte_tamanho=13
        )

        self.btn_godmode = Botao(
            60, 210, 390, 50, "GOD MODE: DESATIVADO",
            (50, 30, 60), (75, 40, 95), 395, 54,
            cor_texto=ROXO_NEON, fonte_tamanho=13
        )

        self.btn_conquistas = Botao(
            60, 280, 390, 50, "DESBLOQUEAR TODAS CONQUISTAS",
            (60, 50, 20), (95, 80, 25), 395, 54,
            cor_texto=AMARELO_OURO, fonte_tamanho=13
        )

        self.btn_restaurar = Botao(
            60, 350, 390, 50, "DESATIVAR CHEATS / NORMALIZAR",
            (45, 30, 30), (70, 40, 40), 395, 54,
            cor_texto=VERMELHO_ALERTA, fonte_tamanho=13
        )

        self.btn_voltar = Botao(
            720, 715, 220, 48, "VOLTAR AO MENU",
            (40, 50, 65), (60, 75, 95), 226, 52,
            cor_texto=TEXTO_CLARO, fonte_tamanho=14,
            sprite_base_path="BACK.png", sprite_hover_path="BACK.png", sprite_clique_path="BACK.png"
        )

        # Definição do catálogo de Skins
        self.catalogo_skins = [
            {"nome": "Pixil Clássico", "arquivo": "pixil.png", "desc": "Visual tradicional"},
            {"nome": "Campeão Dourado", "arquivo": "pixil_ouro.png", "desc": "Armadura de Ouro puro"},
            {"nome": "Agente Cibernético", "arquivo": "pixil_cyber.png", "desc": "Tecnologia de ponta neon"},
            {"nome": "Guerreiro Sombrio", "arquivo": "pixil_sombra.png", "desc": "Energia do Vazio"},
            {"nome": "Sukuna (Chefe)", "arquivo": "Sukuna1.png", "desc": "O Rei das Maldições"},
            {"nome": "Maldição Espiritual", "arquivo": "Maldição1.png", "desc": "Espírito amaldiçoado"},
        ]

        self.miniaturas_skins = {}
        self._carregar_miniaturas()

    def _carregar_miniaturas(self):
        for s in self.catalogo_skins:
            try:
                img = pygame.image.load(caminho_imagem(s["arquivo"])).convert_alpha()
                mini = pygame.transform.scale(img, (60, 70))
                grande = pygame.transform.scale(img, (110, 130))
                self.miniaturas_skins[s["arquivo"]] = {"mini": mini, "grande": grande}
            except Exception as e:
                print(f"⚠️ Erro ao carregar miniatura {s['arquivo']}: {e}")

    def atualizar_eventos(self, evento, posicao_mouse):
        if self.btn_voltar.checar_clique(evento, posicao_mouse):
            self.voltar_clicado = True
            return "menu"

        # Clique em Pontos Infinitos
        if self.btn_pontos.checar_clique(evento, posicao_mouse):
            save_global.adicionar_pontos(999999)
            self.msg_feedback = "✓ +999.999 Pontos adicionados com sucesso ao Save!"
            self.cor_feedback = VERDE_NEON

        # Clique em God Mode
        if self.btn_godmode.checar_clique(evento, posicao_mouse):
            personagem.god_mode = not getattr(personagem, 'god_mode', False)
            if personagem.god_mode:
                personagem.max_hp = 999
                personagem.hp = 999
                personagem.max_mp = 99
                personagem.mp = 99
                self.btn_godmode.texto = "GOD MODE: ATIVADO (ON)"
                self.btn_godmode.cor_texto = VERDE_NEON
                self.msg_feedback = "⚡ MODO DEUS ATIVADO! (Invencível + 999 HP + Mana Infinita)"
                self.cor_feedback = VERDE_NEON
            else:
                personagem.max_hp = 100
                personagem.hp = 100
                personagem.max_mp = 10
                personagem.mp = 10
                self.btn_godmode.texto = "GOD MODE: DESATIVADO"
                self.btn_godmode.cor_texto = ROXO_NEON
                self.msg_feedback = "Modo Deus desativado. Vida e mana normalizadas."
                self.cor_feedback = TEXTO_CINZA

        # Clique em Desbloquear Todas Conquistas
        if self.btn_conquistas.checar_clique(evento, posicao_mouse):
            for c in sistema_conquistas.conquistas:
                c.desbloqueada = True
                save_global.desbloquear_conquista(c.id)
            sistema_conquistas.salvar()
            self.msg_feedback = "🏆 Todas as 14 conquistas foram desbloqueadas e salvas!"
            self.cor_feedback = AMARELO_OURO

        # Clique em Restaurar Padrões
        if self.btn_restaurar.checar_clique(evento, posicao_mouse):
            personagem.god_mode = False
            personagem.max_hp = 100
            personagem.hp = 100
            personagem.max_mp = 10
            personagem.mp = 10
            self.btn_godmode.texto = "GOD MODE: DESATIVADO"
            self.btn_godmode.cor_texto = ROXO_NEON
            personagem.trocar_skin("pixil.png")
            self.msg_feedback = "Padrões restaurados (God Mode desativado e skin padrão aplicada)."
            self.cor_feedback = TEXTO_CLARO

        # Clique no seletor de skins
        if evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            x_ini = 510
            y_ini = 270
            for idx, s in enumerate(self.catalogo_skins):
                col = idx % 2
                lin = idx // 2
                rect_skin = pygame.Rect(x_ini + col * 220, y_ini + lin * 110, 205, 95)
                if rect_skin.collidepoint(posicao_mouse):
                    personagem.trocar_skin(s["arquivo"])
                    self.msg_feedback = f"🎭 Skin '{s['nome']}' equipada com sucesso!"
                    self.cor_feedback = CIANO

        return None

    def atualizar(self, posicao_mouse, estado_clique_mouse):
        self.btn_pontos.atualizar(posicao_mouse, estado_clique_mouse)
        self.btn_godmode.atualizar(posicao_mouse, estado_clique_mouse)
        self.btn_conquistas.atualizar(posicao_mouse, estado_clique_mouse)
        self.btn_restaurar.atualizar(posicao_mouse, estado_clique_mouse)
        self.btn_voltar.atualizar(posicao_mouse, estado_clique_mouse)

        # Manter texto do botão de god mode atualizado
        if getattr(personagem, 'god_mode', False):
            self.btn_godmode.texto = "GOD MODE: ATIVADO (ON)"
            self.btn_godmode.cor_texto = VERDE_NEON
        else:
            self.btn_godmode.texto = "GOD MODE: DESATIVADO"
            self.btn_godmode.cor_texto = ROXO_NEON

    def desenhar(self):
        self.tela.fill(FUNDO)

        # Cabeçalho Cyberpunk / Hacker
        pygame.draw.rect(self.tela, PAINEL, (40, 20, 920, 60), border_radius=8)
        pygame.draw.rect(self.tela, VERDE_NEON, (40, 20, 920, 60), width=2, border_radius=8)

        txt_tit = self.fonte_titulo.render("SEWER ACCESS // CONSOLE DE CHEATS", True, VERDE_NEON)
        txt_sub = self.fonte_mini.render("ACESSO RESTRITO - NÍVEL ADMINISTRADOR CONCEDIDO", True, CIANO)
        self.tela.blit(txt_tit, (60, 28))
        self.tela.blit(txt_sub, (60, 56))

        # -------------------------------------------------------------
        # 1. PAINEL DA ESQUERDA: CHEATS GERAIS
        # -------------------------------------------------------------
        rect_painel_esq = pygame.Rect(40, 100, 430, 590)
        pygame.draw.rect(self.tela, PAINEL, rect_painel_esq, border_radius=8)
        pygame.draw.rect(self.tela, BORDA_PAINEL, rect_painel_esq, width=2, border_radius=8)

        lbl_sec1 = self.fonte_status.render("TRAPAÇAS GERAIS", True, VERDE_NEON)
        self.tela.blit(lbl_sec1, (60, 115))

        self.btn_pontos.desenhar(self.tela)
        self.btn_godmode.desenhar(self.tela)
        self.btn_conquistas.desenhar(self.tela)
        self.btn_restaurar.desenhar(self.tela)

        # Painel de Status do Jogador / Save
        rect_status_box = pygame.Rect(60, 430, 390, 240)
        pygame.draw.rect(self.tela, (18, 22, 28), rect_status_box, border_radius=6)
        pygame.draw.rect(self.tela, BORDA_PAINEL, rect_status_box, width=1, border_radius=6)

        lbl_stats = self.fonte_sub.render("STATUS ATUAL DO SISTEMA:", True, CIANO)
        self.tela.blit(lbl_stats, (75, 442))

        gm_ativo = getattr(personagem, 'god_mode', False)
        txt_gm = "ATIVADO (Imortal)" if gm_ativo else "Desativado"
        cor_gm = VERDE_NEON if gm_ativo else TEXTO_CINZA

        linhas_info = [
            (f"• Pontos Salvos: {save_global.obter_pontos()}", VERDE_NEON),
            (f"• Conquistas: {sistema_conquistas.total_desbloqueadas()}/{sistema_conquistas.total_conquistas()}", AMARELO_OURO),
            (f"• Vida Atual: {personagem.hp}/{personagem.max_hp}", VERMELHO_ALERTA if not gm_ativo else VERDE_NEON),
            (f"• Mana Atual: {personagem.mp}/{personagem.max_mp}", CIANO),
            (f"• Modo Deus: {txt_gm}", cor_gm),
            (f"• Member Card: {'Possui (Liberado)' if save_global.tem_member_card() else 'Não Possui'}", VERDE_NEON if save_global.tem_member_card() else VERMELHO_ALERTA),
            (f"• Skin Equipada: {getattr(personagem, 'nome_imagem', 'pixil.png')}", ROXO_NEON),
        ]

        y_lin = 475
        for texto, cor in linhas_info:
            surf_info = self.fonte_mini.render(texto, True, cor)
            self.tela.blit(surf_info, (75, y_lin))
            y_lin += 26

        # -------------------------------------------------------------
        # 2. PAINEL DA DIREITA: SELETOR DE SKINS
        # -------------------------------------------------------------
        rect_painel_dir = pygame.Rect(490, 100, 470, 590)
        pygame.draw.rect(self.tela, PAINEL, rect_painel_dir, border_radius=8)
        pygame.draw.rect(self.tela, BORDA_PAINEL, rect_painel_dir, width=2, border_radius=8)

        lbl_sec2 = self.fonte_status.render("ARMÁRIO DE SKINS DO PERSONAGEM", True, CIANO)
        self.tela.blit(lbl_sec2, (510, 115))

        # Preview da Skin Atual
        frame_preview = pygame.Rect(510, 145, 100, 110)
        pygame.draw.rect(self.tela, (18, 22, 28), frame_preview, border_radius=8)
        pygame.draw.rect(self.tela, CIANO, frame_preview, width=2, border_radius=8)

        skin_atual = getattr(personagem, 'nome_imagem', 'pixil.png')
        if skin_atual in self.miniaturas_skins:
            surf_preview = self.miniaturas_skins[skin_atual]["grande"]
            # Encaixa no frame
            surf_preview_peq = pygame.transform.scale(surf_preview, (80, 95))
            self.tela.blit(surf_preview_peq, (frame_preview.x + 10, frame_preview.y + 7))

        txt_prev_nome = self.fonte_status.render("EQUIPADA AGORA:", True, TEXTO_CINZA)
        self.tela.blit(txt_prev_nome, (625, 160))
        # Encontra o nome amigável
        nome_skin_amigavel = skin_atual
        for s in self.catalogo_skins:
            if s["arquivo"] == skin_atual:
                nome_skin_amigavel = s["nome"]
                break
        txt_skin_lbl = self.fonte_botao.render(nome_skin_amigavel, True, VERDE_NEON)
        self.tela.blit(txt_skin_lbl, (625, 185))
        txt_dica_skin = self.fonte_mini.render("Clique em qualquer skin abaixo para vestir:", True, TEXTO_CINZA)
        self.tela.blit(txt_dica_skin, (625, 218))

        # Grade de Skins (2 colunas x 3 linhas)
        x_ini = 510
        y_ini = 270
        for idx, s in enumerate(self.catalogo_skins):
            col = idx % 2
            lin = idx // 2
            rect_skin = pygame.Rect(x_ini + col * 225, y_ini + lin * 115, 215, 102)

            esta_equipada = (skin_atual == s["arquivo"])
            cor_bg = (30, 42, 54) if esta_equipada else (20, 25, 34)
            cor_borda = VERDE_NEON if esta_equipada else BORDA_PAINEL
            largura_b = 2 if esta_equipada else 1

            pygame.draw.rect(self.tela, cor_bg, rect_skin, border_radius=8)
            pygame.draw.rect(self.tela, cor_borda, rect_skin, width=largura_b, border_radius=8)

            # Miniatura
            if s["arquivo"] in self.miniaturas_skins:
                mini = self.miniaturas_skins[s["arquivo"]]["mini"]
                self.tela.blit(mini, (rect_skin.x + 8, rect_skin.y + 16))

            # Nome e Descrição
            cor_titulo_s = VERDE_NEON if esta_equipada else TEXTO_CLARO
            txt_n = self.fonte_sub.render(s["nome"], True, cor_titulo_s)
            self.tela.blit(txt_n, (rect_skin.x + 72, rect_skin.y + 16))

            txt_d = self.fonte_mini.render(s["desc"], True, TEXTO_CINZA)
            self.tela.blit(txt_d, (rect_skin.x + 72, rect_skin.y + 40))

            if esta_equipada:
                txt_eq = self.fonte_mini.render("● EM USO", True, VERDE_NEON)
                self.tela.blit(txt_eq, (rect_skin.x + 72, rect_skin.y + 68))
            else:
                txt_eq = self.fonte_mini.render("[ USAR ]", True, CIANO)
                self.tela.blit(txt_eq, (rect_skin.x + 72, rect_skin.y + 68))

        # -------------------------------------------------------------
        # 3. BARRA INFERIOR COM MENSAGEM DE FEEDBACK E BOTÃO VOLTAR
        # -------------------------------------------------------------
        pygame.draw.rect(self.tela, (18, 24, 32), (40, 710, 660, 58), border_radius=6)
        pygame.draw.rect(self.tela, BORDA_PAINEL, (40, 710, 660, 58), width=1, border_radius=6)

        txt_prompt = self.fonte_mini.render("> CONSOLE:", True, CIANO)
        self.tela.blit(txt_prompt, (55, 720))

        surf_fb = self.fonte_sub.render(self.msg_feedback, True, self.cor_feedback)
        self.tela.blit(surf_fb, (55, 740))

        self.btn_voltar.desenhar(self.tela)
