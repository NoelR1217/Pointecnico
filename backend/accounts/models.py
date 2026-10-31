from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Modelo de Usuario personalizado con Control de Acceso Basado en Roles (RBAC).
    
    Roles soportados:
    - VISITANTE: Usuario con acceso público (Landing y FAQ).
    - USUARIO: Cliente/Empleado solicitante (crear y seguir tickets).
    - GESTOR: Técnico de soporte (atender, asignarse y actualizar tickets, notas internas).
    - ADMINISTRADOR: Superusuario con acceso total a Django Admin y métricas.
    """

    class Rol(models.TextChoices):
        VISITANTE = 'VISITANTE', 'Visitante (Público / Solo Lectura)'
        USUARIO = 'USUARIO', 'Usuario (Cliente / Empleado Solicitante)'
        GESTOR = 'GESTOR', 'Gestor (Técnico de Soporte)'
        ADMINISTRADOR = 'ADMINISTRADOR', 'Administrador del Sistema'

    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.USUARIO,
        verbose_name='Rol en el Sistema',
        help_text='Define los permisos, vistas y capacidades operativas del usuario.'
    )
    telefono = models.CharField(
        max_length=25,
        blank=True,
        null=True,
        verbose_name='Teléfono de Contacto'
    )
    departamento = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Departamento / Área / Empresa',
        help_text='Área o sucursal donde labora el usuario'
    )
    especialidad = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='Especialidad Técnica',
        help_text='Aplica a Gestores/Técnicos (p. ej. Redes, Hardware, Software).'
    )

    class Meta:
        verbose_name = 'Usuario del Sistema'
        verbose_name_plural = 'Usuarios del Sistema'
        ordering = ['username']

    def __str__(self):
        full_name = self.get_full_name()
        display = full_name if full_name else self.username
        return f"{display} [{self.get_rol_display()}]"

    # Helpers de verificación de rol
    @property
    def is_visitante(self) -> bool:
        return self.rol == self.Rol.VISITANTE

    @property
    def is_usuario(self) -> bool:
        return self.rol == self.Rol.USUARIO

    @property
    def is_gestor(self) -> bool:
        return self.rol == self.Rol.GESTOR

    @property
    def is_admin_rol(self) -> bool:
        return self.rol == self.Rol.ADMINISTRADOR or self.is_superuser

    def clean(self):
        super().clean()
        if self.email:
            email_lower = self.email.strip().lower()
            allowed = ['gmail.com', 'hotmail.com']
            if '@' in email_lower:
                domain = email_lower.split('@')[-1]
                if domain not in allowed:
                    from django.core.exceptions import ValidationError
                    raise ValidationError({'email': 'El correo debe ser obligatoriamente de dominio @gmail.com o @hotmail.com.'})

    def save(self, *args, **kwargs):
        """
        Sincroniza permisos de staff / superuser si el rol asignado es ADMINISTRADOR,
        o autoasigna rol ADMINISTRADOR si se creó como superuser.
        """
        if self.is_superuser and self.rol != self.Rol.ADMINISTRADOR:
            self.rol = self.Rol.ADMINISTRADOR
        elif self.rol == self.Rol.ADMINISTRADOR:
            self.is_staff = True
            self.is_superuser = True
        super().save(*args, **kwargs)
