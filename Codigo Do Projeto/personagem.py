class personagem:

    def __init__(self,x,y):
        self.y = y
        self.x = x
        self.nome = "nome"
        self.vida = 30
        self.mpm = 6
        self.cor = (255,0,255)
        self.build = "nome do verso"
        self.nivel = 1
        self.atributo = { 
            "Agi": 1 ,
            "For": 1 ,
            "Con": 1 ,
            "Sab": 1 ,             
                    }
        

class inimigo:

    def __init__(self,x,y):
        self.y = y
        self.x = x
        self.xp = 5
        self.vida = 0
        self.mpm = 6
        self.cor = (255,0,255)
        self.categoria = "nome do verso" #Usaremos pra alterar os valores dos atributos
        self.atributo = { 
            "Agi": 1 ,
            "For": 1 ,
            "Con": 1 ,
            "Sab": 1 ,             
                    }