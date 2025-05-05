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
import os
import dj_database_url

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'clave_local_insegura')

DEBUG = os.environ.get('DEBUG', '') != 'False'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

CSRF_TRUSTED_ORIGINS = [
    f"https://{host}" for host in ALLOWED_HOSTS if host != 'localhost'
]


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

# ------------------------------
# DATABASE
# ------------------------------

DATABASES = {
    'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
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
# Archivos estáticos en producción
# ------------------------------
STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Activar almacenamiento de archivos estáticos solo en producción
if not DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
