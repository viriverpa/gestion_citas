# verificar_conexion_neon.py
import os
import django
from django.conf import settings
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_citas.settings')
django.setup()

from django.db import connection

print("🔍 Verificando conexión a la base de datos...")
print(f"📦 ENGINE: {settings.DATABASES['default']['ENGINE']}")
print(f"🧭 HOST: {settings.DATABASES['default']['HOST']}")
print(f"🗃 NAME: {settings.DATABASES['default']['NAME']}")
print(f"👤 USER: {settings.DATABASES['default']['USER']}")

# Ejecuta una consulta directa
with connection.cursor() as cursor:
    cursor.execute("SELECT current_database();")
    dbname = cursor.fetchone()[0]
    print(f"📡 Estás conectado a: {dbname}")

# Muestra todos los usuarios
User = get_user_model()
usuarios = User.objects.all()
print(f"👥 Usuarios existentes en esta base de datos ({len(usuarios)}):")
for u in usuarios:
    print(f"  - {u.username}")
