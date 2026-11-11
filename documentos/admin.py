from django.contrib import admin
from .models import Aba, Arquivo


class AbaInline(admin.TabularInline):
    model = Aba
    extra = 0


@admin.register(Arquivo)
class ArquivoAdmin(admin.ModelAdmin):
    list_display = ("nome", "extensao", "pasta", "modificado_em")
    search_fields = ("nome", "caminho", "conteudo")
    list_filter = ("extensao",)
    inlines = [AbaInline]
