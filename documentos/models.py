from django.db import models


class Arquivo(models.Model):
    caminho = models.CharField(max_length=1024, unique=True)
    nome = models.CharField(max_length=512, db_index=True)
    extensao = models.CharField(max_length=16, db_index=True)
    pasta = models.CharField(max_length=1024)
    tamanho = models.BigIntegerField(default=0)
    modificado_em = models.DateTimeField()
    conteudo = models.TextField(blank=True, help_text="Texto extraído (resumido)")
    erro = models.CharField(max_length=512, blank=True)
    indexado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-modificado_em"]

    def __str__(self):
        return self.caminho


class Aba(models.Model):
    """Uma aba (pasta de trabalho / worksheet) de uma planilha."""
    arquivo = models.ForeignKey(Arquivo, on_delete=models.CASCADE, related_name="abas")
    nome = models.CharField(max_length=255)
    ordem = models.PositiveIntegerField(default=0)
    linhas = models.PositiveIntegerField(default=0)
    colunas = models.PositiveIntegerField(default=0)
    cabecalho = models.TextField(blank=True)
    amostra = models.TextField(blank=True)

    class Meta:
        ordering = ["arquivo", "ordem"]

    def __str__(self):
        return f"{self.arquivo.nome} › {self.nome}"
