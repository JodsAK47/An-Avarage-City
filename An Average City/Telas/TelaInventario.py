import pygame
from Sistemas.SistemaUI import Botao
from Sistemas.Fontes import obter_fonte
from Sistemas.Inventario import inventario_global


class TelaInventario:
    def __init__(self, tela):
        self.tela = tela
        self.fonte_titulo = obter_fonte(30)
        self.fonte_texto = obter_fonte(16)
        self.botao_voltar = Botao(50, 700, 150, 40, "VOLTAR", (100, 50, 50), (150, 50, 50), 50, 700, cor_texto=(255, 255, 255))
        self.botao_melhorar = Botao(700, 250, 200, 40, "MELHORAR (2 MAT)", (50, 100, 50), (50, 150, 50), 700, 250, cor_texto=(255, 255, 255))
        self.botoes_consumir = {}

    def atualizar_eventos(self, evento, posicao_mouse):
        if self.botao_voltar.checar_clique(evento, posicao_mouse):
            return "voltar"
            
        if self.botao_melhorar.checar_clique(evento, posicao_mouse):
            custo = inventario_global.custo_melhoria()
            if inventario_global.equipamento_slot and inventario_global.materiais_totais() >= custo:
                inventario_global.consumir_materiais(custo)
                inventario_global.equipamento_slot.melhorar()
                
        for nome, botao in self.botoes_consumir.items():
            if botao.checar_clique(evento, posicao_mouse):
                for c in inventario_global.consumiveis:
                    if c.nome == nome:
                        c.usar()
                        if c.quantidade <= 0:
                            inventario_global.consumiveis.remove(c)
                        break
        return None

    def atualizar(self, posicao_mouse, estado_clique_mouse):
        self.botao_voltar.atualizar(posicao_mouse, estado_clique_mouse)
        custo = inventario_global.custo_melhoria()
        self.botao_melhorar.texto = f"MELHORAR ({custo} MAT)"
        self.botao_melhorar.atualizar(posicao_mouse, estado_clique_mouse)
        for b in self.botoes_consumir.values():
            b.atualizar(posicao_mouse, estado_clique_mouse)

    def desenhar(self):
        self.tela.fill((20, 25, 35))
        titulo = self.fonte_titulo.render("INVENTÁRIO E EQUIPAMENTOS", True, (255, 255, 255))
        self.tela.blit(titulo, (50, 50))

        # Equipamento
        pygame.draw.rect(self.tela, (40, 50, 70), (50, 150, 400, 150), border_radius=8)
        txt_equip = self.fonte_texto.render("Equipamento Atual:", True, (200, 200, 200))
        self.tela.blit(txt_equip, (70, 170))
        
        if inventario_global.equipamento_slot:
            eq = inventario_global.equipamento_slot
            nome = self.fonte_titulo.render(f"{eq.nome} +{eq.nivel-1}", True, (255, 215, 0))
            self.tela.blit(nome, (70, 200))
            
            y_attr = 240
            for k, v in eq.atributos_bonus.items():
                if v > 0:
                    txt_attr = self.fonte_texto.render(f"+{v} {k}", True, (150, 255, 150))
                    self.tela.blit(txt_attr, (70, y_attr))
                    y_attr += 25
        else:
            nenhum = self.fonte_texto.render("Nenhum equipamento.", True, (100, 100, 100))
            self.tela.blit(nenhum, (70, 200))

        # Melhoria
        mats = inventario_global.materiais_totais()
        txt_mats = self.fonte_texto.render(f"Materiais disponíveis: {mats}", True, (200, 200, 200))
        self.tela.blit(txt_mats, (700, 150))
        self.botao_melhorar.desenhar(self.tela)

        # Consumíveis
        pygame.draw.rect(self.tela, (40, 50, 70), (50, 350, 850, 300), border_radius=8)
        txt_cons = self.fonte_texto.render("Consumíveis:", True, (200, 200, 200))
        self.tela.blit(txt_cons, (70, 370))

        self.botoes_consumir.clear()
        y_cons = 410
        for item in inventario_global.itens_do_inventario():
            if item.quantidade <= 0:
                continue

            if getattr(item, "tipo", None) == "material":
                txt_item = self.fonte_texto.render(f"{item.quantidade}x {item.nome} - {item.descricao}", True, (255, 220, 130))
                self.tela.blit(txt_item, (70, y_cons))
                y_cons += 40
                continue

            txt_c = self.fonte_texto.render(f"{item.quantidade}x {item.nome} - {item.descricao}", True, (255, 255, 255))
            self.tela.blit(txt_c, (70, y_cons))
            btn_usar = Botao(700, y_cons, 100, 30, "USAR", (50, 100, 200), (50, 150, 250), 700, y_cons, cor_texto=(255, 255, 255), fonte_tamanho=12)
            self.botoes_consumir[item.nome] = btn_usar
            btn_usar.desenhar(self.tela)
            y_cons += 40

        self.botao_voltar.desenhar(self.tela)
