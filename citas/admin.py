from django.contrib import admin
from .models import (
    Clinica,
    Paciente,
    Odontologo,
    Tratamiento,
    Cita,
    HorarioAtencion,
    HistoriaClinica,
    FotoTratamiento,
)

@admin.register(Clinica)
class ClinicaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion')
    search_fields = ('nombre',)

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'apellidos', 'documento_id', 'telefono', 'clinica_creacion')
    list_filter = ('clinica_creacion',)
    search_fields = ('nombres', 'apellidos', 'documento_id', 'email')

@admin.register(Odontologo)
class OdontologoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'especialidad', 'clinica_asignada', 'user')
    list_filter = ('especialidad', 'clinica_asignada')
    search_fields = ('nombre', 'user__username')

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'odontologo', 'tratamiento', 'clinica', 'fecha_hora', 'estado')
    list_filter = ('clinica', 'estado', 'odontologo')
    search_fields = ('paciente__nombres', 'tratamiento__nombre', 'odontologo__nombre')

@admin.register(HorarioAtencion)
class HorarioAtencionAdmin(admin.ModelAdmin):
    list_display = ('odontologo', 'clinica', 'dia_semana', 'hora_inicio', 'hora_fin')
    list_filter = ('clinica', 'odontologo')

@admin.register(Tratamiento)
class TratamientoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'duracion', 'especialidad_requerida')
    list_filter = ('especialidad_requerida',)
    search_fields = ('nombre',)

admin.site.register(HistoriaClinica)
admin.site.register(FotoTratamiento)
