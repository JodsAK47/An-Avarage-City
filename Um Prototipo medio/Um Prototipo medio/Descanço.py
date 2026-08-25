import pygame
from Menu import Botao
from Entidades.Personagem import personagem
from Fontes import obter_fonte
class GerenciadorPosLuta:
    def __init__(self, tela):
        self.tela = tela
        self.largura = tela.get_width()
        self.jogadores = [personagem]

        self.fonte_titulo = obter_fonte(60)
        self.fonte_texto = obter_fonte(26)
        self.fonte_desc = obter_fonte(20)
        
        # Botões de Upgrade (quadrados pequenos de "+")
        bw, bh = 40, 40
        # Textos de atributos começam em x=200 abaixo; posicionamos os botões
        # à esquerda do texto para ficarem próximos ao rótulo correspondente.
        margem = 12
        x_texto = 200
        # armazena como atributo para uso em desenhar()
        self.x_texto = x_texto
        x_b = x_texto - bw - margem
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

    def atualizar_eventos(self, evento, posicao_mouse):
        if self.btn_continuar.checar_clique(evento, posicao_mouse):
            return "continuar"

        for jogador in self.jogadores:
            if getattr(jogador, 'pontos_atributo', 0) > 0:
                for botao_atributo, atributo in self.botoes_up:
                    if botao_atributo.checar_clique(evento, posicao_mouse):
                        jogador.atributos[atributo] += 1
                        jogador.pontos_atributo -= 1

                        if atributo == "Con":
                            jogador.max_hp += 10
                            jogador.hp += 10
                        elif atributo == "Sab":
                            jogador.max_mp += 2
                            jogador.mp += 2
        return None

    def atualizar(self, posicao_mouse, estado_clique_mouse):
        self.btn_continuar.atualizar(posicao_mouse, estado_clique_mouse)
        for jogador in self.jogadores:
            if getattr(jogador, 'pontos_atributo', 0) > 0:
                for botao_atributo, atributo in self.botoes_up:
                    botao_atributo.atualizar(posicao_mouse, estado_clique_mouse)

    def desenhar(self):
        self.tela.fill((20, 25, 35))

        tit = self.fonte_titulo.render("VITÓRIA!", True, (255, 215, 0))
        self.tela.blit(tit, ((self.largura - tit.get_width())//2, 80))

        coluna_largura = 420
        inicio_x = 140
        y_topo = 180
        espaco = 60

        for indice, jogador in enumerate(self.jogadores):
            x_coluna = inicio_x + indice * (coluna_largura + 40)
            nome_jogador = "JOGADOR 1" if jogador == personagem else "JOGADOR 2"
            txt_nome = self.fonte_texto.render(nome_jogador, True, (255,255,255))
            self.tela.blit(txt_nome, (x_coluna, y_topo))

            nivel = getattr(jogador, 'nivel', 1)
            xp = getattr(jogador, 'xp', 0)
            pts = getattr(jogador, 'pontos_atributo', 0)
            xp_prox_nivel = nivel * 100

            self.tela.blit(self.fonte_texto.render(f"NÍVEL: {nivel}", True, (255,255,255)), (x_coluna, y_topo + 40))
            self.tela.blit(self.fonte_texto.render(f"XP: {xp} / {xp_prox_nivel}", True, (150, 200, 255)), (x_coluna, y_topo + 80))
            cor_pts = (100, 255, 100) if pts > 0 else (150, 150, 150)
            self.tela.blit(self.fonte_texto.render(f"Pontos: {pts}", True, cor_pts), (x_coluna, y_topo + 120))

            nomes_attr = [
                "Força (Dano Físico)",
                "Agilidade (Dano Distância)",
                "Constituição (HP Máximo)",
                "Sabedoria (PM Máximo)",
                "Intelecto (Dano Magia)"
            ]
            chaves = ["For", "Agi", "Con", "Sab", "Int"]
            y_base = y_topo + 170
            for indice_atributo in range(5):
                valor = jogador.atributos.get(chaves[indice_atributo], 1)
                txt = self.fonte_desc.render(f"{nomes_attr[indice_atributo]}: {valor}", True, (255,255,255))
                self.tela.blit(txt, (x_coluna, y_base + indice_atributo * espaco))

            if pts > 0:
                for btn, attr in self.botoes_up:
                    btn.desenhar(self.tela)

        self.btn_continuar.desenhar(self.tela)
