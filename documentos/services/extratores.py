"""Extrai texto e estrutura de cada tipo de arquivo."""
from pathlib import Path

LIMITE_TEXTO = 200_000  # caracteres guardados por arquivo


def extrair_pdf(caminho: Path) -> str:
    from pypdf import PdfReader
    leitor = PdfReader(str(caminho))
    partes = []
    for pagina in leitor.pages[:200]:
        partes.append(pagina.extract_text() or "")
        if sum(map(len, partes)) > LIMITE_TEXTO:
            break
    return "\n".join(partes)


def extrair_docx(caminho: Path) -> str:
    import docx
    return "\n".join(p.text for p in docx.Document(str(caminho)).paragraphs)


def extrair_texto(caminho: Path) -> str:
    return caminho.read_text(encoding="utf-8", errors="ignore")


def extrair_planilha(caminho: Path) -> tuple[str, list[dict]]:
    """Retorna (texto, lista de abas) de um .xlsx/.xlsm."""
    from openpyxl import load_workbook
    wb = load_workbook(str(caminho), read_only=True, data_only=True)
    abas, textos = [], []
    for ordem, ws in enumerate(wb.worksheets):
        linhas = []
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if i >= 20:
                break
            linhas.append(" | ".join("" if v is None else str(v) for v in row))
        cabecalho = linhas[0] if linhas else ""
        amostra = "\n".join(linhas[1:])
        abas.append({
            "nome": ws.title, "ordem": ordem,
            "linhas": ws.max_row or 0, "colunas": ws.max_column or 0,
            "cabecalho": cabecalho[:2000], "amostra": amostra[:5000],
        })
        textos.append(f"[Aba {ws.title}]\n{cabecalho}\n{amostra}")
    wb.close()
    return "\n".join(textos), abas


def extrair(caminho: Path) -> tuple[str, list[dict]]:
    ext = caminho.suffix.lower()
    if ext in (".xlsx", ".xlsm"):
        texto, abas = extrair_planilha(caminho)
    elif ext == ".pdf":
        texto, abas = extrair_pdf(caminho), []
    elif ext == ".docx":
        texto, abas = extrair_docx(caminho), []
    else:
        texto, abas = extrair_texto(caminho), []
    return texto[:LIMITE_TEXTO], abas
