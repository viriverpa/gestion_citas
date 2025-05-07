from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.http import HttpResponse
from .forms import LoginForm, HistoriaClinicaForm, BusquedaPacienteForm, PacienteForm, PacienteEditForm
from citas.models import Cita, HistoriaClinica, Paciente
from datetime import datetime
from django.db.models import Q
from django.core.mail import send_mail
from django.utils.timezone import now
from django.utils.crypto import get_random_string

def landing(request):
    if request.method == 'GET':
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
    pacientes = Paciente.objects.all().order_by('nombre')
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
            nombre = form.cleaned_data['nombre']

            clave_generada = get_random_string(length=10)

            user = User.objects.create_user(
                username=documento,
                password=clave_generada,
                email=email,
                first_name=nombre
            )

            grupo, _ = Group.objects.get_or_create(name='Pacientes')
            user.groups.add(grupo)

            paciente.user = user
            paciente.save()

            send_mail(
                subject='Tu cuenta ha sido creada en Clínica Dentotis',
                message=(
                    f"Hola {nombre},\n\n"
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
def editar_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)

    if request.method == 'POST':
        form = PacienteEditForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            return redirect('panel_pacientes')
    else:
        form = PacienteEditForm(instance=paciente)

    return render(request, 'web/editar_paciente.html', {'form': form, 'paciente': paciente})


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
            Q(nombre__icontains=q) | Q(documento_id__icontains=q)
        ).order_by('nombre')

    return render(request, 'web/buscar_paciente.html', {
        'form': form,
        'pacientes': pacientes
    })


@login_required
def crear_cita_paciente(request):
    return HttpResponse("<h3>Aquí pronto podrás agendar tu cita eligiendo fecha y hora disponibles.</h3>")


def registro_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            paciente = form.save(commit=False)
            documento = form.cleaned_data['documento_id']
            email = form.cleaned_data['email']
            nombre = form.cleaned_data['nombre']

            clave_generada = get_random_string(length=10)

            user = User.objects.create_user(
                username=documento,
                password=clave_generada,
                email=email,
                first_name=nombre
            )
            grupo, _ = Group.objects.get_or_create(name='Pacientes')
            user.groups.add(grupo)
            paciente.user = user
            paciente.save()

            send_mail(
                subject='Tu cuenta ha sido creada en Clínica Dentotis',
                message=(
                    f"Hola {nombre},\n\n"
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

            messages.success(request, f"¡Cuenta creada! Revisa tu correo para la contraseña.")
            return redirect('landing')
    else:
        form = PacienteForm()

    return render(request, 'web/registro_paciente.html', {'form': form})
