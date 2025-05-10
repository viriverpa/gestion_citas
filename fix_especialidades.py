import psycopg2

# Conexión a la base de datos Neon
conn = psycopg2.connect(
    dbname="neondb",
    user="neondb_owner",
    password="npg_ScsgtRWm0Ew6",
    host="ep-bitter-shape-a4inklxr-pooler.us-east-1.aws.neon.tech",
    port="5432",
    sslmode="require"
)

cursor = conn.cursor()

# Asegurar que la especialidad 'Sin especialidad' exista
cursor.execute("""
    INSERT INTO citas_especialidad (nombre)
    VALUES ('Sin especialidad')
    ON CONFLICT (nombre) DO NOTHING;
""")

# Obtener el ID de 'Sin especialidad'
cursor.execute("""
    SELECT id FROM citas_especialidad WHERE nombre = 'Sin especialidad';
""")
especialidad_id = cursor.fetchone()[0]

# Reemplazar en la tabla citas_odontologo cualquier valor no numérico por el ID de 'Sin especialidad'
cursor.execute("""
    UPDATE citas_odontologo
    SET especialidad = %s
    WHERE especialidad !~ '^[0-9]+';
""", (especialidad_id,))

conn.commit()

# Confirmación
cursor.execute("SELECT COUNT(*) FROM citas_odontologo WHERE especialidad = %s;", (especialidad_id,))
n_actualizados = cursor.fetchone()[0]
print(f"Especialidades corregidas: {n_actualizados}")

cursor.close()
conn.close()

