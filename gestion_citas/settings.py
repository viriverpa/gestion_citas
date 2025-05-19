# settings.py - Archivo Corregido con Base de Datos Condicional

from pathlib import Path
import os
import dj_database_url
from django.core.exceptions import ImproperlyConfigured # Importar para usar la excepción


# ------------------------------
# BASE
# ------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------
# SECURITY
# ------------------------------
# SECRET_KEY: Should be unique and unpredictable. Get from environment in production.
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'clave_local_insegura_y_secreta_para_desarrollo') # Usar una clave insegura por defecto solo para desarrollo local

# DEBUG: Set to True in development, False in production. Controlled by environment variable.
# 'True'.lower() == 'true' es una forma robusta de leer True/False desde strings.
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

# ALLOWED_HOSTS: Hosts/domain names that this Django site can serve.
# Get from environment in production. Allow local hosts in development.
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Añadir manualmente los dominios de producción solo si no estamos en DEBUG
# Esto evita advertencias en producción.
if not DEBUG:
    # Asegúrate de que tu dominio o dominios de producción están aquí
    ALLOWED_HOSTS += ['www.dentotis.com', 'dentotis.com'] # Añadir ambos subdominio si aplica

# CSRF_TRUSTED_ORIGINS: Needed for production for secure form submissions from these origins.
# In DEBUG=True, Django handles this differently for local.
CSRF_TRUSTED_ORIGINS = []
if not DEBUG and os.environ.get('CSRF_TRUSTED_ORIGINS'): # Leer de env en producción si está
     CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS').split(',')
elif not DEBUG: # Fallback o configuración explícita si no está en env (menos común en Railway)
     # Crear la lista a partir de ALLOWED_HOSTS para https
     CSRF_TRUSTED_ORIGINS = [f"https://{host}" for host in ALLOWED_HOSTS if host not in ['localhost', '127.0.0.1']]


# ------------------------------
# Security in HTTPS (Apply these settings ONLY in Production)
# ------------------------------
if not DEBUG:
    SECURE_SSL_REDIRECT = True # Redirigir HTTP a HTTPS
    SESSION_COOKIE_SECURE = True # Asegurar que las cookies de sesión solo se envíen por HTTPS
    CSRF_COOKIE_SECURE = True # Asegurar que la cookie CSRF solo se envíe por HTTPS
    SECURE_HSTS_SECONDS = 31536000 # Activar HSTS (HTTP Strict Transport Security) por 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True # Aplicar HSTS también a subdominios
    # SECURE_HSTS_PRELOAD = True # Activar HSTS Preload (requiere registro y precargado en navegadores - habilitar solo después de probar y si planeas registrar)


# ------------------------------
# APPS
# ------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Tus apps
    'citas',
    'web',

    # Apps de terceros
    'django_countries',
    'widget_tweaks', # <-- ¡Añadir esta línea!
    # 'whitenoise.runserver_nostatic', # Puede ser útil si tienes problemas sirviendo estáticos en desarrollo con WhiteNoise, pero no es la causa del error actual. No la añado por defecto.
]

# ------------------------------
# MIDDLEWARE
# ------------------------------
MIDDLEWARE = [
    # Seguridad de Django debe ir primera o casi.
    'django.middleware.security.SecurityMiddleware',

    # WhiteNoise: Debe ir después de SecurityMiddleware.
    # Ayuda a servir tus archivos estáticos de forma eficiente.
    'whitenoise.middleware.WhiteNoiseMiddleware',

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
        'DIRS': [], # Si tienes plantillas a nivel de proyecto, irían aquí
        'APP_DIRS': True, # Busca plantillas dentro de las carpetas 'templates' de cada app
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
# Configuración de base de datos condicional para desarrollo vs producción
# ---------------------------------

if DEBUG:
    # Configuración para entorno de DESARROLLO (DEBUG=True)
    # Usaremos SQLite por defecto, que es simple y no requiere servidor de BD
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3', # La base de datos se guarda en un archivo llamado db.sqlite3 en la raíz del proyecto
        }
    }
    print("Usando base de datos local (SQLite) para desarrollo.") # Mensaje para confirmar en logs locales

else:
    # Configuración para entorno de PRODUCCIÓN (DEBUG=False)
    # Leeremos la URL de conexión de la variable de entorno DATABASE_URL (establecida por Railway)
    DATABASE_URL = os.environ.get('DATABASE_URL')

    if not DATABASE_URL:
         # Si DATABASE_URL no está definida en producción, algo está mal.
         # Es un error de configuración que debe evitar que el servidor arranque.
         raise ImproperlyConfigured("La variable de entorno DATABASE_URL no está configurada en producción.")

    # Parsear la URL de la base de datos de producción usando dj_database_url
    # conn_max_age ayuda a mantener conexiones persistentes.
    # ssl_require=True es crucial para la seguridad de la conexión a bases de datos remotas como Neon.
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL, # Usar la URL de la variable de entorno
            conn_max_age=600,
            ssl_require=True
        )
    }
    print("Usando base de datos de producción (desde DATABASE_URL).") # Mensaje para confirmar en logs de producción


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
# LOCALIZATION
# ------------------------------
LANGUAGE_CODE = 'es' # Idioma de tu aplicación
TIME_ZONE = 'America/Bogota' # Zona horaria (Asegúrate que sea la correcta)
USE_I18N = True # Habilitar internacionalización
USE_L10N = True # Habilitar localización (formato de números, fechas - Nota: obsoleto en Django 4.0+)
USE_TZ = True # Habilitar zonas horarias (Importante para manejar correctamente fechas/horas)


# ------------------------------
# STATIC FILES
# ------------------------------
# STATIC_URL: La URL base para servir archivos estáticos (ej: /static/)
STATIC_URL = '/static/'

# STATICFILES_DIRS: Lista de directorios donde Django buscará archivos estáticos SOURCE
# durante desarrollo (runserver) y para collectstatic.
STATICFILES_DIRS = [
    # os.path.join(BASE_DIR, 'static'), # Si tuvieras una carpeta 'static' en la raíz del proyecto
    os.path.join(BASE_DIR, 'web/static'), # Tu carpeta de estáticos dentro de la app 'web'
    # Puedes añadir otras carpetas de estáticos de tus apps aquí si no están en su carpeta 'static' por defecto
]

# STATIC_ROOT: El directorio *único* donde collectstatic recopilará todos los archivos estáticos
# de todas las fuentes para producción. Debe estar fuera de tus carpetas de código fuente.
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') # Crea una carpeta 'staticfiles' en la raíz del proyecto


# STATICFILES_STORAGE: Cómo se almacenan y sirven los archivos estáticos.
# Usar Whitenoise en producción para optimización y servir directamente.
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# En desarrollo (DEBUG=True), Django por defecto usa StaticFilesStorage, que sirve desde STATICFILES_DIRS.
# No necesitas especificarlo explícitamente aquí a menos que quieras usar Whitenoise para servir en desarrollo (menos común).


# ------------------------------
# MEDIA FILES (Archivos subidos por usuarios, ej: imágenes de perfil, documentos)
# ------------------------------
MEDIA_URL = '/media/' # URL base para servir archivos de media
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') # Directorio físico donde se guardan los archivos subidos


# ------------------------------
# AUTOFIELD
# ------------------------------
# Tipo de campo autoincremental por defecto para IDs de modelos
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


#-------------------------------
# EMAIL CONFIGURATION (Asegúrate de usar variables de entorno para datos sensibles)
#-------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
# Obtener datos sensibles (usuario y contraseña) de variables de entorno
# NUNCA hardcodees contraseñas o credenciales sensibles directamente en el código.
# Uso de defaults solo para que funcione en desarrollo si no configuras env vars locales,
# pero para producción DEBEN venir de env vars.
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'fundacionnidodevida@gmail.com') # Usuario del remitente
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '¡¡¡CAMBIAR_ESTO_POR_UNA_VARIABLE_DE_ENTORNO_EN_PRODUCCION!!!') # <-- **MUY IMPORTANTE**: Obtener de variable de entorno segura en producción
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER # Usar el mismo usuario como remitente por defecto

# ------------------------------
# OTRAS CONFIGURACIONES (Opcional)
# Puedes añadir configuraciones específicas de tus apps o librerías aquí
# ------------------------------

# Ejemplo: Configuración de django-countries si fuera necesaria alguna específica
# COUNTRIES_ONLY = [...] # Limitar la lista de países si es necesario