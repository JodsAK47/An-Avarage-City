# ==========================================
# CatalogoInimigos.py
# ==========================================

# Dicionário central com as fichas de todos os inimigos
DADOS_INIMIGOS = {
    "Goblin Verde": {
        "max_hp": 25,
        "ataques": ["Mordida", "Soco"],
        "xp": 30,
        "atributos": {"For": 2, "Agi": 3, "Int": 0},
        "verso":"Jujutsu"
    },
    "Goblin Corredor": {
        "max_hp": 20,
        "ataques": ["Mordida"],
        "xp": 20,
        "atributos": {"For": 1, "Agi": 5, "Int": 0}
    },
    "Morcego Gigante": {
        "max_hp": 35,
        "ataques": ["Mordida"],
        "xp": 40,
        "atributos": {"For": 3, "Agi": 4, "Int": 0}
    },
    "Troll da Caverna": {
        "max_hp": 50,
        "ataques": ["Porrete do Chefe", "Soco"],
        "xp": 60,
        "atributos": {"For": 6, "Agi": 1, "Int": 0}
    },
    "Arqueiro Esqueleto": {
        "max_hp": 40,
        "ataques": ["Flechada Letal"],
        "xp": 50,
        "atributos": {"For": 1, "Agi": 6, "Int": 0}
    },
    "Mago Sombrio": {
        "max_hp": 35,
        "ataques": ["Gelo", "Soco"],
        "xp": 50,
        "atributos": {"For": 1, "Agi": 2, "Int": 5}
    },
    "Senhor da Guerra": {
        "max_hp": 120,
        "ataques": ["Porrete do Chefe", "Soco", "Flechada Letal"],
        "xp": 200,
        "atributos": {"For": 8, "Agi": 4, "Int": 2}
    }
}

def carregar_inimigo(objeto_inimigo, nome_inimigo):

    if nome_inimigo in DADOS_INIMIGOS:
        ficha = DADOS_INIMIGOS[nome_inimigo]
        
        objeto_inimigo.nome = nome_inimigo
        objeto_inimigo.max_hp = ficha["max_hp"]
        objeto_inimigo.hp = ficha["max_hp"]
        objeto_inimigo.ataques = ficha["ataques"]
        objeto_inimigo.xp = ficha["xp"]
        
        # O .copy() é crucial para evitar que dois goblins compartilhem a mesma memória de atributos
        objeto_inimigo.atributos = ficha["atributos"].copy()
        
        # Reseta os status padrão da entidade
        objeto_inimigo.mp = getattr(objeto_inimigo, 'max_mp', 0)
        objeto_inimigo.congelado = False
        
    return objeto_inimigo