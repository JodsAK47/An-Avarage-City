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

# Garante que a raiz do projeto e todas as subpastas funcionais estejam acessíveis no sys.path
for subpasta in [
    DIRETORIO_PROJETO,
    DIRETORIO_PROJETO / "Sistemas",
    DIRETORIO_PROJETO / "Telas",
    DIRETORIO_PROJETO / "Gameplay",
    DIRETORIO_PROJETO / "Entidades",
]:
    sub_str = str(subpasta)
    if sub_str not in sys.path:
        sys.path.insert(0, sub_str)


def caminho_recurso(*partes):
    """Retorna o caminho absoluto de um recurso armazenado no projeto."""
    return str(DIRETORIO_PROJETO.joinpath(*partes))


def caminho_dados(nome_arquivo=""):
    """Retorna o caminho absoluto de um arquivo ou da pasta Dados."""
    return caminho_recurso("Dados", nome_arquivo) if nome_arquivo else caminho_recurso("Dados")


def caminho_imagem(nome_arquivo):
    """Retorna o caminho absoluto de uma imagem dentro de Sprites."""
    return caminho_recurso("Sprites", nome_arquivo)


def caminho_botao(nome_arquivo):
    """Retorna o caminho absoluto de uma imagem de botão dentro de Sprites/Botoes."""
    return caminho_recurso("Sprites", "Botoes", nome_arquivo)


def caminho_musica(nome_arquivo):
    """Retorna o caminho absoluto de uma música dentro de OSTs."""
    return caminho_recurso("OSTs", nome_arquivo)


def caminho_fonte(nome_arquivo):
    """Retorna o caminho absoluto de uma fonte dentro de Fontes."""
    return caminho_recurso("Fontes", nome_arquivo)
