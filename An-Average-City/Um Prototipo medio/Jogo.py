
import pygame
import random
from Entidades.Personagem import personagem, Personagem
from Menu import Botao
from Habilidades import banco_habilidades
from Fontes import obter_fonte, quebrar_texto
from GeracaoFases import GeradorFase, BANCO_INIMIGOS, _criar_inimigo_a_partir_template

class GerenciadorJogo:
    def __init__(self, tela):
        self.tela = tela
        self.duas_pessoas = False
        self.personagem2 = None
        self.classe_jogador2 = None
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
        self.evento_neutro = None
        self.fase_numero = 1
        self.gerador_fases = GeradorFase(self.fase_numero)
        self.partida_atual = 1
        self.total_partidas = 9
        self.pontos_jogo = 0

        self.esquiva_x = 0
        self.esquiva_dir = 1
        self.esquiva_vel = 10
        self.barras_esquiva = []
        self.rodada_esquiva = 0
        self.espera_esquiva = 0
        self.total_rodadas_esquiva = 3
        self.acertos_esquiva = 0
        self.acertos_centro_esquiva = 0
        self.reducao_esquiva = 0.0
        self.dano_pendente = 0
        self.atacante_nome = ""
        self.efeito_pendente = None         
        self.chance_efeito_pendente = 0.0   
        
        self.btn_ataque    = Botao(220, 640, 120, 50, "ATAQUE", (100,0,0), (150,0,0), 124, 54, cor_texto=(255,255,255), fonte_tamanho=12)
        self.btn_recuperar = Botao(360, 640, 120, 50, "RECUP", (0,100,0), (0,150,0), 124, 54, cor_texto=(255,255,255), fonte_tamanho=12)
        self.btn_bloquear  = Botao(500, 640, 120, 50, "BLOQ", (100,100,0), (150,150,0), 124, 54, cor_texto=(255,255,255), fonte_tamanho=12)
        self.btn_fugir     = Botao(640, 640, 120, 50, "FUGIR", (50,50,50), (100,100,100), 124, 54, cor_texto=(255,255,255), fonte_tamanho=12)
        self.btn_voltar    = Botao(640, 640, 120, 50, "VOLTAR", (80,80,80), (120,120,120), 124, 54, cor_texto=(255,255,255), fonte_tamanho=12)
        
        self.fonte = obter_fonte(14)
        self.fonte_titulos = obter_fonte(14)
        self.fonte_status = pygame.font.SysFont(["consolas", "courier"], 18, bold=True)
        self.mensagem_log = "A batalha começou!"
        self.ataque_jogador_ativo = None

        if not hasattr(personagem, 'nivel'): personagem.nivel = 1
        if not hasattr(personagem, 'xp'): personagem.xp = 0
        if not hasattr(personagem, 'pontos_atributo'): personagem.pontos_atributo = 0
        if not hasattr(personagem, 'atributos'): 
            personagem.atributos = {"For": 1, "Agi": 1, "Con": 1, "Sab": 1, "Int": 1}

    def _aplicar_classe_personagem2(self):
        if getattr(self, 'personagem2', None) is None:
            return
        classe = getattr(self, 'classe_jogador2', None)
        if not classe:
            return

        # Garante que o bônus seja dado apenas uma vez
        if getattr(self.personagem2, 'classe_aplicada', None) == classe:
            return

        if classe == "Sobrevivente":
            self.personagem2.ataques = ["Soco", "Terremoto"]
            self.personagem2.atributos["For"] = int(self.personagem2.atributos.get("For", 1)) + 3
        elif classe in ("Feiticeiro", "Mago"):
            self.personagem2.ataques = ["Gelo", "Nevasca"]
            self.personagem2.atributos["Int"] = int(self.personagem2.atributos.get("Int", 1)) + 3
        elif classe == "Agente":
            self.personagem2.ataques = ["One Tap", "Spray"]
            self.personagem2.atributos["Agi"] = int(self.personagem2.atributos.get("Agi", 1)) + 3

        self.personagem2.is_player = True
        self.personagem2.classe_aplicada = classe

    def atualizar_posicoes_inimigos(self):
        inimigos_vivos = [entidade for entidade in self.ordem_turnos if not getattr(entidade, 'is_player', False) and entidade.hp > 0]
        quantidade_inimigos = len(inimigos_vivos)
        centro_x_batalha, centro_y_batalha = 750, 400

        if quantidade_inimigos == 1:
            inimigos_vivos[0].rect.center = (centro_x_batalha, centro_y_batalha)
        elif quantidade_inimigos == 2:
            inimigos_vivos[0].rect.center = (centro_x_batalha, centro_y_batalha - 100)
            inimigos_vivos[1].rect.center = (centro_x_batalha, centro_y_batalha + 100)
        elif quantidade_inimigos == 3:
            inimigos_vivos[0].rect.center = (centro_x_batalha, centro_y_batalha - 150)
            inimigos_vivos[1].rect.center = (centro_x_batalha, centro_y_batalha)
            inimigos_vivos[2].rect.center = (centro_x_batalha, centro_y_batalha + 150)

        jogadores_vivos = [entidade for entidade in self.ordem_turnos if getattr(entidade, 'is_player', False) and entidade.hp > 0]
        centro_x_jogador = 250
        if len(jogadores_vivos) == 1:
            jogadores_vivos[0].rect.center = (centro_x_jogador, centro_y_batalha)
        elif len(jogadores_vivos) == 2:
            jogadores_vivos[0].rect.center = (centro_x_jogador, centro_y_batalha - 100)
            jogadores_vivos[1].rect.center = (centro_x_jogador, centro_y_batalha + 100)
            if quantidade_inimigos > 1:
                inimigos_vivos[1].rect.center = (centro_x_batalha, centro_y_batalha + 100)

    def gerar_botoes_ataque(self):
        self.botoes_habilidades_dinamicos = []
        for indice_habilidade, nome_habilidade in enumerate(personagem.ataques):
            posicao_x_botao = 220 + (indice_habilidade * 140)
            botao_habilidade = Botao(posicao_x_botao, 640, 120, 50, nome_habilidade.upper()[:10], (0,100,150), (0,150,200), 124, 54, cor_texto=(255,255,255), fonte_tamanho=11)
            self.botoes_habilidades_dinamicos.append({"botao": botao_habilidade, "nome": nome_habilidade})

    def configurar_classe(self, nova_classe):
        if self.classe_atual != "Nenhuma" and self.classe_atual != nova_classe:
            # Remove o bônus da classe anterior
            if self.classe_atual == "Sobrevivente":
                personagem.atributos["For"] = max(1, personagem.atributos.get("For", 1) - 3)
            elif self.classe_atual in ("Feiticeiro", "Mago"):
                personagem.atributos["Int"] = max(1, personagem.atributos.get("Int", 1) - 3)
            elif self.classe_atual == "Agente":
                personagem.atributos["Agi"] = max(1, personagem.atributos.get("Agi", 1) - 3)

        if self.classe_atual != nova_classe:
            self.classe_atual = nova_classe
            if nova_classe == "Sobrevivente":
                personagem.ataques = ["Soco", "Terremoto"]
                personagem.atributos["For"] = personagem.atributos.get("For", 1) + 3
            elif nova_classe in ("Feiticeiro", "Mago"):
                personagem.ataques = ["Gelo", "Nevasca"]
                personagem.atributos["Int"] = personagem.atributos.get("Int", 1) + 3
            elif nova_classe == "Agente":
                personagem.ataques = ["One Tap", "Spray"]
                personagem.atributos["Agi"] = personagem.atributos.get("Agi", 1) + 3
            self.gerar_botoes_ataque()

    def calcular_pontos_desempenho(self, xp_ganho):
        hp_restante = max(0, int(personagem.hp))
        hp_total = max(1, int(personagem.max_hp))
        hp_bonus = int((hp_restante / hp_total) * 150)
        xp_bonus = int(xp_ganho * 2)
        partida_bonus = self.partida_atual * 75
        return xp_bonus + hp_bonus + partida_bonus

    def configurar_cenario(self, id_cenario):
        self.evento_neutro = None
        self.gerador_fases.fase_num = self.fase_numero

        if self.partida_atual >= self.total_partidas:
            template = random.choice(BANCO_INIMIGOS)
            inimigos_fase = [_criar_inimigo_a_partir_template(template, multiplicador=2.0)]
            self.musica_luta = "Boss.mp3"
            self.mensagem_log = "👑 CHEFE FINAL APARECEU!"
        elif id_cenario.startswith("evento_neutro_"):
            self.fase_numero = int(id_cenario.split("_")[-1])
            self.gerador_fases.fase_num = self.fase_numero
            self.evento_neutro = self.gerador_fases.gerar_evento_neutro(self.fase_numero)
            inimigos_fase = self.gerador_fases.gerar_inimigos_aleatorios(self.fase_numero, quantidade=2)
            self.musica_luta = "Combate.mp3"
            self.mensagem_log = f"⚑ {self.evento_neutro.nome}: {self.evento_neutro.descricao}"
        elif id_cenario == "fase_aleatoria":
            self.fase_numero += 1
            self.gerador_fases.fase_num = self.fase_numero
            fase_gerada = self.gerador_fases.gerar_fase_aleatoria(self.fase_numero)
            self.evento_neutro = fase_gerada.evento
            inimigos_fase = fase_gerada.inimigos
            self.musica_luta = "Boss.mp3" if len(inimigos_fase) == 1 else "Combate.mp3"
            self.mensagem_log = f"🎲 {fase_gerada.nome} - {self.evento_neutro.descricao}"
        else:
            inimigos_fase = []
            self.mensagem_log = "⚠️ Cenário não identificado."
            self.musica_luta = "Combate.mp3"

        self.ordem_turnos = [personagem]
        if getattr(self, 'duas_pessoas', False):
            if self.personagem2 is None:
                self.personagem2 = Personagem(150, 350, "pixil.png")
                setattr(self.personagem2, 'is_player', True)
            self._aplicar_classe_personagem2()
            self.ordem_turnos.append(self.personagem2)

        self.ordem_turnos.extend(inimigos_fase)

        for ent in self.ordem_turnos:
            ent.hp = ent.max_hp
            ent.mp = getattr(ent, 'max_mp', 0)
            ent.congelado = False
            if not hasattr(ent, 'atributos'):
                ent.atributos = {"For": 1, "Agi": 1, "Int": 1}

        self.indice_turno = 0
        self.atualizar_posicoes_inimigos()

    def reiniciar(self):
        inimigos_atuais = [entidade for entidade in self.ordem_turnos if not getattr(entidade, 'is_player', False)]

        if not getattr(self, 'duas_pessoas', False):
            self.personagem2 = None
            self.classe_jogador2 = None
        elif self.personagem2 is None:
            self.personagem2 = Personagem(150, 350, "pixil.png")
            setattr(self.personagem2, 'is_player', True)

        self._aplicar_classe_personagem2()

        self.ordem_turnos = [personagem]
        if getattr(self, 'duas_pessoas', False) and self.personagem2 is not None:
            self.ordem_turnos.append(self.personagem2)
        self.ordem_turnos.extend(inimigos_atuais)

        for entidade in self.ordem_turnos:
            entidade.congelado = False
            entidade.hp = entidade.max_hp
            entidade.mp = getattr(entidade, 'max_mp', 0)
            
        self.ordem_turnos.sort(key=lambda entidade: entidade.atributos.get("Agi", 0), reverse=True)
        
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
        
        primeiro_na_ordem = self.ordem_turnos[0]
        if primeiro_na_ordem == personagem:
            self.mensagem_log = "⚡ Você é o mais rápido! Seu Turno!"
        else:
            self.mensagem_log = f"⚠️ {primeiro_na_ordem.nome} é mais rápido e começa!"

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

    def obter_jogadores(self):
        jogadores = [personagem]
        if getattr(self, 'personagem2', None) is not None:
            jogadores.append(self.personagem2)
        return [jogador for jogador in jogadores if jogador is not None]

    def nome_exibicao(self, entidade):
        if entidade is None:
            return "alvo"
        if hasattr(entidade, 'nome') and entidade.nome:
            return entidade.nome
        if entidade == personagem:
            return "Jogador 1"
        if getattr(self, 'personagem2', None) is not None and entidade == self.personagem2:
            return "Jogador 2"
        return "alvo"

    def classe_do_jogador(self, jogador):
        if jogador == getattr(self, 'personagem2', None):
            return getattr(self, 'classe_jogador2', 'Nenhuma')
        return self.classe_atual

    def velocidade_esquiva(self, entidade):
        agilidade = int(getattr(getattr(entidade, 'atributos', {}), 'get', lambda *args, **kwargs: 1)('Agi', 1))
        reducao = max(0.0, agilidade * 0.001)
        return max(2.5, self.esquiva_vel * (1 - reducao))

    def executar_ataque_jogador(self, nome_habilidade, alvo_principal=None, jogador_ativo=None):
        jogador_ativo = jogador_ativo or personagem
        hab = banco_habilidades[nome_habilidade]
        inimigos_vivos = [entidade for entidade in self.ordem_turnos if not getattr(entidade, 'is_player', False) and entidade.hp > 0]

        jogador_ativo.mp = max(0, jogador_ativo.mp - hab.custo_mp)
        dano_base = hab.dano

        classe_jogador = self.classe_do_jogador(jogador_ativo)
        if classe_jogador == "Sobrevivente" and hab.tipo == "Físico": dano_base *= 2
        elif classe_jogador == "Feiticeiro" and hab.tipo == "Magia": dano_base *= 2
        elif classe_jogador == "Agente" and hab.tipo == "Distância": dano_base = int(dano_base * 1.8)

        dano_final = dano_base + self.calcular_bonus_atributo(jogador_ativo, hab.tipo)

        critico = False
        if random.random() < 0.05:
            critico = True
            dano_final = int(dano_final * 1.5)

        if not critico and random.random() > hab.precisao:
            self.mensagem_log = f"💨 {self.nome_exibicao(jogador_ativo)} tentou {hab.nome}, mas ERROU!"
        else:
            alvos = inimigos_vivos if hab.em_area else [alvo_principal]
            msg = f"🎯 CRÍTICO! " if critico else f"💥 "
            texto_alvo = "EM ÁREA" if hab.em_area else (self.nome_exibicao(alvo_principal) if alvo_principal else "alvo")
            msg += f"{self.nome_exibicao(jogador_ativo)} usou {hab.nome} em {texto_alvo}! ({dano_final} dano)"

            for alvo in alvos:
                alvo.hp -= dano_final
                alvo.hp = max(0, alvo.hp)

                if hab.efeito and random.random() < hab.chance_efeito:
                    if hab.efeito == "Congelar":
                        alvo.congelado = True
                        if len(alvos) == 1: msg += " CONGELOU!"

            self.mensagem_log = msg

        self.avancar_turno()

    def atualizar(self, posicao_mouse, estado_clique_mouse):
        self.atualizar_posicoes_inimigos()

        inimigos_vivos = [entidade for entidade in self.ordem_turnos if not getattr(entidade, 'is_player', False) and entidade.hp > 0]
        jogadores_vivos = [entidade for entidade in self.ordem_turnos if getattr(entidade, 'is_player', False) and entidade.hp > 0]

        if not jogadores_vivos:
            return "game_over"

        if not inimigos_vivos:
            if not self.xp_calculado:
                xp_ganho = sum(getattr(entidade, 'xp', 0) for entidade in self.ordem_turnos if not getattr(entidade, 'is_player', False))
                for jogador_vivo in jogadores_vivos:
                    jogador_vivo.xp += xp_ganho
                    novo_nivel = (jogador_vivo.xp // 100) + 1
                    if novo_nivel > jogador_vivo.nivel:
                        niveis_ganhos = novo_nivel - jogador_vivo.nivel
                        jogador_vivo.pontos_atributo += (3 * niveis_ganhos)
                        jogador_vivo.nivel = novo_nivel

                self.pontos_jogo += self.calcular_pontos_desempenho(xp_ganho)
                self.xp_calculado = True

                if self.partida_atual >= self.total_partidas:
                    self.mensagem_log = f"🏆 CHEFE DERROTADO! Pontos ganhos: {self.pontos_jogo}"
                    return "fim_jogo"

                self.partida_atual += 1
            return "vitoria"

        if self.indice_turno >= len(self.ordem_turnos):
            self.indice_turno = 0
        while self.ordem_turnos[self.indice_turno].hp <= 0:
            self.indice_turno += 1
            if self.indice_turno >= len(self.ordem_turnos):
                self.indice_turno = 0
                break

        entidade_atual = self.ordem_turnos[self.indice_turno]
        clique_agora = estado_clique_mouse[0]
        clicou = not clique_agora and self.clique_anterior

        if entidade_atual == personagem or (getattr(self, 'personagem2', None) is not None and entidade_atual == self.personagem2):
            jogador_atual = entidade_atual
            if jogador_atual.congelado:
                if self.timer_inimigo == 0:
                    self.mensagem_log = "❄️ Você está CONGELADO e perdeu o turno!"
                self.timer_inimigo += 1
                if self.timer_inimigo >= self.tempo_espera_inimigo:
                    jogador_atual.congelado = False
                    self.avancar_turno()
            else:
                if not self.turno_jogador_iniciado:
                    self.turno_jogador_iniciado = True
                    jogador_atual.bloqueando = False
                    jogador_atual.recuperando = False
                    if jogador_atual.mp < jogador_atual.max_mp:
                        jogador_atual.mp += 1

                if self.menu_acoes_estado == "principal":
                    nome_turno = "Seu Turno!" if jogador_atual == personagem else "Turno do Jogador 2!"
                    if "usou" not in self.mensagem_log and "ERROU" not in self.mensagem_log and "falhou" not in self.mensagem_log.lower() and "CRÍTICO" not in self.mensagem_log and "rápido" not in self.mensagem_log:
                        self.mensagem_log = nome_turno

                    self.btn_ataque.atualizar(posicao_mouse, estado_clique_mouse)
                    self.btn_recuperar.atualizar(posicao_mouse, estado_clique_mouse)
                    self.btn_bloquear.atualizar(posicao_mouse, estado_clique_mouse)
                    self.btn_fugir.atualizar(posicao_mouse, estado_clique_mouse)

                    if clicou:
                        if self.btn_ataque.clicado(posicao_mouse):
                            self.menu_acoes_estado = "ataques"
                        elif self.btn_recuperar.clicado(posicao_mouse):
                            jogador_atual.mp = min(jogador_atual.max_mp, jogador_atual.mp + 1)
                            jogador_atual.recuperando = True
                            self.mensagem_log = "🧘 RECUPERAR: +1 PM, mas sofrerá +10% dano!"
                            self.avancar_turno()
                        elif self.btn_bloquear.clicado(posicao_mouse):
                            jogador_atual.bloqueando = True
                            self.mensagem_log = "🛡️ BLOQUEAR: Dano reduzido em 50%!"
                            self.avancar_turno()
                        elif self.btn_fugir.clicado(posicao_mouse):
                            if random.random() < 0.50:
                                return "fugiu"
                            else:
                                self.mensagem_log = "❌ FUGA falhou!"
                                self.avancar_turno()

                elif self.menu_acoes_estado == "ataques":
                    self.btn_voltar.atualizar(posicao_mouse, estado_clique_mouse)
                    for item_habilidade in self.botoes_habilidades_dinamicos:
                        item_habilidade["botao"].atualizar(posicao_mouse, estado_clique_mouse)

                    if clicou:
                        if self.btn_voltar.clicado(posicao_mouse):
                            self.menu_acoes_estado = "principal"
                        else:
                            for item_habilidade in self.botoes_habilidades_dinamicos:
                                if item_habilidade["botao"].clicado(posicao_mouse):
                                    hab = banco_habilidades[item_habilidade["nome"]]
                                    if jogador_atual.mp >= hab.custo_mp:
                                        self.ataque_selecionado = item_habilidade["nome"]
                                        self.ataque_jogador_ativo = jogador_atual
                                        if hab.em_area:
                                            self.executar_ataque_jogador(item_habilidade["nome"], jogador_ativo=jogador_atual)
                                        else:
                                            self.menu_acoes_estado = "selecionar_alvo"
                                    else:
                                        self.mensagem_log = f"💧 PM Insuficiente para {hab.nome}!"
                                        self.menu_acoes_estado = "principal"
                                    break

                elif self.menu_acoes_estado == "selecionar_alvo":
                    self.mensagem_log = f"🎯 Escolha o alvo para {self.ataque_selecionado.upper()}!"
                    self.btn_voltar.atualizar(posicao_mouse, estado_clique_mouse)
                    if clicou:
                        if self.btn_voltar.clicado(posicao_mouse):
                            self.menu_acoes_estado = "ataques"
                        else:
                            for alvo in inimigos_vivos:
                                if alvo.rect.collidepoint(posicao_mouse):
                                    self.executar_ataque_jogador(self.ataque_selecionado, alvo, jogador_ativo=jogador_atual)
                                    break

            self.clique_anterior = clique_agora
            return None

        if self.menu_acoes_estado == "esquivando":
            for barra in self.barras_esquiva:
                if barra["ativa"]:
                    barra["x"] += barra["velocidade"]
                    if barra["x"] >= 400:
                        barra["ativa"] = False
                        self.mensagem_log = "❌ Barra perdida!"
            
            if clicou:
                barras_visiveis = [b for b in self.barras_esquiva if b["ativa"] and b["x"] > 0]
                if barras_visiveis:
                    barra_alvo = max(barras_visiveis, key=lambda b: b["x"])
                    distancia = abs(barra_alvo["x"] - 200)
                    barra_alvo["ativa"] = False
                    
                    if distancia <= 20:
                        self.acertos_centro_esquiva += 1
                        self.reducao_esquiva += 0.33
                        self.mensagem_log = "✨ Centro acertado!"
                    elif distancia <= 80:
                        self.acertos_esquiva += 1
                        self.reducao_esquiva += 0.16
                        self.mensagem_log = "💨 Lateral acertada!"
                    else:
                        self.mensagem_log = "❌ Errou o tempo!"

            if all(not b["ativa"] for b in self.barras_esquiva):
                alvo_esquivando = getattr(self, 'alvo_jogador_pendente', personagem)
                total_acertos = self.acertos_esquiva + self.acertos_centro_esquiva
                condicoes_evitadas = total_acertos == self.total_rodadas_esquiva or self.acertos_centro_esquiva >= (self.total_rodadas_esquiva - 1)
                
                reducao_total = min(0.99, self.reducao_esquiva)
                dano_tomado = max(1, int(self.dano_pendente * (1 - reducao_total)))
                alvo_esquivando.hp = max(0, alvo_esquivando.hp - dano_tomado)

                if condicoes_evitadas:
                    if dano_tomado == 1 and self.dano_pendente > 1:
                        self.mensagem_log = f"✨ Esquiva completa! Apenas {dano_tomado} dano."
                    else:
                        self.mensagem_log = f"💨 Esquiva concluída! {dano_tomado} dano."
                else:
                    msg_base = f"❌ Esquiva incompleta! {dano_tomado} dano."
                    if getattr(self, 'efeito_pendente', None) and random.random() < self.chance_efeito_pendente:
                        if self.efeito_pendente == "Congelar":
                            alvo_esquivando.congelado = True
                            msg_base += " CONGELADO!"
                    self.mensagem_log = msg_base
                self.avancar_turno()
        else:
            nome_inimigo = entidade_atual.nome
            if entidade_atual.congelado:
                if self.timer_inimigo == 0:
                    self.mensagem_log = f"❄️ {nome_inimigo} CONGELADO!"
                self.timer_inimigo += 1
                if self.timer_inimigo >= self.tempo_espera_inimigo:
                    entidade_atual.congelado = False
                    self.avancar_turno()
            else:
                self.timer_inimigo += 1
                if self.timer_inimigo >= self.tempo_espera_inimigo:
                    nome_golpe_inimigo = random.choice(entidade_atual.ataques)
                    hab_usada = banco_habilidades.get(nome_golpe_inimigo) or banco_habilidades["Soco"]

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
                        jogadores_vivos = self.obter_jogadores()
                        alvo_jogador = random.choice(jogadores_vivos)
                        self.alvo_jogador_pendente = alvo_jogador

                        if alvo_jogador.recuperando:
                            dano_inimigo += max(1, int(dano_inimigo * 0.10))

                        if alvo_jogador.bloqueando:
                            dano_reduzido = max(1, int(dano_inimigo * 0.5))
                            alvo_jogador.hp -= dano_reduzido
                            alvo_jogador.hp = max(0, alvo_jogador.hp)
                            self.mensagem_log = f"🛡️ DEFESA de {self.nome_exibicao(alvo_jogador)}! {dano_reduzido} dano."
                            self.avancar_turno()
                        else:
                            self.menu_acoes_estado = "esquivando"
                            self.dano_pendente = dano_inimigo
                            self.atacante_nome = nome_inimigo
                            self.alvo_jogador_pendente = alvo_jogador
                            self.efeito_pendente = hab_usada.efeito
                            self.chance_efeito_pendente = hab_usada.chance_efeito
                            self.barras_esquiva = []
                            espacamento = 180
                            velocidade_base = self.velocidade_esquiva(alvo_jogador)
                            for i in range(self.total_rodadas_esquiva):
                                self.barras_esquiva.append({
                                    "x": random.randint(-20, 0) - (i * espacamento),
                                    "velocidade": velocidade_base + random.randint(-1, 2),
                                    "ativa": True
                                })
                            self.rodada_esquiva = 0
                            self.espera_esquiva = 0
                            self.acertos_esquiva = 0
                            self.acertos_centro_esquiva = 0
                            self.reducao_esquiva = 0.0

                            if critico:
                                self.mensagem_log = f"⚠️ CRÍTICO DE {nome_inimigo}! {self.nome_exibicao(alvo_jogador)} clique rápido!"
                            else:
                                self.mensagem_log = f"⚠️ {nome_inimigo} ataca {self.nome_exibicao(alvo_jogador)}! CLIQUE PARA ESQUIVAR!"

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

    def desenhar(self, posicao_mouse):
        self.tela.fill((20, 20, 20))

        if personagem.hp > 0:
            personagem.desenhar(self.tela)
        if getattr(self, 'duas_pessoas', False) and getattr(self, 'personagem2', None) is not None and self.personagem2.hp > 0:
            self.personagem2.desenhar(self.tela)

        inimigos = [entidade for entidade in self.ordem_turnos if not getattr(entidade, 'is_player', False)]
        for inimigo in inimigos:
            if inimigo.hp > 0: inimigo.desenhar(self.tela)
        
        for entidade in self.ordem_turnos:
            if entidade.hp > 0:
                self.desenhar_barras_status(entidade)
        
        if self.menu_acoes_estado == "selecionar_alvo":
            for alvo in inimigos:
                if alvo.hp > 0 and alvo.rect.collidepoint(posicao_mouse):
                    pygame.draw.rect(self.tela, (255, 255, 0), alvo.rect, width=4)
        
        if self.menu_acoes_estado == "esquivando":
            bar_w = 400
            bar_h = 30
            bar_x = (self.tela.get_width() - bar_w) // 2
            bar_y = 420

            pygame.draw.rect(self.tela, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(self.tela, (200, 200, 0), (bar_x + 120, bar_y, 160, bar_h))
            pygame.draw.rect(self.tela, (0, 255, 0), (bar_x + 180, bar_y, 40, bar_h))
            pygame.draw.rect(self.tela, (255, 255, 255), (bar_x, bar_y, bar_w, bar_h), 3)

            for barra in self.barras_esquiva:
                if not barra["ativa"] or barra["x"] < 0:
                    continue
                pygame.draw.rect(self.tela, (255, 50, 50),
                                 (bar_x + barra["x"] - 4, bar_y - 10, 8, bar_h + 20))
        
        contador_partida = pygame.Rect(30, 25, 170, 42)
        pygame.draw.rect(self.tela, (35, 35, 45), contador_partida, border_radius=10)
        pygame.draw.rect(self.tela, (255, 210, 90), contador_partida, width=3, border_radius=10)
        texto_partida = self.fonte_titulos.render(f"PARTIDA {self.partida_atual}/{self.total_partidas}", True, (255, 255, 255))
        self.tela.blit(texto_partida, (contador_partida.x + 12, contador_partida.y + 10))

        hud_log = pygame.Rect((self.tela.get_width() - 620) // 2, 20, 620, 70)
        pygame.draw.rect(self.tela, (35, 35, 45), hud_log, border_radius=10)
        pygame.draw.rect(self.tela, (120, 120, 140), hud_log, width=3, border_radius=10)
        padding = 12
        linhas = quebrar_texto(self.mensagem_log, self.fonte, hud_log.width - padding*2)
        total_altura = len(linhas) * self.fonte.get_linesize()
        y_inicio = hud_log.y + (hud_log.height - total_altura) // 2
        for indice_linha, linha in enumerate(linhas):
            surf = self.fonte.render(linha, True, (255, 255, 255))
            x = hud_log.x + (hud_log.width - surf.get_width()) // 2
            y = y_inicio + indice_linha * self.fonte.get_linesize()
            self.tela.blit(surf, (x, y))

        hud_acoes = pygame.Rect((self.tela.get_width() - 600) // 2, 600, 600, 110)
        pygame.draw.rect(self.tela, (25, 25, 35), hud_acoes, border_radius=10)
        pygame.draw.rect(self.tela, (150, 150, 170), hud_acoes, width=3, border_radius=10)
        self.tela.blit(self.fonte_titulos.render("BARRA DE AÇÃO", True, (200, 200, 200)), (hud_acoes.x + 15, hud_acoes.y + 8))

        fonte_status = self.fonte_status
        jogadores_status = [personagem]
        if getattr(self, 'duas_pessoas', False) and getattr(self, 'personagem2', None) is not None:
            jogadores_status.append(self.personagem2)

        largura_cartao = 260
        x_base_status = 120
        y_base_status = 720
        for indice, jogador in enumerate(jogadores_status):
            x_cartao = x_base_status + indice * (largura_cartao + 30)
            rect_status = pygame.Rect(x_cartao, y_base_status, largura_cartao, 60)
            pygame.draw.rect(self.tela, (25, 25, 35), rect_status, border_radius=10)
            pygame.draw.rect(self.tela, (100, 100, 120), rect_status, width=3, border_radius=10)

            nome_jogador = "JOGADOR 1" if jogador == personagem else "JOGADOR 2"
            self.tela.blit(fonte_status.render(nome_jogador, True, (255,255,255)), (rect_status.x + 10, rect_status.y + 5))

            x_hp = rect_status.x + 12
            y_hp = rect_status.y + 24
            w_hp_bar = 150
            h_bar = 12
            pygame.draw.rect(self.tela, (80, 10, 10), (x_hp, y_hp, w_hp_bar, h_bar))
            if jogador.max_hp > 0:
                porc_hp = jogador.hp / jogador.max_hp
                pygame.draw.rect(self.tela, (0, 230, 70), (x_hp, y_hp, int(w_hp_bar * porc_hp), h_bar))
            txt_hp = fonte_status.render(f"HP: {jogador.hp}/{jogador.max_hp}", True, (255,255,255))
            self.tela.blit(txt_hp, (x_hp + w_hp_bar + 12, y_hp - 2))

            x_mp = rect_status.x + 12
            y_mp = rect_status.y + 40
            w_mp_bar = 150
            pygame.draw.rect(self.tela, (10, 10, 80), (x_mp, y_mp, w_mp_bar, h_bar))
            if jogador.max_mp > 0:
                porc_mp = jogador.mp / jogador.max_mp
                pygame.draw.rect(self.tela, (0, 160, 255), (x_mp, y_mp, int(w_mp_bar * porc_mp), h_bar))
            txt_mp = fonte_status.render(f"PM: {jogador.mp}/{jogador.max_mp}", True, (255,255,255))
            self.tela.blit(txt_mp, (x_mp + w_mp_bar + 12, y_mp - 2))

        indice_seguro = self.indice_turno if self.indice_turno < len(self.ordem_turnos) else 0
        turno_ativo = self.ordem_turnos[indice_seguro] if self.ordem_turnos else None
        if turno_ativo is not None and turno_ativo in (personagem, getattr(self, 'personagem2', None)) and not turno_ativo.congelado:
            if self.menu_acoes_estado == "principal":
                self.btn_ataque.desenhar(self.tela)
                self.btn_recuperar.desenhar(self.tela)
                self.btn_bloquear.desenhar(self.tela)
                self.btn_fugir.desenhar(self.tela)
            elif self.menu_acoes_estado == "ataques":
                for item_habilidade in self.botoes_habilidades_dinamicos:
                    item_habilidade["botao"].desenhar(self.tela)
                self.btn_voltar.desenhar(self.tela)
            elif self.menu_acoes_estado == "selecionar_alvo":
                self.btn_voltar.desenhar(self.tela)
