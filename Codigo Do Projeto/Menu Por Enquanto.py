import pygame

pygame.init()

# ======================
# CONFIGURAÇÕES DA TELA
# ======================
LARGURA = 800
ALTURA = 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Menu Orientado a Objetos")

clock = pygame.time.Clock()

# ======================
# CLASSE BOTÃO
# ======================
class Botao:
    def __init__(self, x, y, largura, altura, texto, cor_base, cor_hover, largura_hover, altura_hover, cor_texto=(0, 0, 0), fonte_tamanho=40):
        # Guardamos a posição central original para o efeito de expansão/contração centralizada
        self.x_centro = x + largura // 2
        self.y_centro = y + altura // 2
        
        self.largura_base = largura
        self.altura_base = altura
        self.largura_hover = largura_hover
        self.altura_hover = altura_hover
        
        # Criamos as dimensões para o clique (menor que o tamanho base)
        # Reduzimos em 10 pixels a largura e 5 pixels a altura (pode ajustar como preferir)
        self.largura_clique = largura - 10
        self.altura_clique = altura - 5
        
        # O rect principal que o Pygame usa
        self.rect = pygame.Rect(x, y, largura, altura)
        
        self.texto = texto
        self.cor_base = cor_base
        self.cor_hover = cor_hover
        self.cor_atual = cor_base
        
        # Renderização do texto
        self.fonte = pygame.font.SysFont(None, fonte_tamanho)
        self.txt_renderizado = self.fonte.render(texto, True, cor_texto)
        self.txt_rect = self.txt_renderizado.get_rect(center=self.rect.center)

    def atualizar(self, posicao_mouse, clique_mouse):
        # Se o mouse colidir com o botão
        if self.rect.collidepoint(posicao_mouse):
            self.cor_atual = self.cor_hover
            
            # Se o botão esquerdo do mouse estiver pressionado (clique_mouse[0] == True)
            if clique_mouse[0]:
                self.rect.width = self.largura_clique
                self.rect.height = self.altura_clique
            else:
                # Apenas passando o mouse por cima
                self.rect.width = self.largura_hover
                self.rect.height = self.altura_hover
        else:
            self.cor_atual = self.cor_base
            # Volta ao tamanho original fora do botão
            self.rect.width = self.largura_base
            self.rect.height = self.altura_base
            
        # Re-centraliza o botão e o texto para o efeito ficar perfeito
        self.rect.center = (self.x_centro, self.y_centro)
        self.txt_rect.center = self.rect.center

    def desenhar(self, superficie):
        # Desenha o retângulo do botão com o tamanho atualizado
        pygame.draw.rect(superficie, self.cor_atual, self.rect)
        superficie.blit(self.txt_renderizado, self.txt_rect)

    def clicado(self, posicao_mouse):
        return self.rect.collidepoint(posicao_mouse)


# ======================
# INICIALIZAÇÃO DOS ELEMENTOS
# ======================
fonte_titulo = pygame.font.SysFont(None, 60)
txt_titulo = fonte_titulo.render("MENU", True, (255, 255, 255))
titulo_rect = pygame.Rect(250, 50, 300, 80)

botao_jogar = Botao(300, 200, 190, 55, "JOGAR", (0, 200, 0), (0, 255, 0), 200, 60)
botao_creditos = Botao(300, 300, 190, 55, "CRÉDITOS", (200, 200, 0), (255, 255, 0), 200, 60)
botao_sair = Botao(300, 400, 190, 55, "SAIR", (200, 0, 0), (255, 0, 0), 200, 60, cor_texto=(255, 255, 255))

lista_botoes = [botao_jogar, botao_creditos, botao_sair]

# ======================
# LOOP PRINCIPAL
# ======================
rodando = True

while rodando:
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed() # Captura o estado dos botões do mouse (True/False)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        # O clique definitivo da ação ainda acontece aqui no MOUSEBUTTONDOWN
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1: # Garante que é o botão esquerdo
                if botao_jogar.clicado(mouse_pos):
                    print("Jogar")
                    
                if botao_creditos.clicado(mouse_pos):
                    print("Créditos")
                    
                if botao_sair.clicado(mouse_pos):
                    rodando = False

    # Fundo
    tela.fill((30, 30, 40))

    # Desenhar Título fixo
    pygame.draw.rect(tela, (80, 80, 200), titulo_rect)
    tela.blit(txt_titulo, txt_titulo.get_rect(center=titulo_rect.center))

    # Atualizar e Desenhar os Botões dinamicamente
    for botao in lista_botoes:
        # Passamos a posição E o estado do clique para o método atualizar
        botao.atualizar(mouse_pos, mouse_click)
        botao.desenhar(tela)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()