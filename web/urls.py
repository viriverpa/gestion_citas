# web/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('panel/', views.panel_admin, name='panel_admin'),
    path('especialista/', views.panel_especialista, name='panel_especialista'),
    path('cita/<int:cita_id>/atendida/', views.marcar_cita_atendida, name='marcar_cita_atendida'),
    path('historia/<int:paciente_id>/', views.ver_historia, name='ver_historia'),
    path('logout/', views.logout_view, name='logout'),
    path('pacientes/', views.panel_pacientes, name='panel_pacientes'),
    path('pacientes/nuevo/', views.crear_paciente, name='crear_paciente'),
    path('pacientes/<int:paciente_id>/editar/', views.editar_paciente, name='editar_paciente'),
    path('pacientes/<int:paciente_id>/historia/', views.gestionar_historia, name='gestionar_historia'),
    path('historia/<int:paciente_id>/crear/', views.crear_historia_clinica, name='crear_historia'),
    path('historia/<int:paciente_id>/fotos/', views.ver_fotos_tratamiento, name='ver_fotos_tratamiento'),
    path('historia/<int:paciente_id>/subir_foto/', views.subir_foto_tratamiento, name='subir_foto_tratamiento'),
    path('buscar_paciente/', views.buscar_paciente, name='buscar_paciente'),
    path('panel/paciente/', views.panel_paciente, name='panel_paciente'),
    path('panel/paciente/crear-cita/', views.crear_cita_paciente, name='crear_cita_paciente'),
    path('registro/', views.registro_paciente, name='registro_paciente'),

# Flujo completo de recuperación de contraseña
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

]
