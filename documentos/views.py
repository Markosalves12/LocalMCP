import threading

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Arquivo
from .serializers import ArquivoSerializer
from .services import busca, indexador, lmstudio

_estado = {"rodando": False, "ultimo": None}


class ArquivoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Arquivo.objects.prefetch_related("abas")
    serializer_class = ArquivoSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        ext = self.request.query_params.get("extensao")
        return qs.filter(extensao=ext) if ext else qs


@api_view(["GET"])
def buscar(request):
    q = request.query_params.get("q", "")
    if not q.strip():
        return Response({"erro": "informe ?q="}, status=400)
    return Response({"pergunta": q, "resultados": busca.buscar(q, request.query_params.get("extensao"))})


@api_view(["POST"])
def perguntar(request):
    """Busca + resposta em linguagem natural pelo LM Studio."""
    q = request.data.get("pergunta", "")
    resultados = busca.buscar(q)
    try:
        resposta = lmstudio.responder(q, resultados)
    except Exception as e:
        resposta = f"LM Studio indisponível ({e}). Veja os arquivos encontrados abaixo."
    return Response({"resposta": resposta, "resultados": resultados})


@api_view(["GET", "POST"])
def indexar(request):
    if request.method == "POST" and not _estado["rodando"]:
        def rodar():
            _estado["rodando"] = True
            try:
                _estado["ultimo"] = indexador.indexar()
            finally:
                _estado["rodando"] = False
        threading.Thread(target=rodar, daemon=True).start()
        _estado["rodando"] = True
    return Response({**_estado, "total_no_indice": Arquivo.objects.count()})


def pagina_inicial(request):
    return render(request, "documentos/index.html")
