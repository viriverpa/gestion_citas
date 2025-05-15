from django.db import models
from django_countries.fields import CountryField
from django.contrib.auth.models import User

from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField

class Paciente(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    documento_id = models.CharField(max_length=10, unique=True, verbose_name="Cédula o Documento")
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    pais = CountryField(blank_label='(Selecciona el país)')
    telefono = models.CharField(
        max_length=20,
        help_text="Escribe el número sin el código del país. Ej: 3001234567"
    )

    def __str__(self):
        return f"{self.nombre} ({self.documento_id})"

class Odontologo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  # NUEVA LÍNEA
    nombre = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre} ({self.especialidad})"



class Tratamiento(models.Model):
    nombre = models.CharField(max_length=100)
    duracion = models.IntegerField(help_text="Duración en minutos")

    def __str__(self):
        return f"{self.nombre} ({self.duracion} min)"

class Cita(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    odontologo = models.ForeignKey(Odontologo, on_delete=models.CASCADE)
    tratamiento = models.ForeignKey(Tratamiento, on_delete=models.SET_NULL, null=True)
    fecha_hora = models.DateTimeField()
    motivo_consulta = models.TextField(blank=True)

    ESTADOS_CITA = [
        ('P', 'Pendiente'),
        ('T', 'Terminada'),
    ]
    estado = models.CharField(max_length=1, choices=ESTADOS_CITA, default='P')

    def __str__(self):
        return f"{self.paciente.nombre} - {self.tratamiento.nombre} ({self.fecha_hora})"


class HorarioAtencion(models.Model):
    dia_semana = models.IntegerField(help_text="1=Lunes ... 7=Domingo")
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __str__(self):
        return f"Día {self.dia_semana}: {self.hora_inicio} - {self.hora_fin}"

class HistoriaClinica(models.Model):
    paciente = models.OneToOneField(Paciente, on_delete=models.CASCADE)
    antecedentes = models.TextField(blank=True)
    medicamentos = models.TextField(blank=True)
    alergias = models.TextField(blank=True)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"Historia Clínica de {self.paciente.nombre}"

class FotoTratamiento(models.Model):
    historia_clinica = models.ForeignKey(HistoriaClinica, on_delete=models.CASCADE, related_name='fotos')
    imagen = models.ImageField(upload_to='tratamientos/')
    descripcion = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Foto de {self.historia_clinica.paciente.nombre} - {self.fecha.strftime('%Y-%m-%d')}"
