import random
import pygame


class MinigameEsquiva:
    """
    Controlador encapsulado do Minigame de Esquiva em Tempo Real (QTE).
    Gerencia:
    - O avanço das barras móveis em direção à zona de esquiva (x=200);
    - Detecção de clique (Zona Central de Parry vs Zona Lateral vs Erro);
    - Cálculo de redução de dano percentual e imunidade a efeitos de controle.
    """

    def __init__(self, total_rodadas: int = 3):
        self.total_rodadas = total_rodadas
        self.barras = []
        self.ativo = False

        self.acertos = 0
        self.acertos_centro = 0
        self.reducao = 0.0

        self.dano_pendente = 0
        self.alvo = None
        self.atacante_nome = ""
        self.efeitos_pendentes = []
        self.chance_efeito_pendente = 0.0
        self.ultimo_feedback = ""

    def esta_ativo(self) -> bool:
        return self.ativo

    def iniciar(self, velocidade_base: float, dano_pendente: int, alvo=None,
                atacante_nome: str = "", efeitos=None, chance_efeito: float = 0.0):
        self.ativo = True
        self.barras = []
        self.acertos = 0
        self.acertos_centro = 0
        self.reducao = 0.0

        self.dano_pendente = dano_pendente
        self.alvo = alvo
        self.atacante_nome = atacante_nome
        self.efeitos_pendentes = list(efeitos or [])
        self.chance_efeito_pendente = chance_efeito
        self.ultimo_feedback = ""

        espacamento = 180
        for i in range(self.total_rodadas):
            self.barras.append({
                "x": random.randint(-20, 0) - (i * espacamento),
                "velocidade": max(2.0, velocidade_base + random.randint(-1, 2)),
                "ativa": True
            })

    def atualizar(self, clicou: bool = False):
        """
        Atualiza o movimento das barras e processa cliques de esquiva.
        Retorna None enquanto ativo, ou um dicionário de resultado ao concluir.
        """
        if not self.ativo:
            return None

        for barra in self.barras:
            if barra["ativa"]:
                barra["x"] += barra["velocidade"]
                if barra["x"] >= 400:
                    barra["ativa"] = False
                    self.ultimo_feedback = "❌ Barra perdida!"

        if clicou:
            barras_visiveis = [b for b in self.barras if b["ativa"] and b["x"] > 0]
            if barras_visiveis:
                barra_alvo = max(barras_visiveis, key=lambda b: b["x"])
                distancia = abs(barra_alvo["x"] - 200)
                barra_alvo["ativa"] = False

                if distancia <= 20:
                    self.acertos_centro += 1
                    self.reducao += 0.33
                    self.ultimo_feedback = "⚡ Centro acertado!"
                elif distancia <= 80:
                    self.acertos += 1
                    self.reducao += 0.16
                    self.ultimo_feedback = "💨 Lateral acertada!"
                else:
                    self.ultimo_feedback = "❌ Errou o tempo!"

        # Verifica se todas as barras finalizaram
        if all(not b["ativa"] for b in self.barras):
            self.ativo = False
            total_acertos = self.acertos + self.acertos_centro
            evitou_tudo = (total_acertos == self.total_rodadas or
                           self.acertos_centro >= (self.total_rodadas - 1))

            reducao_total = min(0.99, self.reducao)
            dano_calculado = max(1, int(self.dano_pendente * (1 - reducao_total)))

            if getattr(self.alvo, "god_mode", False):
                dano_calculado = 0

            return {
                "concluido": True,
                "dano_tomado": dano_calculado,
                "reducao_total": reducao_total,
                "evitou_tudo": evitou_tudo,
                "acertos": self.acertos,
                "acertos_centro": self.acertos_centro,
                "alvo": self.alvo,
                "efeitos_pendentes": self.efeitos_pendentes,
                "chance_efeito": self.chance_efeito_pendente,
                "feedback": self.ultimo_feedback,
            }

        return None

    def desenhar(self, superficie: pygame.Surface, bar_x: int, bar_y: int,
                 bar_w: int = 400, bar_h: int = 24):
        """
        Desenha a trilha de esquiva, zona de acerto e as barras de sincronização.
        """
        if not self.ativo:
            return

        # Fundo do trilho
        pygame.draw.rect(superficie, (18, 22, 32), (bar_x, bar_y, bar_w, bar_h), border_radius=5)
        # Zona lateral (amarela)
        pygame.draw.rect(superficie, (230, 190, 50), (bar_x + 120, bar_y, 160, bar_h))
        # Zona central crítica (verde)
        pygame.draw.rect(superficie, (30, 220, 90), (bar_x + 180, bar_y, 40, bar_h))
        # Borda externa
        pygame.draw.rect(superficie, (240, 240, 240), (bar_x, bar_y, bar_w, bar_h), width=2, border_radius=5)

        # Marcadores móveis vermelhos
        for barra in self.barras:
            if not barra["ativa"] or barra["x"] < 0:
                continue
            bx = bar_x + barra["x"] - 4
            if bar_x <= bx <= bar_x + bar_w:
                pygame.draw.rect(superficie, (255, 60, 60), (bx, bar_y - 6, 8, bar_h + 12), border_radius=2)
