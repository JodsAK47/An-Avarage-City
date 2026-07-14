import pygame
from Menu import Botao
from Entidades.Personagem import personagem

class GerenciadorPosLuta:
    def __init__(self, tela):
        self.tela = tela
        self.largura = tela.get_width()
        
        self.fonte_titulo = pygame.font.SysFont(["consolas", "courier"], 60, bold=True)
        self.fonte_texto = pygame.font.SysFont(["consolas", "courier"], 26, bold=True)
        self.fonte_desc = pygame.font.SysFont(["consolas", "courier"], 20)
        
        # Botões de Upgrade (quadrados pequenos de "+" )
        bw, bh = 40, 40
        x_b = 650
        y_base = 300
        espaco = 60
        
        self.btn_for = Botao(x_b, y_base, bw, bh, "+", (0,150,0), (0,255,0), bw, bh, cor_texto=(255,255,255))
        self.btn_agi = Botao(x_b, y_base+espaco, bw, bh, "+", (0,150,0), (0,255,0), bw, bh, cor_texto=(255,255,255))
        self.btn_con = Botao(x_b, y_base+espaco*2, bw, bh, "+", (0,150,0), (0,255,0), bw, bh, cor_texto=(255,255,255))
        self.btn_sab = Botao(x_b, y_base+espaco*3, bw, bh, "+", (0,150,0), (0,255,0), bw, bh, cor_texto=(255,255,255))
        self.btn_int = Botao(x_b, y_base+espaco*4, bw, bh, "+", (0,150,0), (0,255,0), bw, bh, cor_texto=(255,255,255))
        
        self.botoes_up = [
            (self.btn_for, "For"),
            (self.btn_agi, "Agi"),
            (self.btn_con, "Con"),
            (self.btn_sab, "Sab"),
            (self.btn_int, "Int")
        ]
        
        self.btn_continuar = Botao(self.largura//2 - 150, 650, 300, 60, "CONTINUAR", (100,100,100), (150,150,150), 300, 60, cor_texto=(255,255,255), fonte_tamanho=28)

    def atualizar_eventos(self, evento, mouse_pos):
        if self.btn_continuar.checar_clique(evento, mouse_pos):
            return "continuar"
            
        # Se tiver pontos para gastar, permite clicar no [+]
        if getattr(personagem, 'pontos_atributo', 0) > 0:
            for btn, attr in self.botoes_up:
                if btn.checar_clique(evento, mouse_pos):
                    personagem.atributos[attr] += 1
                    personagem.pontos_atributo -= 1
                    
                    # Bônus imediatos
                    if attr == "Con":
                        personagem.max_hp += 10
                        personagem.hp += 10
                    elif attr == "Sab":
                        personagem.max_mp += 2
                        personagem.mp += 2
        return None

    def atualizar(self, mouse_pos, mouse_click):
        self.btn_continuar.atualizar(mouse_pos, mouse_click)
        if getattr(personagem, 'pontos_atributo', 0) > 0:
            for btn, attr in self.botoes_up:
                btn.atualizar(mouse_pos, mouse_click)

    def desenhar(self):
        self.tela.fill((20, 25, 35))
        
        tit = self.fonte_titulo.render("VITÓRIA!", True, (255, 215, 0))
        self.tela.blit(tit, ((self.largura - tit.get_width())//2, 80))
        
        nivel = getattr(personagem, 'nivel', 1)
        xp = getattr(personagem, 'xp', 0)
        pts = getattr(personagem, 'pontos_atributo', 0)
        
        # Meta do próximo nível
        xp_prox_nivel = nivel * 100
        
        txt_nivel = self.fonte_texto.render(f"NÍVEL ATUAL: {nivel}", True, (255,255,255))
        txt_xp = self.fonte_texto.render(f"XP TOTAL: {xp} / {xp_prox_nivel}", True, (150, 200, 255))
        self.tela.blit(txt_nivel, (300, 180))
        self.tela.blit(txt_xp, (300, 220))
        
        # Cor verde se tiver pontos, cinza se não tiver
        cor_pts = (100, 255, 100) if pts > 0 else (150, 150, 150)
        txt_pts = self.fonte_texto.render(f"Pontos Disponíveis: {pts}", True, cor_pts)
        self.tela.blit(txt_pts, (300, 260))
        
        y_base = 310
        espaco = 60
        nomes_attr = [
            "Força (Dano Físico)", 
            "Agilidade (Dano Distância)", 
            "Constituição (HP Máximo)", 
            "Sabedoria (PM Máximo)", 
            "Intelecto (Dano Magia)"
        ]
        chaves = ["For", "Agi", "Con", "Sab", "Int"]
        
        for i in range(5):
            val = personagem.atributos.get(chaves[i], 1)
            txt = self.fonte_texto.render(f"{nomes_attr[i]}: {val}", True, (255,255,255))
            self.tela.blit(txt, (200, y_base + (i*espaco)))
            
        # Desenha os botões apenas se tiver pontos
        if pts > 0:
            for btn, attr in self.botoes_up:
                btn.desenhar(self.tela)
                
        self.btn_continuar.desenhar(self.tela)
