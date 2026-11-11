"""Busca por palavras no nome, conteúdo e abas das planilhas."""
import re

from django.db.models import Q

from ..models import Aba, Arquivo

STOPWORDS = {"a", "o", "as", "os", "de", "da", "do", "das", "dos", "e", "em", "que", "trata",
             "onde", "esta", "está", "tá", "ta", "qual", "um", "uma", "sobre", "assunto",
             "pdf", "planilha", "arquivo", "documento", "com", "para", "por", "no", "na"}


def termos(pergunta: str) -> list[str]:
    palavras = re.findall(r"\w+", pergunta.lower())
    return [p for p in palavras if p not in STOPWORDS and len(p) > 2]


def trecho(texto: str, termo: str, raio: int = 120) -> str:
    i = texto.lower().find(termo)
    if i < 0:
        return ""
    ini, fim = max(0, i - raio), i + len(termo) + raio
    return ("…" if ini else "") + texto[ini:fim].replace("\n", " ") + "…"


def buscar(pergunta: str, extensao: str | None = None, limite: int = 20) -> list[dict]:
    lista = termos(pergunta) or [pergunta.lower().strip()]
    filtro = Q()
    for t in lista:
        filtro |= Q(nome__icontains=t) | Q(conteudo__icontains=t) | Q(abas__nome__icontains=t)
    qs = Arquivo.objects.filter(filtro).distinct()
    if extensao:
        qs = qs.filter(extensao=extensao if extensao.startswith(".") else f".{extensao}")

    resultados = []
    for arq in qs[:500]:
        nome, conteudo = arq.nome.lower(), arq.conteudo.lower()
        pontos = sum(5 * (t in nome) + min(conteudo.count(t), 20) for t in lista)
        abas = [a.nome for a in arq.abas.all() if any(t in a.nome.lower() or t in a.cabecalho.lower() for t in lista)]
        pontos += 3 * len(abas)
        resultados.append({
            "id": arq.id, "nome": arq.nome, "caminho": arq.caminho, "extensao": arq.extensao,
            "modificado_em": arq.modificado_em.isoformat(), "pontuacao": pontos,
            "abas_relevantes": abas,
            "trecho": next((s for s in (trecho(arq.conteudo, t) for t in lista) if s), ""),
        })
    resultados.sort(key=lambda r: r["pontuacao"], reverse=True)
    return resultados[:limite]


def abas_da_planilha(arquivo_id: int) -> list[dict]:
    return list(Aba.objects.filter(arquivo_id=arquivo_id).values(
        "nome", "ordem", "linhas", "colunas", "cabecalho"))
