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
from .forms import BusquedaPacienteForm
from django.utils.formats import date_format 
from datetime import datetime, timedelta, time

from .forms import (
    LoginForm,
    HistoriaClinicaForm,
    BusquedaPacienteForm,
    PacienteForm,
    PacienteEditForm,
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
    if cita.odontologo.nombre == request.user.username:
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
    return redirect('landing')@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('landing')
    return HttpResponse(status=405)  # Method not allowed


@login_required
def crear_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
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

            messages.success(
                request,
                f"Paciente creado exitosamente. Usuario: {documento} - Contraseña enviada por correo."
            )

            return redirect('panel_pacientes')
    else:
        form = PacienteForm()

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
        form = PacienteForm(request.POST)
        if form.is_valid():
            paciente = form.save(commit=False)

            documento = form.cleaned_data['documento_id']
            email = form.cleaned_data['email']
            nombres = form.cleaned_data['nombres']
            apellidos = form.cleaned_data['apellidos']
            clinica = form.cleaned_data['clinica_creacion']

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
            paciente.clinica_creacion = clinica  # ✅ esta es la línea que faltaba
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
        form = PacienteForm()

    return render(request, 'web/registro_paciente.html', {'form': form})



@login_required
def crear_cita_admin(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    clinica = paciente.clinica_creacion

    odontologos = Odontologo.objects.filter(clinica_asignada=clinica)
    tratamientos = Tratamiento.objects.all()

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
            clinica=clinica,
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

from django.utils import timezone

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
        return redirect('crear_cita_paciente')

    hoy = datetime.now().date()
    pagina = int(request.GET.get('pagina', 0))

    # Buscar los próximos miércoles y viernes
    dias_disponibles = []
    for i in range(60):
        dia = hoy + timedelta(days=i)
        if dia.weekday() in [2, 4]:  # Miércoles o Viernes
            dias_disponibles.append(dia)

    desde = pagina * 12
    hasta = desde + 12
    dias_mostrados = dias_disponibles[desde:hasta]

    # Cargar todas las citas pendientes de esos días
    citas = Cita.objects.filter(
        fecha_hora__date__in=dias_mostrados,
        estado='P'
    ).values_list('fecha_hora', 'cabina')

    citas_ocupadas = set((fecha.replace(second=0, microsecond=0), cabina) for fecha, cabina in citas)

    malla = []
    for dia in dias_mostrados:
        bloques_disponibles = []

        hora_inicio = timezone.make_aware(datetime.combine(dia, time(8, 0)))
        hora_fin = timezone.make_aware(datetime.combine(dia, time(18, 0)))

        while hora_inicio < hora_fin:
            for cabina in range(1, 4):
                if (hora_inicio, cabina) not in citas_ocupadas:
                    bloques_disponibles.append({
                        'hora': hora_inicio.strftime("%I:%M %p").lstrip("0").lower(),
                        'cabina': cabina,
                        'especialista': odontologo.nombre if odontologo else 'Por asignar',
                    })
            hora_inicio += timedelta(minutes=30)

        malla.append({'fecha': dia, 'disponibles': bloques_disponibles})

    return render(request, 'web/malla_disponibilidad_paciente.html', {
        'malla': malla,
        'pagina': pagina,
        'hay_anteriores': pagina > 0,
        'hay_mas': hasta < len(dias_disponibles),
        'tratamiento_seleccionado': tratamiento.nombre,
        'odontologo_seleccionado': odontologo.nombre,
        'tratamiento_id': tratamiento.id,
        'odontologo_id': odontologo.id,
        'reprogramar_id': reprogramar_id,
        'paciente': paciente,
    })


@login_required
def guardar_cita_paciente(request):
    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        cabina = request.POST.get('cabina')
        tratamiento_id = request.POST.get('tratamiento_id')
        odontologo_id = request.POST.get('odontologo_id')
        reprogramar_id = request.POST.get('reprogramar_id')

        # Detectar al paciente correctamente según el flujo
        if request.user.groups.filter(name='Pacientes').exists():
            paciente = Paciente.objects.filter(user=request.user).first()
        elif reprogramar_id:
            cita_origen = get_object_or_404(Cita, id=reprogramar_id)
            paciente = cita_origen.paciente
        else:
            return redirect('landing')

        tratamiento = Tratamiento.objects.filter(id=tratamiento_id).first()
        odontologo = Odontologo.objects.filter(id=odontologo_id).first()
        clinica = paciente.clinica_creacion if paciente else None

        if not all([fecha, hora, cabina, tratamiento, odontologo, paciente, clinica]):
            messages.error(request, "Faltan datos para registrar la cita.")
            return redirect('malla_disponibilidad_paciente')

        try:
            from datetime import datetime
            fecha_hora = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %I:%M %p")
        except ValueError:
            messages.error(request, "Formato de fecha u hora inválido.")
            return redirect('malla_disponibilidad_paciente')

        # Validar que la franja no esté ocupada (excepto si reprograma la misma)
        if Cita.objects.filter(fecha_hora=fecha_hora, cabina=int(cabina)).exclude(id=reprogramar_id).exists():
            messages.warning(request, "Ese espacio ya fue reservado. Por favor elige otro.")
            return redirect('malla_disponibilidad_paciente')

        if reprogramar_id:
            cita = get_object_or_404(Cita, id=reprogramar_id, paciente=paciente, estado='P')
            cita.fecha_hora = fecha_hora
            cita.cabina = int(cabina)
            cita.save()

            # ✅ Fecha traducida al español
            request.session['reprogramada'] = {
                'paciente': f"{paciente.nombres} {paciente.apellidos}",
                'fecha': date_format(cita.fecha_hora, "l d/m/Y", use_l10n=True),
                'hora': cita.fecha_hora.strftime("%I:%M %p").lstrip("0"),
                'odontologo': cita.odontologo.nombre,
                'tratamiento': cita.tratamiento.nombre,
                'cabina': cita.cabina,
            }

            messages.success(request, "✅ Tu cita ha sido reprogramada con éxito.")
        else:
            Cita.objects.create(
                paciente=paciente,
                odontologo=odontologo,
                tratamiento=tratamiento,
                clinica=clinica,
                fecha_hora=fecha_hora,
                cabina=int(cabina),
                motivo_consulta="Asignado por paciente",
                estado='P'
            )
            request.session['cita_creada'] = True
            messages.success(request, "✅ Cita agendada exitosamente.")

        if request.user.groups.filter(name='Pacientes').exists():
            return redirect('panel_paciente')
        else:
            return redirect('panel_pacientes')


# -------------------
# Mostrar resumen de la última cita
# -------------------
    
@login_required
def panel_paciente(request):
    paciente = get_object_or_404(Paciente, user=request.user)

    # Limpiar mensajes almacenados (solo si los usas vía messages.success)
    storage = messages.get_messages(request)
    storage.used = True

    # Detectar y limpiar señales de éxito únicas
    cita_reprogramada = request.session.pop('reprogramada', False)
    request.session.pop('cita_creada', None)

    # Obtener última cita y próximas citas
    ultima_cita = Cita.objects.filter(paciente=paciente).order_by('-fecha_hora').first()
    citas_proximas = Cita.objects.filter(
        paciente=paciente,
        fecha_hora__gte=now()
    ).order_by('fecha_hora')

    return render(request, 'web/panel_paciente.html', {
        'paciente': paciente,
        'ultima_cita': ultima_cita,
        'cita_reprogramada': cita_reprogramada,
        'citas': citas_proximas,
    })

    
# -------------------
# Reprogramar cita
# -------------------

@login_required
def reprogramar_cita_paciente(request, cita_id):
    """
    Permite reprogramar una cita pendiente ('P').

    - Si el usuario es del grupo 'Pacientes', solo puede reprogramar su propia cita pendiente.
    - Si el usuario es del staff (Administrador o Especialista), puede reprogramar cualquier cita pendiente.
    - Citas terminadas ('T') no pueden ser reprogramadas, ni siquiera accediendo manualmente por URL.
    """

    if request.user.groups.filter(name='Pacientes').exists():
        # El paciente solo puede acceder a su propia cita pendiente
        cita = get_object_or_404(Cita, id=cita_id, paciente__user=request.user, estado='P')
    else:
        # Admin o especialista puede acceder a cualquier cita pendiente
        cita = get_object_or_404(Cita, id=cita_id, estado='P')

    tratamiento_id = cita.tratamiento.id
    odontologo_id = cita.odontologo.id

    # Redirigir a la malla con los datos necesarios para reprogramación
    return redirect(f"/panel/paciente/malla-disponible/?tratamiento={tratamiento_id}&odontologo={odontologo_id}&reprogramar={cita.id}")

# -------------------
# Crear cita paciente
# -------------------

@login_required
def crear_cita_paciente(request):
    paciente = get_object_or_404(Paciente, user=request.user)
    clinica = paciente.clinica_creacion

    tratamientos = Tratamiento.objects.all()
    odontologos = Odontologo.objects.filter(clinica_asignada=clinica)

    if request.method == 'POST':
        tratamiento_id = request.POST.get('tratamiento')
        odontologo_id = request.POST.get('odontologo')

        if not tratamiento_id or not odontologo_id:
            messages.error(request, "Debes seleccionar un tratamiento y un odontólogo.")
            return redirect('crear_cita_paciente')

        tratamiento = get_object_or_404(Tratamiento, id=tratamiento_id)
        odontologo = get_object_or_404(Odontologo, id=odontologo_id, clinica_asignada=clinica)

        if odontologo.especialidad != tratamiento.especialidad_requerida:
            messages.error(request, "El odontólogo seleccionado no tiene la especialidad requerida para este tratamiento.")
            return redirect('crear_cita_paciente')

        return redirect(f"/panel/paciente/malla-disponible/?tratamiento={tratamiento.id}&odontologo={odontologo.id}")

    return render(request, 'web/crear_cita_paciente.html', {
        'paciente': paciente,
        'odontologos': odontologos,
        'tratamientos': tratamientos,
    })

# -------------------
# Ver cita pendiente de Paciente
# -------------------

@login_required
def ver_panel_paciente_admin(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)

    # Verifica si el usuario pertenece a staff (admin o especialista)
    if not request.user.is_staff and not request.user.groups.filter(name__in=['Administradores', 'Especialistas']).exists():
        return redirect('landing')

    # Obtener última cita del paciente
    ultima_cita = Cita.objects.filter(paciente=paciente).order_by('-fecha_hora').first()

    es_administrador = request.user.groups.filter(name='Administrador').exists()

    return render(request, 'web/panel_paciente.html', {
        'paciente': paciente,
        'ultima_cita': ultima_cita,
        'cita_reprogramada': False,
        'citas': [ultima_cita] if ultima_cita else [],
        'acceso_admin': True,
        'es_administrador': es_administrador
    })

# -------------------
#Ver solo los mis citas de Paciente
# -------------------

@login_required
def mis_pacientes_agendados(request):
    especialista = Odontologo.objects.filter(user=request.user).first()
    if not especialista:
        messages.warning(request, "No tienes pacientes asignados aún.")
        return redirect('panel_admin')

    # Obtener pacientes únicos con citas futuras asignadas a este odontólogo
    pacientes = Paciente.objects.filter(
        cita__odontologo=especialista,
        cita__fecha_hora__gte=timezone.now()
    ).distinct().order_by('apellidos', 'nombres')

    saludo = request.session.pop('saludo', None)  # ✅ Extraer saludo de sesión

    return render(request, 'web/panel_pacientes.html', {
        'pacientes': pacientes,
        'especialista': True,
        'es_administrador': False,
        'saludo': saludo,  # ✅ Pasar el saludo al template
    })


