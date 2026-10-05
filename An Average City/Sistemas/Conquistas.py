import json
import os
import pygame
from Sistemas.Fontes import obter_fonte
from Sistemas.Recursos import caminho_imagem, caminho_botao, caminho_dados

CAMINHO_DADOS = caminho_dados()
ARQUIVO_CONQUISTAS = caminho_dados("conquistas.json")


def converter_para_cinza(surface):
    """Converte uma superfície Pygame para escala de cinza (preto e branco)."""
    try:
        return pygame.transform.grayscale(surface)
    except (AttributeError, pygame.error):
        copia = surface.copy()
        w, h = copia.get_size()
        for x in range(w):
            for y in range(h):
                r, g, b, a = copia.get_at((x, y))
                if a > 0:
                    cinza = int(0.299 * r + 0.587 * g + 0.114 * b)
                    copia.set_at((x, y), (cinza, cinza, cinza, a))
        return copia


class Conquista:
    def __init__(self, id_conquista, nome, como_liberar, icone_arquivo, desbloqueada=False):
        self.id = id_conquista
        self.nome = nome
        self.como_liberar = como_liberar
        self.icone_arquivo = icone_arquivo
        self.desbloqueada = desbloqueada
        self._superficie_colorida = None
        self._superficie_cinza = None

    def carregar_icones(self):
        if self._superficie_colorida is not None:
            return

        surf = None
        for tentativa in (
            caminho_imagem(self.icone_arquivo),
            caminho_botao(self.icone_arquivo),
        ):
            if os.path.exists(tentativa):
                try:
                    surf = pygame.image.load(tentativa).convert_alpha()
                except pygame.error:
                    surf = pygame.image.load(tentativa)
                break

        if surf is None:
            surf = pygame.Surface((64, 64), pygame.SRCALPHA)
            surf.fill((100, 100, 120))
            pygame.draw.rect(surf, (255, 215, 0), (2, 2, 60, 60), width=3)

        self._superficie_colorida = surf
        self._superficie_cinza = converter_para_cinza(surf)

    def obter_icone(self, desbloqueada=None, tamanho=(48, 48)):
        self.carregar_icones()
        esta_ativa = self.desbloqueada if desbloqueada is None else desbloqueada
        base = self._superficie_colorida if esta_ativa else self._superficie_cinza
        return pygame.transform.smoothscale(base, tamanho)


class SistemaConquistas:
    def __init__(self):
        self.conquistas = []
        self.mapa_conquistas = {}
        self.notificacoes = []
        self.fonte_notificacao = None
        self.fonte_sub = None
        self.carregar()

    def carregar(self):
        self.conquistas.clear()
        self.mapa_conquistas.clear()
        if not os.path.exists(ARQUIVO_CONQUISTAS):
            return

        try:
            from Sistemas.SaveSystem import save_global
            with open(ARQUIVO_CONQUISTAS, "r", encoding="utf-8") as f:
                dados = json.load(f)
                for item in dados:
                    id_c = item["id"]
                    ja_desbloqueada = item.get("desbloqueada", False) or save_global.esta_desbloqueada(id_c)
                    c = Conquista(
                        id_conquista=id_c,
                        nome=item["nome"],
                        como_liberar=item["como_liberar"],
                        icone_arquivo=item.get("icone", "SELECT.png"),
                        desbloqueada=ja_desbloqueada
                    )
                    self.conquistas.append(c)
                    self.mapa_conquistas[c.id] = c
                    if ja_desbloqueada and not save_global.esta_desbloqueada(id_c):
                        save_global.desbloquear_conquista(id_c)
        except Exception as e:
            print(f"⚠️ Erro ao carregar conquistas: {e}")

    def salvar(self):
        try:
            from Sistemas.SaveSystem import save_global
            dados = []
            for c in self.conquistas:
                if c.desbloqueada:
                    save_global.desbloquear_conquista(c.id)
                dados.append({
                    "id": c.id,
                    "nome": c.nome,
                    "como_liberar": c.como_liberar,
                    "icone": c.icone_arquivo,
                    "desbloqueada": c.desbloqueada
                })
            with open(ARQUIVO_CONQUISTAS, "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"⚠️ Erro ao salvar conquistas: {e}")

    def esta_desbloqueada(self, id_conquista):
        c = self.mapa_conquistas.get(id_conquista)
        return bool(c and c.desbloqueada)

    def desbloquear(self, id_conquista):
        c = self.mapa_conquistas.get(id_conquista)
        if c and not c.desbloqueada:
            c.desbloqueada = True
            from Sistemas.SaveSystem import save_global
            save_global.desbloquear_conquista(id_conquista)
            self.salvar()
            # Adiciona notificação de conquista na tela
            self.notificacoes.append({
                "nome": c.nome,
                "icone": c.obter_icone(desbloqueada=True, tamanho=(40, 40)),
                "tempo": 220,  # ~3.5 segundos a 60 fps
                "y_anim": -70
            })
            return True
        return False

    def total_desbloqueadas(self):
        return sum(1 for c in self.conquistas if c.desbloqueada)

    def total_conquistas(self):
        return len(self.conquistas)

    def resetar_todas(self):
        """Bloqueia novamente todas as conquistas e salva o estado."""
        for c in self.conquistas:
            c.desbloqueada = False
        self.salvar()

    def atualizar_notificacoes(self):
        for notif in list(self.notificacoes):
            notif["tempo"] -= 1
            if notif["y_anim"] < 20:
                notif["y_anim"] += 5
            if notif["tempo"] <= 0:
                self.notificacoes.remove(notif)

    def desenhar_notificacao(self, tela):
        if not self.notificacoes:
            return

        if self.fonte_notificacao is None:
            self.fonte_notificacao = obter_fonte(14)
            self.fonte_sub = obter_fonte(11)

        for notif in self.notificacoes:
            y = notif["y_anim"]
            x = (tela.get_width() - 360) // 2
            rect_banner = pygame.Rect(x, y, 360, 56)

            # Sombra e fundo
            pygame.draw.rect(tela, (15, 15, 20), (rect_banner.x + 3, rect_banner.y + 3, rect_banner.width, rect_banner.height), border_radius=10)
            pygame.draw.rect(tela, (30, 36, 50), rect_banner, border_radius=10)
            pygame.draw.rect(tela, (230, 190, 60), rect_banner, width=2, border_radius=10)

            # Ícone
            icone = notif.get("icone")
            if icone:
                tela.blit(icone, (rect_banner.x + 10, rect_banner.y + 8))

            # Textos
            txt_topo = self.fonte_sub.render("🏆 CONQUISTA DESBLOQUEADA!", True, (255, 215, 0))
            txt_nome = self.fonte_notificacao.render(notif["nome"], True, (255, 255, 255))
            tela.blit(txt_topo, (rect_banner.x + 60, rect_banner.y + 8))
            tela.blit(txt_nome, (rect_banner.x + 60, rect_banner.y + 28))


sistema_conquistas = SistemaConquistas()
