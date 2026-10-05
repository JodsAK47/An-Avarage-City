import json
import os
from Sistemas.Recursos import caminho_dados

CAMINHO_DADOS = caminho_dados()
ARQUIVO_SAVE = caminho_dados("save.json")


class GerenciadorSave:
    def __init__(self):
        self.pontos = 10  # Pontos iniciais padrão
        self.total_pontos_acumulados = 10
        self.maior_pontuacao = 0
        self.conquistas = []
        self.member_card_coletado = False
        self.carregar()

    def carregar(self):
        """Carrega o arquivo de save ou cria um novo com dados iniciais se não existir."""
        if not os.path.exists(CAMINHO_DADOS):
            os.makedirs(CAMINHO_DADOS, exist_ok=True)

        if not os.path.exists(ARQUIVO_SAVE):
            # Cria o save inicial imediatamente
            self.salvar()
            return

        try:
            with open(ARQUIVO_SAVE, "r", encoding="utf-8") as f:
                dados = json.load(f)
                self.pontos = int(dados.get("pontos", 10))
                self.total_pontos_acumulados = int(dados.get("total_pontos_acumulados", self.pontos))
                self.maior_pontuacao = int(dados.get("maior_pontuacao", 0))
                self.conquistas = list(dados.get("conquistas", []))
                self.member_card_coletado = bool(dados.get("member_card_coletado", False))
        except Exception as e:
            print(f"⚠️ Erro ao carregar save.json: {e}. Criando novo save...")
            self.salvar()

    def salvar(self):
        """Escreve o estado persistente no arquivo Dados/save.json."""
        try:
            if not os.path.exists(CAMINHO_DADOS):
                os.makedirs(CAMINHO_DADOS, exist_ok=True)

            dados = {
                "pontos": int(self.pontos),
                "total_pontos_acumulados": int(self.total_pontos_acumulados),
                "maior_pontuacao": int(self.maior_pontuacao),
                "conquistas": list(self.conquistas),
                "member_card_coletado": bool(self.member_card_coletado),
            }

            with open(ARQUIVO_SAVE, "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"⚠️ Erro ao salvar em save.json: {e}")

    def obter_pontos(self):
        return self.pontos

    def definir_pontos(self, novos_pontos):
        self.pontos = max(0, int(novos_pontos))
        self.salvar()

    def adicionar_pontos(self, quantidade):
        qtd = int(quantidade)
        self.pontos = max(0, self.pontos + qtd)
        if qtd > 0:
            self.total_pontos_acumulados += qtd
        self.salvar()

    def registrar_partida(self, pontos_partida):
        pts = int(pontos_partida)
        if pts > self.maior_pontuacao:
            self.maior_pontuacao = pts
        self.adicionar_pontos(pts)

    def desbloquear_conquista(self, id_conquista):
        if id_conquista not in self.conquistas:
            self.conquistas.append(id_conquista)
            self.salvar()
            return True
        return False

    def esta_desbloqueada(self, id_conquista):
        return id_conquista in self.conquistas

    def tem_member_card(self):
        return bool(getattr(self, 'member_card_coletado', False))

    def coletar_member_card(self):
        self.member_card_coletado = True
        self.salvar()
        return True

    def definir_member_card(self, valor):
        self.member_card_coletado = bool(valor)
        self.salvar()

    def resetar_tudo(self):
        """Redefine os pontos, conquistas e itens para o estado inicial e salva no disco."""
        self.pontos = 10
        self.total_pontos_acumulados = 10
        self.maior_pontuacao = 0
        self.conquistas.clear()
        self.member_card_coletado = False
        self.salvar()


save_global = GerenciadorSave()
