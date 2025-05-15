from django.contrib import admin
from .models import (
    Paciente,
    Odontologo,
    Tratamiento,
    Cita,
    HorarioAtencion,
    HistoriaClinica,
    FotoTratamiento,
)

@admin.register(Odontologo)
class OdontologoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'especialidad', 'user')
    list_filter = ('especialidad',)
    search_fields = ('nombre', 'user__username')

# Registro de los demás modelos
admin.site.register(Paciente)
admin.site.register(Tratamiento)
admin.site.register(Cita)
admin.site.register(HorarioAtencion)
admin.site.register(HistoriaClinica)
admin.site.register(FotoTratamiento)
