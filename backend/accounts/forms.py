from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """
    Formulario para el registro de nuevos usuarios en el sistema.
    Exige obligatoriamente correos con dominio @gmail.com o @hotmail.com.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ejemplo@gmail.com o ejemplo@hotmail.com'
        })
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'rol', 'telefono', 'departamento')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            elif not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise forms.ValidationError("El correo electrónico es obligatorio.")

        if '@' not in email:
            raise forms.ValidationError("Por favor, introduce un correo electrónico válido.")

        domain = email.split('@')[-1].strip().lower()
        allowed_domains = ['gmail.com', 'hotmail.com']

        if domain not in allowed_domains:
            raise forms.ValidationError(
                "Solo se permiten registros con correos de dominio @gmail.com o @hotmail.com."
            )

        # Validar que el correo no esté ya registrado
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Este correo electrónico ya se encuentra registrado.")

        return email


class CustomUserChangeForm(UserChangeForm):
    """
    Formulario para la modificación de usuarios desde el Admin.
    Usa fields = '__all__' para permitir a UserAdmin gobernar los fieldsets sin errores de password.
    """
    class Meta:
        model = CustomUser
        fields = '__all__'


class CustomLoginForm(AuthenticationForm):
    """
    Formulario estilizado de inicio de sesión con soporte nativo de AuthenticationForm.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nombre de usuario',
            'autofocus': True
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
