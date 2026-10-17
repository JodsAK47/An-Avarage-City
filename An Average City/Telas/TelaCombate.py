
import math
import pygame
import random
from Entidades.Personagem import personagem, Personagem
from Sistemas.SistemaUI import Botao
from Gameplay.Habilidades import banco_habilidades, obter_ultimate
from Sistemas.Fontes import obter_fonte, quebrar_texto
from Gameplay.GeracaoFases import GeradorFase, BANCO_INIMIGOS, _criar_inimigo_a_partir_template, executar_efeito_evento
from Sistemas.Recursos import caminho_imagem
MAPA_ATRIBUTO_CLASSE = {
    "Físico": "For",
    "Fisico": "For",
    "Magia": "Int",
    "Distância": "Agi",
    "Distancia": "Agi",
}

TABELA_EQUIPAMENTOS_INICIAIS = {
    ("Sobrevivente", "Físico"): ("Machado", {"For": 2}),
    ("Sobrevivente", "Fisico"): ("Machado", {"For": 2}),
    ("Sobrevivente", "Distância"): ("Estilingue", {"Agi": 2}),
    ("Sobrevivente", "Distancia"): ("Estilingue", {"Agi": 2}),
    ("Sobrevivente", "Magia"): ("Pedra Preciosa Multicor", {"Int": 2}),
    ("Survivor", "Físico"): ("Machado", {"For": 2}),
    ("Survivor", "Fisico"): ("Machado", {"For": 2}),
    ("Survivor", "Distância"): ("Estilingue", {"Agi": 2}),
    ("Survivor", "Distancia"): ("Estilingue", {"Agi": 2}),
    ("Survivor", "Magia"): ("Pedra Preciosa Multicor", {"Int": 2}),

    ("Agente", "Físico"): ("Faca de Confronto", {"For": 2}),
    ("Agente", "Fisico"): ("Faca de Confronto", {"For": 2}),
    ("Agente", "Distância"): ("Vandal", {"Agi": 2}),
    ("Agente", "Distancia"): ("Vandal", {"Agi": 2}),
    ("Agente", "Magia"): ("Rocha De Radianita", {"Int": 2}),
    ("Agent", "Físico"): ("Faca de Confronto", {"For": 2}),
    ("Agent", "Fisico"): ("Faca de Confronto", {"For": 2}),
    ("Agent", "Distância"): ("Vandal", {"Agi": 2}),
    ("Agent", "Distancia"): ("Vandal", {"Agi": 2}),
    ("Agent", "Magia"): ("Rocha De Radianita", {"Int": 2}),

    ("Feiticeiro", "Físico"): ("Katana", {"For": 2}),
    ("Feiticeiro", "Fisico"): ("Katana", {"For": 2}),
    ("Feiticeiro", "Distância"): ("Amplificador de alcance", {"Agi": 2}),
    ("Feiticeiro", "Distancia"): ("Amplificador de alcance", {"Agi": 2}),
    ("Feiticeiro", "Magia"): ("Ferramenta Amaldiçoada", {"Int": 2}),
    ("Sorcerer", "Físico"): ("Katana", {"For": 2}),
    ("Sorcerer", "Fisico"): ("Katana", {"For": 2}),
    ("Sorcerer", "Distância"): ("Amplificador de alcance", {"Agi": 2}),
    ("Sorcerer", "Distancia"): ("Amplificador de alcance", {"Agi": 2}),
    ("Sorcerer", "Magia"): ("Ferramenta Amaldiçoada", {"Int": 2}),
}

def _obter_equipamento_inicial(verso, classe_dano):
    if (verso, classe_dano) in TABELA_EQUIPAMENTOS_INICIAIS:
        return TABELA_EQUIPAMENTOS_INICIAIS[(verso, classe_dano)]

    v_str = str(verso or "").strip().lower()
    c_str = str(classe_dano or "").strip().lower()

    for (k_v, k_c), item in TABELA_EQUIPAMENTOS_INICIAIS.items():
        if k_v.lower() == v_str and k_c.lower() == c_str:
            return item

    mapa_v = {
        "sobrevivente": "Sobrevivente", "survivor": "Sobrevivente",
        "agente": "Agente", "agent": "Agente",
        "feiticeiro": "Feiticeiro", "sorcerer": "Feiticeiro",
    }
    mapa_c = {
        "fisico": "Físico", "físico": "Físico",
        "distancia": "Distância", "distância": "Distância",
        "magia": "Magia",
    }
    v_norm = mapa_v.get(v_str, verso)
    c_norm = mapa_c.get(c_str, classe_dano)
    return TABELA_EQUIPAMENTOS_INICIAIS.get((v_norm, c_norm), ("Equipamento Padrão", {}))

MULTIPLICADORES_VERSO_TIPO = {
    ("Sobrevivente", "Físico"): 2.0,
    ("Sobrevivente", "Fisico"): 2.0,
    ("Survivor", "Físico"): 2.0,
    ("Survivor", "Fisico"): 2.0,
    ("Feiticeiro", "Magia"): 2.0,
    ("Sorcerer", "Magia"): 2.0,
    ("Agente", "Distância"): 1.8,
    ("Agente", "Distancia"): 1.8,
    ("Agent", "Distância"): 1.8,
    ("Agent", "Distancia"): 1.8,
}

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
        self.multiplicador_recompensa = 1.0
        self.fase_numero = 1
        self.gerador_fases = GeradorFase(self.fase_numero)
        self.partida_atual = 1
        self.total_partidas = 9
        self.pontos_jogo = 0
        self.kills_total = 0
        self.dano_causado_total = 0
        self.dificuldade_total = 0
        self.ultimo_resultado_batalha = None

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

        hud_x = (self.tela.get_width() - 640) // 2
        largura_btn = 125
        gap = 16
        y_btn = 640
        h_btn = 46
        self.btn_ataque    = Botao(hud_x + 25 + 0 * (largura_btn + gap), y_btn, largura_btn, h_btn, "ATAQUE", (140, 25, 25), (190, 40, 40), largura_btn + 4, h_btn + 4, cor_texto=(255,255,255), fonte_tamanho=12)
        self.btn_recuperar = Botao(hud_x + 25 + 1 * (largura_btn + gap), y_btn, largura_btn, h_btn, "RECUP", (25, 120, 45), (40, 170, 65), largura_btn + 4, h_btn + 4, cor_texto=(255,255,255), fonte_tamanho=12)
        self.btn_bloquear  = Botao(hud_x + 25 + 2 * (largura_btn + gap), y_btn, largura_btn, h_btn, "BLOQ", (150, 120, 20), (200, 160, 30), largura_btn + 4, h_btn + 4, cor_texto=(255,255,255), fonte_tamanho=12)
        self.btn_fugir     = Botao(hud_x + 25 + 3 * (largura_btn + gap), y_btn, largura_btn, h_btn, "FUGIR", (60, 60, 75), (95, 95, 115), largura_btn + 4, h_btn + 4, cor_texto=(255,255,255), fonte_tamanho=12)
        self.btn_voltar    = Botao(hud_x + 25 + 3 * (largura_btn + gap), y_btn, largura_btn, h_btn, "VOLTAR", (75, 75, 85), (110, 110, 120), largura_btn + 4, h_btn + 4, cor_texto=(255,255,255), fonte_tamanho=12)

        self.fundo_luta = self._carregar_fundo_luta()
        self.fundo_luta_redimensionado = None
        self.fundo_luta_tamanho = None
        self.tempo_animacao = 0.0

        self.fonte = obter_fonte(14)
        self.fonte_titulos = obter_fonte(14)
        self.fonte_status = pygame.font.SysFont(["consolas", "courier", "arial"], 14, bold=True)
        self.fonte_inimigo = obter_fonte(12)
        self.mensagem_log = "A batalha começou!"
        self.ataque_jogador_ativo = None

        if not hasattr(personagem, 'nivel'): personagem.nivel = 1
        if not hasattr(personagem, 'xp'): personagem.xp = 0
        if not hasattr(personagem, 'pontos_atributo'): personagem.pontos_atributo = 0
        if not hasattr(personagem, 'atributos'): 
            personagem.atributos = {"For": 1, "Agi": 1, "Con": 1, "Sab": 1, "Int": 1, "Sor": 1}

    def _carregar_fundo_luta(self):
        try:
            imagem = pygame.image.load(caminho_imagem("Fight.png"))
            if pygame.display.get_surface() is not None:
                imagem = imagem.convert_alpha()
            return imagem
        except (pygame.error, FileNotFoundError) as e:
            print(f"[Aviso] Nao foi possivel carregar 'Fight.png': {e}")
            return None

    def _atualizar_ataques_jogador(self, jogador, verso, classe_dano):
        if not verso or not classe_dano or verso == "Nenhuma":
            return

        ataques = [
            nome for nome, hab in banco_habilidades.items()
            if hab.verso == verso and hab.tipo == classe_dano and not getattr(hab, 'is_ultimate', False)
        ]

        ultimate = obter_ultimate(verso, classe_dano)
        nodo_req = {"Sobrevivente": "S4", "Agente": "A4", "Feiticeiro": "F4"}.get(verso)
        ultimates_desbloqueadas = set(getattr(jogador, 'ultimates_desbloqueadas', set()))
        talentos_jogador = set(getattr(jogador, 'talentos', set()))

        is_desbloqueada = (
            (nodo_req and nodo_req in talentos_jogador)
            or (verso in ultimates_desbloqueadas)
            or ((verso, classe_dano) in ultimates_desbloqueadas)
            or (ultimate and ultimate.nome in ultimates_desbloqueadas)
        )

        if ultimate and is_desbloqueada:
            if ultimate.nome not in ataques:
                ataques.append(ultimate.nome)

        jogador.ataques = ataques

    def _aplicar_classe_personagem2(self):
        if getattr(self, 'personagem2', None) is None:
            return
        verso = getattr(self, 'classe_jogador2', None)
        classe_dano = getattr(self, 'classe_jogador2_tipo', None)
        if not verso or not classe_dano:
            return

        chave_aplicada = f"{verso}-{classe_dano}"
        if getattr(self.personagem2, 'classe_aplicada', None) == chave_aplicada:
            return

        self._atualizar_ataques_jogador(self.personagem2, verso, classe_dano)

        if attr_classe := MAPA_ATRIBUTO_CLASSE.get(classe_dano):
            self.personagem2.atributos[attr_classe] = int(self.personagem2.atributos.get(attr_classe, 1)) + 3

        self.personagem2.is_player = True
        self.personagem2.classe_aplicada = chave_aplicada

    def atualizar_posicoes_inimigos(self):
        inimigos_vivos = [entidade for entidade in self.ordem_turnos if not getattr(entidade, 'is_player', False) and entidade.hp > 0]
        quantidade_inimigos = len(inimigos_vivos)

        posicoes_inimigos = {
            1: [(740, 400)],
            2: [(670, 335), (780, 465)],
            3: [(770, 315), (635, 400), (770, 485)],
            4: [(630, 325), (790, 325), (630, 475), (790, 475)],
        }

        layout_inimigos = posicoes_inimigos.get(quantidade_inimigos, [(740, 400)] * quantidade_inimigos)
        for inimigo, (px, py) in zip(inimigos_vivos, layout_inimigos):
            inimigo.rect.center = (px, py)

        centro_x_jogadores = 260
        jogadores_vivos = [entidade for entidade in self.ordem_turnos if getattr(entidade, 'is_player', False) and entidade.hp > 0]
        if len(jogadores_vivos) == 1:
            jogadores_vivos[0].rect.center = (centro_x_jogadores, 400)
        elif len(jogadores_vivos) == 2:
            jogadores_vivos[0].rect.center = (centro_x_jogadores, 335)
            jogadores_vivos[1].rect.center = (centro_x_jogadores, 465)

    def gerar_botoes_ataque(self, jogador=None):
        self.botoes_habilidades_dinamicos = []
        alvo = jogador if jogador is not None else personagem
        ataques = list(alvo.ataques)
        total_botoes = len(ataques)

        hud_x = (self.tela.get_width() - 640) // 2
        hud_largura = 640
        y_botoes = 640
        altura_botao = 46

        if total_botoes <= 3:
            largura_btn = 125
            espaco = 16
            inicio_x = hud_x + 25
            for idx, nome_hab in enumerate(ataques):
                bx = inicio_x + idx * (largura_btn + espaco)
                btn = Botao(bx, y_botoes, largura_btn, altura_botao, nome_hab.upper()[:12], (0, 100, 150), (0, 150, 200), largura_btn + 4, altura_botao + 4, cor_texto=(255, 255, 255), fonte_tamanho=11)
                self.botoes_habilidades_dinamicos.append({"botao": btn, "nome": nome_hab})
            self.btn_voltar = Botao(hud_x + hud_largura - largura_btn - 25, y_botoes, largura_btn, altura_botao, "VOLTAR", (75, 75, 85), (110, 110, 120), largura_btn + 4, altura_botao + 4, cor_texto=(255, 255, 255), fonte_tamanho=11)
        else:
            largura_btn = 105
            espaco = 10
            inicio_x = hud_x + 15
            for idx, nome_hab in enumerate(ataques):
                bx = inicio_x + idx * (largura_btn + espaco)
                btn = Botao(bx, y_botoes, largura_btn, altura_botao, nome_hab.upper()[:10], (0, 100, 150), (0, 150, 200), largura_btn + 4, altura_botao + 4, cor_texto=(255, 255, 255), fonte_tamanho=10)
                self.botoes_habilidades_dinamicos.append({"botao": btn, "nome": nome_hab})
            self.btn_voltar = Botao(hud_x + hud_largura - largura_btn - 15, y_botoes, largura_btn, altura_botao, "VOLTAR", (75, 75, 85), (110, 110, 120), largura_btn + 4, altura_botao + 4, cor_texto=(255, 255, 255), fonte_tamanho=10)

    def _custo_habilidade(self, hab, jogador_ativo=None):
        jogador_ativo = jogador_ativo or personagem
        return hab.custo_para(jogador_ativo) if hasattr(hab, "custo_para") else hab.custo_mp

    def configurar_classe(self, novo_verso, nova_classe_dano):
        if getattr(self, "classe_dano_atual", None) and getattr(self, "classe_dano_atual") != nova_classe_dano:
            if attr_antigo := MAPA_ATRIBUTO_CLASSE.get(self.classe_dano_atual):
                personagem.atributos[attr_antigo] = max(1, personagem.atributos.get(attr_antigo, 1) - 3)

        self.classe_atual = novo_verso
        self.classe_dano_atual = nova_classe_dano

        self._atualizar_ataques_jogador(personagem, novo_verso, nova_classe_dano)

        if attr_novo := MAPA_ATRIBUTO_CLASSE.get(nova_classe_dano):
            personagem.atributos[attr_novo] = personagem.atributos.get(attr_novo, 1) + 3

        from Sistemas.Inventario import inventario_global, Equipamento
        eq_nome, eq_attr = _obter_equipamento_inicial(novo_verso, nova_classe_dano)
        inventario_global.equipar(Equipamento(eq_nome, eq_attr))

        self.gerar_botoes_ataque(personagem)

    def calcular_pontos_desempenho(self, xp_ganho=0, dano_causado=0, inimigos_eliminados=0, dificuldade_total=0):
        hp_restante = max(0, int(personagem.hp))
        hp_total = max(1, int(personagem.max_hp))
        hp_bonus = int((hp_restante / hp_total) * 150)

        dano_causado = max(0, int(dano_causado))
        inimigos_eliminados = max(0, int(inimigos_eliminados))
        dificuldade_total = max(0, int(dificuldade_total))

        kill_bonus = inimigos_eliminados * 150
        dano_bonus = int(dano_causado * 0.35)
        dificuldade_bonus = int(dificuldade_total * 0.5)
        xp_bonus = int(xp_ganho * 0.5)
        partida_bonus = self.partida_atual * 50

        return hp_bonus + kill_bonus + dano_bonus + dificuldade_bonus + xp_bonus + partida_bonus

    def configurar_cenario(self, id_cenario, rolagem_forcada=None):
        dados_efeito = None
        self.dados_ultimo_evento = None
        self.evento_neutro = None
        self.multiplicador_recompensa = 1.0
        self.gerador_fases.fase_num = self.fase_numero

        if getattr(self, 'duas_pessoas', False):
            if self.personagem2 is None:
                self.personagem2 = Personagem(150, 350, "pixil.png")
                setattr(self.personagem2, 'is_player', True)
            self._aplicar_classe_personagem2()

        if id_cenario in ("ignorar_evento", "cancelar_evento", "dormir"):
            self.fase_numero += 1
            self.gerador_fases.fase_num = self.fase_numero
            if self.partida_atual >= self.total_partidas:
                chefe = self.gerador_fases.gerar_chefe_verso(self.classe_atual)
                inimigos_fase = [chefe]
                self.musica_luta = "Boss.mp3"
                self.mensagem_log = "👑 CHEFE FINAL APARECEU!"
            else:
                inimigos_fase = self.gerador_fases.gerar_inimigos_aleatorios(self.fase_numero, quantidade=2, verso=self.classe_atual)
                self.musica_luta = "Combate.mp3"
                if id_cenario == "dormir":
                    self.mensagem_log = "💤 Você descansou no dormitório e seguiu para a próxima batalha!"
                else:
                    self.mensagem_log = "⚑ Você ignorou o evento e seguiu para a próxima batalha!"
        elif id_cenario.startswith("evento_acao:") or id_cenario.startswith("evento_neutro_"):
            if id_cenario.startswith("evento_neutro_"):
                prefixo_id = id_cenario.split(":", 1)[0]
                sufixo_num = prefixo_id.split("_")[-1]
                if sufixo_num.isdigit():
                    self.fase_numero = int(sufixo_num)
                else:
                    self.fase_numero += 1
            else:
                self.fase_numero += 1
            self.gerador_fases.fase_num = self.fase_numero
            dados_efeito = executar_efeito_evento(id_cenario, jogo_tela=self, rolagem_forcada=rolagem_forcada)
            self.evento_neutro = dados_efeito["evento"]
            self.multiplicador_recompensa = dados_efeito.get("multiplicador_recompensa", 1.0)
            if self.partida_atual >= self.total_partidas:
                chefe = self.gerador_fases.gerar_chefe_verso(self.classe_atual)
                inimigos_fase = [chefe]
                self.musica_luta = "Boss.mp3"
                self.mensagem_log = f"👑 CHEFE FINAL! {dados_efeito['mensagem']}"
            else:
                inimigos_fase = self.gerador_fases.gerar_inimigos_aleatorios(
                    self.fase_numero,
                    quantidade=dados_efeito["quantidade_inimigos"],
                    verso=self.classe_atual,
                    multiplicador_extra=dados_efeito["multiplicador_forca"],
                )
                self.musica_luta = "Boss.mp3" if len(inimigos_fase) == 1 and self.multiplicador_recompensa > 1.0 else "Combate.mp3"
                self.mensagem_log = dados_efeito["mensagem"]
        elif self.partida_atual >= self.total_partidas:
            chefe = self.gerador_fases.gerar_chefe_verso(self.classe_atual)
            inimigos_fase = [chefe]
            self.musica_luta = "Boss.mp3"
            self.mensagem_log = "👑 CHEFE FINAL APARECEU!"
        else:
            inimigos_fase = []
            self.mensagem_log = "⚠️ Cenário não identificado."
            self.musica_luta = "Combate.mp3"

        self.ordem_turnos = [personagem]
        if getattr(self, 'duas_pessoas', False) and self.personagem2 is not None:
            self.ordem_turnos.append(self.personagem2)

        self.ordem_turnos.extend(inimigos_fase)

        for ent in self.ordem_turnos:
            if not getattr(ent, 'is_player', False):
                ent.hp = ent.max_hp
                ent.mp = getattr(ent, 'max_mp', 0)
            ent.congelado = False
            if not hasattr(ent, 'atributos'):
                ent.atributos = {"For": 1, "Agi": 1, "Int": 1, "Sor": 1}

        self.indice_turno = 0
        self.atualizar_posicoes_inimigos()
        self.dados_ultimo_evento = dados_efeito
        return dados_efeito

    def reiniciar(self):
        inimigos_atuais = [entidade for entidade in self.ordem_turnos if not getattr(entidade, 'is_player', False)]
        if not inimigos_atuais:
            inimigos_atuais = self.gerador_fases.gerar_inimigos_aleatorios(self.fase_numero, quantidade=2, verso=self.classe_atual)

        if not getattr(self, 'duas_pessoas', False):
            self.personagem2 = None
            self.classe_jogador2 = None
        elif self.personagem2 is None:
            self.personagem2 = Personagem(150, 350, "pixil.png")
            setattr(self.personagem2, 'is_player', True)

        if getattr(self, 'classe_atual', 'Nenhuma') != 'Nenhuma' and getattr(self, 'classe_dano_atual', None):
            self._atualizar_ataques_jogador(personagem, self.classe_atual, self.classe_dano_atual)
            from Sistemas.Inventario import inventario_global, Equipamento
            if inventario_global.equipamento_slot is None:
                eq_nome, eq_attr = _obter_equipamento_inicial(self.classe_atual, self.classe_dano_atual)
                inventario_global.equipar(Equipamento(eq_nome, eq_attr))
        self._aplicar_classe_personagem2()

        self.ordem_turnos = [personagem]
        if getattr(self, 'duas_pessoas', False) and self.personagem2 is not None:
            self.ordem_turnos.append(self.personagem2)
        self.ordem_turnos.extend(inimigos_atuais)

        for entidade in self.ordem_turnos:
            entidade.congelado = False
            if not getattr(entidade, 'is_player', False):
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
        self.pontos_salvos_na_partida = False
        self.gerar_botoes_ataque(personagem)
        self.atualizar_posicoes_inimigos()

        if self.evento_neutro is None and "👑" not in self.mensagem_log and "💤" not in self.mensagem_log and "⚑" not in self.mensagem_log:
            primeiro_na_ordem = self.ordem_turnos[0]
            if primeiro_na_ordem == personagem:
                self.mensagem_log = "⚡ Você é o mais rápido! Seu Turno!"
            else:
                self.mensagem_log = f"⚠️ {primeiro_na_ordem.nome} é mais rápido e começa!"

    def calcular_chance_drop_bilhete(self, inimigo):
        tipo = getattr(inimigo, "tipo", "").lower()
        max_hp = getattr(inimigo, "max_hp", 30)
        xp = getattr(inimigo, "xp", 20)
        nome = getattr(inimigo, "nome", "").lower()

        if tipo == "chefe" or "chefe" in nome or "sukuna" in nome or "nemesis" in nome or "comandante supremo" in nome or max_hp >= 120 or xp >= 200:
            return 0.35
        elif tipo == "grande" or "especial" in nome or "aberração" in nome or "gigante" in nome or "mecanoide" in nome or max_hp >= 60 or xp >= 70:
            return 0.20
        elif tipo == "medio" or max_hp >= 40 or xp >= 40:
            return 0.10
        else:
            return 0.05

    def recuperar_apos_batalha(self, dormir=False):
        from Sistemas.Inventario import inventario_global
        dormiu = False
        if dormir:
            if inventario_global.consumir_bilhete_dormitorio(1):
                dormiu = True

        percentual_hp = 0.70 if dormiu else 0.30
        pontos_mp = 7 if dormiu else 3

        cura_info = {
            "hp": 0,
            "mp": 0,
            "percentual_hp": int(percentual_hp * 100),
            "pontos_mp": pontos_mp,
            "dormiu": dormiu,
            "jogadores": []
        }

        for jogador in self.obter_jogadores():
            hp_antes = jogador.hp
            mp_antes = jogador.mp
            jogador.hp = min(jogador.max_hp, jogador.hp + int(jogador.max_hp * percentual_hp))
            jogador.mp = min(jogador.max_mp, jogador.mp + pontos_mp)
            ganho_hp = int(jogador.hp - hp_antes)
            ganho_mp = int(jogador.mp - mp_antes)
            cura_info["hp"] = max(cura_info["hp"], ganho_hp)
            cura_info["mp"] = max(cura_info["mp"], ganho_mp)
            cura_info["jogadores"].append({
                "nome": getattr(jogador, 'nome', 'Jogador'),
                "hp": ganho_hp,
                "mp": ganho_mp
            })
        return cura_info

    def avancar_turno(self):
        self.indice_turno += 1
        self.timer_inimigo = 0
        self.turno_jogador_iniciado = False
        self.menu_acoes_estado = "principal"

    def calcular_bonus_atributo(self, atacante, tipo_ataque):
        attr = MAPA_ATRIBUTO_CLASSE.get(tipo_ataque)
        if not attr:
            return 0
        bonus = getattr(atacante, 'atributos', {}).get(attr, 0)
        if getattr(atacante, 'is_player', False):
            from Sistemas.Inventario import inventario_global
            if eq := inventario_global.equipamento_slot:
                bonus += eq.atributos_bonus.get(attr, 0)
        return bonus

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

    def tem_talento(self, entidade, id_talento):
        if not entidade or not getattr(entidade, 'is_player', False):
            return False
        if hasattr(entidade, 'tem_talento'):
            return entidade.tem_talento(id_talento)
        return id_talento in getattr(entidade, 'talentos', set())

    def velocidade_esquiva(self, entidade):
        agilidade = int(getattr(getattr(entidade, 'atributos', {}), 'get', lambda *args, **kwargs: 1)('Agi', 1))
        reducao = max(0.0, agilidade * 0.001)
        vel = max(2.5, self.esquiva_vel * (1 - reducao))
        if self.tem_talento(entidade, "A3"):
            vel = max(2.0, vel * 0.85)
        return vel

    def executar_ataque_jogador(self, nome_habilidade, alvo_principal=None, jogador_ativo=None):
        jogador_ativo = jogador_ativo or personagem
        hab = banco_habilidades[nome_habilidade]
        inimigos_vivos = [entidade for entidade in self.ordem_turnos if not getattr(entidade, 'is_player', False) and entidade.hp > 0]
        custo_mp = self._custo_habilidade(hab, jogador_ativo)

        jogador_ativo.mp = max(0, jogador_ativo.mp - custo_mp)
        dano_base = hab.dano

        classe_jogador = self.classe_do_jogador(jogador_ativo)
        mult_verso = MULTIPLICADORES_VERSO_TIPO.get((classe_jogador, hab.tipo), 1.0)
        dano_base = int(dano_base * mult_verso)

        dano_final = dano_base + self.calcular_bonus_atributo(jogador_ativo, hab.tipo)

        tem_a2 = self.tem_talento(jogador_ativo, "A2")
        chance_crit_base = 0.15 if tem_a2 else 0.05
        sorte_jogador = getattr(jogador_ativo, "atributos", {}).get("Sor", 1)
        chance_crit = min(1.0, chance_crit_base + (sorte_jogador * 0.001))
        mult_crit = 3.0 if tem_a2 else 1.5

        critico = False
        if getattr(jogador_ativo, 'god_mode', False):
            critico = True
            dano_final = max(dano_final, 9999)
        elif random.random() < chance_crit:
            critico = True
            dano_final = int(dano_final * mult_crit)
            from Sistemas.Conquistas import sistema_conquistas
            sistema_conquistas.desbloquear("critico_devastador")

        precisao_final = 1.0 if getattr(jogador_ativo, 'god_mode', False) else hab.precisao
        if self.tem_talento(jogador_ativo, "A1"):
            precisao_final = min(1.0, precisao_final + 0.05)

        if not critico and random.random() > precisao_final:
            self.mensagem_log = f"💨 {self.nome_exibicao(jogador_ativo)} tentou {hab.nome}, mas ERROU!"
        else:
            alvos = inimigos_vivos if hab.em_area else [alvo_principal]
            msg = f"⚡ GOD MODE! " if getattr(jogador_ativo, 'god_mode', False) else (f"🎯 CRÍTICO! " if critico else f"💥 ")
            texto_alvo = "EM ÁREA" if hab.em_area else (self.nome_exibicao(alvo_principal) if alvo_principal else "alvo")
            msg += f"{self.nome_exibicao(jogador_ativo)} usou {hab.nome} em {texto_alvo}! ({dano_final} dano)"

            for alvo in alvos:
                alvo.hp -= dano_final
                alvo.hp = max(0, alvo.hp)

                if getattr(jogador_ativo, 'is_player', False):
                    self.dano_causado_total += int(dano_final)
                    if alvo.hp <= 0:
                        self.kills_total += 1
                        self.dificuldade_total += max(1, int(getattr(alvo, 'xp', 0)))
                        from Sistemas.Conquistas import sistema_conquistas
                        sistema_conquistas.desbloquear("primeiro_sangue")

                if hab.efeito and random.random() < hab.chance_efeito:
                    if hab.efeito == "Congelar":
                        alvo.congelado = True
                        if len(alvos) == 1: msg += " CONGELOU!"

            self.mensagem_log = msg
            self.pontos_jogo = self.calcular_pontos_desempenho(
                xp_ganho=sum(getattr(entidade, 'xp', 0) for entidade in self.ordem_turnos if not getattr(entidade, 'is_player', False) and entidade.hp <= 0),
                dano_causado=self.dano_causado_total,
                inimigos_eliminados=self.kills_total,
                dificuldade_total=self.dificuldade_total,
            )

        self.avancar_turno()

    def atualizar(self, posicao_mouse, estado_clique_mouse):
        self.tempo_animacao += 0.04
        self.atualizar_posicoes_inimigos()

        for j in self.obter_jogadores():
            if getattr(j, 'god_mode', False):
                j.hp = j.max_hp
                j.mp = j.max_mp
                j.congelado = False

        inimigos_vivos = [entidade for entidade in self.ordem_turnos if not getattr(entidade, 'is_player', False) and entidade.hp > 0]
        jogadores_vivos = [entidade for entidade in self.ordem_turnos if getattr(entidade, 'is_player', False) and entidade.hp > 0]

        if not jogadores_vivos:
            self.pontos_jogo = self.calcular_pontos_desempenho(
                xp_ganho=sum(getattr(entidade, 'xp', 0) for entidade in self.ordem_turnos if not getattr(entidade, 'is_player', False) and entidade.hp <= 0),
                dano_causado=self.dano_causado_total,
                inimigos_eliminados=self.kills_total,
                dificuldade_total=self.dificuldade_total,
            )
            return "game_over"

        if not inimigos_vivos:
            if not self.xp_calculado:
                multiplicador_rec = getattr(self, "multiplicador_recompensa", 1.0)
                xp_base = sum(getattr(entidade, 'xp', 0) for entidade in self.ordem_turnos if not getattr(entidade, 'is_player', False))
                xp_ganho = int(xp_base * multiplicador_rec)
                jogadores_participantes = [entidade for entidade in self.ordem_turnos if getattr(entidade, 'is_player', False)]
                for jogador in jogadores_participantes:
                    jogador.xp += xp_ganho
                    novo_nivel = (jogador.xp // 100) + 1
                    if novo_nivel > jogador.nivel:
                        niveis_ganhos = novo_nivel - jogador.nivel
                        jogador.pontos_atributo += (3 * niveis_ganhos)
                        jogador.nivel = novo_nivel

                self.pontos_jogo += int(self.calcular_pontos_desempenho(xp_ganho) * multiplicador_rec)
                self.xp_calculado = True

                from Sistemas.Conquistas import sistema_conquistas
                if self.classe_atual == "Sobrevivente":
                    sistema_conquistas.desbloquear("vitoria_sobrevivente")
                elif self.classe_atual == "Agente":
                    sistema_conquistas.desbloquear("vitoria_agente")
                elif self.classe_atual == "Feiticeiro":
                    sistema_conquistas.desbloquear("vitoria_feiticeiro")

                from Sistemas.Inventario import inventario_global
                inimigos_derrotados = [e for e in self.ordem_turnos if not getattr(e, 'is_player', False)]
                drop_msg = []
                itens_obtidos = []
                for inimigo in inimigos_derrotados:
                    if random.random() < 0.3:
                        inventario_global.adicionar_consumivel("Poção de Vida", "Restaura 30 HP", 30, 0)
                        drop_msg.append("Vida")
                        itens_obtidos.append("Poção de Vida")
                    elif random.random() < 0.2:
                        inventario_global.adicionar_consumivel("Poção de Mana", "Restaura 10 MP", 0, 10)
                        drop_msg.append("Mana")
                        itens_obtidos.append("Poção de Mana")
                    if random.random() < 0.4:
                        inventario_global.adicionar_material("Sucata", "Melhora equips.")
                        drop_msg.append("Sucata")
                        itens_obtidos.append("Sucata")

                    chance_bilhete = self.calcular_chance_drop_bilhete(inimigo)
                    if random.random() < chance_bilhete:
                        inventario_global.adicionar_bilhete_dormitorio(1)
                        drop_msg.append("Bilhete Dormitório")
                        itens_obtidos.append("Bilhete do Dormitório")

                if drop_msg:
                    self.mensagem_log = f"🎁 Drops: {', '.join(drop_msg)}"

                cura_info = self.recuperar_apos_batalha(dormir=False)
                self.ultimo_resultado_batalha = {
                    "cura": cura_info,
                    "itens": itens_obtidos,
                    "xp": xp_ganho
                }

                if self.partida_atual >= self.total_partidas:
                    sistema_conquistas.desbloquear("chefe_derrotado")
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
                        ganho_passivo = 2 if self.tem_talento(jogador_atual, "F1") else 1
                        jogador_atual.mp = min(jogador_atual.max_mp, jogador_atual.mp + ganho_passivo)
                manipuladores_menu = {
                    "principal": lambda: self._processar_menu_principal(jogador_atual, posicao_mouse, estado_clique_mouse, clicou),
                    "ataques": lambda: self._processar_menu_ataques(jogador_atual, posicao_mouse, estado_clique_mouse, clicou),
                    "selecionar_alvo": lambda: self._processar_menu_selecionar_alvo(jogador_atual, posicao_mouse, estado_clique_mouse, clicou, inimigos_vivos),
                }
                if manipulador := manipuladores_menu.get(self.menu_acoes_estado):
                    if resultado_menu := manipulador():
                        return resultado_menu

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
                if getattr(alvo_esquivando, 'god_mode', False):
                    dano_tomado = 0
                alvo_esquivando.hp = max(0, alvo_esquivando.hp - dano_tomado)

                if condicoes_evitadas:
                    if self.acertos_centro_esquiva >= 2:
                        from Sistemas.Conquistas import sistema_conquistas
                        sistema_conquistas.desbloquear("mestre_esquiva")
                    if dano_tomado == 1 and self.dano_pendente > 1:
                        self.mensagem_log = f"✨ Esquiva completa! Apenas {dano_tomado} dano."
                    else:
                        self.mensagem_log = f"💨 Esquiva concluída! {dano_tomado} dano."
                else:
                    msg_base = f"❌ Esquiva incompleta! {dano_tomado} dano."
                    if getattr(self, 'efeito_pendente', None) and random.random() < self.chance_efeito_pendente:
                        if self.tem_talento(alvo_esquivando, "S3"):
                            msg_base += " (Imune a efeitos!)"
                        elif self.efeito_pendente == "Congelar":
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
                    ataques_possiveis = [a for a in entidade_atual.ataques if entidade_atual.obter_habilidade(a).custo_mp <= entidade_atual.mp]
                    if not ataques_possiveis:
                        ataques_possiveis = ["Soco" if "Soco" in entidade_atual.ataques else "Mordida"]

                    nome_golpe_inimigo = random.choice(ataques_possiveis)
                    hab_usada = entidade_atual.obter_habilidade(nome_golpe_inimigo)

                    entidade_atual.mp -= hab_usada.custo_mp
                    entidade_atual.mp = max(0, entidade_atual.mp)
                    if entidade_atual.mp == 0:
                        from Sistemas.Conquistas import sistema_conquistas
                        sistema_conquistas.desbloquear("mana_esgotada")

                    bonus_inimigo = self.calcular_bonus_atributo(entidade_atual, hab_usada.tipo)
                    dano_inimigo = hab_usada.dano + bonus_inimigo

                    sorte_inimigo = getattr(entidade_atual, "atributos", {}).get("Sor", 1)
                    chance_crit_inimigo = min(1.0, 0.05 + (sorte_inimigo * 0.001))
                    critico = False
                    if random.random() < chance_crit_inimigo:
                        critico = True
                        dano_inimigo = int(dano_inimigo * 1.5)

                    jogadores_vivos = self.obter_jogadores()
                    alvo_jogador = random.choice(jogadores_vivos)
                    self.alvo_jogador_pendente = alvo_jogador

                    precisao_inimigo = hab_usada.precisao
                    if self.tem_talento(alvo_jogador, "A3"):
                        precisao_inimigo = max(0.15, precisao_inimigo - 0.20)

                    if not critico and random.random() > precisao_inimigo:
                        self.mensagem_log = f"💨 {nome_inimigo} usou {hab_usada.nome} em {self.nome_exibicao(alvo_jogador)}, mas ERROU!"
                        self.avancar_turno()
                    else:

                        if alvo_jogador.recuperando:
                            dano_inimigo += max(1, int(dano_inimigo * 0.10))

                        if alvo_jogador.bloqueando:
                            dano_reduzido = max(1, int(dano_inimigo * 0.5))
                            if getattr(alvo_jogador, 'god_mode', False):
                                dano_reduzido = 0
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

    def _desenhar_sombra_contato(self, entidade, deslocamento_y=0):
        if not entidade or getattr(entidade, 'hp', 0) <= 0:
            return
        rect = entidade.rect
        largura_sombra = max(34, int(rect.width * 0.72))
        altura_sombra = 14
        sombra_surf = pygame.Surface((largura_sombra, altura_sombra), pygame.SRCALPHA)
        pygame.draw.ellipse(sombra_surf, (0, 0, 0, 115), (0, 0, largura_sombra, altura_sombra))
        x_sombra = rect.centerx - (largura_sombra // 2)
        y_sombra = rect.bottom - 7 + int(deslocamento_y)
        self.tela.blit(sombra_surf, (x_sombra, y_sombra))

    def desenhar_barras_status(self, entidade, deslocamento_flutuacao=0):
        if getattr(entidade, 'is_player', False):
            return

        rect = entidade.rect
        largura_placa = max(95, rect.width + 12)
        altura_placa = 28 if getattr(entidade, 'max_mp', 0) > 0 else 20
        x_placa = rect.centerx - (largura_placa // 2)
        y_placa = rect.top - altura_placa - 14 + int(deslocamento_flutuacao)

        fundo_placa = pygame.Surface((largura_placa, altura_placa), pygame.SRCALPHA)
        pygame.draw.rect(fundo_placa, (16, 18, 28, 195), (0, 0, largura_placa, altura_placa), border_radius=6)
        pygame.draw.rect(fundo_placa, (70, 80, 105, 220), (0, 0, largura_placa, altura_placa), width=1, border_radius=6)
        self.tela.blit(fundo_placa, (x_placa, y_placa))

        nome_texto = entidade.nome[:14]
        if entidade.congelado:
            nome_texto = f"❄ {nome_texto}"
        txt_nome = self.fonte_inimigo.render(nome_texto, True, (240, 240, 240))
        self.tela.blit(txt_nome, (x_placa + (largura_placa - txt_nome.get_width()) // 2, y_placa + 2))

        bar_w = largura_placa - 12
        bar_h = 5
        x_bar = x_placa + 6
        y_bar = y_placa + 16
        pygame.draw.rect(self.tela, (70, 15, 20), (x_bar, y_bar, bar_w, bar_h), border_radius=2)
        if getattr(entidade, 'max_hp', 0) > 0:
            porc_hp = max(0.0, min(1.0, entidade.hp / entidade.max_hp))
            cor_hp = (45, 215, 85) if porc_hp > 0.35 else (230, 70, 50)
            pygame.draw.rect(self.tela, cor_hp, (x_bar, y_bar, int(bar_w * porc_hp), bar_h), border_radius=2)

        if getattr(entidade, 'max_mp', 0) > 0:
            y_mp = y_bar + bar_h + 2
            pygame.draw.rect(self.tela, (15, 25, 60), (x_bar, y_mp, bar_w, 3), border_radius=1)
            porc_mp = max(0.0, min(1.0, entidade.mp / entidade.max_mp))
            pygame.draw.rect(self.tela, (40, 160, 255), (x_bar, y_mp, int(bar_w * porc_mp), 3), border_radius=1)

    def desenhar(self, posicao_mouse):
        tamanho_tela = self.tela.get_size()
        if self.fundo_luta is not None:
            if self.fundo_luta_redimensionado is None or self.fundo_luta_tamanho != tamanho_tela:
                self.fundo_luta_redimensionado = pygame.transform.scale(self.fundo_luta, tamanho_tela)
                self.fundo_luta_tamanho = tamanho_tela
            self.tela.blit(self.fundo_luta_redimensionado, (0, 0))
        else:
            self.tela.fill((20, 20, 20))

        entidades_vivas = [e for e in self.ordem_turnos if getattr(e, 'hp', 0) > 0]
        for entidade in entidades_vivas:
            self._desenhar_sombra_contato(entidade)

        entidades_ordenadas = sorted(entidades_vivas, key=lambda e: e.rect.bottom)
        for idx, entidade in enumerate(entidades_ordenadas):
            fase = idx * 1.3
            bob = math.sin(self.tempo_animacao * 3.0 + fase) * 2.2
            rect_original = entidade.rect.copy()
            entidade.rect.y += int(bob)

            if getattr(entidade, 'is_player', False):
                entidade.desenhar(self.tela)
            else:
                if hasattr(entidade, 'desenhar'):
                    try:
                        entidade.desenhar(self.tela, desenhar_nome=False)
                    except TypeError:
                        entidade.desenhar(self.tela)

            self.desenhar_barras_status(entidade, deslocamento_flutuacao=bob)
            entidade.rect = rect_original

        indice_seguro = self.indice_turno if self.indice_turno < len(self.ordem_turnos) else 0
        turno_ativo = self.ordem_turnos[indice_seguro] if self.ordem_turnos else None
        if turno_ativo is not None and getattr(turno_ativo, 'is_player', False) and turno_ativo.hp > 0:
            indicador_y = turno_ativo.rect.top - 24 + int(math.sin(self.tempo_animacao * 5.0) * 3)
            seta_surf = self.fonte_inimigo.render("▲ SEU TURNO ▲", True, (255, 220, 90))
            self.tela.blit(seta_surf, (turno_ativo.rect.centerx - seta_surf.get_width() // 2, indicador_y))

        if self.menu_acoes_estado == "selecionar_alvo":
            inimigos = [entidade for entidade in self.ordem_turnos if not getattr(entidade, 'is_player', False) and entidade.hp > 0]
            pulso = int(math.sin(self.tempo_animacao * 6.0) * 3)
            for alvo in inimigos:
                if alvo.rect.collidepoint(posicao_mouse):
                    txt_alvo = self.fonte_inimigo.render("▼ ALVO ▼", True, (255, 230, 80))
                    self.tela.blit(txt_alvo, (alvo.rect.centerx - txt_alvo.get_width() // 2, alvo.rect.top - 46 + pulso))

                    r = alvo.rect.inflate(10 + pulso, 10 + pulso)
                    c_tam = 14
                    c_cor = (255, 225, 70)
                    w_ln = 3
                    pygame.draw.line(self.tela, c_cor, (r.left, r.top), (r.left + c_tam, r.top), w_ln)
                    pygame.draw.line(self.tela, c_cor, (r.left, r.top), (r.left, r.top + c_tam), w_ln)
                    pygame.draw.line(self.tela, c_cor, (r.right, r.top), (r.right - c_tam, r.top), w_ln)
                    pygame.draw.line(self.tela, c_cor, (r.right, r.top), (r.right, r.top + c_tam), w_ln)
                    pygame.draw.line(self.tela, c_cor, (r.left, r.bottom), (r.left + c_tam, r.bottom), w_ln)
                    pygame.draw.line(self.tela, c_cor, (r.left, r.bottom), (r.left, r.bottom - c_tam), w_ln)
                    pygame.draw.line(self.tela, c_cor, (r.right, r.bottom), (r.right - c_tam, r.bottom), w_ln)
                    pygame.draw.line(self.tela, c_cor, (r.right, r.bottom), (r.right, r.bottom - c_tam), w_ln)

        if self.menu_acoes_estado == "esquivando":
            painel_w = 460
            painel_h = 56
            painel_x = (self.tela.get_width() - painel_w) // 2
            painel_y = 250
            painel_surf = pygame.Surface((painel_w, painel_h), pygame.SRCALPHA)
            pygame.draw.rect(painel_surf, (15, 18, 28, 220), (0, 0, painel_w, painel_h), border_radius=10)
            pygame.draw.rect(painel_surf, (255, 215, 80, 200), (0, 0, painel_w, painel_h), width=2, border_radius=10)
            self.tela.blit(painel_surf, (painel_x, painel_y))

            bar_w = 400
            bar_h = 24
            bar_x = (self.tela.get_width() - bar_w) // 2
            bar_y = painel_y + (painel_h - bar_h) // 2

            pygame.draw.rect(self.tela, (40, 42, 52), (bar_x, bar_y, bar_w, bar_h), border_radius=5)
            pygame.draw.rect(self.tela, (210, 180, 30), (bar_x + 120, bar_y, 160, bar_h))
            pygame.draw.rect(self.tela, (30, 220, 90), (bar_x + 180, bar_y, 40, bar_h))
            pygame.draw.rect(self.tela, (240, 240, 240), (bar_x, bar_y, bar_w, bar_h), width=2, border_radius=5)

            for barra in self.barras_esquiva:
                if not barra["ativa"] or barra["x"] < 0:
                    continue
                bx = bar_x + barra["x"] - 4
                if bar_x <= bx <= bar_x + bar_w:
                    pygame.draw.rect(self.tela, (255, 60, 60), (bx, bar_y - 6, 8, bar_h + 12), border_radius=2)

        contador_partida = pygame.Rect(30, 25, 175, 42)
        pygame.draw.rect(self.tela, (24, 26, 36), contador_partida, border_radius=10)
        pygame.draw.rect(self.tela, (255, 210, 90), contador_partida, width=2, border_radius=10)
        texto_partida = self.fonte_titulos.render(f"PARTIDA {self.partida_atual}/{self.total_partidas}", True, (255, 255, 255))
        self.tela.blit(texto_partida, (contador_partida.x + 14, contador_partida.y + 11))

        hud_log = pygame.Rect((self.tela.get_width() - 620) // 2, 20, 620, 70)
        pygame.draw.rect(self.tela, (22, 25, 36), hud_log, border_radius=10)
        pygame.draw.rect(self.tela, (110, 115, 140), hud_log, width=2, border_radius=10)
        padding = 12
        linhas = quebrar_texto(self.mensagem_log, self.fonte, hud_log.width - padding*2)
        total_altura = len(linhas) * self.fonte.get_linesize()
        y_inicio = hud_log.y + (hud_log.height - total_altura) // 2
        for indice_linha, linha in enumerate(linhas):
            surf = self.fonte.render(linha, True, (255, 255, 255))
            x = hud_log.x + (hud_log.width - surf.get_width()) // 2
            y = y_inicio + indice_linha * self.fonte.get_linesize()
            self.tela.blit(surf, (x, y))

        hud_acoes = pygame.Rect((self.tela.get_width() - 640) // 2, 596, 640, 106)
        pygame.draw.rect(self.tela, (20, 22, 32), hud_acoes, border_radius=12)
        pygame.draw.rect(self.tela, (85, 95, 120), hud_acoes, width=2, border_radius=12)
        self.tela.blit(self.fonte_titulos.render("AÇÕES", True, (180, 190, 215)), (hud_acoes.x + 16, hud_acoes.y + 8))

        jogadores_status = [personagem]
        if getattr(self, 'duas_pessoas', False) and getattr(self, 'personagem2', None) is not None:
            jogadores_status.append(self.personagem2)

        largura_cartao = 290
        espaco_cartao = 20
        largura_total_cards = len(jogadores_status) * largura_cartao + (len(jogadores_status) - 1) * espaco_cartao
        x_base_status = (self.tela.get_width() - largura_total_cards) // 2
        y_base_status = 716

        for indice, jogador in enumerate(jogadores_status):
            x_cartao = x_base_status + indice * (largura_cartao + espaco_cartao)
            rect_status = pygame.Rect(x_cartao, y_base_status, largura_cartao, 68)

            pygame.draw.rect(self.tela, (22, 24, 34), rect_status, border_radius=10)

            eh_turno = (turno_ativo == jogador)
            cor_borda = (255, 210, 80) if eh_turno else (75, 80, 100)
            espessura_borda = 3 if eh_turno else 2
            pygame.draw.rect(self.tela, cor_borda, rect_status, width=espessura_borda, border_radius=10)

            nome_jogador = "JOGADOR 1" if jogador == personagem else "JOGADOR 2"
            cor_nome = (255, 230, 120) if eh_turno else (230, 230, 240)
            self.tela.blit(self.fonte_status.render(nome_jogador, True, cor_nome), (rect_status.x + 12, rect_status.y + 6))

            x_hp = rect_status.x + 12
            y_hp = rect_status.y + 28
            w_bar = 150
            h_bar = 13
            pygame.draw.rect(self.tela, (65, 14, 18), (x_hp, y_hp, w_bar, h_bar), border_radius=3)
            if jogador.max_hp > 0:
                porc_hp = max(0.0, min(1.0, jogador.hp / jogador.max_hp))
                pygame.draw.rect(self.tela, (40, 210, 80), (x_hp, y_hp, int(w_bar * porc_hp), h_bar), border_radius=3)
            txt_hp = self.fonte_status.render(f"HP {jogador.hp}/{jogador.max_hp}", True, (255, 255, 255))
            self.tela.blit(txt_hp, (x_hp + w_bar + 10, y_hp - 1))

            y_mp = rect_status.y + 46
            pygame.draw.rect(self.tela, (14, 22, 60), (x_hp, y_mp, w_bar, h_bar), border_radius=3)
            if jogador.max_mp > 0:
                porc_mp = max(0.0, min(1.0, jogador.mp / jogador.max_mp))
                pygame.draw.rect(self.tela, (30, 150, 255), (x_hp, y_mp, int(w_bar * porc_mp), h_bar), border_radius=3)
            txt_mp = self.fonte_status.render(f"PM {jogador.mp}/{jogador.max_mp}", True, (255, 255, 255))
            self.tela.blit(txt_mp, (x_hp + w_bar + 10, y_mp - 1))

        if turno_ativo is not None and turno_ativo in (personagem, getattr(self, 'personagem2', None)) and not turno_ativo.congelado:
            desenhadores_menu = {
                "principal": self._desenhar_menu_principal,
                "ataques": self._desenhar_menu_ataques,
                "selecionar_alvo": self._desenhar_menu_selecionar_alvo,
            }
            if desenhador := desenhadores_menu.get(self.menu_acoes_estado):
                desenhador()

    def _desenhar_menu_principal(self):
        self.btn_ataque.desenhar(self.tela)
        self.btn_recuperar.desenhar(self.tela)
        self.btn_bloquear.desenhar(self.tela)
        self.btn_fugir.desenhar(self.tela)

    def _desenhar_menu_ataques(self):
        for item_habilidade in self.botoes_habilidades_dinamicos:
            item_habilidade["botao"].desenhar(self.tela)
        self.btn_voltar.desenhar(self.tela)

    def _desenhar_menu_selecionar_alvo(self):
        self.btn_voltar.desenhar(self.tela)

    def _processar_menu_principal(self, jogador_atual, posicao_mouse, estado_clique_mouse, clicou):
        nome_turno = "Seu Turno!" if jogador_atual == personagem else "Turno do Jogador 2!"
        if (
            "usou" not in self.mensagem_log
            and "ERROU" not in self.mensagem_log
            and "falhou" not in self.mensagem_log.lower()
            and "CRÍTICO" not in self.mensagem_log
            and "rápido" not in self.mensagem_log
            and "⚑" not in self.mensagem_log
            and "🎲" not in self.mensagem_log
            and "👑" not in self.mensagem_log
        ):
            self.mensagem_log = nome_turno

        self.btn_ataque.atualizar(posicao_mouse, estado_clique_mouse)
        self.btn_recuperar.atualizar(posicao_mouse, estado_clique_mouse)
        self.btn_bloquear.atualizar(posicao_mouse, estado_clique_mouse)
        self.btn_fugir.atualizar(posicao_mouse, estado_clique_mouse)

        if not clicou:
            return None

        if self.btn_ataque.clicado(posicao_mouse):
            self.gerar_botoes_ataque(jogador_atual)
            self.menu_acoes_estado = "ataques"
        elif self.btn_recuperar.clicado(posicao_mouse):
            pm_rec = 2 if self.tem_talento(jogador_atual, "F1") else 1
            if self.tem_talento(jogador_atual, "F2"):
                pm_rec += 2
            jogador_atual.mp = min(jogador_atual.max_mp, jogador_atual.mp + pm_rec)
            jogador_atual.recuperando = True

            hp_rec = 0
            if self.tem_talento(jogador_atual, "F3"):
                hp_rec = max(1, int(jogador_atual.max_hp * 0.10))
                jogador_atual.hp = min(jogador_atual.max_hp, jogador_atual.hp + hp_rec)

            txt_hp = f" e +{hp_rec} HP" if hp_rec > 0 else ""
            self.mensagem_log = f"🧘 RECUPERAR: +{pm_rec} PM{txt_hp}, mas sofrerá +10% dano!"
            self.avancar_turno()
        elif self.btn_bloquear.clicado(posicao_mouse):
            jogador_atual.bloqueando = True
            self.mensagem_log = "🛡️ BLOQUEAR: Dano reduzido em 50%!"
            self.avancar_turno()
        elif self.btn_fugir.clicado(posicao_mouse):
            chance_fuga = 1.0 if self.tem_talento(jogador_atual, "S1") else 0.50
            if random.random() < chance_fuga:
                from Sistemas.Conquistas import sistema_conquistas
                sistema_conquistas.desbloquear("fuga_estrategica")
                cura_info = self.recuperar_apos_batalha(dormir=False)
                self.ultimo_resultado_batalha = {
                    "cura": cura_info,
                    "itens": [],
                    "xp": 0
                }
                return "fugiu"
            else:
                self.mensagem_log = "❌ FUGA falhou!"
                self.avancar_turno()
        return None

    def _processar_menu_ataques(self, jogador_atual, posicao_mouse, estado_clique_mouse, clicou):
        self.btn_voltar.atualizar(posicao_mouse, estado_clique_mouse)
        for item_habilidade in self.botoes_habilidades_dinamicos:
            item_habilidade["botao"].atualizar(posicao_mouse, estado_clique_mouse)

        if not clicou:
            return None

        if self.btn_voltar.clicado(posicao_mouse):
            self.menu_acoes_estado = "principal"
            return None

        for item_habilidade in self.botoes_habilidades_dinamicos:
            if item_habilidade["botao"].clicado(posicao_mouse):
                hab = banco_habilidades[item_habilidade["nome"]]
                custo_mp = self._custo_habilidade(hab, jogador_atual)
                if jogador_atual.mp >= custo_mp:
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
        return None

    def _processar_menu_selecionar_alvo(self, jogador_atual, posicao_mouse, estado_clique_mouse, clicou, inimigos_vivos):
        self.mensagem_log = f"🎯 Escolha o alvo para {self.ataque_selecionado.upper()}!"
        self.btn_voltar.atualizar(posicao_mouse, estado_clique_mouse)

        if not clicou:
            return None

        if self.btn_voltar.clicado(posicao_mouse):
            self.menu_acoes_estado = "ataques"
        else:
            for alvo in inimigos_vivos:
                if alvo.rect.collidepoint(posicao_mouse):
                    self.executar_ataque_jogador(self.ataque_selecionado, alvo, jogador_ativo=jogador_atual)
                    break
        return None
