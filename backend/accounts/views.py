from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import CustomUser
from .forms import CustomUserCreationForm, CustomLoginForm


class CustomLoginView(LoginView):
    """
    Vista de inicio de sesión con branding institucional PoinTécnico.
    """
    form_class = CustomLoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if user.is_admin_rol:
            return reverse_lazy('admin:index')
        elif user.is_gestor:
            return reverse_lazy('tickets:gestor_dashboard')
        else:
            return reverse_lazy('tickets:user_dashboard')


class CustomLogoutView(LogoutView):
    """
    Cierre de sesión seguro con redirección a la Landing pública.
    Acepta tanto GET como POST para máxima compatibilidad.
    """
    next_page = reverse_lazy('tickets:landing')
    http_method_names = ['post', 'get', 'options']

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class RegisterView(CreateView):
    """
    Registro público de usuarios (asigna rol USUARIO por defecto).
    """
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('tickets:user_dashboard')

    def form_valid(self, form):
        user = form.save(commit=False)
        # Si el usuario no especificó rol o intentó ponerse admin, asegurar USUARIO
        if not user.rol or user.rol not in [CustomUser.Rol.USUARIO, CustomUser.Rol.VISITANTE]:
            user.rol = CustomUser.Rol.USUARIO
        user.save()
        messages.success(self.request, f"¡Bienvenido a PoinTécnico, {user.first_name or user.username}! Tu cuenta ha sido creada con éxito.")
        login(self.request, user)
        return super().form_valid(form)


class CurrentUserInfoAPIView(APIView):
    """
    Endpoint DRF para que Vite.js obtenga el perfil y rol del usuario autenticado.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'rol': user.rol,
            'rol_display': user.get_rol_display(),
            'is_gestor': user.is_gestor,
            'is_usuario': user.is_usuario,
            'is_admin': user.is_admin_rol,
            'departamento': user.departamento,
            'especialidad': user.especialidad,
        })
