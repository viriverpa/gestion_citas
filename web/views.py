from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.http import HttpResponse
from .forms import LoginForm, HistoriaClinicaForm, BusquedaPacienteForm, PacienteForm, PacienteEditForm
from citas.models import Cita, HistoriaClinica, Paciente, Odontologo, Tratamiento
from datetime import datetime, timedelta, time
from django.db.models import Q
from django.core.mail import send_mail
from django.utils.timezone import now
from django.utils.crypto import get_random_string
from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import make_aware
from django.utils import timezone



def landing(request):
    if request.user.is_authenticated:
        logout(request)  # Solo cierra sesión si ya está logueado

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

                if 'Administrador' in grupos:
                    return redirect('panel_admin')
                elif 'Especialistas' in grupos:
                    return redirect('panel_especialista')
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
    grupos = request.user.groups.values_list('name', flat=True)
    return render(request, 'web/panel_admin.html', {'grupos': grupos})


@login_required
def panel_especialista(request):
    hoy = datetime.now().date()
    citas = Cita.objects.filter(
        odontologo__nombre=request.user.username,
        fecha_hora__date__gte=hoy,
        estado='P'
    ).order_by('fecha_hora')

    return render(request, 'web/panel_especialista.html', {'citas': citas})


@login_required
def panel_paciente(request):
    try:
        paciente = Paciente.objects.get(user=request.user)
    except Paciente.DoesNotExist:
        messages.error(request, "No se encontró información del paciente.")
        return redirect('landing')

    citas_proximas = Cita.objects.filter(
        paciente=paciente,
        fecha_hora__gte=now()
    ).order_by('fecha_hora')

    return render(request, 'web/panel_paciente.html', {
        'paciente': paciente,
        'citas': citas_proximas
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
    return render(request, 'web/panel_pacientes.html', {'pacientes': pacientes})


@login_required
def logout_view(request):
    logout(request)
    return redirect('landing')


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

    return render(request, 'web/buscar_paciente.html', {
        'form': form,
        'pacientes': pacientes
    })


from django.utils import timezone  # Asegúrate de tener esta línea arriba

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

        cita = Cita.objects.create(
            paciente=paciente,
            odontologo=odontologo,
            tratamiento=tratamiento,
            clinica=clinica,
            motivo_consulta="Pendiente definir fecha y hora",
            estado='P',
            fecha_hora=timezone.now()  # Provisional
        )

        messages.success(request, "La cita ha sido registrada. Falta definir fecha y hora.")
        return redirect('panel_paciente')

    return render(request, 'web/crear_cita_paciente.html', {
        'paciente': paciente,
        'odontologos': odontologos,
        'tratamientos': tratamientos,
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
def malla_disponibilidad_paciente(request):
    paciente = get_object_or_404(Paciente, user=request.user)
    tratamiento_id = request.GET.get('tratamiento')

    if not tratamiento_id:
        messages.error(request, "Debes seleccionar un tratamiento válido.")
        return redirect('crear_cita_paciente')

    tratamiento = get_object_or_404(Tratamiento, id=tratamiento_id)
    clinica = paciente.clinica_creacion
    especialidad_requerida = tratamiento.especialidad_requerida

    odontologos = Odontologo.objects.filter(clinica_asignada=clinica, especialidad=especialidad_requerida)

    hoy = datetime.now().date()
    dias = [hoy + timedelta(days=d) for d in range(0, 7) if (hoy + timedelta(days=d)).weekday() in [2, 4]]  # Miércoles=2, Viernes=4

    bloques_por_dia = []

    for dia in dias:
        bloques = []
        hora_inicio = time(8, 0)
        hora_fin = time(12, 0)

        while datetime.combine(dia, hora_inicio) < datetime.combine(dia, hora_fin):
            for cabina in range(1, 4):
                bloques.append({
                    'inicio': datetime.combine(dia, hora_inicio),
                    'cabina': cabina
                })
            hora_inicio = (datetime.combine(dia, hora_inicio) + timedelta(minutes=tratamiento.duracion)).time()

        hora_inicio = time(14, 0)
        hora_fin = time(18, 0)

        while datetime.combine(dia, hora_inicio) < datetime.combine(dia, hora_fin):
            for cabina in range(1, 4):
                bloques.append({
                    'inicio': datetime.combine(dia, hora_inicio),
                    'cabina': cabina
                })
            hora_inicio = (datetime.combine(dia, hora_inicio) + timedelta(minutes=tratamiento.duracion)).time()

        bloques_por_dia.append({'fecha': dia, 'bloques': bloques})

    return render(request, 'web/malla_disponibilidad_paciente.html', {
        'paciente': paciente,
        'tratamiento': tratamiento,
        'bloques_por_dia': bloques_por_dia,
    })

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
