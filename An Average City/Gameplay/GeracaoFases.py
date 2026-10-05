import json
import os
import random
from Sistemas.Recursos import caminho_dados

CAMINHO_DADOS = caminho_dados()


class EventoNeutro:
    def __init__(self, nome, tipo, descricao, fase_num=1):
        self.nome = nome
        self.tipo = tipo
        self.descricao = descricao
        self.fase_num = fase_num

    def para_dict(self):
        return {
            "fase": self.fase_num,
            "nome": self.nome,
            "tipo": self.tipo,
            "descricao": self.descricao,
        }


class FaseAleatoria:
    def __init__(self, id_fase, nome, descricao, evento, inimigos):
        self.id_fase = id_fase
        self.nome = nome
        self.descricao = descricao
        self.evento = evento
        self.inimigos = inimigos

    def para_dict(self):
        return {
            "id": self.id_fase,
            "nome": self.nome,
            "descricao": self.descricao,
            "evento": self.evento.para_dict(),
            "inimigos": self.inimigos,
        }


def carregar_inimigos():
    try:
        arquivo = caminho_dados("inimigos.json")
        with open(arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️ Erro: arquivo inimigos.json não encontrado.")
        return []


BANCO_INIMIGOS = carregar_inimigos()


def _criar_inimigo_a_partir_template(template, x=0, y=0, multiplicador=1.0):
    hp = max(12, int(template.get("max_hp", 20) * multiplicador + random.randint(0, 12)))
    xp = int(template.get("xp", 10) * multiplicador)
    
    atributos_base = template.get("atributos", {"For": 1, "Agi": 1, "Int": 1})
    atributos = {
        "For": max(1, int(atributos_base.get("For", 1) + (multiplicador - 1) * 3)),
        "Agi": max(1, int(atributos_base.get("Agi", 1) + (multiplicador - 1) * 3)),
        "Int": max(1, int(atributos_base.get("Int", 1) + (multiplicador - 1) * 3)),
    }

    max_mp_base = template.get("max_mp")
    max_mp_calc = int(max_mp_base * multiplicador) if max_mp_base is not None else None

    from Entidades.Inimigo import Inimigo
    return Inimigo(
        x,
        y,
        hp,
        template.get("arquivo_imagem", "Maldição1.png"),
        template.get("nome", "Inimigo"),
        list(template.get("ataques", ["Soco"])),
        xp,
        atributos,
        max_mp=max_mp_calc
    )


def listar_inimigos_disponiveis(verso=None, incluir_chefes=False):
    """Retorna os templates disponíveis filtrados por verso e tipo."""
    inimigos = BANCO_INIMIGOS
    if verso:
        inimigos = [i for i in inimigos if i.get("verso") == verso]
    if not incluir_chefes:
        inimigos = [i for i in inimigos if i.get("tipo") != "chefe"]
        
    if not inimigos:
        inimigos = [i for i in BANCO_INIMIGOS if i.get("tipo") != "chefe"]
        
    return inimigos


class GeradorFase:
    EVENTOS_NEUTROS = []

    def _carregar_eventos(self):
        if self.EVENTOS_NEUTROS:
            return
        try:
            arquivo = caminho_dados("eventos.json")
            with open(arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)
                self.EVENTOS_NEUTROS = [EventoNeutro(d["nome"], d["tipo"], d["descricao"], d.get("fase_num", 1)) for d in dados]
        except FileNotFoundError:
            print("⚠️ Erro: arquivo eventos.json não encontrado.")
            self.EVENTOS_NEUTROS = [EventoNeutro("Caminho normal", "neutro", "Nada de especial acontece.", 1)]

    def __init__(self, fase_num=1):
        self.fase_num = fase_num
        self._carregar_eventos()

    def gerar_evento_neutro(self, fase_num=None):
        fase = self.fase_num if fase_num is None else fase_num
        evento = random.choice(self.EVENTOS_NEUTROS)
        return EventoNeutro(evento.nome, evento.tipo, evento.descricao, fase)

    def gerar_inimigos_aleatorios(self, fase_num=None, quantidade=None, verso=None):
        fase = self.fase_num if fase_num is None else fase_num
        if quantidade is None:
            quantidade = max(1, min(4, 1 + (fase // 2)))

        templates = listar_inimigos_disponiveis(verso=verso)
        inimigos = []

        for _ in range(quantidade):
            template = random.choice(templates)
            multiplicador = 1 + (fase * 0.22)
            inimigos.append(_criar_inimigo_a_partir_template(template, multiplicador=multiplicador))

        return inimigos
        
    def gerar_chefe_verso(self, verso):
        chefes = [i for i in BANCO_INIMIGOS if i.get("verso") == verso and i.get("tipo") == "chefe"]
        if not chefes:
            chefes = [i for i in BANCO_INIMIGOS if i.get("tipo") == "chefe"]
        template = random.choice(chefes)
        return _criar_inimigo_a_partir_template(template, multiplicador=1.5)

    def gerar_fase_aleatoria(self, fase_num=None, verso=None):
        fase = self.fase_num if fase_num is None else fase_num
        evento = self.gerar_evento_neutro(fase)
        quantidade = max(1, min(4, 1 + (fase // 2)))
        inimigos = self.gerar_inimigos_aleatorios(fase, quantidade=quantidade, verso=verso)
        return FaseAleatoria(
            f"fase_aleatoria_{fase}",
            f"Fase Aleatória {fase}",
            "Uma rota improvisada com inimigos e eventos inesperados.",
            evento,
            inimigos,
        )
