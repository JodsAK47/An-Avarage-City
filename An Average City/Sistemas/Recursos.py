import unicodedata
from pathlib import Path
import os
import sys
from typing import Dict, Optional

def _descobrir_raiz() -> Path:
    candidato = Path(__file__).resolve().parent
    for _ in range(4):
        if (candidato / "Sprites").exists() or (candidato / "Dados").exists():
            return candidato
        candidato = candidato.parent
    return Path(__file__).resolve().parent

DIRETORIO_PROJETO = _descobrir_raiz()

if str(DIRETORIO_PROJETO) not in sys.path:
    sys.path.insert(0, str(DIRETORIO_PROJETO))

# Cache de resolução rápida de caminhos de arquivos
_CACHE_SPRITES: Dict[str, str] = {}
_INDICE_SPRITES: Optional[Dict[str, Path]] = None

def _normalizar_chave(nome: str) -> str:
    """Normaliza o nome do arquivo para buscas insensíveis a maiúsculas/minúsculas, espaços, traços e acentos."""
    norm = unicodedata.normalize("NFD", str(nome))
    sem_acentos = "".join(c for c in norm if unicodedata.category(c) != "Mn")
    return sem_acentos.strip().lower().replace("\\", "/").replace(" ", "").replace("_", "")


def _construir_indice_sprites() -> Dict[str, Path]:
    """Indexa recursivamente todos os arquivos sob a pasta Sprites para resolução O(1)."""
    global _INDICE_SPRITES
    indice: Dict[str, Path] = {}
    pasta_sprites = DIRETORIO_PROJETO / "Sprites"
    if pasta_sprites.exists():
        for arq in pasta_sprites.rglob("*"):
            if arq.is_file():
                # Chave exata minúscula (ex: "fight.png")
                nome_lower = arq.name.lower()
                if nome_lower not in indice:
                    indice[nome_lower] = arq

                # Chave normalizada sem espaços e sublinhados (ex: "passaroolhudo.png")
                chave_norm = _normalizar_chave(arq.name)
                if chave_norm not in indice:
                    indice[chave_norm] = arq

                # Também indexa caminho relativo relativo a Sprites (ex: "cenarios/fight.png")
                try:
                    rel_lower = str(arq.relative_to(pasta_sprites)).replace("\\", "/").lower()
                    if rel_lower not in indice:
                        indice[rel_lower] = arq
                except ValueError:
                    pass
    _INDICE_SPRITES = indice
    return indice

def reindexar_sprites():
    """Força a reconstrução do índice de sprites se novos arquivos forem adicionados em tempo de execução."""
    global _INDICE_SPRITES, _CACHE_SPRITES
    _CACHE_SPRITES.clear()
    _construir_indice_sprites()

def caminho_recurso(*partes) -> str:
    return str(DIRETORIO_PROJETO.joinpath(*partes))

def caminho_dados(nome_arquivo: str = "") -> str:
    return caminho_recurso("Dados", nome_arquivo) if nome_arquivo else caminho_recurso("Dados")

def caminho_saves(nome_arquivo: str = "") -> str:
    return caminho_recurso("Saves", nome_arquivo) if nome_arquivo else caminho_recurso("Saves")

def caminho_imagem(nome_arquivo: str) -> str:
    """
    Localiza um sprite de imagem de forma inteligente e tolerante a reorganizações de pastas.
    Busca na raiz de Sprites, nas subpastas organizadas (Cenarios, Inimigos, Minions, Ataques,
    De_Buffs, Botoes) ou em qualquer subpasta recursiva de Sprites, com suporte insensível a maiúsculas/minúsculas.
    """
    if not nome_arquivo:
        return caminho_recurso("Sprites")

    nome_str = str(nome_arquivo).strip().replace("\\", "/")

    # 1. Verifica cache rápido
    if nome_str in _CACHE_SPRITES:
        caminho_cached = _CACHE_SPRITES[nome_str]
        if os.path.exists(caminho_cached):
            return caminho_cached

    # 2. Se o caminho já for absoluto e existir
    if os.path.isabs(nome_str) and os.path.exists(nome_str):
        _CACHE_SPRITES[nome_str] = nome_str
        return nome_str

    pasta_sprites = DIRETORIO_PROJETO / "Sprites"

    # 3. Busca direta na raiz de Sprites
    direto = pasta_sprites / nome_str
    if direto.exists() and direto.is_file():
        res = str(direto)
        _CACHE_SPRITES[nome_str] = res
        return res

    # 4. Busca nas subpastas conhecidas mais frequentes
    nome_base = Path(nome_str).name
    subpastas_comuns = ["Cenarios", "Inimigos", "Minions", "Ataques", "De_Buffs", "Botoes", "Inventario", "Conquistas"]
    for sub in subpastas_comuns:
        tentativa = pasta_sprites / sub / nome_base
        if tentativa.exists() and tentativa.is_file():
            res = str(tentativa)
            _CACHE_SPRITES[nome_str] = res
            return res

    # 5. Busca através do índice recursivo de Sprites
    global _INDICE_SPRITES
    if _INDICE_SPRITES is None:
        _construir_indice_sprites()

    # Tentativa por nome de arquivo em minúsculo
    chave_lower = nome_base.lower()
    if chave_lower in _INDICE_SPRITES:
        res = str(_INDICE_SPRITES[chave_lower])
        _CACHE_SPRITES[nome_str] = res
        return res

    # Tentativa por caminho relativo normalizado (ex: "cenarios/menu.png")
    chave_rel = nome_str.lower()
    if chave_rel in _INDICE_SPRITES:
        res = str(_INDICE_SPRITES[chave_rel])
        _CACHE_SPRITES[nome_str] = res
        return res

    # Tentativa por chave normalizada (sem espaços, sem sublinhados)
    chave_norm = _normalizar_chave(nome_base)
    if chave_norm in _INDICE_SPRITES:
        res = str(_INDICE_SPRITES[chave_norm])
        _CACHE_SPRITES[nome_str] = res
        return res

    # Se ainda não encontrou, reconstrói o índice uma vez (caso arquivo tenha sido adicionado)
    reindexar_sprites()
    if chave_lower in _INDICE_SPRITES:
        res = str(_INDICE_SPRITES[chave_lower])
        _CACHE_SPRITES[nome_str] = res
        return res
    if chave_norm in _INDICE_SPRITES:
        res = str(_INDICE_SPRITES[chave_norm])
        _CACHE_SPRITES[nome_str] = res
        return res

    # Fallback padrão
    fallback = str(pasta_sprites / nome_str)
    return fallback

def caminho_cenario(nome_arquivo: str = "") -> str:
    """Retorna o caminho de um cenário na subpasta Cenarios ou através do localizador de imagens."""
    if not nome_arquivo:
        return caminho_recurso("Sprites", "Cenarios")

    pasta_cenarios = DIRETORIO_PROJETO / "Sprites" / "Cenarios"
    direto = pasta_cenarios / nome_arquivo
    if direto.exists():
        return str(direto)

    # Usa o localizador inteligente
    return caminho_imagem(nome_arquivo)

def caminho_botao(nome_arquivo: str) -> str:
    """Retorna o caminho de um botão na subpasta Botoes ou através do localizador de imagens."""
    if not nome_arquivo:
        return caminho_recurso("Sprites", "Botoes")

    pasta_botoes = DIRETORIO_PROJETO / "Sprites" / "Botoes"
    direto = pasta_botoes / nome_arquivo
    if direto.exists():
        return str(direto)

    # Usa o localizador inteligente
    return caminho_imagem(nome_arquivo)

def caminho_vfx(nome_arquivo: str) -> str:
    """Retorna o caminho de VFX ou ataques."""
    if not nome_arquivo:
        return caminho_recurso("VFX")

    pasta_vfx = DIRETORIO_PROJETO / "VFX"
    direto = pasta_vfx / nome_arquivo
    if direto.exists():
        return str(direto)

    pasta_ataques = DIRETORIO_PROJETO / "Sprites" / "Ataques"
    tentativa_ataque = pasta_ataques / nome_arquivo
    if tentativa_ataque.exists():
        return str(tentativa_ataque)

    return caminho_imagem(nome_arquivo)

def caminho_conquista(nome_arquivo: str = "") -> str:
    """Retorna o caminho de um ícone de conquista na subpasta Conquistas ou através do localizador de imagens."""
    if not nome_arquivo:
        return caminho_recurso("Sprites", "Conquistas")

    pasta_conquistas = DIRETORIO_PROJETO / "Sprites" / "Conquistas"
    direto = pasta_conquistas / nome_arquivo
    if direto.exists():
        return str(direto)

    return caminho_imagem(nome_arquivo)

def caminho_cutscene(nome_arquivo: str = "") -> str:
    """Retorna o caminho de arquivos de cutscene com suporte a variações de nome de pasta."""
    if not nome_arquivo:
        return caminho_recurso("Cutcene") if (DIRETORIO_PROJETO / "Cutcene").exists() else caminho_recurso("Cutscene")

    for pasta in ["Cutcene", "Cutscene"]:
        tentativa = DIRETORIO_PROJETO / pasta / nome_arquivo
        if tentativa.exists():
            return str(tentativa)

    # Busca insensível a maiúsculas/minúsculas
    for pasta in ["Cutcene", "Cutscene"]:
        p = DIRETORIO_PROJETO / pasta
        if p.exists():
            for f in p.glob("*"):
                if f.name.lower() == nome_arquivo.lower():
                    return str(f)

    return caminho_recurso("Cutcene", nome_arquivo)

def caminho_musica(nome_arquivo: str) -> str:
    return caminho_recurso("OSTs", nome_arquivo)

def caminho_fonte(nome_arquivo: str) -> str:
    return caminho_recurso("Fontes", nome_arquivo)
