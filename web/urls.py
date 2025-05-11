# web/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [

    # -------------------
    # Panel de inicio y autenticación
    # -------------------
    path('', views.landing, name='landing'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_paciente, name='registro_paciente'),

    # -------------------
    # Paneles según rol
    # -------------------
    path('panel/', views.panel_admin, name='panel_admin'),
    path('especialista/', views.panel_especialista, name='panel_especialista'),
    path('panel/paciente/', views.panel_paciente, name='panel_paciente'),
    path('panel/paciente/crear-cita/', views.crear_cita_paciente, name='crear_cita_paciente'),

    # -------------------
    # Gestión de pacientes
    # -------------------
    path('pacientes/', views.panel_pacientes, name='panel_pacientes'),
    path('pacientes/nuevo/', views.crear_paciente, name='crear_paciente'),
    path('editar-perfil/', views.editar_paciente, name='editar_paciente'), # Paciente edita su perfil
    path('editar-paciente/<int:pk>/', views.editar_paciente, name='editar_paciente_admin'), # Admin/especialista

    # -------------------
    # Historia clínica y tratamiento
    # -------------------
    path('pacientes/<int:paciente_id>/historia/', views.gestionar_historia, name='gestionar_historia'),
    path('historia/<int:paciente_id>/', views.ver_historia, name='ver_historia'),
    path('historia/<int:paciente_id>/crear/', views.crear_historia_clinica, name='crear_historia'),
    path('historia/<int:paciente_id>/fotos/', views.ver_fotos_tratamiento, name='ver_fotos_tratamiento'),
    path('historia/<int:paciente_id>/subir_foto/', views.subir_foto_tratamiento, name='subir_foto_tratamiento'),

    # -------------------
    # Citas
    # -------------------
    path('cita/<int:cita_id>/atendida/', views.marcar_cita_atendida, name='marcar_cita_atendida'),
    path('panel/paciente/guardar-cita/', views.guardar_cita_paciente, name='guardar_cita_paciente'),
    path('pacientes/<int:paciente_id>/crear-cita/', views.crear_cita_admin, name='crear_cita_admin'),
    path('pacientes/<int:paciente_id>/cita/', views.ver_panel_paciente_admin, name='ver_panel_paciente_admin'),
    path('citas/', views.panel_citas, name='panel_citas'),
    path('panel/paciente/reprogramar/<int:cita_id>/', views.reprogramar_cita_paciente, name='reprogramar_cita_paciente'),

    # -------------------
    # Búsqueda
    # -------------------
    path('buscar_paciente/', views.buscar_paciente, name='buscar_paciente'),

    # -------------------
    # Recuperación de contraseña
    # -------------------
    path('recuperar-contrasena/', auth_views.PasswordResetView.as_view(
        template_name='web/password_reset_form.html',
        email_template_name='web/password_reset_email.html',
        subject_template_name='web/password_reset_subject.txt',
        success_url='/recuperar-contrasena/enviado/',
    ), name='password_reset'),

    path('recuperar-contrasena/enviado/', auth_views.PasswordResetDoneView.as_view(
        template_name='web/password_reset_done.html',
    ), name='password_reset_done'),

    path('recuperar-contrasena/confirmar/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='web/password_reset_confirm.html',
        success_url='/recuperar-contrasena/completado/',
    ), name='password_reset_confirm'),

    path('recuperar-contrasena/completado/', auth_views.PasswordResetCompleteView.as_view(
        template_name='web/password_reset_complete.html',
    ), name='password_reset_complete'),
    
    # -------------------
    #  Crear la URL y vista para mostrar la malla
    # -------------------
    
    path('panel/paciente/malla-disponible/', views.malla_disponibilidad_paciente, name='malla_disponibilidad_paciente'),
    

]  
