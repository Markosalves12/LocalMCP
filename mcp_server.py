"""
Servidor MCP do LocalMCP.

Expõe o índice de documentos do seu computador para assistentes que falam MCP
(LM Studio, Claude Desktop, etc.). Roda por stdio:

    python mcp_server.py
"""
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "localmcp.settings")
django.setup()

from mcp.server.fastmcp import FastMCP  # noqa: E402

from documentos.models import Arquivo  # noqa: E402
from documentos.services import busca, indexador  # noqa: E402

mcp = FastMCP("localmcp")


@mcp.tool()
def buscar_documentos(pergunta: str, extensao: str | None = None, limite: int = 10) -> list[dict]:
    """Procura arquivos (PDF, Word, planilhas, texto) pelo assunto, nome ou conteúdo.
    Ex.: 'contrato de aluguel', extensao='pdf'. Retorna caminho, trecho e abas relevantes."""
    return busca.buscar(pergunta, extensao, limite)


@mcp.tool()
def listar_abas(caminho: str) -> list[dict]:
    """Lista as abas (pastas de trabalho) de uma planilha já indexada, com cabeçalho de cada uma."""
    arq = Arquivo.objects.filter(caminho=caminho).first()
    return busca.abas_da_planilha(arq.id) if arq else []


@mcp.tool()
def localizar_aba(nome_ou_assunto: str) -> list[dict]:
    """Encontra em qual planilha e em qual aba está um assunto (busca no nome e cabeçalho das abas)."""
    from documentos.models import Aba
    from django.db.models import Q
    qs = Aba.objects.select_related("arquivo").filter(
        Q(nome__icontains=nome_ou_assunto) | Q(cabecalho__icontains=nome_ou_assunto))[:30]
    return [{"planilha": a.arquivo.caminho, "aba": a.nome, "cabecalho": a.cabecalho} for a in qs]


@mcp.tool()
def ler_trecho(caminho: str, inicio: int = 0, tamanho: int = 4000) -> str:
    """Lê parte do texto extraído de um arquivo indexado."""
    arq = Arquivo.objects.filter(caminho=caminho).first()
    return arq.conteudo[inicio:inicio + min(tamanho, 20000)] if arq else "Arquivo não indexado."


@mcp.tool()
def reindexar(pasta: str | None = None) -> dict:
    """Atualiza o índice (todas as pastas configuradas ou só a informada)."""
    return indexador.indexar([pasta] if pasta else None)


if __name__ == "__main__":
    mcp.run()
