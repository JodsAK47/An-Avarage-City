import random

from Entidades.Inimigo import Inimigo, listar_inimigos_disponiveis


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


class GeradorFase:
    EVENTOS_NEUTROS = [
        EventoNeutro("Mochila de suprimentos", "ajuda", "Você encontra suprimentos e ganha fôlego para a viagem. (placeholder)", 1),
        EventoNeutro("Armadilha de pedra", "atrapalha", "Uma pedra solta te derruba e te deixa mais cansado. (placeholder)", 1),
        EventoNeutro("Fonte mística", "ajuda", "Uma fonte antiga reabastece sua energia por um momento. (placeholder)", 1),
        EventoNeutro("Fenda no caminho", "atrapalha", "Uma rachadura no terreno atrapalha seus passos e enfraquece a formação. (placeholder)", 1),
        EventoNeutro("Mercador solitário", "ajuda", "Um mercador lhe oferece uma dica útil e um pequeno presente. (placeholder)", 1),
        EventoNeutro("Pista falsa", "atrapalha", "Você toma um caminho ruim e perde tempo em uma rota perigosa. (placeholder)", 1),
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

        modelos = listar_inimigos_disponiveis()
        inimigos = []

        for _ in range(quantidade):
            modelo = random.choice(modelos)
            multiplicador = 1 + (fase * 0.22)
            hp = max(12, int(modelo.max_hp * multiplicador + random.randint(0, 12)))
            xp = int(modelo.xp * (1 + (fase * 0.18)))

            atributos = {
                "For": max(1, int(modelo.atributos.get("For", 1) + (fase * 0.35))),
                "Agi": max(1, int(modelo.atributos.get("Agi", 1) + (fase * 0.30))),
                "Int": max(1, int(modelo.atributos.get("Int", 1) + (fase * 0.25))),
            }

            inimigos.append(
                Inimigo(
                    0,
                    0,
                    hp,
                    modelo.arquivo_imagem,
                    modelo.nome,
                    list(modelo.ataques),
                    xp,
                    atributos,
                )
            )

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
