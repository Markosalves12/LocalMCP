"""Percorre as pastas configuradas e grava o índice no banco."""
import os
from datetime import datetime, timezone
from pathlib import Path

from django.conf import settings
from django.db import transaction

from ..models import Aba, Arquivo
from .extratores import extrair


def _ignorar(pasta: str) -> bool:
    return pasta.lower() in settings.PASTAS_IGNORADAS or pasta.startswith(".")


def indexar_arquivo(caminho: Path) -> Arquivo:
    stat = caminho.stat()
    modificado = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
    existente = Arquivo.objects.filter(caminho=str(caminho)).first()
    if existente and existente.modificado_em == modificado and not existente.erro:
        return existente  # não mudou, pula

    texto, abas, erro = "", [], ""
    if stat.st_size <= settings.TAMANHO_MAX_MB * 1024 * 1024:
        try:
            texto, abas = extrair(caminho)
        except Exception as e:  # arquivo corrompido, protegido por senha etc.
            erro = repr(e)[:500]
    else:
        erro = "arquivo maior que o limite"

    with transaction.atomic():
        arq, _ = Arquivo.objects.update_or_create(
            caminho=str(caminho),
            defaults={
                "nome": caminho.name, "extensao": caminho.suffix.lower(),
                "pasta": str(caminho.parent), "tamanho": stat.st_size,
                "modificado_em": modificado, "conteudo": texto, "erro": erro,
            },
        )
        arq.abas.all().delete()
        Aba.objects.bulk_create([Aba(arquivo=arq, **a) for a in abas])
    return arq


def indexar(pastas: list[str] | None = None, progresso=None) -> dict:
    pastas = pastas or settings.PASTAS_INDEXADAS
    vistos, total, erros = set(), 0, 0
    for raiz in pastas:
        for atual, subpastas, arquivos in os.walk(raiz):
            subpastas[:] = [s for s in subpastas if not _ignorar(s)]
            for nome in arquivos:
                caminho = Path(atual) / nome
                if caminho.suffix.lower() not in settings.EXTENSOES or nome.startswith("~$"):
                    continue
                try:
                    arq = indexar_arquivo(caminho)
                    vistos.add(arq.caminho)
                    total += 1
                    erros += bool(arq.erro)
                    if progresso:
                        progresso(caminho)
                except OSError:
                    erros += 1
    # remove do índice arquivos que sumiram do disco
    removidos = 0
    for raiz in pastas:
        qs = Arquivo.objects.filter(caminho__startswith=raiz).exclude(caminho__in=vistos)
        removidos += qs.count()
        qs.delete()
    return {"indexados": total, "com_erro": erros, "removidos": removidos}
