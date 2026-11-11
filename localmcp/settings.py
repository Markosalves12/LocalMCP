import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-troque-no-env")
DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"
# Servidor interno: por padrão só aceita acesso da própria máquina
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "documentos",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "localmcp.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]
WSGI_APPLICATION = "localmcp.wsgi.application"

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_TZ = True
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {"DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination", "PAGE_SIZE": 50}

# --- Indexação ---
PASTAS_INDEXADAS = [p.strip() for p in os.getenv("PASTAS_INDEXADAS", str(Path.home() / "Documents")).split(";") if p.strip()]
EXTENSOES = [e.strip().lower() for e in os.getenv("EXTENSOES", ".pdf,.xlsx,.xlsm,.docx,.txt,.md,.csv").split(",")]
TAMANHO_MAX_MB = int(os.getenv("TAMANHO_MAX_MB", "50"))
PASTAS_IGNORADAS = {"windows", "program files", "program files (x86)", "programdata", "$recycle.bin", "appdata", "node_modules", ".git"}

# --- LM Studio (mesmo padrão do ChatComLocalLM) ---
LMSTUDIO_URL = os.getenv("LMSTUDIO_URL", "http://localhost:1234/v1")
LMSTUDIO_API_KEY = os.getenv("LMSTUDIO_API_KEY", "lm-studio")
LMSTUDIO_CHAT_MODEL = os.getenv("LMSTUDIO_CHAT_MODEL", "google/gemma-4-e4b")
