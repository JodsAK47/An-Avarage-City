import os
import sys
import unittest
from pathlib import Path

os.environ["SDL_VIDEODRIVER"] = "dummy"

RAIZ = Path(__file__).resolve().parent.parent / "An Average City"
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import pygame
pygame.init()
pygame.display.set_mode((1000, 780))

from Sistemas.Constantes import (
    Verso,
    Classe,
    normalizar_identificador,
    obter_equipamento_inicial,
    obter_multiplicador_verso_classe,
)
from Entidades.EntidadeCombate import EntidadeCombate
from Gameplay.MinigameEsquiva import MinigameEsquiva


class TestCombate(unittest.TestCase):
    def test_normalizacao_identificadores(self):
        self.assertEqual(normalizar_identificador("Físico"), "fisico")
        self.assertEqual(normalizar_identificador("Distância"), "distancia")
        self.assertEqual(normalizar_identificador("Sobrevivente"), "sobrevivente")
        self.assertEqual(Verso.normalizar("Survivor"), Verso.SOBREVIVENTE)
        self.assertEqual(Verso.normalizar("agent"), Verso.AGENTE)
        self.assertEqual(Classe.normalizar("MAGIA"), Classe.MAGIA)

    def test_equipamentos_e_multiplicadores(self):
        arma, bonus = obter_equipamento_inicial("Sobrevivente", "Físico")
        self.assertEqual(arma, "Machado")
        self.assertEqual(bonus.get("For"), 2)

        arma_ag, _ = obter_equipamento_inicial("Agente", "Distância")
        self.assertEqual(arma_ag, "Vandal")

        mult_sob = obter_multiplicador_verso_classe("Sobrevivente", "Físico")
        self.assertEqual(mult_sob, 2.0)

        mult_feiti = obter_multiplicador_verso_classe("Feiticeiro", "Magia")
        self.assertEqual(mult_feiti, 2.0)

    def test_entidade_combate_mecanica(self):
        ent = EntidadeCombate("Guerreiro", max_hp=100, max_mp=20)
        self.assertTrue(ent.esta_vivo)
        self.assertEqual(ent.hp, 100)

        dano_causado = ent.receber_dano(30)
        self.assertEqual(dano_causado, 30)
        self.assertEqual(ent.hp, 70)

        ent.bloqueando = True
        dano_bloqueado = ent.receber_dano(20)
        self.assertEqual(dano_bloqueado, 10)
        self.assertEqual(ent.hp, 60)

        curado = ent.curar_hp(25)
        self.assertEqual(curado, 25)
        self.assertEqual(ent.hp, 85)

    def test_minigame_esquiva(self):
        esquiva = MinigameEsquiva(total_rodadas=3)
        esquiva.iniciar(velocidade_base=5.0, dano_pendente=50)
        self.assertTrue(esquiva.esta_ativo())
        self.assertEqual(len(esquiva.barras), 3)

    def test_mecanica_confinamento(self):
        from Entidades.Inimigo import Inimigo
        conf = Inimigo(100, 200, 80, "Confinamento.png", nome="Confinamento", ataques=["Confinamento"])
        self.assertTrue(conf.eh_confinamento)
        self.assertEqual(conf.carga_confinamento, 0)
        self.assertEqual(conf.max_carga_confinamento, 5)

        # Simula o ciclo de carga por 5 rodadas
        for _ in range(4):
            conf.carga_confinamento += 1
            self.assertLess(conf.carga_confinamento, conf.max_carga_confinamento)

        conf.carga_confinamento += 1
        self.assertEqual(conf.carga_confinamento, 5)
        # Detonação e reset
        conf.carga_confinamento = 0
        self.assertEqual(conf.carga_confinamento, 0)

    def test_confinamento_mudanca_sprite_e_fade_out(self):
        from Entidades.Inimigo import Inimigo
        conf = Inimigo(100, 200, 75, "Confinamento.png", nome="Confinamento", ataques=["Confinamento"])
        self.assertFalse(conf.derrotado)
        self.assertEqual(conf.timer_fade_derrota, 0)

        # Guarda dimensões da sprite ativa
        w_ativa, h_ativa = conf.imagem.get_size()
        bottom_inicial = conf.rect.bottom

        # Causa dano letal
        conf.receber_dano(100)
        self.assertEqual(conf.hp, 0)
        self.assertTrue(conf.derrotado)
        self.assertEqual(conf.timer_fade_derrota, conf.max_fade_derrota)

        # Verifica que a sprite mudou para a destruída (altura menor que a ativa)
        w_dest, h_dest = conf.imagem.get_size()
        self.assertLess(h_dest, h_ativa)
        # Verifica que o chão (midbottom) foi preservado
        self.assertEqual(conf.rect.bottom, bottom_inicial)

        # Atualiza a animação de derrota
        conf.atualizar_animacao_derrota()
        self.assertEqual(conf.timer_fade_derrota, conf.max_fade_derrota - 1)

        # Testa restaurar estado vivo
        conf.restaurar_estado_vivo()
        self.assertFalse(conf.derrotado)
        self.assertEqual(conf.timer_fade_derrota, 0)
        self.assertEqual(conf.imagem.get_size(), (w_ativa, h_ativa))

    def test_fade_out_inimigos_gerais(self):
        from Entidades.Inimigo import Inimigo
        torreta = Inimigo(100, 200, 25, "Torreta.png", nome="Torreta")
        self.assertFalse(torreta.derrotado)

        # Dano letal ativa fade-out
        torreta.receber_dano(30)
        self.assertTrue(torreta.derrotado)
        self.assertEqual(torreta.timer_fade_derrota, torreta.max_fade_derrota)

        # Simula renderização do fade-out com alpha
        tela_mock = pygame.Surface((300, 300))
        torreta.desenhar(tela_mock)

        for _ in range(10):
            torreta.atualizar_animacao_derrota()
        self.assertEqual(torreta.timer_fade_derrota, torreta.max_fade_derrota - 10)
        self.assertGreater(len(torreta.particulas_derrota), 0)


    def test_cooldown_acoes_aumentado_50_porcento(self):
        """Verifica se o cooldown entre ações e o tempo de espera do inimigo foram aumentados em 50%."""
        from Telas.TelaCombate import GerenciadorJogo
        tela_mock = pygame.Surface((1000, 800))
        jogo = GerenciadorJogo(tela_mock)

        # Tempo de espera do inimigo aumentado em 50% (80 * 1.5 = 120)
        self.assertEqual(jogo.tempo_espera_inimigo, 120)
        self.assertEqual(jogo.MULTIPLICADOR_COOLDOWN_ACOES, 1.5)

        # Cooldown padrão de 50 frames agora resulta em 75 frames (50 * 1.5 = 75)
        jogo.iniciar_cooldown_feedback(50)
        self.assertEqual(jogo.cooldown_feedback, 75)
        self.assertEqual(jogo.tempo_cooldown_maximo, 75)

        # Cooldown de 60 frames resulta em 90 frames (60 * 1.5 = 90)
        jogo.iniciar_cooldown_feedback(60)
        self.assertEqual(jogo.cooldown_feedback, 90)
        self.assertEqual(jogo.tempo_cooldown_maximo, 90)

        # Cooldown de 40 frames resulta em 60 frames (40 * 1.5 = 60)
        jogo.iniciar_cooldown_feedback(40)
        self.assertEqual(jogo.cooldown_feedback, 60)
        self.assertEqual(jogo.tempo_cooldown_maximo, 60)

    def test_skin_sukuna_nao_da_ataque_novo(self):
        """Verifica se a skin do Sukuna não concede mais a habilidade Santuário Malevolente."""
        from Telas.TelaCombate import GerenciadorJogo
        from Entidades.EntidadeCombate import EntidadeCombate
        from Entidades.Inimigo import Inimigo

        tela_mock = pygame.Surface((1000, 800))
        jogo = GerenciadorJogo(tela_mock)

        jogador = EntidadeCombate("Jogador", max_hp=100, max_mp=50, is_player=True)
        jogador.arquivo_imagem = "Sukuna1.png"
        jogador.talentos = set()
        jogador.ultimates_desbloqueadas = set()

        # Atualiza ataques com verso Feiticeiro e classe Magia
        jogo._atualizar_ataques_jogador(jogador, "Feiticeiro", "Magia")

        self.assertNotIn("Santuário Malevolente", jogador.ataques)

        # Verifica se o boss Sukuna possui a habilidade carregada via habilidades_inimigos.json
        sukuna = Inimigo(0, 0, 150, "Sukuna1.png", nome="Sukuna", ataques=["Santuário Malevolente"])
        hab_santuario = sukuna.obter_habilidade("Santuário Malevolente")
        self.assertEqual(hab_santuario.nome, "Santuário Malevolente")
        self.assertEqual(hab_santuario.minion, "Pequeno Santuário")
        self.assertTrue(hab_santuario.is_ultimate)

    def test_selecao_alvo_hover_e_clique_com_cooldown_padrao(self):
        """Verifica se a seleção de alvo define alvo_destaque, aplica tempo padrão de espera e exibe o alvo no log."""
        from Telas.TelaCombate import GerenciadorJogo
        from Entidades.EntidadeCombate import EntidadeCombate
        from Entidades.Inimigo import Inimigo

        tela_mock = pygame.Surface((1000, 800))
        jogo = GerenciadorJogo(tela_mock)

        jogador = EntidadeCombate("Herói", max_hp=100, max_mp=50, is_player=True)
        jogador.rect = pygame.Rect(100, 400, 60, 80)
        inimigo = Inimigo(500, 400, 100, "Maldicao1.png", nome="Monstro Alpha")
        inimigo.rect = pygame.Rect(500, 400, 60, 80)

        jogo.ordem_turnos = [jogador, inimigo]
        jogo.indice_turno = 0
        jogo.menu_acoes_estado = "selecionar_alvo"
        jogo.ataque_selecionado = "Machadada"

        # 1. Hover sobre o inimigo: log deve indicar o alvo
        pos_mouse_sobre_inimigo = (520, 420)
        jogo._processar_menu_selecionar_alvo(jogador, pos_mouse_sobre_inimigo, (0, 0, 0), False, [inimigo])
        self.assertIn("Alvo: Monstro Alpha", jogo.mensagem_log)

        # 2. Clique no inimigo: deve destacar o alvo e aplicar o cooldown padrão (75 frames * 1.5 = 112)
        jogo._processar_menu_selecionar_alvo(jogador, pos_mouse_sobre_inimigo, (1, 0, 0), True, [inimigo])
        self.assertEqual(jogo.alvo_destaque, inimigo)
        self.assertEqual(jogo.cooldown_feedback, 112)
        self.assertEqual(jogo.tempo_cooldown_maximo, 112)
        self.assertIn("alvo Monstro Alpha", jogo.mensagem_log)

        # 3. Avançar turno deve limpar o destaque do alvo
        jogo.avancar_turno()
        self.assertIsNone(jogo.alvo_destaque)

    def test_mensagem_log_e_destaque_ataque_inimigo_e_minion(self):
        """Verifica se ataques de inimigos e minions também destacam o alvo e identificam o alvo na mensagem."""
        from Telas.TelaCombate import GerenciadorJogo
        from Entidades.Personagem import personagem
        from Entidades.Inimigo import Inimigo
        from Entidades.Minion import Minion

        tela_mock = pygame.Surface((1000, 800))
        jogo = GerenciadorJogo(tela_mock)

        personagem.rect = pygame.Rect(100, 400, 60, 80)
        personagem.hp = 100
        personagem.max_hp = 100
        inimigo = Inimigo(500, 400, 100, "Maldicao1.png", nome="Boss")
        inimigo.rect = pygame.Rect(500, 400, 60, 80)

        jogo.ordem_turnos = [inimigo, personagem]
        jogo.indice_turno = 0

        # Simula minion atacando inimigo
        minion = Minion(nome="Abelha", vida_maxima=30, dono=personagem)
        jogo.executar_turno_minion(minion, alvo_forcado=inimigo)
        self.assertEqual(jogo.alvo_destaque, inimigo)
        self.assertIn("alvo Boss", jogo.mensagem_log)

        # Simula avanço de turno
        jogo.avancar_turno()
        self.assertIsNone(jogo.alvo_destaque)

        # Simula turno do inimigo atacando o jogador
        jogo.indice_turno = 0
        jogo.timer_inimigo = jogo.tempo_espera_inimigo
        jogo.atualizar((0, 0), (0, 0, 0))
        self.assertEqual(jogo.alvo_destaque, personagem)

        # Avançar turno limpa alvo_destaque
        jogo.avancar_turno()
        self.assertIsNone(jogo.alvo_destaque)

    def test_2p_nome_exibicao_distinto(self):
        """Verifica se Player 1 e Player 2 são distinguidos nos nomes de exibição."""
        from Telas.TelaCombate import GerenciadorJogo
        from Entidades.Personagem import personagem, Personagem

        tela_mock = pygame.Surface((1000, 800))
        jogo = GerenciadorJogo(tela_mock)
        p2 = Personagem(150, 350)
        jogo.personagem2 = p2

        self.assertEqual(jogo.nome_exibicao(personagem), "Jogador 1")
        self.assertEqual(jogo.nome_exibicao(p2), "Jogador 2")

    def test_2p_dead_player_skip(self):
        """Verifica se o loop de turnos nunca entrega a vez a um jogador derrotado (hp=0)."""
        from Telas.TelaCombate import GerenciadorJogo
        from Entidades.Personagem import personagem, Personagem
        from Entidades.Inimigo import Inimigo

        tela_mock = pygame.Surface((1000, 800))
        jogo = GerenciadorJogo(tela_mock)

        p2 = Personagem(150, 350)
        p2.hp = 80
        jogo.personagem2 = p2
        jogo.duas_pessoas = True

        personagem.hp = 0  # Jogador 1 derrotado
        inimigo = Inimigo(500, 400, 100, "Maldicao1.png", nome="Monstro")
        inimigo.hp = 100

        jogo.ordem_turnos = [personagem, inimigo, p2]
        jogo.indice_turno = 1  # Inimigo terminou turno

        jogo.avancar_turno()
        self.assertEqual(jogo.indice_turno, 2)
        # Ao atualizar, deve entregar turno para p2 (hp=80)
        jogo.atualizar((0, 0), (0, 0, 0))
        self.assertEqual(jogo.ordem_turnos[jogo.indice_turno], p2)

        # Agora p2 termina o turno e avança
        jogo.avancar_turno()
        # indice_turno avança para 3 -> wrap para 0 (personagem, morto) -> deve pular personagem e ir para inimigo!
        jogo.atualizar((0, 0), (0, 0, 0))
        self.assertNotEqual(jogo.ordem_turnos[jogo.indice_turno], personagem)
        self.assertEqual(jogo.ordem_turnos[jogo.indice_turno], inimigo)

    def test_2p_talentos_e_classe_personagem2(self):
        """Verifica se personagem2 recebe talentos e ataques corretamente."""
        from Telas.TelaCombate import GerenciadorJogo
        from Entidades.Personagem import Personagem
        from Sistemas.SaveSystem import save_global

        save_global.definir_progresso_verso("Feiticeiro", ["F1", "F2", "F3", "F4"])

        tela_mock = pygame.Surface((1000, 800))
        jogo = GerenciadorJogo(tela_mock)
        p2 = Personagem(150, 350)
        jogo.personagem2 = p2
        jogo.classe_jogador2 = "Feiticeiro"
        jogo.classe_jogador2_tipo = "Magia"

        jogo._aplicar_classe_personagem2()
        self.assertTrue(p2.is_player)
        self.assertIn("F1", p2.talentos)
        self.assertIn("Feiticeiro", p2.ultimates_desbloqueadas)
        self.assertIn("Azul", p2.ataques)
        self.assertIn("Ultimate do Feiticeiro: Eclipse Sombrio", p2.ataques)

    def test_2p_revival_ao_iniciar_combate(self):
        """Garante que jogadores com HP zerado recebem cura mínima de 30% ao entrar em combate."""
        from Telas.TelaCombate import GerenciadorJogo
        from Entidades.Personagem import personagem, Personagem
        from Entidades.Inimigo import Inimigo

        tela_mock = pygame.Surface((1000, 800))
        jogo = GerenciadorJogo(tela_mock)
        p2 = Personagem(150, 350)
        jogo.personagem2 = p2
        jogo.duas_pessoas = True

        personagem.hp = 0
        p2.hp = 0
        inimigo = Inimigo(500, 400, 100, "Maldicao1.png", nome="Monstro")

        jogo.ordem_turnos = [personagem, p2, inimigo]
        jogo.reiniciar()

        self.assertGreaterEqual(personagem.hp, 30)
        self.assertGreaterEqual(p2.hp, 30)

if __name__ == "__main__":
    unittest.main()
