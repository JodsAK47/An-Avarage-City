class Habilidade:
    def __init__(self, nome, tipo, dano, custo_mp, precisao, descricao, efeito=None, chance_efeito=0.0, em_area=False):
        self.nome = nome
        self.tipo = tipo
        self.dano = dano              
        self.custo_mp = custo_mp      
        self.precisao = precisao      
        self.descricao = descricao    
        self.efeito = efeito          
        self.chance_efeito = chance_efeito 
        self.em_area = em_area

banco_habilidades = {
    "Soco": Habilidade(nome="Soco", tipo="Físico", dano=5, custo_mp=0, precisao=0.90, descricao="Um ataque corpo a corpo."),
    "Gelo": Habilidade(nome="Gelo", tipo="Magia", dano=5, custo_mp=1, precisao=0.80, descricao="Lança uma estaca de gelo.", efeito="Congelar", chance_efeito=0.10),
    "One Tap": Habilidade(nome="One Tap", tipo="Distância", dano=14, custo_mp=0, precisao=0.60, descricao="Tiro preciso e poderoso."),
    "Spray": Habilidade(nome="Spray", tipo="Distância", dano=9, custo_mp=2, precisao=0.70, descricao="Rajada de projéteis em área.", em_area=True),
    "Terremoto": Habilidade(nome="Terremoto", tipo="Físico", dano=8, custo_mp=3, precisao=0.85, descricao="Pisa forte, atingindo todos.", em_area=True),
    "Nevasca": Habilidade(nome="Nevasca", tipo="Magia", dano=10, custo_mp=4, precisao=0.75, descricao="Congela todos na tela.", efeito="Congelar", chance_efeito=0.15, em_area=True),
    "Fogo": Habilidade(nome="Fogo", tipo="Magia", dano=6, custo_mp=2, precisao=0.80, descricao="Encendeia todos na tela.", efeito="Queimar", chance_efeito=0.15, em_area=True),
    "Mordida": Habilidade(nome="Mordida", tipo="Físico", dano=6, custo_mp=0, precisao=0.95, descricao="Uma mordida selvagem."),
    "Porrete do Chefe": Habilidade(nome="Porrete do Chefe", tipo="Físico", dano=15, custo_mp=0, precisao=0.75, descricao="Golpe esmagador.")
}