from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("arquivos", views.ArquivoViewSet)

urlpatterns = [
    path("", views.pagina_inicial, name="inicio"),
    path("api/", include(router.urls)),
    path("api/buscar/", views.buscar),
    path("api/perguntar/", views.perguntar),
    path("api/indexar/", views.indexar),
]
