from Entidades.Personagem import personagem


class Consumivel:
    def __init__(self, nome, descricao, rec_hp=0, rec_mp=0):
        self.nome = nome
        self.descricao = descricao
        self.quantidade = 1
        self.rec_hp = rec_hp
        self.rec_mp = rec_mp

    def usar(self, alvo=None):
        if self.quantidade > 0:
            alvo_final = alvo if alvo is not None else personagem
            fator = 2 if getattr(alvo_final, "tem_talento", lambda t: False)("S2") else 1
            alvo_final.hp = min(alvo_final.max_hp, alvo_final.hp + (self.rec_hp * fator))
            alvo_final.mp = min(alvo_final.max_mp, alvo_final.mp + (self.rec_mp * fator))
            self.quantidade -= 1
            from Sistemas.Conquistas import sistema_conquistas
            sistema_conquistas.desbloquear("alquimista")


class Material:
    def __init__(self, nome, descricao):
        self.nome = nome
        self.descricao = descricao
        self.quantidade = 1
        self.tipo = "material"

    def usar(self):
        return False


class Equipamento:
    def __init__(self, nome, atributos_bonus):
        self.nome = nome
        self.atributos_bonus = atributos_bonus
        self.nivel = 1

    def melhorar(self):
        self.nivel += 1
        for k in self.atributos_bonus:
            if self.atributos_bonus[k] > 0:
                self.atributos_bonus[k] += 1


class SistemaInventario:
    def __init__(self):
        self.consumiveis = []
        self.materiais = []
        self.equipamento_slot = None

    def adicionar_consumivel(self, nome, descricao, rec_hp, rec_mp):
        for c in self.consumiveis:
            if c.nome == nome:
                c.quantidade += 1
                return
        self.consumiveis.append(Consumivel(nome, descricao, rec_hp, rec_mp))

    def adicionar_material(self, nome, descricao):
        for m in self.materiais:
            if m.nome == nome:
                m.quantidade += 1
                return
        self.materiais.append(Material(nome, descricao))
        
    def equipar(self, equipamento):
        self.equipamento_slot = equipamento

    def resetar(self):
        self.consumiveis.clear()
        self.materiais.clear()
        self.equipamento_slot = None

    def itens_do_inventario(self):
        return self.consumiveis + self.materiais

    def custo_melhoria(self):
        if not self.equipamento_slot: return 0
        custo = self.equipamento_slot.nivel * 2
        if getattr(personagem, "tem_talento", lambda t: False)("S2"):
            custo = max(1, custo // 2)
        return custo

    def materiais_totais(self):
        return sum(m.quantidade for m in self.materiais)

    def consumir_materiais(self, quantidade):
        gastos = 0
        for m in self.materiais:
            while m.quantidade > 0 and gastos < quantidade:
                m.quantidade -= 1
                gastos += 1
        self.materiais = [m for m in self.materiais if m.quantidade > 0]


inventario_global = SistemaInventario()

# Retrocompatibilidade: exporta TelaInventario sob demanda
def __getattr__(name):
    if name == "TelaInventario":
        from Telas.TelaInventario import TelaInventario
        return TelaInventario
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
