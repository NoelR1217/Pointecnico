from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Administración personalizada de CustomUser en Django Admin para el rol ADMINISTRADOR.
    """
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'rol_badge',
        'departamento',
        'is_staff',
        'is_active',
    )
    list_filter = ('rol', 'is_staff', 'is_active', 'departamento')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'departamento', 'especialidad')
    ordering = ('username',)

    fieldsets = (
        ('Identificación de Usuario', {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email', 'telefono')}),
        ('Control de Acceso y Perfil Operativo (RBAC)', {
            'fields': ('rol', 'departamento', 'especialidad'),
            'description': 'Asignación de privilegios entre Visitante, Usuario, Gestor y Administrador.'
        }),
        ('Permisos de Django', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'rol', 'departamento', 'password1', 'password2'),
        }),
    )

    @admin.display(description='Rol Asignado')
    def rol_badge(self, obj):
        colors = {
            CustomUser.Rol.ADMINISTRADOR: '#e63946',  # Rojo
            CustomUser.Rol.GESTOR: '#0084ff',         # Azul Eléctrico PoinTécnico
            CustomUser.Rol.USUARIO: '#2a9d8f',        # Verde
            CustomUser.Rol.VISITANTE: '#6c757d',      # Gris
        }
        color = colors.get(obj.rol, '#333')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 0.85rem;">{}</span>',
            color,
            obj.get_rol_display()
        )

