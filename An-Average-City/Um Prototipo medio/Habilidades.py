class Habilidade:
    def __init__(self, nome, tipo, dano, custo_mp, precisao, descricao, efeito=None, chance_efeito=0.0, em_area=False, verso="Nenhum"):
        self.nome = nome
        self.tipo = tipo
        self.dano = dano              
        self.custo_mp = custo_mp      
        self.precisao = precisao      
        self.descricao = descricao    
        self.efeito = efeito          
        self.chance_efeito = chance_efeito 
        self.em_area = em_area
        self.verso = verso

banco_habilidades = {
    # Sobrevivente: 2 ataques físicos, 2 mágicos e 2 à distância.
    "Machadada": Habilidade(nome="Machadada", tipo="Físico", dano=5, custo_mp=0, precisao=0.90, descricao="Golpeia um inimigo com um machado.", verso="Sobrevivente"),
    "HamBat": Habilidade(nome="HamBat", tipo="Físico", dano=8, custo_mp=3, precisao=0.85, descricao="Bate no chão e causa dano a todos os inimigos.", em_area=True, verso="Sobrevivente"),
    "Tentaculo Das Sombras": Habilidade(nome="Tentaculo Das Sombras", tipo="Magia", dano=5, custo_mp=2, chance_efeito=0.50, efeito="Congelar", precisao=0.85, descricao="Invoca tentáculos que atingem todos os inimigos e podem congelá-los.", em_area=True, verso="Sobrevivente"),
    "Chamas Das Trevas": Habilidade(nome="Chamas Das Trevas", tipo="Magia", dano=10, custo_mp=4, precisao=0.75, descricao="Lança chamas sombrias contra um inimigo.", verso="Sobrevivente"),
    "Boomerang": Habilidade(nome="Boomerang", tipo="Distância", dano=6, custo_mp=0, precisao=0.90, descricao="Arremessa um bumerangue contra um inimigo.", verso="Sobrevivente"),
    "Estilingada de Vidro": Habilidade(nome="Estilingada de Vidro", tipo="Distância", dano=11, custo_mp=1, precisao=0.75, descricao="Dispara um fragmento de vidro contra um inimigo.", verso="Sobrevivente"),

    # Feiticeiro: 2 ataques físicos, 2 mágicos e 2 à distância.
    "Flash Negro": Habilidade(nome="Flash Negro", tipo="Físico", dano=8, custo_mp=1, precisao=0.85, descricao="Canaliza energia amaldiçoada em um golpe físico.", verso="Feiticeiro"),
    "Colisão 24 Frames": Habilidade(nome="Colisão 24 Frames", tipo="Físico", dano=12, custo_mp=3, precisao=0.70, descricao="Concentra força arcana em um impacto contra um inimigo.", verso="Feiticeiro"),
    "Azul": Habilidade(nome="Azul", tipo="Magia", dano=5, custo_mp=1, precisao=0.80, descricao="Dispara uma força azul que pode congelar um inimigo.", efeito="Congelar", chance_efeito=0.10, verso="Feiticeiro"),
    "Vermelho": Habilidade(nome="Vermelho", tipo="Magia", dano=10, custo_mp=4, precisao=0.75, descricao="Libera uma explosão que atinge todos os inimigos e pode congelá-los.", efeito="Congelar", chance_efeito=0.15, em_area=True, verso="Feiticeiro"),
    "Disparo Lazer": Habilidade(nome="Disparo Lazer", tipo="Distância", dano=9, custo_mp=2, precisao=0.80, descricao="Dispara um orbe de energia contra um inimigo.", verso="Feiticeiro"),
    "La Jullyet": Habilidade(nome="La Jullyet", tipo="Distância", dano=20, custo_mp=3, precisao=0.70, descricao="Projeta um raio concentrado contra um inimigo.", verso="Feiticeiro"),

    # Agente: 2 ataques físicos, 2 mágicos e 2 à distância.
    "Facada": Habilidade(nome="Facada", tipo="Físico", dano=9, custo_mp=0, precisao=0.85, descricao="Avança e golpeia um inimigo.", verso="Agente"),
    "Segura o Regue": Habilidade(nome="Segura o Regue", tipo="Físico", dano=7, custo_mp=0, precisao=0.90, descricao="Ataca um inimigo com um golpe rápido.", verso="Agente"),
    "Head Hunter": Habilidade(nome="Head Hunter", tipo="Distância", dano=6, custo_mp=2, precisao=0.80, descricao="Dispara contra todos os inimigos e pode queimá-los.", efeito="Queimar", chance_efeito=0.15, em_area=True, verso="Agente"),
    "Tour de Force": Habilidade(nome="Tour de Force", tipo="Distância", dano=11, custo_mp=4, precisao=0.75, descricao="Atinge um inimigo com um disparo concentrado.", verso="Agente"),
    "Domo Compressado": Habilidade(nome="Domo Compressado", tipo="Magia", dano=14, custo_mp=0, precisao=0.60, descricao="Cria um domo de energia que explode em um inimigo.", verso="Agente"),
    "Mare Dagua": Habilidade(nome="Mare Dagua", tipo="Magia", dano=10, custo_mp=2, precisao=0.70, descricao="Invoca uma onda que atinge todos os inimigos.", em_area=True, verso="Agente")
}