from rest_framework import serializers
from .models import Aba, Arquivo


class AbaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aba
        fields = ["nome", "ordem", "linhas", "colunas", "cabecalho"]


class ArquivoSerializer(serializers.ModelSerializer):
    abas = AbaSerializer(many=True, read_only=True)

    class Meta:
        model = Arquivo
        fields = ["id", "nome", "caminho", "extensao", "pasta", "tamanho", "modificado_em", "erro", "abas"]
