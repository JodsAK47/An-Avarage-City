import random

from Entidades.Inimigo import Inimigo


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


BANCO_INIMIGOS = [
    {"max_hp": 25, "arquivo_imagem": "Maldição1.png", "nome": "Goblin Verde", "ataques": ["Mordida", "Soco"], "xp": 30, "atributos": {"For": 2, "Agi": 3, "Int": 0}},
    {"max_hp": 20, "arquivo_imagem": "Maldição1.png", "nome": "Goblin Corredor", "ataques": ["Mordida"], "xp": 20, "atributos": {"For": 1, "Agi": 5, "Int": 0}},
    {"max_hp": 35, "arquivo_imagem": "Maldição1.png", "nome": "Morcego Gigante", "ataques": ["Mordida"], "xp": 40, "atributos": {"For": 3, "Agi": 4, "Int": 0}},
    {"max_hp": 50, "arquivo_imagem": "Maldição1.png", "nome": "Troll Brutal", "ataques": ["Porrete do Chefe", "Soco"], "xp": 60, "atributos": {"For": 6, "Agi": 1, "Int": 0}},
    {"max_hp": 40, "arquivo_imagem": "Maldição1.png", "nome": "Agente Esqueleto", "ataques": ["Gelo"], "xp": 50, "atributos": {"For": 1, "Agi": 6, "Int": 0}},
    {"max_hp": 35, "arquivo_imagem": "Maldição1.png", "nome": "Mago Sombrio", "ataques": ["Gelo", "Soco"], "xp": 50, "atributos": {"For": 1, "Agi": 2, "Int": 5}},
    {"max_hp": 120, "arquivo_imagem": "Sukuna1.png", "nome": "Sukuna", "ataques": ["Fogo", "Soco", "Nevasca"], "xp": 200, "atributos": {"For": 8, "Agi": 4, "Int": 20}},
]

def _criar_inimigo_a_partir_template(template, x=0, y=0, multiplicador=1.0):
    hp = max(12, int(template.get("max_hp", 20) * multiplicador + random.randint(0, 12)))
    xp = int(template.get("xp", 10) * multiplicador)
    
    atributos_base = template.get("atributos", {"For": 1, "Agi": 1, "Int": 1})
    atributos = {
        "For": max(1, int(atributos_base.get("For", 1) + (multiplicador - 1) * 3)),
        "Agi": max(1, int(atributos_base.get("Agi", 1) + (multiplicador - 1) * 3)),
        "Int": max(1, int(atributos_base.get("Int", 1) + (multiplicador - 1) * 3)),
    }

    return Inimigo(
        x,
        y,
        hp,
        template.get("arquivo_imagem", "Maldição1.png"),
        template.get("nome", "Inimigo"),
        list(template.get("ataques", ["Soco"])),
        xp,
        atributos,
    )

def listar_inimigos_disponiveis():
    """Retorna os templates disponíveis."""
    return list(BANCO_INIMIGOS)

class GeradorFase:
    EVENTOS_NEUTROS = [
        EventoNeutro("Mochila de suprimentos", "ajuda", "Você encontra suprimentos e ganha fôlego para a viagem.", 1),
        EventoNeutro("Armadilha de pedra", "atrapalha", "Uma pedra solta te derruba e te deixa mais cansado.", 1),
        EventoNeutro("Fonte mística", "ajuda", "Uma fonte antiga reabastece sua energia por um momento.", 1),
        EventoNeutro("Fenda no caminho", "atrapalha", "Uma rachadura no terreno atrapalha seus passos e enfraquece a formação.", 1),
        EventoNeutro("Mercador solitário", "ajuda", "Um mercador lhe oferece uma dica útil e um pequeno presente.", 1),
        EventoNeutro("Pista falsa", "atrapalha", "Você toma um caminho ruim e perde tempo em uma rota perigosa.", 1),
    ]

    def __init__(self, fase_num=1):
        self.fase_num = fase_num

    def gerar_evento_neutro(self, fase_num=None):
        fase = self.fase_num if fase_num is None else fase_num
        evento = random.choice(self.EVENTOS_NEUTROS)
        return EventoNeutro(evento.nome, evento.tipo, evento.descricao, fase)

    def gerar_inimigos_aleatorios(self, fase_num=None, quantidade=None):
        fase = self.fase_num if fase_num is None else fase_num
        if quantidade is None:
            quantidade = max(1, min(4, 1 + (fase // 2)))

        templates = listar_inimigos_disponiveis()
        inimigos = []

        for _ in range(quantidade):
            template = random.choice(templates)
            multiplicador = 1 + (fase * 0.22)
            inimigos.append(_criar_inimigo_a_partir_template(template, multiplicador=multiplicador))

        return inimigos

    def gerar_fase_aleatoria(self, fase_num=None):
        fase = self.fase_num if fase_num is None else fase_num
        evento = self.gerar_evento_neutro(fase)
        quantidade = max(1, min(4, 1 + (fase // 2)))
        inimigos = self.gerar_inimigos_aleatorios(fase, quantidade=quantidade)
        return FaseAleatoria(
            f"fase_aleatoria_{fase}",
            f"Fase Aleatória {fase}",
            "Uma rota improvisada com inimigos e eventos inesperados.",
            evento,
            inimigos,
        )
