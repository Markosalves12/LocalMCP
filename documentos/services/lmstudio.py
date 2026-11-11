"""Mesmo cliente do ChatComLocalLM: usado para responder em linguagem natural."""
import requests
from django.conf import settings

TIMEOUT = 120


def chat(mensagens: list[dict], temperature: float = 0.2) -> str:
    r = requests.post(
        f"{settings.LMSTUDIO_URL.rstrip('/')}/chat/completions",
        headers={"Authorization": f"Bearer {settings.LMSTUDIO_API_KEY}"},
        json={"model": settings.LMSTUDIO_CHAT_MODEL, "messages": mensagens, "temperature": temperature},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def responder(pergunta: str, resultados: list[dict]) -> str:
    contexto = "\n\n".join(
        f"- {r['nome']} ({r['caminho']})\n  abas: {', '.join(r['abas_relevantes']) or '-'}\n  trecho: {r['trecho']}"
        for r in resultados[:8]
    ) or "Nenhum arquivo encontrado."
    return chat([
        {"role": "system", "content": "Você é um assistente de documentos local. Responda em português, "
         "indicando o caminho completo dos arquivos e, para planilhas, a aba. Use só os arquivos listados."},
        {"role": "user", "content": f"Pergunta: {pergunta}\n\nArquivos encontrados:\n{contexto}"},
    ])
