from django.core.management.base import BaseCommand

from documentos.services.indexador import indexar


class Command(BaseCommand):
    help = "Indexa as pastas configuradas em PASTAS_INDEXADAS (ou as informadas)."

    def add_arguments(self, parser):
        parser.add_argument("pastas", nargs="*")

    def handle(self, *args, **opts):
        r = indexar(opts["pastas"] or None, progresso=lambda c: self.stdout.write(f"  {c}"))
        self.stdout.write(self.style.SUCCESS(f"Concluído: {r}"))
