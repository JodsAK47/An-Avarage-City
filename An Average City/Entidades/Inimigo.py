import pygame
from Sistemas.Fontes import obter_fonte
from Sistemas.Recursos import caminho_imagem, caminho_dados

import json
import os

CAMINHO_DADOS = caminho_dados()

def carregar_habilidades_inimigos():
    try:
        from Gameplay.Habilidades import Habilidade
        with open(os.path.join(CAMINHO_DADOS, "habilidades_inimigos.json"), "r", encoding="utf-8") as f:
            dados = json.load(f)
            banco = {}
            for k, v in dados.items():
                banco[k] = Habilidade(
                    nome=v["nome"],
                    tipo=v["tipo"],
                    dano=v["dano"],
                    custo_mp=v["custo_mp"],
                    precisao=v["precisao"],
                    descricao=v["descricao"],
                    efeito=v.get("efeito"),
                    chance_efeito=v.get("chance_efeito", 0.0),
                    em_area=v.get("em_area", False),
                    verso=v.get("verso", "Inimigo")
                )
            return banco
    except FileNotFoundError:
        print("⚠️ Erro: arquivo habilidades_inimigos.json não encontrado.")
        return {}

_banco_habilidades_inimigos = carregar_habilidades_inimigos()

class Inimigo:
    def __init__(self, x, y, vida_maxima, nome_imagem, nome="Inimigo", ataques=None, xp=0, atributos=None, max_mp=None):
        self.nome = nome
        self.arquivo_imagem = nome_imagem
        self.max_hp = vida_maxima
        self.hp = vida_maxima
        self.ataques = ataques if ataques is not None else ["Soco"]
        if max_mp is not None:
            self.max_mp = max_mp
        else:
            custo_max_mp = max(
                (
                    _banco_habilidades_inimigos.get(nome_ataque, _banco_habilidades_inimigos["Soco"]).custo_mp
                    for nome_ataque in self.ataques
                ),
                default=0,
            )
            self.max_mp = max(10, custo_max_mp * 3)
        self.mp = self.max_mp

        self.congelado = False
        self.xp = xp

        self.atributos = atributos if atributos is not None else {"For": 1, "Agi": 1, "Int": 1}
        self.is_player = False
        
        try:
            self.imagem_original = pygame.image.load(caminho_imagem(nome_imagem))
            self.imagem = pygame.transform.scale(self.imagem_original, (100, 120))
        except (pygame.error, FileNotFoundError) as e:
            print(f"⚠️ Erro ao carregar imagem do inimigo ({nome_imagem}): {e}")
            self.imagem = pygame.Surface((100, 120))
            self.imagem.fill((200, 50, 50))

        self.rect = self.imagem.get_rect(topleft=(x, y))
        self.convertida = False
        self.fonte_nome = obter_fonte(16)

    def obter_habilidade(self, nome):
        return _banco_habilidades_inimigos.get(nome, _banco_habilidades_inimigos["Soco"])

    def clone(self):
        novo_inimigo = Inimigo(
            self.rect.x,
            self.rect.y,
            self.max_hp,
            self.arquivo_imagem,
            self.nome,
            list(self.ataques),
            self.xp,
            dict(self.atributos),
            max_mp=self.max_mp
        )
        novo_inimigo.hp = self.hp
        novo_inimigo.mp = self.mp
        novo_inimigo.congelado = self.congelado
        return novo_inimigo

    def desenhar(self, tela):
        if self.hp > 0:
            if not self.convertida:
                try:
                    self.imagem = self.imagem.convert_alpha()
                except pygame.error:
                    pass
                self.convertida = True

            tela.blit(self.imagem, self.rect)
             
            txt = self.fonte_nome.render(self.nome, True, (255, 255, 255))
            tela.blit(txt, (self.rect.centerx - txt.get_width()//2, self.rect.y - 20))

