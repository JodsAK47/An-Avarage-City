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
        self.botao_melhorar = Botao(700, 220, 220, 40, "MELHORAR (2 MAT)", (50, 100, 50), (50, 150, 50), 700, 220, cor_texto=(255, 255, 255))
        self.botoes_consumir = {}

    def atualizar_eventos(self, evento, posicao_mouse):
        if self.botao_voltar.checar_clique(evento, posicao_mouse):
            return "voltar"

        if self.botao_melhorar.checar_clique(evento, posicao_mouse):
            alvo = inventario_global.obter_equipamento_alvo()
            custo = inventario_global.custo_melhoria(alvo)
            if alvo and inventario_global.materiais_totais() >= custo:
                inventario_global.consumir_materiais(custo)
                alvo.melhorar()

            inventario_global.comprar_equipamento_loja()

        for chave, (botao, item_ref) in list(self.botoes_consumir.items()):
            if botao.checar_clique(evento, posicao_mouse):
                if getattr(item_ref, "tipo", None) == "polidor":
                    inventario_global.usar_polidor_itens()
                    break
                if getattr(item_ref, "tipo", None) == "equipamento":
                    inventario_global.equipar(item_ref)
                    break
                for c in inventario_global.consumiveis:
                    if c.nome == item_ref.nome:
                        c.usar()
                        if c.quantidade <= 0:
                            inventario_global.consumiveis.remove(c)
                        break
        return None

    def atualizar(self, posicao_mouse, estado_clique_mouse):
        self.botao_voltar.atualizar(posicao_mouse, estado_clique_mouse)
        alvo = inventario_global.obter_equipamento_alvo()
        custo = inventario_global.custo_melhoria(alvo)
        self.botao_melhorar.texto = f"MELHORAR ({custo} MAT)"
        self.botao_melhorar.atualizar(posicao_mouse, estado_clique_mouse)
        for b, _ in self.botoes_consumir.values():
            b.atualizar(posicao_mouse, estado_clique_mouse)

    def desenhar(self):
        self.tela.fill((20, 25, 35))
        titulo = self.fonte_titulo.render("INVENTÁRIO E EQUIPAMENTOS", True, (255, 255, 255))
        self.tela.blit(titulo, (50, 50))

        pygame.draw.rect(self.tela, (40, 50, 70), (50, 130, 600, 195), border_radius=8)
        txt_equipamento = self.fonte_texto.render("Equipamentos Equipados (Capacete, Peitoral, Calça, Bota, Amuletos x3):", True, (200, 200, 200))
        self.tela.blit(txt_equipamento, (70, 145))

        equipados = inventario_global.todos_equipamentos_equipados()
        if equipados:
            y_eq = 175
            for eq in equipados[:6]:
                sufixo_polido = " [Polido]" if getattr(eq, "polido", False) else ""
                bonus_str = ", ".join(f"+{v} {k}" for k, v in eq.atributos_bonus.items() if v > 0)
                linha = self.fonte_texto.render(f"[{eq.categoria.upper()}] {eq.nome} +{eq.nivel-1}{sufixo_polido} ({bonus_str})", True, (255, 215, 0))
                self.tela.blit(linha, (70, y_eq))
                y_eq += 24
        else:
            nenhum = self.fonte_texto.render("Nenhum equipamento equipado.", True, (100, 100, 100))
            self.tela.blit(nenhum, (70, 190))

        mats = inventario_global.materiais_totais()
        txt_mats = self.fonte_texto.render(f"Materiais disponíveis: {mats}", True, (200, 200, 200))
        self.tela.blit(txt_mats, (700, 150))
        self.botao_melhorar.desenhar(self.tela)

        pygame.draw.rect(self.tela, (40, 50, 70), (50, 350, 850, 300), border_radius=8)
        txt_cons = self.fonte_texto.render("Mochila (Consumíveis e Equipamentos):", True, (200, 200, 200))
        self.tela.blit(txt_cons, (70, 370))

        self.botoes_consumir.clear()
        y_cons = 410
        for idx, item in enumerate(inventario_global.itens_do_inventario()):
            if item.quantidade <= 0:
                continue

            if getattr(item, "tipo", None) == "material":
                txt_item = self.fonte_texto.render(f"{item.quantidade}x {item.nome} - {item.descricao}", True, (255, 220, 130))
                self.tela.blit(txt_item, (70, y_cons))
                y_cons += 36
                continue

            if getattr(item, "tipo", None) == "bilhete" or item.nome == "Bilhete do Dormitório":
                txt_item = self.fonte_texto.render(f"{item.quantidade}x {item.nome} - {item.descricao}", True, (255, 205, 110))
                self.tela.blit(txt_item, (70, y_cons))
                y_cons += 36
                continue

            rotulo_btn = "EQUIPAR" if getattr(item, "tipo", None) == "equipamento" else "USAR"
            txt_c = self.fonte_texto.render(f"{item.quantidade}x {item.nome} - {item.descricao}", True, (255, 255, 255))
            self.tela.blit(txt_c, (70, y_cons))
            btn_usar = Botao(700, y_cons, 110, 28, rotulo_btn, (50, 100, 200), (50, 150, 250), 700, y_cons, cor_texto=(255, 255, 255), fonte_tamanho=12)
            self.botoes_consumir[f"{idx}:{item.nome}"] = (btn_usar, item)
            btn_usar.desenhar(self.tela)
            y_cons += 36

        self.botao_voltar.desenhar(self.tela)

