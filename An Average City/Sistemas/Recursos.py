from pathlib import Path
import sys

def _descobrir_raiz():
    candidato = Path(__file__).resolve().parent
    for _ in range(4):
        if (candidato / "Sprites").exists() or (candidato / "Dados").exists():
            return candidato
        candidato = candidato.parent
    return Path(__file__).resolve().parent

DIRETORIO_PROJETO = _descobrir_raiz()

if str(DIRETORIO_PROJETO) not in sys.path:
    sys.path.insert(0, str(DIRETORIO_PROJETO))

def caminho_recurso(*partes):
    return str(DIRETORIO_PROJETO.joinpath(*partes))

def caminho_dados(nome_arquivo=""):
    return caminho_recurso("Dados", nome_arquivo) if nome_arquivo else caminho_recurso("Dados")

def caminho_saves(nome_arquivo=""):
    return caminho_recurso("Saves", nome_arquivo) if nome_arquivo else caminho_recurso("Saves")

def caminho_imagem(nome_arquivo):
    return caminho_recurso("Sprites", nome_arquivo)

def caminho_botao(nome_arquivo):
    return caminho_recurso("Sprites", "Botoes", nome_arquivo)

def caminho_musica(nome_arquivo):
    return caminho_recurso("OSTs", nome_arquivo)

def caminho_fonte(nome_arquivo):
    return caminho_recurso("Fontes", nome_arquivo)
