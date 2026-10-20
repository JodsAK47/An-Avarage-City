def _obter_personagem_padrao():
    from Entidades.Personagem import personagem
    return personagem

class Consumivel:
    def __init__(self, nome, descricao, rec_hp=0, rec_mp=0):
        self.nome = nome
        self.descricao = descricao
        self.quantidade = 1
        self.rec_hp = rec_hp
        self.rec_mp = rec_mp

    def usar(self, alvo=None):
        if self.quantidade > 0:
            alvo_final = alvo if alvo is not None else _obter_personagem_padrao()
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

class ItemBilhete:
    def __init__(self, quantidade=1):
        self.nome = "Bilhete do Dormitório"
        self.descricao = "Permite dormir no dormitório para recuperar mais HP e PM."
        self.quantidade = quantidade
        self.tipo = "bilhete"

    def usar(self, alvo=None):
        return False

CATEGORIAS_EQUIPAMENTO = ("arma", "capacete", "peitoral", "calca", "bota", "amuleto")

CATALOGO_EQUIPAMENTOS = [
    {"nome": "Capacete de Ferro", "categoria": "capacete", "atributos_bonus": {"Con": 2}},
    {"nome": "Capacete Tático", "categoria": "capacete", "atributos_bonus": {"Sab": 2, "Agi": 1}},
    {"nome": "Capuz Sombrio", "categoria": "capacete", "atributos_bonus": {"Int": 2, "Sor": 1}},
    {"nome": "Peitoral de Aço", "categoria": "peitoral", "atributos_bonus": {"Con": 3, "For": 1}},
    {"nome": "Colete Balístico", "categoria": "peitoral", "atributos_bonus": {"Con": 2, "Agi": 2}},
    {"nome": "Manto Arcano", "categoria": "peitoral", "atributos_bonus": {"Int": 3, "Sab": 1}},
    {"nome": "Calça Reforçada", "categoria": "calca", "atributos_bonus": {"Con": 2, "For": 1}},
    {"nome": "Calça Tática", "categoria": "calca", "atributos_bonus": {"Agi": 2, "Con": 1}},
    {"nome": "Calça de Feiticeiro", "categoria": "calca", "atributos_bonus": {"Sab": 2, "Int": 1}},
    {"nome": "Botas de Combate", "categoria": "bota", "atributos_bonus": {"For": 2, "Agi": 1}},
    {"nome": "Botas Velozes", "categoria": "bota", "atributos_bonus": {"Agi": 3}},
    {"nome": "Botas Místicas", "categoria": "bota", "atributos_bonus": {"Int": 1, "Sab": 1, "Sor": 1}},
    {"nome": "Amuleto do Mago", "categoria": "amuleto", "atributos_bonus": {"Int": 2}},
    {"nome": "Amuleto da Força", "categoria": "amuleto", "atributos_bonus": {"For": 2}},
    {"nome": "Amuleto da Agilidade", "categoria": "amuleto", "atributos_bonus": {"Agi": 2}},
    {"nome": "Amuleto da Sorte", "categoria": "amuleto", "atributos_bonus": {"Sor": 2}},
    {"nome": "Amuleto Vital", "categoria": "amuleto", "atributos_bonus": {"Con": 2}},
    {"nome": "Amuleto da Sabedoria", "categoria": "amuleto", "atributos_bonus": {"Sab": 2}},
]


def _normalizar_categoria(categoria, nome=""):
    if categoria:
        c = str(categoria).strip().lower()
        mapa = {
            "arma": "arma",
            "equipamento": "arma",
            "capacete": "capacete",
            "elmo": "capacete",
            "capuz": "capacete",
            "peitoral": "peitoral",
            "colete": "peitoral",
            "manto": "peitoral",
            "armadura": "peitoral",
            "calca": "calca",
            "calça": "calca",
            "calcas": "calca",
            "calças": "calca",
            "bota": "bota",
            "botas": "bota",
            "amuleto": "amuleto",
            "amuletos": "amuleto",
        }
        if c in mapa:
            return mapa[c]

    nome_low = str(nome or "").strip().lower()
    if any(p in nome_low for p in ("capacete", "elmo", "capuz")):
        return "capacete"
    if any(p in nome_low for p in ("peitoral", "colete", "manto", "armadura")):
        return "peitoral"
    if any(p in nome_low for p in ("calça", "calca")):
        return "calca"
    if any(p in nome_low for p in ("bota", "botas")):
        return "bota"
    if "amuleto" in nome_low:
        return "amuleto"
    return "arma"


class ItemPolidor:
    def __init__(self, quantidade=0):
        self.nome = "Polidor de Itens"
        self.descricao = "Dobra permanentemente os bônus do equipamento."
        self.quantidade = quantidade
        self.tipo = "polidor"

    def usar(self, alvo=None):
        if self.quantidade <= 0:
            return False
        equipamento_alvo = None
        if isinstance(alvo, Equipamento):
            equipamento_alvo = alvo
        elif alvo is not None and hasattr(alvo, "obter_equipamento_alvo"):
            equipamento_alvo = alvo.obter_equipamento_alvo()
        elif alvo is not None and hasattr(alvo, "equipamento_slot") and alvo.equipamento_slot is not None:
            equipamento_alvo = alvo.equipamento_slot
        else:
            equipamento_alvo = inventario_global.obter_equipamento_alvo()

        if equipamento_alvo is not None:
            equipamento_alvo.polir()
            self.quantidade -= 1
            return True
        return False


class Equipamento:
    def __init__(self, nome, atributos_bonus, categoria=None, descricao=None):
        self.nome = nome
        self.atributos_bonus = dict(atributos_bonus)
        self.nivel = 1
        self.polido = False
        self.fator_polimento = 1
        self.categoria = _normalizar_categoria(categoria, nome)
        self.tipo = "equipamento"
        self.quantidade = 1
        self._descricao_custom = descricao

    @property
    def descricao(self):
        if self._descricao_custom:
            return self._descricao_custom
        bonus_str = ", ".join(f"+{v} {k}" for k, v in self.atributos_bonus.items() if v > 0)
        cat_legivel = {
            "arma": "Arma",
            "capacete": "Capacete",
            "peitoral": "Peitoral",
            "calca": "Calça",
            "bota": "Bota",
            "amuleto": "Amuleto",
        }.get(self.categoria, "Equipamento")
        return f"{cat_legivel} ({bonus_str})" if bonus_str else cat_legivel

    @descricao.setter
    def descricao(self, valor):
        self._descricao_custom = valor

    def melhorar(self):
        self.nivel += 1
        for k in self.atributos_bonus:
            if self.atributos_bonus[k] > 0:
                self.atributos_bonus[k] += 1 * self.fator_polimento

    def polir(self):
        self.polido = True
        self.fator_polimento *= 2
        for k in self.atributos_bonus:
            if self.atributos_bonus[k] > 0:
                self.atributos_bonus[k] *= 2
        return True

    def usar(self, alvo=None):
        return inventario_global.equipar(self)


class SistemaInventario:
    MAX_AMULETOS = 3

    def __init__(self):
        self.consumiveis = []
        self.materiais = []
        self.equipamento_slot = None
        self.capacete_slot = None
        self.peitoral_slot = None
        self.calca_slot = None
        self.bota_slot = None
        self.amuletos_slots = []
        self.equipamentos_inventario = []
        self.equipamento_selecionado = None
        self.item_bilhete = ItemBilhete(quantidade=1)
        self.item_polidor = ItemPolidor(quantidade=0)

    @property
    def capacete(self):
        return self.capacete_slot

    @capacete.setter
    def capacete(self, valor):
        self.capacete_slot = valor

    @property
    def peitoral(self):
        return self.peitoral_slot

    @peitoral.setter
    def peitoral(self, valor):
        self.peitoral_slot = valor

    @property
    def calca(self):
        return self.calca_slot

    @calca.setter
    def calca(self, valor):
        self.calca_slot = valor

    @property
    def bota(self):
        return self.bota_slot

    @bota.setter
    def bota(self, valor):
        self.bota_slot = valor

    @property
    def amuletos(self):
        return self.amuletos_slots

    @amuletos.setter
    def amuletos(self, valor):
        self.amuletos_slots = list(valor) if valor is not None else []

    @property
    def bilhetes_dormitorio(self):
        return self.item_bilhete.quantidade

    @bilhetes_dormitorio.setter
    def bilhetes_dormitorio(self, valor):
        self.item_bilhete.quantidade = max(0, int(valor))

    def obter_bilhetes_dormitorio(self):
        return self.item_bilhete.quantidade

    def adicionar_bilhete_dormitorio(self, quantidade=1):
        self.item_bilhete.quantidade += max(0, int(quantidade))

    def consumir_bilhete_dormitorio(self, quantidade=1):
        qtd = max(0, int(quantidade))
        if self.item_bilhete.quantidade >= qtd and qtd > 0:
            self.item_bilhete.quantidade -= qtd
            return True
        return False

    @property
    def polidores_itens(self):
        return self.item_polidor.quantidade

    @polidores_itens.setter
    def polidores_itens(self, valor):
        self.item_polidor.quantidade = max(0, int(valor))

    @property
    def polidores(self):
        return self.item_polidor.quantidade

    @polidores.setter
    def polidores(self, valor):
        self.item_polidor.quantidade = max(0, int(valor))

    def obter_polidores_itens(self):
        return self.item_polidor.quantidade

    def obter_polidores(self):
        return self.item_polidor.quantidade

    def adicionar_polidor_itens(self, quantidade=1):
        self.item_polidor.quantidade += max(0, int(quantidade))

    def adicionar_polidor(self, quantidade=1):
        self.adicionar_polidor_itens(quantidade)

    def consumir_polidor_itens(self, quantidade=1):
        qtd = max(0, int(quantidade))
        if self.item_polidor.quantidade >= qtd and qtd > 0:
            self.item_polidor.quantidade -= qtd
            return True
        return False

    def obter_equipamento_alvo(self):
        if self.equipamento_selecionado is not None and self.equipamento_selecionado in self.todos_equipamentos_equipados():
            return self.equipamento_selecionado
        if self.equipamento_slot is not None:
            return self.equipamento_slot
        equipados = self.todos_equipamentos_equipados()
        if equipados:
            return equipados[0]
        return None

    def usar_polidor_itens(self, equipamento=None):
        alvo = equipamento if equipamento is not None else self.obter_equipamento_alvo()
        if alvo is None or self.item_polidor.quantidade <= 0:
            return False
        return self.item_polidor.usar(alvo)

    def usar_polidor(self, equipamento=None):
        return self.usar_polidor_itens(equipamento)

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

    def pode_equipar(self, equipamento, substituir=True):
        if not isinstance(equipamento, Equipamento):
            return False
        cat = getattr(equipamento, "categoria", "arma")
        if cat == "amuleto":
            if any(a.nome == equipamento.nome for a in self.amuletos_slots):
                return False
            if len(self.amuletos_slots) >= self.MAX_AMULETOS:
                return False
            return True
        if not substituir:
            mapa_slot = {
                "arma": self.equipamento_slot,
                "capacete": self.capacete_slot,
                "peitoral": self.peitoral_slot,
                "calca": self.calca_slot,
                "bota": self.bota_slot,
            }
            return mapa_slot.get(cat) is None
        return True

    def equipar(self, equipamento):
        if equipamento is None:
            return False
        cat = getattr(equipamento, "categoria", "arma")

        if cat == "amuleto":
            if any(a.nome == equipamento.nome for a in self.amuletos_slots):
                return False
            if len(self.amuletos_slots) >= self.MAX_AMULETOS:
                return False
            if equipamento in self.equipamentos_inventario:
                self.equipamentos_inventario.remove(equipamento)
            self.amuletos_slots.append(equipamento)
            self.equipamento_selecionado = equipamento
            return True

        if cat == "capacete":
            if self.capacete_slot is not None and self.capacete_slot is not equipamento:
                if self.capacete_slot not in self.equipamentos_inventario:
                    self.equipamentos_inventario.append(self.capacete_slot)
            if equipamento in self.equipamentos_inventario:
                self.equipamentos_inventario.remove(equipamento)
            self.capacete_slot = equipamento
            self.equipamento_selecionado = equipamento
            return True

        if cat == "peitoral":
            if self.peitoral_slot is not None and self.peitoral_slot is not equipamento:
                if self.peitoral_slot not in self.equipamentos_inventario:
                    self.equipamentos_inventario.append(self.peitoral_slot)
            if equipamento in self.equipamentos_inventario:
                self.equipamentos_inventario.remove(equipamento)
            self.peitoral_slot = equipamento
            self.equipamento_selecionado = equipamento
            return True

        if cat == "calca":
            if self.calca_slot is not None and self.calca_slot is not equipamento:
                if self.calca_slot not in self.equipamentos_inventario:
                    self.equipamentos_inventario.append(self.calca_slot)
            if equipamento in self.equipamentos_inventario:
                self.equipamentos_inventario.remove(equipamento)
            self.calca_slot = equipamento
            self.equipamento_selecionado = equipamento
            return True

        if cat == "bota":
            if self.bota_slot is not None and self.bota_slot is not equipamento:
                if self.bota_slot not in self.equipamentos_inventario:
                    self.equipamentos_inventario.append(self.bota_slot)
            if equipamento in self.equipamentos_inventario:
                self.equipamentos_inventario.remove(equipamento)
            self.bota_slot = equipamento
            self.equipamento_selecionado = equipamento
            return True

        if equipamento in self.equipamentos_inventario:
            self.equipamentos_inventario.remove(equipamento)
        self.equipamento_slot = equipamento
        self.equipamento_selecionado = equipamento
        return True

    def desequipar(self, equipamento_ou_categoria):
        alvo = None
        if isinstance(equipamento_ou_categoria, Equipamento):
            alvo = equipamento_ou_categoria
            if alvo is self.equipamento_slot:
                self.equipamento_slot = None
            elif alvo is self.capacete_slot:
                self.capacete_slot = None
            elif alvo is self.peitoral_slot:
                self.peitoral_slot = None
            elif alvo is self.calca_slot:
                self.calca_slot = None
            elif alvo is self.bota_slot:
                self.bota_slot = None
            elif alvo in self.amuletos_slots:
                self.amuletos_slots.remove(alvo)
            else:
                return False
        elif isinstance(equipamento_ou_categoria, str):
            cat = _normalizar_categoria(equipamento_ou_categoria)
            if cat == "capacete" and self.capacete_slot:
                alvo, self.capacete_slot = self.capacete_slot, None
            elif cat == "peitoral" and self.peitoral_slot:
                alvo, self.peitoral_slot = self.peitoral_slot, None
            elif cat == "calca" and self.calca_slot:
                alvo, self.calca_slot = self.calca_slot, None
            elif cat == "bota" and self.bota_slot:
                alvo, self.bota_slot = self.bota_slot, None
            elif cat == "amuleto" and self.amuletos_slots:
                alvo = self.amuletos_slots.pop(0)
            elif cat == "arma" and self.equipamento_slot:
                alvo, self.equipamento_slot = self.equipamento_slot, None

        if alvo is not None:
            if alvo not in self.equipamentos_inventario:
                self.equipamentos_inventario.append(alvo)
            if self.equipamento_selecionado is alvo:
                self.equipamento_selecionado = self.obter_equipamento_alvo()
            return True
        return False

    def adicionar_equipamento(self, equipamento, auto_equipar=True):
        if not isinstance(equipamento, Equipamento):
            return None
        if auto_equipar and self.pode_equipar(equipamento, substituir=False):
            self.equipar(equipamento)
        else:
            if equipamento not in self.equipamentos_inventario:
                self.equipamentos_inventario.append(equipamento)
        return equipamento

    def gerar_equipamento_aleatorio(self, categoria=None):
        import random
        opcoes = CATALOGO_EQUIPAMENTOS
        if categoria:
            cat_norm = _normalizar_categoria(categoria)
            filtradas = [item for item in CATALOGO_EQUIPAMENTOS if item["categoria"] == cat_norm]
            if filtradas:
                opcoes = filtradas

        nomes_amuletos_equipados = {a.nome for a in self.amuletos_slots}
        opcoes_preferenciais = [
            item for item in opcoes
            if not (item["categoria"] == "amuleto" and item["nome"] in nomes_amuletos_equipados)
        ]
        escolha = random.choice(opcoes_preferenciais if opcoes_preferenciais else opcoes)
        return Equipamento(escolha["nome"], dict(escolha["atributos_bonus"]), categoria=escolha["categoria"])

    def custo_compra_equipamento(self):
        custo = 2
        if getattr(_obter_personagem_padrao(), "tem_talento", lambda t: False)("S2"):
            custo = max(1, custo // 2)
        return custo

    def adicionar_sucata(self, quantidade=1):
        for _ in range(max(0, int(quantidade))):
            self.adicionar_material("Sucata", "Material para melhorar equipamentos.")

    def comprar_equipamento_loja(self, categoria=None, custo=None):
        custo_final = self.custo_compra_equipamento() if custo is None else max(0, int(custo))
        if self.materiais_totais() < custo_final:
            return None
        if custo_final > 0:
            self.consumir_materiais(custo_final)
        novo_eq = self.gerar_equipamento_aleatorio(categoria=categoria)
        self.adicionar_equipamento(novo_eq, auto_equipar=True)
        return novo_eq

    def obter_slots_equipamento(self):
        return [
            ("ARMA", self.equipamento_slot),
            ("CAP", self.capacete_slot),
            ("PEIT", self.peitoral_slot),
            ("CALÇ", self.calca_slot),
            ("BOTA", self.bota_slot),
            ("AMU1", self.amuletos_slots[0] if len(self.amuletos_slots) > 0 else None),
            ("AMU2", self.amuletos_slots[1] if len(self.amuletos_slots) > 1 else None),
            ("AMU3", self.amuletos_slots[2] if len(self.amuletos_slots) > 2 else None),
        ]

    def todos_equipamentos_equipados(self):
        equips = []
        for eq in (self.equipamento_slot, self.capacete_slot, self.peitoral_slot, self.calca_slot, self.bota_slot):
            if eq is not None:
                equips.append(eq)
        for am in self.amuletos_slots:
            if am is not None:
                equips.append(am)
        return equips

    def obter_bonus_atributo(self, atributo):
        total = 0
        for eq in self.todos_equipamentos_equipados():
            total += int(eq.atributos_bonus.get(atributo, 0))
        return total

    def obter_todos_bonus_atributos(self):
        totais = {"For": 0, "Agi": 0, "Con": 0, "Sab": 0, "Int": 0, "Sor": 0}
        for eq in self.todos_equipamentos_equipados():
            for k, v in eq.atributos_bonus.items():
                totais[k] = totais.get(k, 0) + int(v)
        return totais

    def resetar(self):
        self.consumiveis.clear()
        self.materiais.clear()
        self.equipamento_slot = None
        self.capacete_slot = None
        self.peitoral_slot = None
        self.calca_slot = None
        self.bota_slot = None
        self.amuletos_slots.clear()
        self.equipamentos_inventario.clear()
        self.equipamento_selecionado = None
        self.item_bilhete = ItemBilhete(quantidade=1)
        self.item_polidor = ItemPolidor(quantidade=0)

    def itens_do_inventario(self):
        itens = list(self.consumiveis) + list(self.materiais)
        if self.item_bilhete.quantidade > 0:
            itens.append(self.item_bilhete)
        if self.item_polidor.quantidade > 0:
            itens.append(self.item_polidor)
        itens.extend(self.equipamentos_inventario)
        return itens

    def custo_melhoria(self, equipamento=None):
        alvo = equipamento if equipamento is not None else self.obter_equipamento_alvo()
        if not alvo:
            return 0
        custo = alvo.nivel * 2
        if getattr(_obter_personagem_padrao(), "tem_talento", lambda t: False)("S2"):
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

def __getattr__(name):
    if name == "TelaInventario":
        from Telas.TelaInventario import TelaInventario
        return TelaInventario
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
