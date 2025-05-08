# web/forms.py

from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from citas.models import Paciente
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from citas.models import Paciente
from citas.models import HistoriaClinica

class LoginForm(forms.Form):
    documento = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario o Número de documento'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )

class PacienteEditForm(forms.ModelForm):
    class Meta:
        model = Paciente
        exclude = ['user', 'documento_id', 'clinica_creacion']
        widgets = {
            'nombres': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
            'pais': forms.Select(attrs={'class': 'form-select'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
        }


class HistoriaClinicaForm(forms.ModelForm):
    class Meta:
        model = HistoriaClinica
        fields = ['antecedentes', 'medicamentos', 'alergias', 'observaciones']
        widgets = {
            'antecedentes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Escribe antecedentes relevantes'}),
            'medicamentos': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Medicamentos actuales o frecuentes'}),
            'alergias': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Alergias conocidas'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Otras observaciones importantes'}),
        }

class BusquedaPacienteForm(forms.Form):
    query = forms.CharField(
        label='Buscar paciente',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre o documento...'
        })
    )


from citas.models import Clinica  # asegúrate de tener esto al inicio del archivo

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['nombres', 'apellidos', 'documento_id', 'email', 'pais', 'telefono', 'clinica_creacion']
        widgets = {
            'nombres': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}),
            'documento_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de documento'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
            'pais': forms.Select(attrs={'class': 'form-select'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono (sin código de país)'}),
            'clinica_creacion': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_documento_id(self):
        documento = self.cleaned_data.get('documento_id')
        if Paciente.objects.filter(documento_id=documento).exists():
            raise ValidationError("Ya existe un paciente con esa cédula.")
        return documento

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Paciente.objects.filter(email=email).exists():
            raise ValidationError("Ya existe un paciente con este correo.")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este correo ya está registrado como usuario.")
        return email
