from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# SEGURIDAD: En producción usar variables de entorno
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-tu-clave-secreta-local')
DEBUG = 'RENDER' not in os.environ # False en Render, True en tu PC
ALLOWED_HOSTS = ['*'] # Permitir acceso desde cualquier lugar

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # --- MIS APPS ---
    'corsheaders',      # Permisos
    'rest_framework',   # API
    'segmentacion',     # Tu IA
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # <--- PRIMERO
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # <--- SEGUNDO (Para Render)
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # <--- RUTA TEMPLATES
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Archivos Estáticos (CSS, JS, Imágenes)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Configuración CORS (Permitir todo para pruebas)
CORS_ALLOW_ALL_ORIGINS = True