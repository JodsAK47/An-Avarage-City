
import pygame
import random
from Entidades.Personagem import personagem
from Entidades.Inimigo import obter_inimigos_por_cenario # <-- Importa a lista e não mais os inimigos fixos
from Menu import Botao
from Habilidades import banco_habilidades
from Fontes import obter_fonte

class GerenciadorJogo:
    def __init__(self, tela):
        self.tela = tela
        # Inicialmente apenas o personagem; os inimigos entram quando a fase é escolhida
        self.ordem_turnos = [personagem] 
        
        self.indice_turno = 0
        self.classe_atual = "Nenhuma"
        self.ataque_selecionado = None
        self.botoes_habilidades_dinamicos = []
        self.musica_luta = "Combate.mp3"
        self.xp_calculado = False 
        
        self.turno_jogador_iniciado = False
        self.menu_acoes_estado = "principal"
        self.clique_anterior = False
        self.timer_inimigo = 0
        self.tempo_espera_inimigo = 80 
        
        # VARIÁVEIS DA ESQUIVA
        self.esquiva_x = 0
        self.esquiva_dir = 1
        self.esquiva_vel = 12 
        self.dano_pendente = 0
        self.atacante_nome = ""
        self.efeito_pendente = None         
        self.chance_efeito_pendente = 0.0   
        
        # BOTÕES DA HUD 
        self.btn_ataque    = Botao(220, 640, 120, 50, "ATAQUE", (100,0,0), (150,0,0), 124, 54, cor_texto=(255,255,255), fonte_tamanho=20)
        self.btn_recuperar = Botao(360, 640, 120, 50, "RECUPERAR", (0,100,0), (0,150,0), 124, 54, cor_texto=(255,255,255), fonte_tamanho=18)
        self.btn_bloquear  = Botao(500, 640, 120, 50, "BLOQUEAR", (100,100,0), (150,150,0), 124, 54, cor_texto=(255,255,255), fonte_tamanho=18)
        self.btn_fugir     = Botao(640, 640, 120, 50, "FUGIR", (50,50,50), (100,100,100), 124, 54, cor_texto=(255,255,255), fonte_tamanho=20)
        self.btn_voltar    = Botao(640, 640, 120, 50, "VOLTAR", (80,80,80), (120,120,120), 124, 54, cor_texto=(255,255,255), fonte_tamanho=20)
        
        self.fonte = obter_fonte(22)
        self.fonte_titulos = obter_fonte(18)
        self.mensagem_log = "A batalha começou!"

        # GARANTIA DE STATUS DO JOGADOR
        if not hasattr(personagem, 'nivel'): personagem.nivel = 1
        if not hasattr(personagem, 'xp'): personagem.xp = 0
        if not hasattr(personagem, 'pontos_atributo'): personagem.pontos_atributo = 0
        if not hasattr(personagem, 'atributos'): 
            personagem.atributos = {"For": 1, "Agi": 1, "Con": 1, "Sab": 1, "Int": 1}

    def atualizar_posicoes_inimigos(self):
        inimigos_vivos = [e for e in self.ordem_turnos if e != personagem and e.hp > 0]
        num = len(inimigos_vivos)
        centro_x, centro_y = 750, 400
        
        if num == 1:
            inimigos_vivos[0].rect.center = (centro_x, centro_y)
        elif num == 2:
            inimigos_vivos[0].rect.center = (centro_x, centro_y - 100)
            inimigos_vivos[1].rect.center = (centro_x, centro_y + 100)
        elif num == 3:
            inimigos_vivos[0].rect.center = (centro_x, centro_y - 150)
            inimigos_vivos[1].rect.center = (centro_x, centro_y)
            inimigos_vivos[2].rect.center = (centro_x, centro_y + 150)

    def gerar_botoes_ataque(self):
        self.botoes_habilidades_dinamicos = []
        for i, nome_hab in enumerate(personagem.ataques):
            x = 220 + (i * 140)
            btn = Botao(x, 640, 120, 50, nome_hab.upper()[:10], (0,100,150), (0,150,200), 124, 54, cor_texto=(255,255,255), fonte_tamanho=16)
            self.botoes_habilidades_dinamicos.append({"botao": btn, "nome": nome_hab})

    def configurar_classe(self, nova_classe):
        self.classe_atual = nova_classe
        if nova_classe == "Lutador":
            personagem.ataques = ["Soco", "Terremoto"]
            personagem.atributos["For"] += 3
        elif nova_classe == "Manipulador":
            personagem.ataques = ["Gelo", "Nevasca"]
            personagem.atributos["Int"] += 3
        elif nova_classe == "Arqueiro":
            personagem.ataques = ["Flechada Letal", "Chuva de Flechas"]
            personagem.atributos["Agi"] += 3
        self.gerar_botoes_ataque()

    # ==========================================================
    # CÓDIGO REFATORADO: CARREGA OS INIMIGOS DIRETAMENTE DO BANCO
    # ==========================================================
    def configurar_cenario(self, id_cenario):
        self.musica_luta = "Boss.mp3" if id_cenario == "cenario_4" else "Combate.mp3"
        
        # Pega do novo banco de inimigos!
        inimigos_fase = obter_inimigos_por_cenario(id_cenario)
        self.ordem_turnos = [personagem] + inimigos_fase
        
        if id_cenario == "cenario_1": self.mensagem_log = "🌲 Floresta: Goblins apareceram!"
        elif id_cenario == "cenario_2": self.mensagem_log = "🦇 Caverna: Monstros fortes à vista!"
        elif id_cenario == "cenario_3": self.mensagem_log = "🏛️ Ruínas: Guardiões atacam à distância!"
        elif id_cenario == "cenario_4": self.mensagem_log = "🔥 O COVIL! Enfrentas o Grande Chefe sozinho!"
        
        for ent in self.ordem_turnos:
            ent.hp = ent.max_hp
            ent.mp = getattr(ent, 'max_mp', 0)
            ent.congelado = False
            if not hasattr(ent, 'atributos'): ent.atributos = {"For": 1, "Agi": 1, "Int": 1}
                
        self.indice_turno = 0
        self.atualizar_posicoes_inimigos()

    def reiniciar(self):
        for entidade in self.ordem_turnos:
            entidade.congelado = False
            entidade.hp = entidade.max_hp
            entidade.mp = getattr(entidade, 'max_mp', 0)
            
        # SISTEMA DE INICIATIVA: ORDENA PELA AGILIDADE (Agi)
        self.ordem_turnos.sort(key=lambda e: e.atributos.get("Agi", 0), reverse=True)
        
        personagem.bloqueando = False
        personagem.recuperando = False
        self.turno_jogador_iniciado = False
        self.indice_turno = 0
        self.timer_inimigo = 0
        self.menu_acoes_estado = "principal"
        self.ataque_selecionado = None
        self.xp_calculado = False 
        self.gerar_botoes_ataque()
        self.atualizar_posicoes_inimigos()
        
        primeiro = self.ordem_turnos[0]
        if primeiro == personagem:
            self.mensagem_log = "⚡ Você é o mais rápido! Seu Turno!"
        else:
            self.mensagem_log = f"⚠️ {primeiro.nome} é mais rápido e começa!"

    def avancar_turno(self):
        self.indice_turno += 1
        self.timer_inimigo = 0
        self.turno_jogador_iniciado = False
        self.menu_acoes_estado = "principal"

    def calcular_bonus_atributo(self, atacante, tipo_ataque):
        atributos = getattr(atacante, 'atributos', {})
        if tipo_ataque == "Físico": return atributos.get("For", 0)
        elif tipo_ataque == "Distância": return atributos.get("Agi", 0)
        elif tipo_ataque == "Magia": return atributos.get("Int", 0)
        return 0

    def executar_ataque_jogador(self, nome_habilidade, alvo_principal=None):
        hab = banco_habilidades[nome_habilidade]
        inimigos_vivos = [e for e in self.ordem_turnos if e != personagem and e.hp > 0]
        
        personagem.mp -= hab.custo_mp
        dano_base = hab.dano
        
        if self.classe_atual == "Lutador" and hab.tipo == "Físico": dano_base *= 2
        elif self.classe_atual == "Manipulador" and hab.tipo == "Magia": dano_base *= 2
        elif self.classe_atual == "Arqueiro" and hab.tipo == "Distância": dano_base = int(dano_base * 1.8)

        dano_final = dano_base + self.calcular_bonus_atributo(personagem, hab.tipo)

        critico = False
        if random.random() < 0.05: 
            critico = True
            dano_final = int(dano_final * 1.5) 

        if not critico and random.random() > hab.precisao:
            self.mensagem_log = f"💨 Você tentou {hab.nome}, mas ERROU!"
        else:
            alvos = inimigos_vivos if hab.em_area else [alvo_principal]
            msg = f"🎯 CRÍTICO! " if critico else f"💥 "
            texto_alvo = "EM ÁREA" if hab.em_area else alvo_principal.nome
            msg += f"Usou {hab.nome} {texto_alvo}! ({dano_final} dano)"
            
            for alvo in alvos:
                alvo.hp -= dano_final
                alvo.hp = max(0, alvo.hp)
                
                if hab.efeito and random.random() < hab.chance_efeito:
                    if hab.efeito == "Congelar":
                        alvo.congelado = True
                        if len(alvos) == 1: msg += " CONGELOU!"
                        
            self.mensagem_log = msg

        self.avancar_turno()

    def atualizar(self, mouse_pos, mouse_click):
        self.atualizar_posicoes_inimigos()
        
        inimigos_vivos = [e for e in self.ordem_turnos if e != personagem and e.hp > 0]
        
        if personagem.hp <= 0: 
            return "game_over"
            
        elif not inimigos_vivos: 
            if not self.xp_calculado:
                xp_ganho = sum(getattr(e, 'xp', 0) for e in self.ordem_turnos if e != personagem)
                personagem.xp += xp_ganho
                novo_nivel = (personagem.xp // 100) + 1 
                
                if novo_nivel > personagem.nivel:
                    niveis_ganhos = novo_nivel - personagem.nivel
                    personagem.pontos_atributo += (3 * niveis_ganhos)
                    personagem.nivel = novo_nivel
                    
                self.xp_calculado = True
            return "vitoria"

        if self.indice_turno >= len(self.ordem_turnos): self.indice_turno = 0
        while self.ordem_turnos[self.indice_turno].hp <= 0:
            self.indice_turno += 1
            if self.indice_turno >= len(self.ordem_turnos): 
                self.indice_turno = 0
                break 

        entidade_atual = self.ordem_turnos[self.indice_turno]
        clique_agora = mouse_click[0]
        clicou = not clique_agora and self.clique_anterior
        
        if entidade_atual == personagem:
            if personagem.congelado:
                if self.timer_inimigo == 0: self.mensagem_log = "❄️ Você está CONGELADO e perdeu o turno!"
                self.timer_inimigo += 1
                if self.timer_inimigo >= self.tempo_espera_inimigo:
                    personagem.congelado = False
                    self.avancar_turno()
            else:
                if not self.turno_jogador_iniciado:
                    self.turno_jogador_iniciado = True
                    personagem.bloqueando = False
                    personagem.recuperando = False
                    if personagem.mp < personagem.max_mp:
                        personagem.mp += 1

                if self.menu_acoes_estado == "principal":
                    if "usou" not in self.mensagem_log and "ERROU" not in self.mensagem_log and "falhou" not in self.mensagem_log.lower() and "CRÍTICO" not in self.mensagem_log and "rápido" not in self.mensagem_log:
                        self.mensagem_log = "Seu Turno!"
                    
                    self.btn_ataque.atualizar(mouse_pos, mouse_click)
                    self.btn_recuperar.atualizar(mouse_pos, mouse_click)
                    self.btn_bloquear.atualizar(mouse_pos, mouse_click)
                    self.btn_fugir.atualizar(mouse_pos, mouse_click)
                    
                    if clicou:
                        if self.btn_ataque.clicado(mouse_pos):
                            self.menu_acoes_estado = "ataques"
                        elif self.btn_recuperar.clicado(mouse_pos):
                            personagem.mp = min(personagem.max_mp, personagem.mp + 1)
                            personagem.recuperando = True
                            self.mensagem_log = "🧘 RECUPERAR: +1 PM, mas sofrerá +10% dano!"
                            self.avancar_turno()
                        elif self.btn_bloquear.clicado(mouse_pos):
                            personagem.bloqueando = True
                            self.mensagem_log = "🛡️ BLOQUEAR: Dano reduzido em 50%!"
                            self.avancar_turno()
                        elif self.btn_fugir.clicado(mouse_pos):
                            if random.random() < 0.50:
                                return "fugiu"
                            else:
                                self.mensagem_log = "❌ FUGA falhou!"
                                self.avancar_turno()

                elif self.menu_acoes_estado == "ataques":
                    self.btn_voltar.atualizar(mouse_pos, mouse_click)
                    for item in self.botoes_habilidades_dinamicos:
                        item["botao"].atualizar(mouse_pos, mouse_click)
                        
                    if clicou:
                        if self.btn_voltar.clicado(mouse_pos):
                            self.menu_acoes_estado = "principal"
                        else:
                            for item in self.botoes_habilidades_dinamicos:
                                if item["botao"].clicado(mouse_pos):
                                    hab = banco_habilidades[item["nome"]]
                                    if personagem.mp >= hab.custo_mp:
                                        self.ataque_selecionado = item["nome"]
                                        if hab.em_area:
                                            self.executar_ataque_jogador(item["nome"])
                                        else:
                                            self.menu_acoes_estado = "selecionar_alvo"
                                    else:
                                        self.mensagem_log = f"💧 PM Insuficiente para {hab.nome}!"
                                        self.menu_acoes_estado = "principal"
                                    break

                elif self.menu_acoes_estado == "selecionar_alvo":
                    self.mensagem_log = f"🎯 Escolha o alvo para {self.ataque_selecionado.upper()}!"
                    self.btn_voltar.atualizar(mouse_pos, mouse_click)
                    if clicou:
                        if self.btn_voltar.clicado(mouse_pos):
                            self.menu_acoes_estado = "ataques"
                        else:
                            for alvo in inimigos_vivos:
                                if alvo.rect.collidepoint(mouse_pos):
                                    self.executar_ataque_jogador(self.ataque_selecionado, alvo)
                                    break
                            
        else:
            if self.menu_acoes_estado == "esquivando":
                self.esquiva_x += self.esquiva_vel * self.esquiva_dir
                if self.esquiva_x >= 400 or self.esquiva_x <= 0:
                    self.esquiva_dir *= -1
                    
                if clicou:
                    centro = 200
                    distancia = abs(self.esquiva_x - centro)
                    
                    if distancia < 20: 
                        self.mensagem_log = f"✨ PERFEITO! Anulou ataque e efeitos."
                    else:
                        if distancia < 80: 
                            dano_reduzido = max(1, int(self.dano_pendente * 0.5))
                            personagem.hp -= dano_reduzido
                            msg_base = f"💨 Esquiva parcial! {dano_reduzido} dano."
                        else: 
                            personagem.hp -= self.dano_pendente
                            msg_base = f"❌ Falhou! {self.dano_pendente} dano."
                        
                        personagem.hp = max(0, personagem.hp)
                            
                        if getattr(self, 'efeito_pendente', None) and random.random() < self.chance_efeito_pendente:
                            if self.efeito_pendente == "Congelar":
                                personagem.congelado = True
                                msg_base += " CONGELADO!"
                        self.mensagem_log = msg_base
                    self.avancar_turno()
                    
            else:
                nome_inimigo = entidade_atual.nome
                if entidade_atual.congelado:
                    if self.timer_inimigo == 0: self.mensagem_log = f"❄️ {nome_inimigo} CONGELADO!"
                    self.timer_inimigo += 1
                    if self.timer_inimigo >= self.tempo_espera_inimigo:
                        entidade_atual.congelado = False
                        self.avancar_turno()
                else:
                    self.timer_inimigo += 1
                    if self.timer_inimigo >= self.tempo_espera_inimigo:
                        
                        nome_golpe_inimigo = random.choice(entidade_atual.ataques)
                        hab_usada = banco_habilidades[nome_golpe_inimigo]
                        
                        bonus_inimigo = self.calcular_bonus_atributo(entidade_atual, hab_usada.tipo)
                        dano_inimigo = hab_usada.dano + bonus_inimigo
                        
                        critico = False
                        if random.random() < 0.05:
                            critico = True
                            dano_inimigo = int(dano_inimigo * 1.5)
                        
                        if not critico and random.random() > hab_usada.precisao:
                            self.mensagem_log = f"💨 {nome_inimigo} usou {hab_usada.nome} e ERROU!"
                            self.avancar_turno()
                        else:
                            if personagem.recuperando:
                                dano_inimigo += max(1, int(dano_inimigo * 0.10)) 
                                
                            if personagem.bloqueando:
                                dano_reduzido = max(1, int(dano_inimigo * 0.5))
                                personagem.hp -= dano_reduzido
                                personagem.hp = max(0, personagem.hp)
                                self.mensagem_log = f"🛡️ DEFESA! {dano_reduzido} dano."
                                self.avancar_turno()
                            else:
                                self.menu_acoes_estado = "esquivando"
                                self.dano_pendente = dano_inimigo
                                self.atacante_nome = nome_inimigo
                                self.efeito_pendente = hab_usada.efeito
                                self.chance_efeito_pendente = hab_usada.chance_efeito
                                self.esquiva_x = random.randint(50, 350)
                                self.esquiva_dir = random.choice([-1, 1])
                                
                                if critico:
                                    self.mensagem_log = f"⚠️ CRÍTICO DE {nome_inimigo}! CLIQUE RÁPIDO!"
                                else:
                                    self.mensagem_log = f"⚠️ {nome_inimigo} ataca! CLIQUE PARA ESQUIVAR!"
                    
        self.clique_anterior = clique_agora

    def desenhar_barras_status(self, entidade):
        rect = entidade.rect
        largura_barra = rect.width
        altura_barra = 6
        
        y_hp = rect.bottom + 6
        pygame.draw.rect(self.tela, (80, 10, 10), (rect.x, y_hp, largura_barra, altura_barra))
        if getattr(entidade, 'max_hp', 0) > 0:
            porc = entidade.hp / entidade.max_hp
            pygame.draw.rect(self.tela, (0, 230, 70), (rect.x, y_hp, int(largura_barra * porc), altura_barra))
            
        y_mp = y_hp + altura_barra + 3
        pygame.draw.rect(self.tela, (10, 10, 80), (rect.x, y_mp, largura_barra, altura_barra))
        if getattr(entidade, 'max_mp', 0) > 0:
            porc = entidade.mp / entidade.max_mp
            pygame.draw.rect(self.tela, (0, 160, 255), (rect.x, y_mp, int(largura_barra * porc), altura_barra))

    def desenhar(self):
        self.tela.fill((20, 20, 20))
        
        if personagem.hp > 0: personagem.desenhar(self.tela)
        
        inimigos = [e for e in self.ordem_turnos if e != personagem]
        for ini in inimigos:
            if ini.hp > 0: ini.desenhar(self.tela)
        
        for entidade in self.ordem_turnos:
            if entidade.hp > 0:
                self.desenhar_barras_status(entidade)
        
        mouse_pos = pygame.mouse.get_pos()
        if self.menu_acoes_estado == "selecionar_alvo":
            for alvo in inimigos:
                if alvo.hp > 0 and alvo.rect.collidepoint(mouse_pos):
                    pygame.draw.rect(self.tela, (255, 255, 0), alvo.rect, width=4)
        
        if self.menu_acoes_estado == "esquivando":
            bar_w = 400
            bar_h = 30
            bar_x = (self.tela.get_width() - bar_w) // 2
            bar_y = 480 
            
            pygame.draw.rect(self.tela, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(self.tela, (200, 200, 0), (bar_x + 120, bar_y, 160, bar_h))
            pygame.draw.rect(self.tela, (0, 255, 0), (bar_x + 180, bar_y, 40, bar_h))
            pygame.draw.rect(self.tela, (255, 255, 255), (bar_x, bar_y, bar_w, bar_h), 3)
            pygame.draw.rect(self.tela, (255, 50, 50), (bar_x + self.esquiva_x - 4, bar_y - 10, 8, bar_h + 20))
        
        hud_log = pygame.Rect((self.tela.get_width() - 800) // 2, 20, 800, 60)
        pygame.draw.rect(self.tela, (35, 35, 45), hud_log, border_radius=10)
        pygame.draw.rect(self.tela, (120, 120, 140), hud_log, width=3, border_radius=10)
        texto_surface = self.fonte.render(self.mensagem_log, True, (255, 255, 255))
        self.tela.blit(texto_surface, texto_surface.get_rect(center=hud_log.center))

        hud_acoes = pygame.Rect((self.tela.get_width() - 600) // 2, 600, 600, 110)
        pygame.draw.rect(self.tela, (25, 25, 35), hud_acoes, border_radius=10)
        pygame.draw.rect(self.tela, (150, 150, 170), hud_acoes, width=3, border_radius=10)
        self.tela.blit(self.fonte_titulos.render("BARRA DE AÇÃO", True, (200, 200, 200)), (hud_acoes.x + 15, hud_acoes.y + 8))

        hud_status = pygame.Rect((self.tela.get_width() - 600) // 2, 720, 600, 60)
        pygame.draw.rect(self.tela, (25, 25, 35), hud_status, border_radius=10)
        pygame.draw.rect(self.tela, (100, 100, 120), hud_status, width=3, border_radius=10)
        
        fonte_status = pygame.font.SysFont(["consolas", "courier"], 18, bold=True)
        
        x_hp = hud_status.x + 30
        y_hp = hud_status.y + 25
        w_hp_bar = 160
        h_bar = 14
        pygame.draw.rect(self.tela, (80, 10, 10), (x_hp, y_hp, w_hp_bar, h_bar))
        if personagem.max_hp > 0:
            porc_hp = personagem.hp / personagem.max_hp
            pygame.draw.rect(self.tela, (0, 230, 70), (x_hp, y_hp, int(w_hp_bar * porc_hp), h_bar))
        txt_hp = fonte_status.render(f"HP: {personagem.hp}/{personagem.max_hp}", True, (255, 255, 255))
        self.tela.blit(txt_hp, (x_hp + w_hp_bar + 10, y_hp - 3))

        x_mp = hud_status.x + 330
        y_mp = hud_status.y + 25
        w_mp_bar = 120
        pygame.draw.rect(self.tela, (10, 10, 80), (x_mp, y_mp, w_mp_bar, h_bar))
        if personagem.max_mp > 0:
            porc_mp = personagem.mp / personagem.max_mp
            pygame.draw.rect(self.tela, (0, 160, 255), (x_mp, y_mp, int(w_mp_bar * porc_mp), h_bar))
        txt_mp = fonte_status.render(f"PM: {personagem.mp}/{personagem.max_mp}", True, (255, 255, 255))
        self.tela.blit(txt_mp, (x_mp + w_mp_bar + 10, y_mp - 3))

        indice_seguro = self.indice_turno if self.indice_turno < len(self.ordem_turnos) else 0
        if self.ordem_turnos[indice_seguro] == personagem and not personagem.congelado:
            if self.menu_acoes_estado == "principal":
                self.btn_ataque.desenhar(self.tela)
                self.btn_recuperar.desenhar(self.tela)
                self.btn_bloquear.desenhar(self.tela)
                self.btn_fugir.desenhar(self.tela)
            elif self.menu_acoes_estado == "ataques":
                for item in self.botoes_habilidades_dinamicos:
                    item["botao"].desenhar(self.tela)
                self.btn_voltar.desenhar(self.tela)
            elif self.menu_acoes_estado == "selecionar_alvo":
                self.btn_voltar.desenhar(self.tela)
