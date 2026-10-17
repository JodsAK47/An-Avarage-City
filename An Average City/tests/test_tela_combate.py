import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

DIRETORIO_RAIZ = Path(__file__).resolve().parent.parent
if str(DIRETORIO_RAIZ) not in sys.path:
    sys.path.insert(0, str(DIRETORIO_RAIZ))

import pygame
pygame.init()
pygame.display.set_mode((1000, 800))

from Telas.TelaCombate import GerenciadorJogo
from Entidades.Personagem import personagem
from Entidades.Inimigo import Inimigo

def test_tela_combate_visual_e_render():
    tela = pygame.display.get_surface()
    gerenciador = GerenciadorJogo(tela)

    gerenciador.configurar_classe("Sobrevivente", "Físico")
    gerenciador.configurar_cenario("evento_neutro_1:Um Estranho te convida para beber")

    gerenciador.atualizar_posicoes_inimigos()
    for ent in gerenciador.ordem_turnos:
        assert ent.rect.left >= 0, f"Entidade {getattr(ent, 'nome', 'heroi')} saiu pela esquerda: {ent.rect}"
        assert ent.rect.right <= 1000, f"Entidade {getattr(ent, 'nome', 'heroi')} saiu pela direita: {ent.rect}"
        assert ent.rect.top >= 0, f"Entidade {getattr(ent, 'nome', 'heroi')} saiu pelo topo: {ent.rect}"
        assert ent.rect.bottom <= 800, f"Entidade {getattr(ent, 'nome', 'heroi')} saiu pelo fundo: {ent.rect}"

    for frame in range(15):
        gerenciador.atualizar((720, 395), (0, 0, 0))
        gerenciador.desenhar((720, 395))

    assert gerenciador.tempo_animacao > 0.5, "Timer de animação deveria ter incrementado"
    assert gerenciador.fundo_luta_redimensionado is not None, "Cache do plano de fundo deveria estar ativo"

    gerenciador.menu_acoes_estado = "selecionar_alvo"
    gerenciador.desenhar((720, 395))

    gerenciador.menu_acoes_estado = "esquivando"
    gerenciador.desenhar((500, 400))

    for qtd in [1, 2, 3, 4]:
        inimigos = [Inimigo(0, 0, 100, "Maldicao1.png", nome=f"Inimigo_{i}") for i in range(qtd)]
        gerenciador.ordem_turnos = [personagem] + inimigos
        gerenciador.atualizar_posicoes_inimigos()
        gerenciador.desenhar((500, 400))
        for ent in gerenciador.ordem_turnos:
            assert 0 <= ent.rect.left and ent.rect.right <= 1000, f"Inimigo fora da tela em grupo de {qtd}: {ent.rect}"
            assert 200 <= ent.rect.centery <= 600, f"Inimigo fora do ringue em grupo de {qtd}: {ent.rect}"

        for i in range(len(inimigos)):
            for j in range(i + 1, len(inimigos)):
                dx = inimigos[i].rect.centerx - inimigos[j].rect.centerx
                dy = inimigos[i].rect.centery - inimigos[j].rect.centery
                distancia = (dx**2 + dy**2) ** 0.5
                assert distancia >= 120, f"Inimigos {i} e {j} muito próximos em grupo de {qtd}: distância={distancia}"

    gerenciador.duas_pessoas = True
    p2 = Inimigo(0, 0, 100, "pixil.png", nome="Jogador 2")
    p2.is_player = True
    gerenciador.personagem2 = p2
    gerenciador.ordem_turnos = [personagem, p2]
    gerenciador.atualizar_posicoes_inimigos()
    assert personagem.rect.centerx == p2.rect.centerx == 260, f"Jogadores não estão alinhados verticalmente: p1={personagem.rect}, p2={p2.rect}"
    assert abs(personagem.rect.centery - p2.rect.centery) >= 120, "Espaço vertical insuficiente entre jogadores"

    print("✓ Testes visuais, alinhamento vertical dos jogadores e espaçamento dos inimigos passaram com sucesso!")

if __name__ == "__main__":
    test_tela_combate_visual_e_render()
