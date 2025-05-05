from pathlib import Path
import os

# ------------------------------
# BASE
# ------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------
# SEGURIDAD
# ------------------------------
SECRET_KEY = 'django-insecure-$bi34q5_o71fe7j&_9b5q*l608%+ycmstseavzupk3lm)&s-j0'
DEBUG = True

ALLOWED_HOSTS = [
    '192.168.1.64', 'localhost', '127.0.0.1',
    'dentotis.com', 'www.dentotis.com'
]
CSRF_TRUSTED_ORIGINS = ['http://192.168.1.64']

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
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gestion_citas_db',
        'USER': 'gestion_user',
        'PASSWORD': 'gestion_pass',
        'HOST': 'localhost',
        'PORT': '5432',
    }
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

