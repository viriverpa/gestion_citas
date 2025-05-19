# web/views.py - Archivo Corregido

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.http import HttpResponse
from django.core.mail import send_mail
from django.db.models import Q
from django.utils import timezone
from django.utils.timezone import now
from django.utils.crypto import get_random_string
from .forms import BusquedaPacienteForm # Esta importación parece redundante si ya está en el bloque de abajo, pero la dejo
from django.utils.formats import date_format
from datetime import datetime, timedelta, time

from .forms import (
    LoginForm,
    HistoriaClinicaForm,
    BusquedaPacienteForm,
    # PacienteForm, # <-- Eliminada esta línea
    PacienteEditForm, # <-- Aseguramos que se importa PacienteEditForm
)

from citas.models import (
    Cita,
    HistoriaClinica,
    Paciente,
    Odontologo,
    Tratamiento,
)


def landing(request):
    if request.user.is_authenticated:
        logout(request)

    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            documento = form.cleaned_data['documento']
            password = form.cleaned_data['password']
            user = authenticate(username=documento, password=password)

            if user is not None:
                login(request, user)
                grupos = list(user.groups.values_list('name', flat=True))

                nombre = f"{user.first_name} {user.last_name}".strip() or user.username

                if 'Administrador' in grupos:
                    request.session['saludo'] = f"👨‍💼 Bienvenido Administrador: {nombre}"
                    return redirect('panel_admin')

                elif 'Especialistas' in grupos:
                    request.session['saludo'] = f"🦷 Bienvenido Dr. {nombre}"
                    return redirect('panel_admin')  # o 'mis_pacientes_agendados' si decides redirigir allí

                elif 'Pacientes' in grupos:
                    return redirect('panel_paciente')

                else:
                    logout(request)
                    form.add_error(None, 'Este usuario no tiene un rol asignado.')
            else:
                form.add_error(None, 'Documento o contraseña incorrectos.')

    return render(request, 'web/landing.html', {'form': form})


@login_required
def panel_admin(request):
    grupos = list(request.user.groups.values_list('name', flat=True))

    saludo = request.session.get('saludo')  # ✅ Usar .get en lugar de .pop
    return render(request, 'web/panel_admin.html', {
        'grupos': grupos,
        'saludo': saludo,
    })


@login_required
def panel_especialista(request):
    hoy = now().date()

    # Obtener las citas futuras del especialista autenticado
    citas = Cita.objects.filter(
        odontologo__user=request.user,
        fecha_hora__date__gte=hoy,
        estado='P'
    ).order_by('fecha_hora')

    return render(request, 'web/panel_especialista.html', {
        'citas': citas,
        'pendientes_count': citas.count()
    })




@login_required
def marcar_cita_atendida(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    if cita.odontologo.nombre == request.user.username: # Posible bug: comparar nombre con username. Debería ser user=request.user. Pero no es el error actual.
        cita.estado = 'T' if cita.estado != 'T' else 'P'
        cita.save()
    return redirect('panel_especialista')


@login_required
def ver_historia(request, paciente_id):
    historia = HistoriaClinica.objects.filter(paciente_id=paciente_id).first()
    if not historia:
        return render(request, 'web/ver_historia.html', {
            'historia': None,
            'paciente_id': paciente_id
        })
    return render(request, 'web/ver_historia.html', {'historia': historia})


@login_required
def panel_pacientes(request):
    pacientes = Paciente.objects.all().order_by('apellidos', 'nombres')
    es_administrador = request.user.groups.filter(name='Administrador').exists()

    # Extraer y eliminar el mensaje de reprogramación si existe
    reprogramada = request.session.pop('reprogramada', None)

    return render(request, 'web/panel_pacientes.html', {
        'pacientes': pacientes,
        'es_administrador': es_administrador,
        'reprogramada': reprogramada,
    })


@login_required
def logout_view(request):
    logout(request)
    return redirect('landing')

# Hay una segunda definición de logout_view, esto es un bug.
# Dejaré la primera (redirect) y comentaré la segunda (HttpResponse)
# @login_required
# def logout_view(request):
#     if request.method == 'POST':
#         logout(request)
#         return redirect('landing')
#     return HttpResponse(status=405)  # Method not allowed


@login_required
def crear_paciente(request):
    if request.method == 'POST':
        form = PacienteEditForm(request.POST) # <-- Uso corregido
        if form.is_valid():
            paciente = form.save(commit=False)

            documento = form.cleaned_data['documento_id']
            email = form.cleaned_data['email']
            nombres = form.cleaned_data['nombres']
            apellidos = form.cleaned_data['apellidos']
            nombre_completo = f"{nombres} {apellidos}"

            clave_generada = get_random_string(length=10)

            user = User.objects.create_user(
                username=documento,
                password=clave_generada,
                email=email,
                first_name=nombres,
                last_name=apellidos,
            )

            grupo, _ = Group.objects.get_or_create(name='Pacientes')
            user.groups.add(grupo)

            paciente.user = user
            paciente.save() # ✅ Paciente guardado después de asignar user

            send_mail(
                subject='Tu cuenta ha sido creada en Clínica Dentotis',
                message=(
                    f"Hola {nombre_completo},\n\n"
                    f"Tu cuenta ha sido creada exitosamente.\n\n"
                    f"Usuario: {documento}\n"
                    f"Contraseña temporal: {clave_generada}\n\n"
                    f"Te recomendamos cambiar tu contraseña luego de iniciar sesión.\n\n"
                    f"Atentamente,\nClínica Dentotis"
                ),
                from_email=None, # Usará DEFAULT_FROM_EMAIL de settings.py
                recipient_list=[email],
                fail_silently=False,
            )

            messages.success(
                request,
                f"Paciente creado exitosamente. Usuario: {documento} - Contraseña enviada por correo."
            )

            return redirect('panel_pacientes')
    else:
        form = PacienteEditForm() # <-- Uso corregido

    return render(request, 'web/crear_paciente.html', {'form': form})

@login_required
def editar_paciente(request, pk=None):
    # Si es un paciente, edita su propio perfil
    if request.user.groups.filter(name='Pacientes').exists():
        paciente = get_object_or_404(Paciente, user=request.user)
    else:
        paciente = get_object_or_404(Paciente, pk=pk)

    if request.method == 'POST':
        form = PacienteEditForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, "Información actualizada correctamente.")
            return redirect('panel_paciente') if request.user.groups.filter(name='Pacientes').exists() else redirect('panel_pacientes')
    else:
        form = PacienteEditForm(instance=paciente)
        es_paciente = request.user.groups.filter(name='Pacientes').exists()
        return render(request, 'web/editar_paciente.html', {
            'form': form,
            'es_paciente': es_paciente
        })



@login_required
def gestionar_historia(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    historia, _ = HistoriaClinica.objects.get_or_create(paciente=paciente)

    if request.method == 'POST':
        form = HistoriaClinicaForm(request.POST, instance=historia)
        if form.is_valid():
            form.save()
            return render(request, 'web/gestionar_historia.html', {
                'form': form,
                'paciente': paciente,
                'historia': historia,
                'mensaje_exito': f'Historia clínica de {paciente.nombre} guardada correctamente.'
            })
    else:
        form = HistoriaClinicaForm(instance=historia)

    return render(request, 'web/gestionar_historia.html', {
        'form': form,
        'paciente': paciente,
        'historia': historia
    })


@login_required
def crear_historia_clinica(request, paciente_id):
    return HttpResponse("Crear historia clínica en construcción.")


@login_required
def ver_fotos_tratamiento(request, paciente_id):
    return HttpResponse("Aquí se mostrarán las fotos del tratamiento del paciente.")


@login_required
def subir_foto_tratamiento(request, paciente_id):
    return HttpResponse("Aquí se podrá subir la foto de tratamiento del paciente.")


@login_required
def buscar_paciente(request):
    pacientes = []
    form = BusquedaPacienteForm(request.GET or None)

    if form.is_valid():
        q = form.cleaned_data['query']
        pacientes = Paciente.objects.filter(
            Q(nombres__icontains=q) |
            Q(apellidos__icontains=q) |
            Q(documento_id__icontains=q)
        ).order_by('apellidos', 'nombres')

    return render(request, 'web/panel_pacientes.html', {
        'pacientes': pacientes,
        'busqueda': True,
        'form': form  # ✅ necesario para que {{ form.query }} funcione
    })





def registro_paciente(request):
    if request.method == 'POST':
        form = PacienteEditForm(request.POST) # <-- Uso corregido
        if form.is_valid():
            paciente = form.save(commit=False)

            documento = form.cleaned_data['documento_id']
            email = form.cleaned_data['email']
            nombres = form.cleaned_data['nombres']
            apellidos = form.cleaned_data['apellidos']
            # clinica = form.cleaned_data['clinica_creacion'] # <-- Este campo no parece estar en PacienteEditForm

            nombre_completo = f"{nombres} {apellidos}"
            clave_generada = get_random_string(length=10)

            user = User.objects.create_user(
                username=documento,
                password=clave_generada,
                email=email,
                first_name=nombres,
                last_name=apellidos
            )

            grupo, _ = Group.objects.get_or_create(name='Pacientes')
            user.groups.add(grupo)

            paciente.user = user
            # paciente.clinica_creacion = clinica  # <-- Este campo tampoco parece estar en PacienteEditForm, o su manejo es diferente
            paciente.save()

            send_mail(
                subject='Tu cuenta ha sido creada en Clínica Dentotis',
                message=(
                    f"Hola {nombre_completo},\n\n"
                    f"Tu cuenta ha sido creada exitosamente.\n\n"
                    f"Usuario: {documento}\n"
                    f"Contraseña temporal: {clave_generada}\n\n"
                    f"Te recomendamos cambiar tu contraseña luego de iniciar sesión.\n\n"
                    f"Atentamente,\nClínica Dentotis"
                ),
                from_email=None,
                recipient_list=[email],
                fail_silently=False,
            )

            messages.success(request, "¡Cuenta creada! Revisa tu correo para la contraseña.")
            return redirect('landing')
    else:
        form = PacienteEditForm() # <-- Uso corregido

    return render(request, 'web/registro_paciente.html', {'form': form})



@login_required
def crear_cita_admin(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    clinica = paciente.clinica_creacion # Asumo que este campo existe y es un modelo Clinica

    odontologos = Odontologo.objects.filter(clinica_asignada=clinica) # Asumo que clinica_asignada es un ForeignKey a Clinica en Odontologo
    tratamientos = Tratamiento.objects.all() # Asumo que Tratamiento no depende de clinica

    if request.method == 'POST':
        odontologo_id = request.POST.get('odontologo')
        tratamiento_id = request.POST.get('tratamiento')

        if not odontologo_id or not tratamiento_id:
            messages.error(request, "Debes seleccionar un odontólogo y un tratamiento.")
            return redirect('crear_cita_admin', paciente_id=paciente.id)

        odontologo = get_object_or_404(Odontologo, id=odontologo_id, clinica_asignada=clinica)
        tratamiento = get_object_or_404(Tratamiento, id=tratamiento_id)

        Cita.objects.create(
            paciente=paciente,
            odontologo=odontologo,
            tratamiento=tratamiento,
            clinica=clinica, # Asumo que Cita tiene un ForeignKey a Clinica
            motivo_consulta="Pendiente definir fecha y hora",
            estado='P',
            fecha_hora=timezone.now()  # provisional
        )

        messages.success(request, "La cita ha sido registrada. Falta definir fecha y hora.")
        return redirect('panel_pacientes')

    return render(request, 'web/crear_cita_admin.html', {
        'paciente': paciente,
        'odontologos': odontologos,
        'tratamientos': tratamientos,
    })

@login_required
def panel_citas(request):
    return render(request, 'web/panel_citas.html')

# -------------------
# Crear la URL y vista para mostrar la malla
# -------------------


@login_required
def malla_disponibilidad_paciente(request):
    tratamiento_id = request.GET.get('tratamiento')
    odontologo_id = request.GET.get('odontologo')
    reprogramar_id = request.GET.get('reprogramar')

    tratamiento = Tratamiento.objects.filter(id=tratamiento_id).first()
    odontologo = Odontologo.objects.filter(id=odontologo_id).first()

    # Obtener el paciente según el rol
    if request.user.groups.filter(name='Pacientes').exists():
        paciente = get_object_or_404(Paciente, user=request.user)
    elif reprogramar_id:
        cita = get_object_or_404(Cita, id=reprogramar_id)
        paciente = cita.paciente
    else:
        return redirect('landing')

    if not tratamiento or not odontologo:
        messages.error(request, "Debes seleccionar primero tratamiento y odontólogo.")
        # Redirigir a la vista correcta para crear cita paciente
        return redirect('crear_cita_paciente') # Corregir si la URL se llama diferente

    hoy = datetime.now().date()
    pagina = int(request.GET.get('pagina', 0))

    # Buscar los próximos miércoles y viernes
    dias_disponibles = []
    for i in range(60): # Buscar hasta 60 días en el futuro
        dia = hoy + timedelta(days=i)
        if dia.weekday() in [2, 4]:  # Miércoles (2) o Viernes (4)
             # Opcional: si el día actual es M o V, incluirlo si la hora ya pasó
             if dia == hoy and datetime.now().time() > time(18, 0): # Si hoy es M o V y ya pasaron las 6pm
                 continue # No incluir este día si ya pasó el horario de trabajo
             dias_disponibles.append(dia)

    desde = pagina * 12 # Mostrar bloques de 12 días
    hasta = desde + 12
    dias_mostrados = dias_disponibles[desde:hasta]

    # Cargar todas las citas pendientes de esos días para el odontólogo Y las cabinas
    # Agregamos filtro por odontologo para solo cargar las citas relevantes
    citas = Cita.objects.filter(
        odontologo=odontologo, # Filtrar por odontologo
        fecha_hora__date__in=dias_mostrados,
        estado='P'
    ).values_list('fecha_hora', 'cabina') # Solo necesitamos fecha_hora y cabina

    # Convertir a set de tuplas (datetime, cabina) para búsqueda rápida
    # Asegurarse de que las horas sean timezone-aware si fecha_hora es aware
    citas_ocupadas = set()
    for fecha, cabina in citas:
        # Convertir a la zona horaria adecuada si es necesario, o asegurar que sea aware
        # Asumo que fecha_hora es timezone-aware como timezone.now()
        if timezone.is_naive(fecha):
             fecha = timezone.make_aware(fecha, timezone.get_current_timezone()) # Hacer aware si es naive
        citas_ocupadas.add((fecha.replace(second=0, microsecond=0), cabina))


    malla = []
    # Asumir que las cabinas disponibles son de 1 a 3 (como en el código original)
    cabinas_disponibles = range(1, 4)

    for dia in dias_mostrados:
        bloques_disponibles_dia = [] # Usar un nombre diferente para evitar confusión
        # Hacer la hora de inicio y fin timezone-aware
        hora_inicio = timezone.make_aware(datetime.combine(dia, time(8, 0)))
        hora_fin = timezone.make_aware(datetime.combine(dia, time(18, 0)))


        intervalo = timedelta(minutes=30) # Intervalo de 30 minutos
        current_hora = hora_inicio # Usar un nombre diferente

        while current_hora < hora_fin:
            # Solo mostrar bloques si la hora actual es en el futuro (considerando timezone)
            if current_hora >= timezone.now():
                for cabina in cabinas_disponibles: # Iterar sobre cabinas
                    if (current_hora, cabina) not in citas_ocupadas:
                         # Formatear la hora para la plantilla
                         # %I:%M %p da "08:00 AM", lstrip("0") quita el cero inicial para 8:00 AM
                         hora_formateada = current_hora.strftime("%I:%M %p").lstrip("0").lower()

                         bloques_disponibles_dia.append({
                            'fecha_hora_completa': current_hora, # Pasar el datetime completo para el link/form
                            'hora': hora_formateada,
                            'cabina': cabina,
                            'especialista': odontologo.nombre if odontologo else 'Por asignar',
                         })
            current_hora += intervalo # Sumar el intervalo

        malla.append({'fecha': dia, 'disponibles': bloques_disponibles_dia}) # Usar bloques_disponibles_dia

    # Calcular si hay días anteriores o siguientes para paginación
    hay_anteriores = pagina > 0
    hay_mas = hasta < len(dias_disponibles)


    return render(request, 'web/malla_disponibilidad_paciente.html', {
        'malla': malla,
        'pagina': pagina,
        'hay_anteriores': hay_anteriores,
        'hay_mas': hay_mas,
        'tratamiento_seleccionado': tratamiento.nombre if tratamiento else 'No Seleccionado',
        'odontologo_seleccionado': odontologo.nombre if odontologo else 'No Seleccionado',
        'tratamiento_id': tratamiento.id if tratamiento else '',
        'odontologo_id': odontologo.id if odontologo else '',
        'reprogramar_id': reprogramar_id if reprogramar_id else '',
        'paciente': paciente,
    })


@login_required
def guardar_cita_paciente(request):
    if request.method == 'POST':
        # Obtener fecha_hora_completa del formulario (viene como string, necesitas parsearla)
        fecha_hora_str = request.POST.get('fecha_hora_completa')
        cabina = request.POST.get('cabina')
        tratamiento_id = request.POST.get('tratamiento_id')
        odontologo_id = request.POST.get('odontologo_id')
        reprogramar_id = request.POST.get('reprogramar_id')


        # Convertir fecha_hora_str a un objeto datetime timezone-aware
        # El formato string debe coincidir con cómo lo pases desde la plantilla
        try:
             # Asumo que lo pasas como ISO format o algún formato parseable por Django/Python
             fecha_hora = datetime.fromisoformat(fecha_hora_str) # Ejemplo si pasas ISO
             # Asegurar que es timezone-aware si es necesario
             if timezone.is_naive(fecha_hora):
                  fecha_hora = timezone.make_aware(fecha_hora, timezone.get_current_timezone())
        except (ValueError, TypeError):
             messages.error(request, "Formato de fecha u hora inválido.")
             # Redirigir de vuelta a la malla, pasando los parámetros necesarios
             url_malla = reverse('malla_disponibilidad_paciente') # Usar reverse para urls
             params = f"?tratamiento={tratamiento_id}&odontologo={odontologo_id}"
             if reprogramar_id:
                 params += f"&reprogramar={reprogramar_id}"
             return redirect(f"{url_malla}{params}")


        # Detectar al paciente correctamente según el flujo (mismo código que antes)
        if request.user.groups.filter(name='Pacientes').exists():
            paciente = Paciente.objects.filter(user=request.user).first()
        elif reprogramar_id:
            cita_origen = get_object_or_404(Cita, id=reprogramar_id)
            paciente = cita_origen.paciente
        else:
            return redirect('landing') # Si no es paciente ni reprograma, redirigir al landing

        # Obtener objetos Treatment, Odontologo y Clinica
        tratamiento = get_object_or_404(Tratamiento, id=tratamiento_id)
        odontologo = get_object_or_404(Odontologo, id=odontologo_id)
        clinica = paciente.clinica_creacion # Asumo que paciente tiene clinica_creacion


        # Validar que la franja no esté ocupada (excepto si reprograma la misma cita)
        qs_citas_existentes = Cita.objects.filter(fecha_hora=fecha_hora, cabina=int(cabina))
        if reprogramar_id:
             # Excluir la cita original si estamos reprogramando
             qs_citas_existentes = qs_citas_existentes.exclude(id=reprogramar_id)

        if qs_citas_existentes.exists():
            messages.warning(request, "Ese espacio ya fue reservado. Por favor elige otro.")
            # Redirigir de vuelta a la malla, pasando los parámetros necesarios
            url_malla = reverse('malla_disponibilidad_paciente')
            params = f"?tratamiento={tratamiento_id}&odontologo={odontologo_id}"
            if reprogramar_id:
                 params += f"&reprogramar={reprogramar_id}"
            return redirect(f"{url_malla}{params}")


        if reprogramar_id:
            # Si reprograma una cita existente
            cita = get_object_or_404(Cita, id=reprogramar_id, paciente=paciente, estado='P') # Asegurar que la cita existe, es de este paciente y está pendiente
            cita.fecha_hora = fecha_hora
            cita.cabina = int(cabina)
            cita.save()

            # Preparar mensaje de éxito para reprogramación
            request.session['reprogramada'] = {
                'paciente': f"{paciente.nombres} {paciente.apellidos}",
                'fecha': date_format(cita.fecha_hora, "l d/m/Y", use_l10n=True), # ✅ Fecha traducida
                'hora': cita.fecha_hora.strftime("%I:%M %p").lstrip("0").lower(), # Hora con AM/PM
                'odontologo': cita.odontologo.nombre,
                'tratamiento': cita.tratamiento.nombre,
                'cabina': cita.cabina,
            }
            messages.success(request, "✅ Tu cita ha sido reprogramada con éxito.")

        else:
            # Si crea una cita nueva
            Cita.objects.create(
                paciente=paciente,
                odontologo=odontologo,
                tratamiento=tratamiento,
                clinica=clinica,
                fecha_hora=fecha_hora,
                cabina=int(cabina),
                motivo_consulta="Asignado por paciente", # O un campo de formulario si aplica
                estado='P' # Estado inicial 'Pendiente'
            )
            request.session['cita_creada'] = True # Señal para mostrar mensaje en panel
            messages.success(request, "✅ Cita agendada exitosamente.")

        # Redirigir al panel del paciente o lista de pacientes admin después de guardar
        if request.user.groups.filter(name='Pacientes').exists():
            return redirect('panel_paciente')
        else:
            return redirect('panel_pacientes')

    # Si la solicitud no es POST, simplemente redirigir o mostrar formulario vacío si aplica
    # Esta vista es solo para POST, si llegan por GET es un error
    return HttpResponse(status=405) # Method Not Allowed


# -------------------
# Mostrar resumen de la última cita
# -------------------

@login_required
def panel_paciente(request):
    paciente = get_object_or_404(Paciente, user=request.user)

    # Limpiar mensajes almacenados (messages framework los usa una vez automáticamente)
    # storage = messages.get_messages(request)
    # storage.used = True # No siempre necesario, messages framework lo hace

    # Detectar y limpiar señales de éxito únicas desde sesión
    # No usar pop(..., False) si False es un valor posible y quieres diferenciar entre False y None/valor por defecto
    # Usar pop(..., None) y luego verificar si el resultado es None
    cita_reprogramada_data = request.session.pop('reprogramada', None)
    cita_creada_signal = request.session.pop('cita_creada', None)


    # Obtener última cita y próximas citas
    ultima_cita = Cita.objects.filter(paciente=paciente).order_by('-fecha_hora').first()
    citas_proximas = Cita.objects.filter(
        paciente=paciente,
        fecha_hora__gte=timezone.now() # Citas desde ahora en adelante
    ).order_by('fecha_hora')

    return render(request, 'web/panel_paciente.html', {
        'paciente': paciente,
        'ultima_cita': ultima_cita,
        'cita_reprogramada': cita_reprogramada_data, # Pasar los datos si existen
        'cita_creada_signal': cita_creada_signal, # Pasar la señal si existe
        'citas': citas_proximas,
    })


# -------------------
# Reprogramar cita (solo redirige a malla)
# -------------------

@login_required
def reprogramar_cita_paciente(request, cita_id):
    """
    Prepara los datos y redirige a la malla para seleccionar nueva fecha/hora.
    """

    # Obtener la cita pendiente (estado='P')
    # Si el usuario es 'Pacientes', solo su propia cita
    if request.user.groups.filter(name='Pacientes').exists():
        cita = get_object_or_404(Cita, id=cita_id, paciente__user=request.user, estado='P')
    else:
        # Admin o especialista puede reprogramar cualquier cita pendiente
        cita = get_object_or_404(Cita, id=cita_id, estado='P')

    # Citas terminadas ('T') no deben ser reprogramadas. Ya se filtra por estado='P'

    tratamiento_id = cita.tratamiento.id
    odontologo_id = cita.odontologo.id

    # Redirigir a la malla con los datos necesarios para reprogramación
    # Usar reverse para generar URLs dinámicamente es mejor
    from django.urls import reverse
    url_malla = reverse('malla_disponibilidad_paciente')
    return redirect(f"{url_malla}?tratamiento={tratamiento_id}&odontologo={odontologo_id}&reprogramar={cita.id}")


# -------------------
# Crear cita paciente (muestra formulario selección tratado/odontologo)
# -------------------

@login_required
def crear_cita_paciente(request):
    # Asumo que esta vista permite al paciente seleccionar Tratamiento y Odontologo
    paciente = get_object_or_404(Paciente, user=request.user)
    clinica = paciente.clinica_creacion # Asumo que este campo existe

    tratamientos = Tratamiento.objects.all() # Asumo que todos los tratamientos son visibles
    odontologos = Odontologo.objects.filter(clinica_asignada=clinica) # Filtrar odontologos por la clínica del paciente

    if request.method == 'POST':
        tratamiento_id = request.POST.get('tratamiento')
        odontologo_id = request.POST.get('odontologo')

        if not tratamiento_id or not odontologo_id:
            messages.error(request, "Debes seleccionar un tratamiento y un odontólogo.")
            return render(request, 'web/crear_cita_paciente.html', {
                'paciente': paciente,
                'odontologos': odontologos,
                'tratamientos': tratamientos,
            }) # Volver a renderizar el formulario con el error

        tratamiento = get_object_or_404(Tratamiento, id=tratamiento_id)
        odontologo = get_object_or_404(Odontologo, id=odontologo_id, clinica_asignada=clinica)


        # Validar si la especialidad del odontólogo coincide con la requerida por el tratamiento
        # Asumo que odontologo.especialidad y tratamiento.especialidad_requerida son campos comparables
        if odontologo.especialidad != tratamiento.especialidad_requerida:
            messages.error(request, "El odontólogo seleccionado no tiene la especialidad requerida para este tratamiento.")
            return render(request, 'web/crear_cita_paciente.html', {
                'paciente': paciente,
                'odontologos': odontologos,
                'tratamientos': tratamientos,
            }) # Volver a renderizar el formulario con el error


        # Si todo es válido, redirigir a la malla de disponibilidad
        from django.urls import reverse
        url_malla = reverse('malla_disponibilidad_paciente')
        return redirect(f"{url_malla}?tratamiento={tratamiento.id}&odontologo={odontologo.id}")

    # Si no es POST, renderizar el formulario inicial de selección
    return render(request, 'web/crear_cita_paciente.html', {
        'paciente': paciente,
        'odontologos': odontologos,
        'tratamientos': tratamientos,
    })

# -------------------
# Ver cita pendiente de Paciente (para Admin/Especialista)
# -------------------

@login_required
def ver_panel_paciente_admin(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)

    # Verifica si el usuario pertenece a staff (admin o especialista)
    # Asumo que 'Administrador' y 'Especialistas' son los nombres de los grupos
    if not request.user.is_staff and not request.user.groups.filter(name__in=['Administrador', 'Especialistas']).exists():
         messages.error(request, "No tienes permiso para ver este panel.") # Añadir mensaje
         return redirect('landing')


    # Obtener última cita del paciente
    # Si un paciente tiene varias citas, quizás quieras mostrar una lista, no solo la última
    # Pero siguiendo la lógica original, obtengo solo la última
    ultima_cita = Cita.objects.filter(paciente=paciente).order_by('-fecha_hora').first()

    # Si quieres mostrar todas las citas pendientes, podrías hacer:
    # citas_pendientes = Cita.objects.filter(paciente=paciente, estado='P').order_by('fecha_hora')

    es_administrador = request.user.groups.filter(name='Administrador').exists()
    es_especialista = request.user.groups.filter(name='Especialistas').exists() # Añadido check para especialista

    return render(request, 'web/panel_paciente.html', {
        'paciente': paciente,
        'ultima_cita': ultima_cita, # Pasando la última cita
        # 'citas_pendientes': citas_pendientes, # O pasar la lista de pendientes si se cambia la lógica
        'cita_reprogramada': None, # No aplica señal de reprogramación aquí
        'cita_creada_signal': None, # No aplica señal de creación aquí
        'citas': [ultima_cita] if ultima_cita else [], # Pasando la última cita en una lista (para iterar en template?)
        'acceso_admin': True, # Indica que se accedió desde un panel staff
        'es_administrador': es_administrador,
        'es_especialista': es_especialista, # Pasar si es especialista
    })


# -------------------
#Ver solo los mis citas de Paciente (para Especialista)
# -------------------

@login_required
def mis_pacientes_agendados(request):
    # Esta vista parece para que un especialista vea los pacientes QUE TIENEN citas agendadas CON ÉL
    especialista = Odontologo.objects.filter(user=request.user).first()
    if not especialista:
        messages.warning(request, "Tu usuario no está asociado a un odontólogo. Contacta al administrador.") # Mensaje más claro
        return redirect('panel_admin') # Redirigir al panel general si no es odontologo

    # Obtener pacientes únicos con citas futuras asignadas a este odontólogo
    # Asumo que quieres pacientes con citas PENDIENTES o FUTURAS con este especialista
    pacientes = Paciente.objects.filter(
        # Asegurarse que la cita está asignada a este especialista
        cita__odontologo=especialista,
        # Opcional: filtrar por fecha futura o estado pendiente si aplica
        # cita__fecha_hora__gte=timezone.now(),
        # cita__estado='P'
    ).distinct().order_by('apellidos', 'nombres')

    saludo = request.session.pop('saludo', None)  # ✅ Extraer saludo de sesión

    return render(request, 'web/panel_pacientes.html', {
        'pacientes': pacientes,
        'especialista_view': True, # Indica que se accedió desde la vista de especialista
        'es_administrador': False,
        'es_especialista': True, # Pasar si es especialista
        'saludo': saludo,
    })

# Importaciones que faltaban (si se usan):
# from django.urls import reverse # Ya importada en guardar_cita_paciente y reprogramar_cita_paciente
# from .forms import PacienteForm # Ya no se usa PacienteForm, solo PacienteEditForm