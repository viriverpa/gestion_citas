from pathlib import Path
import os
import dj_database_url


# ------------------------------
# BASE
# ------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------
# SEGURIDAD
# ------------------------------

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'clave_local_insegura')
DEBUG = os.environ.get('DEBUG', '') != 'False'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Añadimos manualmente los dominios permitidos
ALLOWED_HOSTS += ['www.dentotis.com']

CSRF_TRUSTED_ORIGINS = [
    f"https://{host}" for host in ALLOWED_HOSTS if host != 'localhost'
]

# ------------------------------
# Seguridad en HTTPS
# ------------------------------
# Seguridad en HTTPS
if not DEBUG:
    SECURE_SSL_REDIRECT = True  # Actívalo de nuevo
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
#   PREPEND_WWW = False  # NO forzar desde Django; Cloudflare ya lo hace

# ------------------------------
# APLICACIONES
# ------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'citas',
    'django_countries',
    'web',
]

# ------------------------------
# MIDDLEWARE
# ------------------------------
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',  # <-- debe estar antes que otros middlewares
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ------------------------------
# TEMPLATES
# ------------------------------
ROOT_URLCONF = 'gestion_citas.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'gestion_citas.wsgi.application'

# ---------------------------------
# DATA BASES
# -------------------------------

# Intenta obtener DATABASE_URL desde el entorno
DATABASE_URL = os.environ.get("DATABASE_URL")

# Si no está definida (como está pasando en Railway), usar manualmente la conexión de Neon
if not DATABASE_URL:
    DATABASE_URL = "postgresql://neondb_owner:npg_ScsgtRWm0Ew6@ep-bitter-shape-a4inklxr-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

DATABASES = {
    'default': dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        ssl_require=True
    )
}

# ------------------------------
# PASSWORD VALIDATION
# ------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ------------------------------
# LOCALIZACIÓN
# ------------------------------
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ------------------------------
# ARCHIVOS ESTÁTICOS
# ------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'web/static'),  # Aquí apunta a tu carpeta correcta
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# ------------------------------
# ARCHIVOS DE MEDIA (imágenes)
# ------------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ------------------------------
# AUTOINCREMENTO
# ------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


#-------------------------------
# EMAIL GOOGLE NIDO
#-------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'fundacionnidodevida@gmail.com'
EMAIL_HOST_PASSWORD = 'tjxj vhlq yjgp jczo'  # Usa clave de aplicación segura
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ------------------------------
# ARCHIVOS ESTÁTICOS
# ------------------------------
STATIC_URL = '/static/'

# Ruta de archivos estáticos en desarrollo
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'web/static'),
]

# Ruta donde se recopilan para producción
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Activar almacenamiento de archivos estáticos solo en producción
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
