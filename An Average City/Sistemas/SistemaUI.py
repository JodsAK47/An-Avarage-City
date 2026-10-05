import math
from typing import Callable, Optional, Any, Dict, List, Tuple
import pygame
from Sistemas.Fontes import obter_fonte
from Sistemas.Recursos import caminho_botao, caminho_imagem


class Botao:
    """
    Componente reutilizável de Botão encapsulado.
    
    Suporta:
    - Assinatura moderna com valores padrão inteligentes.
    - 100% de retrocompatibilidade com a assinatura legada de 9+ argumentos posicionais.
    - Callback opcional `acao` disparado no clique.
    - Transições suaves de hover (aumento de tamanho e realce de cor).
    - Sprites visuais (base, hover e clique) ou renderização vetorial arredondada.
    - Modo alternador (toggle/switch).
    """

    def __init__(
        self,
        x: int,
        y: int,
        largura: int,
        altura: int,
        texto: str = "",
        cor_base: Tuple[int, int, int] = (50, 58, 72),
        cor_hover: Optional[Tuple[int, int, int]] = None,
        largura_hover: Optional[int] = None,
        altura_hover: Optional[int] = None,
        cor_texto: Tuple[int, int, int] = (240, 245, 250),
        fonte_tamanho: int = 16,
        sprite_base_path: Optional[str] = None,
        sprite_hover_path: Optional[str] = None,
        sprite_clique_path: Optional[str] = None,
        alternado: bool = False,
        ativo_inicial: bool = False,
        acao: Optional[Callable[[], Any]] = None,
        borda_raio: int = 6,
        tooltip: str = "",
        id_botao: Optional[str] = None,
        sem_texto: bool = False
    ):
        self.x_centro = x + largura // 2
        self.y_centro = y + altura // 2
        self.largura_base = largura
        self.altura_base = altura

        # Se hover não foi especificado, calcula expansão natural de +6x+4
        self.largura_hover = largura_hover if largura_hover is not None else largura + 6
        self.altura_hover = altura_hover if altura_hover is not None else altura + 4

        self.largura_clique = max(10, largura - 8)
        self.altura_clique = max(8, altura - 4)

        self.rect = pygame.Rect(x, y, largura, altura)
        self.pressionado = False
        self.alternado = alternado
        self.ativo = ativo_inicial
        self.sem_texto = sem_texto
        self.acao = acao
        self.borda_raio = borda_raio
        self.tooltip = tooltip
        self.id_botao = id_botao

        self.cor_base = cor_base
        # Se cor_hover não foi especificada, calcula tom iluminado automaticamente
        if cor_hover is not None:
            self.cor_hover = cor_hover
        else:
            self.cor_hover = tuple(min(255, int(c * 1.3 + 25)) for c in cor_base)

        self.cor_texto = cor_texto
        self.cor_atual = self.cor_base
        self.texto = str(texto)
        self.fonte_tamanho = fonte_tamanho

        # Configuração de Sprites
        sprite_base_path = sprite_base_path or None
        sprite_hover_path = sprite_hover_path or sprite_base_path
        sprite_clique_path = sprite_clique_path or sprite_base_path

        self.usar_sprites = bool(sprite_base_path and sprite_clique_path)
        self.sprite_base = None
        self.sprite_hover = None
        self.sprite_clique = None
        self.sprite_atual = None

        if self.usar_sprites:
            try:
                caminho_base = caminho_botao(sprite_base_path)
                caminho_hover = caminho_botao(sprite_hover_path)
                caminho_clique = caminho_botao(sprite_clique_path)

                img_base = pygame.image.load(caminho_base)
                if pygame.display.get_surface() is not None:
                    img_base = img_base.convert_alpha()
                self.sprite_base = pygame.transform.scale(img_base, (largura, altura))

                img_hover = pygame.image.load(caminho_hover)
                if pygame.display.get_surface() is not None:
                    img_hover = img_hover.convert_alpha()
                self.sprite_hover = pygame.transform.scale(img_hover, (largura, altura))

                img_clique = pygame.image.load(caminho_clique)
                if pygame.display.get_surface() is not None:
                    img_clique = img_clique.convert_alpha()
                self.sprite_clique = pygame.transform.scale(img_clique, (largura, altura))

                self.sprite_atual = self.sprite_base
            except (FileNotFoundError, pygame.error) as erro:
                print(f"[Aviso] Nao foi possivel carregar os sprites do botao '{texto}': {erro}")
                self.usar_sprites = False

        self.fonte = obter_fonte(fonte_tamanho)
        self._atualizar_superficie_texto()

    def _atualizar_superficie_texto(self):
        """Renderiza e centraliza a superfície de texto do botão."""
        if self.texto:
            self.txt_renderizado = self.fonte.render(self.texto, True, self.cor_texto)
            self.txt_rect = self.txt_renderizado.get_rect(center=self.rect.center)
        else:
            self.txt_renderizado = None
            self.txt_rect = self.rect.copy()

    def definir_texto(self, novo_texto: str):
        """Atualiza o texto exibido no botão dinamicamente."""
        self.texto = str(novo_texto)
        self._atualizar_superficie_texto()

    def definir_ativo(self, ativo: bool):
        """Define o estado ativo em botões do tipo alternador."""
        self.ativo = bool(ativo)

    def checar_clique(self, evento: pygame.event.Event, posicao_mouse: Tuple[int, int]) -> Any:
        """
        Verifica se o botão foi clicado (MOUSEBUTTONDOWN seguido de MOUSEBUTTONUP dentro do botão).
        Se possuir um callback `acao`, ele é executado e o retorno da ação é repassado.
        Caso contrário, retorna True em caso de clique ou False caso não clicado.
        """
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(posicao_mouse):
                self.pressionado = True

        if evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            if self.pressionado and self.rect.collidepoint(posicao_mouse):
                self.pressionado = False
                if self.alternado:
                    self.ativo = not self.ativo

                if self.acao is not None:
                    resultado = self.acao()
                    return resultado if resultado is not None else True
                return True
            self.pressionado = False

        return False

    def clicado(self, posicao_mouse: Tuple[int, int]) -> bool:
        """Verificação simples de colisão com o ponto do mouse."""
        return self.rect.collidepoint(posicao_mouse)

    def atualizar(self, posicao_mouse: Tuple[int, int], estado_clique_mouse: Tuple[bool, ...]):
        """Atualiza a geometria e cores do botão de acordo com o estado do mouse (Hover / Pressionado)."""
        if self.alternado:
            if self.usar_sprites:
                self.sprite_atual = self.sprite_clique if self.ativo else self.sprite_base
            self.cor_atual = self.cor_hover if self.ativo else self.cor_base
            self.rect.width = self.largura_base
            self.rect.height = self.altura_base
            self.rect.center = (self.x_centro, self.y_centro)
            if self.txt_rect:
                self.txt_rect.center = self.rect.center
            return

        if self.rect.collidepoint(posicao_mouse):
            self.cor_atual = self.cor_hover
            if estado_clique_mouse[0]:
                if self.usar_sprites:
                    self.sprite_atual = self.sprite_clique
                self.rect.width = self.largura_clique
                self.rect.height = self.altura_clique
            else:
                if self.usar_sprites:
                    self.sprite_atual = self.sprite_hover
                self.rect.width = self.largura_hover
                self.rect.height = self.altura_hover
        else:
            if self.usar_sprites:
                self.sprite_atual = self.sprite_base
            self.cor_atual = self.cor_base
            self.rect.width = self.largura_base
            self.rect.height = self.altura_base

        self.rect.center = (self.x_centro, self.y_centro)
        if self.txt_rect:
            self.txt_rect.center = self.rect.center

    def desenhar(self, superficie: pygame.Surface):
        """Renderiza o botão na superfície informada."""
        if self.usar_sprites and self.sprite_atual is not None:
            superficie.blit(self.sprite_atual, self.rect)
            if not self.sem_texto and self.txt_renderizado is not None:
                superficie.blit(self.txt_renderizado, self.txt_rect)
        else:
            pygame.draw.rect(superficie, self.cor_atual, self.rect, border_radius=self.borda_raio)
            if not self.sem_texto and self.txt_renderizado is not None:
                superficie.blit(self.txt_renderizado, self.txt_rect)


class TelaBase:
    """
    Classe Abstrata / Base para todas as Telas do jogo.
    
    Encapsula:
    - Superfície de desenho (`self.tela`) e dimensões (`largura`, `altura`).
    - Gerenciamento e fábrica de botões (`criar_botao`, `adicionar_botao`).
    - Carregamento padronizado de imagem de fundo com escala proporcional e centralização.
    - Sistema integrado de mensagens temporárias de feedback (*toast*).
    - Ciclo de vida uniforme (`ao_entrar`, `ao_sair`, `atualizar_eventos`, `atualizar`, `desenhar`).
    """

    def __init__(self, tela: pygame.Surface, gerenciador_telas=None, nome: str = "tela"):
        self.tela = tela
        self.largura = tela.get_width() if tela else 1000
        self.altura = tela.get_height() if tela else 800
        self.gerenciador_telas = gerenciador_telas
        self.nome = nome

        # Cores e Fundo
        self.cor_fundo: Tuple[int, int, int] = (16, 20, 26)
        self.imagem_fundo: Optional[pygame.Surface] = None
        self.posicao_fundo: Tuple[int, int] = (0, 0)
        self.escala_fundo: float = 1.0

        # Coleção de Botões
        self.botoes: List[Botao] = []
        self.mapa_botoes: Dict[str, Botao] = {}

        # Feedback Temporário (Toasts / Avisos na tela)
        self.msg_feedback: Optional[str] = None
        self.cor_feedback: Tuple[int, int, int] = (100, 255, 140)
        self.timer_feedback: int = 0
        self.fonte_feedback = obter_fonte(14)

        # Flag utilitária comum em telas com botão voltar
        self.voltar_clicado: bool = False

    def criar_botao(
        self,
        x: int,
        y: int,
        largura: int,
        altura: int,
        texto: str = "",
        cor_base: Tuple[int, int, int] = (50, 58, 72),
        cor_hover: Optional[Tuple[int, int, int]] = None,
        largura_hover: Optional[int] = None,
        altura_hover: Optional[int] = None,
        cor_texto: Tuple[int, int, int] = (240, 245, 250),
        fonte_tamanho: int = 16,
        sprite_base_path: Optional[str] = None,
        sprite_hover_path: Optional[str] = None,
        sprite_clique_path: Optional[str] = None,
        alternado: bool = False,
        ativo_inicial: bool = False,
        acao: Optional[Callable[[], Any]] = None,
        borda_raio: int = 6,
        id_botao: Optional[str] = None
    ) -> Botao:
        """
        Fábrica de botões: instancia um novo `Botao`, registra-o na tela
        e o adiciona automaticamente ao ciclo de atualização, desenho e eventos.
        """
        botao = Botao(
            x=x,
            y=y,
            largura=largura,
            altura=altura,
            texto=texto,
            cor_base=cor_base,
            cor_hover=cor_hover,
            largura_hover=largura_hover,
            altura_hover=altura_hover,
            cor_texto=cor_texto,
            fonte_tamanho=fonte_tamanho,
            sprite_base_path=sprite_base_path,
            sprite_hover_path=sprite_hover_path,
            sprite_clique_path=sprite_clique_path,
            alternado=alternado,
            ativo_inicial=ativo_inicial,
            acao=acao,
            borda_raio=borda_raio,
            id_botao=id_botao
        )
        self.adicionar_botao(botao, id_botao)
        return botao

    def adicionar_botao(self, botao: Botao, id_botao: Optional[str] = None):
        """Registra um botão existente no gerenciamento da tela."""
        if botao not in self.botoes:
            self.botoes.append(botao)
        chave = id_botao or botao.id_botao
        if chave:
            self.mapa_botoes[chave] = botao

    def remover_botao(self, botao: Botao):
        """Remove um botão do gerenciamento da tela."""
        if botao in self.botoes:
            self.botoes.remove(botao)
        for chave, b in list(self.mapa_botoes.items()):
            if b == botao:
                del self.mapa_botoes[chave]

    def limpar_botoes(self):
        """Limpa todos os botões registrados."""
        self.botoes.clear()
        self.mapa_botoes.clear()

    def carregar_fundo(self, nome_arquivo: str, pasta: str = "sprites") -> bool:
        """
        Carrega uma imagem de fundo, calcula a escala correta cobrindo a tela
        sem distorcer a proporção, e calcula as coordenadas para centralização perfeita.
        """
        try:
            if pasta.lower() == "botoes":
                caminho = caminho_botao(nome_arquivo)
            else:
                caminho = caminho_imagem(nome_arquivo)

            imagem_original = pygame.image.load(caminho)
            if pygame.display.get_surface() is not None:
                imagem_original = imagem_original.convert()
            escala = max(self.largura / imagem_original.get_width(), self.altura / imagem_original.get_height())
            novo_tamanho = (int(imagem_original.get_width() * escala), int(imagem_original.get_height() * escala))
            self.imagem_fundo = pygame.transform.scale(imagem_original, novo_tamanho)
            x_fundo = (self.largura - novo_tamanho[0]) // 2
            y_fundo = (self.altura - novo_tamanho[1]) // 2
            self.posicao_fundo = (x_fundo, y_fundo)
            self.escala_fundo = escala
            return True
        except (FileNotFoundError, pygame.error) as erro:
            print(f"[Aviso] Nao foi possivel carregar o fundo '{nome_arquivo}': {erro}")
            self.imagem_fundo = None
            self.posicao_fundo = (0, 0)
            self.escala_fundo = 1.0
            return False

    def mostrar_feedback(self, mensagem: str, cor: Tuple[int, int, int] = (100, 255, 140), duracao: int = 120):
        """Exibe uma mensagem temporária de aviso/sucesso na tela."""
        self.msg_feedback = mensagem
        self.cor_feedback = cor
        self.timer_feedback = duracao

    # ==========================
    # Ganchos de Ciclo de Vida
    # ==========================
    def ao_entrar(self, **kwargs):
        """Chamado quando a tela se torna ativa."""
        self.voltar_clicado = False

    def ao_sair(self):
        """Chamado quando a tela deixa de ser ativa."""
        pass

    def atualizar_eventos(self, evento: pygame.event.Event, posicao_mouse: Tuple[int, int]) -> Any:
        """
        Processa eventos. Por padrão, testa cliques em todos os botões registrados.
        Se um botão possuir callback ou for clicado, retorna a ação ou True.
        Subclasses podem sobrescrever para adicionar atalhos de teclado ou áreas especiais.
        """
        for botao in self.botoes:
            resultado = botao.checar_clique(evento, posicao_mouse)
            if resultado:
                return resultado
        return None

    def atualizar(self, posicao_mouse: Tuple[int, int], estado_clique_mouse: Tuple[bool, ...]):
        """
        Atualiza o estado de todos os botões e temporizadores.
        Chama `atualizar_conteudo` para lógicas específicas da subclasse.
        """
        if self.timer_feedback > 0:
            self.timer_feedback -= 1

        for botao in self.botoes:
            botao.atualizar(posicao_mouse, estado_clique_mouse)

        self.atualizar_conteudo(posicao_mouse, estado_clique_mouse)

    def atualizar_conteudo(self, posicao_mouse: Tuple[int, int], estado_clique_mouse: Tuple[bool, ...]):
        """Gancho opcional para lógica dinâmica de subclasses (ex: timers, animações)."""
        pass

    def desenhar(self):
        """
        Pipeline padronizado de renderização:
        1. Desenha o fundo (imagem ou cor sólida).
        2. Chama `desenhar_conteudo()` (específico da tela).
        3. Desenha automaticamente todos os botões registrados.
        4. Renderiza feedback temporário se ativo.
        """
        if self.imagem_fundo is not None:
            self.tela.blit(self.imagem_fundo, self.posicao_fundo)
        else:
            self.tela.fill(self.cor_fundo)

        self.desenhar_conteudo()

        for botao in self.botoes:
            botao.desenhar(self.tela)

        self.desenhar_feedback()

    def desenhar_conteudo(self):
        """Método de gancho onde a subclasse desenha seus textos, painéis e elementos exclusivos."""
        pass

    def desenhar_feedback(self):
        """Desenha a caixa de feedback/aviso no topo da tela se ativo."""
        if self.timer_feedback <= 0 or not self.msg_feedback:
            return

        alpha = min(255, self.timer_feedback * 6)
        surf_msg = self.fonte_feedback.render(self.msg_feedback, True, self.cor_feedback)
        largura_box = surf_msg.get_width() + 40
        altura_box = surf_msg.get_height() + 16
        x_box = (self.largura - largura_box) // 2
        y_box = 24

        overlay = pygame.Surface((largura_box, altura_box), pygame.SRCALPHA)
        overlay.fill((16, 20, 26, int(min(230, alpha))))
        pygame.draw.rect(overlay, (*self.cor_feedback[:3], int(alpha)), overlay.get_rect(), width=1, border_radius=6)
        surf_msg.set_alpha(alpha)
        overlay.blit(surf_msg, (20, 8))

        self.tela.blit(overlay, (x_box, y_box))


class GerenciadorTelas:
    """
    Máquina de estados centralizada para navegação de telas.
    
    Gerencia:
    - Registro de instâncias de `TelaBase`.
    - Troca de telas chamando os ganchos de ciclo de vida (`ao_sair` e `ao_entrar`).
    - Despacho transparente de eventos, atualizações e renderização.
    """

    def __init__(self, tela: Optional[pygame.Surface] = None):
        self.tela = tela
        self.telas: Dict[str, TelaBase] = {}
        self.estado_atual: Optional[str] = None

    def registrar_tela(self, nome: str, tela_instancia: Any) -> Any:
        """Registra uma tela associada a uma chave de identificação."""
        self.telas[nome] = tela_instancia
        if hasattr(tela_instancia, 'gerenciador_telas'):
            tela_instancia.gerenciador_telas = self
        if hasattr(tela_instancia, 'nome'):
            tela_instancia.nome = nome
        return tela_instancia

    def trocar_tela(self, novo_estado: str, **kwargs) -> Optional[TelaBase]:
        """Troca o estado atual para uma nova tela, acionando seus ciclos de vida."""
        if novo_estado not in self.telas:
            print(f"[Erro] GerenciadorTelas: tela '{novo_estado}' nao registrada.")
            return None

        if self.estado_atual and self.estado_atual in self.telas:
            tela_antiga = self.telas[self.estado_atual]
            if hasattr(tela_antiga, 'ao_sair'):
                tela_antiga.ao_sair()

        self.estado_atual = novo_estado
        tela_nova = self.telas[novo_estado]
        if hasattr(tela_nova, 'ao_entrar'):
            tela_nova.ao_entrar(**kwargs)

        return tela_nova

    def obter_tela_atual(self) -> Optional[TelaBase]:
        """Retorna a instância da tela atualmente ativa."""
        if self.estado_atual:
            return self.telas.get(self.estado_atual)
        return None

    def obter_tela(self, nome: str) -> Optional[TelaBase]:
        """Retorna uma tela registrada pelo seu nome."""
        return self.telas.get(nome)

    def processar_evento(self, evento: pygame.event.Event, posicao_mouse: Tuple[int, int]) -> Any:
        """Despacha o evento para a tela ativa."""
        tela = self.obter_tela_atual()
        if tela is not None:
            if hasattr(tela, 'atualizar_eventos'):
                return tela.atualizar_eventos(evento, posicao_mouse)
        return None

    def atualizar(self, posicao_mouse: Tuple[int, int], estado_clique_mouse: Tuple[bool, ...]):
        """Despacha a atualização para a tela ativa."""
        tela = self.obter_tela_atual()
        if tela is not None:
            if hasattr(tela, 'atualizar'):
                tela.atualizar(posicao_mouse, estado_clique_mouse)

    def desenhar(self):
        """Despacha o desenho para a tela ativa."""
        tela = self.obter_tela_atual()
        if tela is not None:
            if hasattr(tela, 'desenhar'):
                tela.desenhar()
