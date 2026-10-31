from django import forms
from .models import Ticket, Comentario, Categoria
from accounts.models import CustomUser


class TicketCreateForm(forms.ModelForm):
    """
    Formulario utilizado por los usuarios con rol USUARIO para crear tickets.
    """
    class Meta:
        model = Ticket
        fields = ['titulo', 'categoria', 'prioridad', 'descripcion']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Impresora láser del dpto. contable no responde'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'prioridad': forms.Select(attrs={
                'class': 'form-select'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describa detalladamente el problema, síntomas, mensajes de error y equipo afectado...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].queryset = Categoria.objects.filter(activa=True)


class GestorTicketUpdateForm(forms.ModelForm):
    """
    Formulario utilizado por los GESTORES (Técnicos) para cambiar estado y asignación.
    """
    class Meta:
        model = Ticket
        fields = ['estado', 'tecnico_asignado', 'prioridad']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'tecnico_asignado': forms.Select(attrs={'class': 'form-select'}),
            'prioridad': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar usuarios que sean GESTORES o ADMINS para asignación
        self.fields['tecnico_asignado'].queryset = CustomUser.objects.filter(
            rol__in=[CustomUser.Rol.GESTOR, CustomUser.Rol.ADMINISTRADOR]
        )


class ComentarioForm(forms.ModelForm):
    """
    Formulario para agregar comentarios al hilo de un ticket.
    """
    class Meta:
        model = Comentario
        fields = ['mensaje', 'es_interno']
        widgets = {
            'mensaje': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Escribe una respuesta o actualización...'
            }),
            'es_interno': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, es_gestor=False, **kwargs):
        super().__init__(*args, **kwargs)
        # Si no es gestor ni admin, no puede marcar notas como internas
        if not es_gestor:
            self.fields['es_interno'].widget = forms.HiddenInput()
            self.fields['es_interno'].initial = False

