import tempfile
from pathlib import Path

from django.test import TestCase, override_settings
from openpyxl import Workbook

from .services import busca, indexador


class IndexacaoTests(TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        Path(self.dir, "aluguel.txt").write_text("Contrato de aluguel do apartamento", encoding="utf-8")
        wb = Workbook()
        wb.active.title = "Vendas"
        wb.active.append(["Produto", "Valor"])
        for nome in ["Estoque", "Financeiro", "RH", "Compras"]:
            wb.create_sheet(nome).append(["Coluna", nome])
        wb.save(Path(self.dir, "empresa.xlsx"))

    @override_settings(EXTENSOES=[".txt", ".xlsx"])
    def test_planilha_com_cinco_abas_e_localizada(self):
        indexador.indexar([self.dir])
        r = busca.buscar("onde está a aba financeiro")
        self.assertEqual(r[0]["nome"], "empresa.xlsx")
        self.assertIn("Financeiro", r[0]["abas_relevantes"])
        self.assertEqual(len(busca.abas_da_planilha(r[0]["id"])), 5)

    @override_settings(EXTENSOES=[".txt", ".xlsx"])
    def test_texto_por_assunto(self):
        indexador.indexar([self.dir])
        self.assertEqual(busca.buscar("documento sobre aluguel")[0]["nome"], "aluguel.txt")
