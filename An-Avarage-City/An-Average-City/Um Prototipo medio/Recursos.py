from pathlib import Path

DIRETORIO_PROJETO = Path(__file__).resolve().parent


def caminho_recurso(*partes):
    """Retorna o caminho absoluto de um recurso armazenado no projeto."""
    return str(DIRETORIO_PROJETO.joinpath(*partes))


def caminho_imagem(nome_arquivo):
    return caminho_recurso("Sprites", nome_arquivo)


def caminho_botao(nome_arquivo):
    return caminho_recurso("Sprites", "Botoes", nome_arquivo)


def caminho_musica(nome_arquivo):
    return caminho_recurso("OSTs", nome_arquivo)


def caminho_fonte(nome_arquivo):
    return caminho_recurso("Fontes", nome_arquivo)
