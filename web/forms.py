# web/forms.py

from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from citas.models import Paciente

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
        fields = ['nombre', 'documento_id', 'email', 'pais', 'telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
            'documento_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de documento'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
            'pais': forms.Select(attrs={'class': 'form-select'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono (sin código de país)'}),
        }

from django import forms
from citas.models import HistoriaClinica

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
