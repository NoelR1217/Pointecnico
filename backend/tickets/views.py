from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Count, Q
from django.core.exceptions import PermissionDenied

from .models import Ticket, Categoria, Comentario
from .forms import TicketCreateForm, GestorTicketUpdateForm, ComentarioForm
from accounts.models import CustomUser


# ============================================================================
# 1. VISTAS PÚBLICAS (ACCESO VISITANTE)
# ============================================================================

class LandingPageView(TemplateView):
    """
    Vista pública principal para VISITANTES y usuarios del sistema.
    Presenta la propuesta de valor de PoinTécnico.
    """
    template_name = 'tickets/landing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_categorias'] = Categoria.objects.filter(activa=True).count()
        context['tickets_resueltos'] = Ticket.objects.filter(estado=Ticket.Estado.RESUELTO).count()
        return context


class FAQPageView(TemplateView):
    """
    Preguntas Frecuentes de acceso público para VISITANTES.
    """
    template_name = 'tickets/faq.html'


# ============================================================================
# 2. DISPATCHER DE REDIRECCIÓN INTELIGENTE SEGÚN ROL
# ============================================================================

class DashboardDispatcherRedirectView(LoginRequiredMixin, View):
    """
    Enrutador central post-login:
    Dirige a cada usuario a su vista correspondiente según su RBAC:
    - ADMINISTRADOR -> Django Admin / Métricas globales
    - GESTOR        -> Panel de Control Técnico (tickets entrantes y asignados)
    - USUARIO       -> Portal de Tickets Propios e incidencias
    - VISITANTE     -> Landing informativa
    """
    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_admin_rol:
            return redirect('/admin/')
        elif user.is_gestor:
            return redirect('tickets:gestor_dashboard')
        elif user.is_usuario:
            return redirect('tickets:user_dashboard')
        else:
            return redirect('tickets:landing')


# ============================================================================
# 3. VISTAS PARA ROL USUARIO (CLIENTE / EMPLEADO SOLICITANTE)
# ============================================================================

class UsuarioDashboardView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Panel del Solicitante (Rol: USUARIO).
    Permite visualizar el historial, avance y estado de sus propios tickets.
    """
    model = Ticket
    template_name = 'tickets/user_dashboard.html'
    context_object_name = 'tickets'
    paginate_by = 10

    def test_func(self):
        # Permiso: USUARIO o ADMINISTRADOR
        return self.request.user.rol in [CustomUser.Rol.USUARIO, CustomUser.Rol.ADMINISTRADOR]

    def handle_no_permission(self):
        if self.request.user.is_gestor:
            return redirect('tickets:gestor_dashboard')
        raise PermissionDenied("No tienes permisos para acceder al portal de usuario solicitante.")

    def get_queryset(self):
        qs = Ticket.objects.filter(usuario_creador=self.request.user).select_related('categoria', 'tecnico_asignado')
        # Filtro opcional por estado
        estado = self.request.GET.get('estado')
        if estado:
            qs = qs.filter(estado=estado)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_tickets = Ticket.objects.filter(usuario_creador=self.request.user)
        context['total_tickets'] = user_tickets.count()
        context['abiertos'] = user_tickets.filter(estado=Ticket.Estado.ABIERTO).count()
        context['en_proceso'] = user_tickets.filter(estado=Ticket.Estado.EN_PROCESO).count()
        context['resueltos'] = user_tickets.filter(estado__in=[Ticket.Estado.RESUELTO, Ticket.Estado.CERRADO]).count()
        context['estado_filtro'] = self.request.GET.get('estado', '')
        return context


class TicketCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Permite a los usuarios con rol USUARIO reportar nuevas incidencias.
    """
    model = Ticket
    form_class = TicketCreateForm
    template_name = 'tickets/ticket_create.html'

    def test_func(self):
        # Solo USUARIOS y ADMINISTRADORES pueden crear tickets desde esta vista
        return self.request.user.rol in [CustomUser.Rol.USUARIO, CustomUser.Rol.ADMINISTRADOR]

    def form_valid(self, form):
        form.instance.usuario_creador = self.request.user
        form.instance.estado = Ticket.Estado.ABIERTO
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"¡Ticket #{self.object.id:04d} creado exitosamente! Un técnico de soporte lo revisará en breve."
        )
        return response

    def get_success_url(self):
        return reverse('tickets:ticket_detail', kwargs={'pk': self.object.pk})


# ============================================================================
# 4. VISTA DETALLE DEL TICKET (ACCESIBLE POR SOLICITANTE, GESTOR Y ADMIN)
# ============================================================================

class TicketDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Visualización detallada de un ticket con su cronología de comentarios.
    Aplica filtros de seguridad: Los comentarios con es_interno=True son visibles
    ÚNICAMENTE para Gestores y Administradores.
    """
    model = Ticket
    template_name = 'tickets/ticket_detail.html'
    context_object_name = 'ticket'

    def test_func(self):
        user = self.request.user
        ticket = self.get_object()
        # Pueden ver el ticket:
        # 1. El usuario creador
        # 2. El técnico asignado
        # 3. Cualquier GESTOR o ADMINISTRADOR
        return (
            ticket.usuario_creador == user or
            ticket.tecnico_asignado == user or
            user.is_gestor or
            user.is_admin_rol
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ticket = self.object
        user = self.request.user
        es_gestor_o_admin = user.is_gestor or user.is_admin_rol

        # Filtrar comentarios internos para usuarios convencionales
        if es_gestor_o_admin:
            comentarios = ticket.comentarios.all().select_related('autor')
        else:
            comentarios = ticket.comentarios.filter(es_interno=False).select_related('autor')

        context['comentarios'] = comentarios
        context['form_comentario'] = ComentarioForm(es_gestor=es_gestor_o_admin)
        context['es_gestor_o_admin'] = es_gestor_o_admin
        if es_gestor_o_admin:
            context['form_gestor'] = GestorTicketUpdateForm(instance=ticket)
        return context


# ============================================================================
# 5. VISTAS PARA ROL GESTOR (TÉCNICO DE SOPORTE)
# ============================================================================

class GestorDashboardView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Panel de Control Técnico especializado (Rol: GESTOR).
    Permite:
    - Visualizar la cola de tickets entrantes sin asignar.
    - Gestionar tickets asignados a mi persona.
    - Filtrar por estado (Abierto, En Diagnóstico / Proceso, Resuelto, Cerrado).
    - Monitorear carga de soporte técnico.
    """
    model = Ticket
    template_name = 'tickets/gestor_dashboard.html'
    context_object_name = 'tickets'
    paginate_by = 15

    def test_func(self):
        # Acceso exclusivo para GESTOR o ADMINISTRADOR
        return self.request.user.rol in [CustomUser.Rol.GESTOR, CustomUser.Rol.ADMINISTRADOR]

    def handle_no_permission(self):
        if self.request.user.is_usuario:
            return redirect('tickets:user_dashboard')
        raise PermissionDenied("Solo el personal técnico (Gestor) tiene acceso al panel de control de soporte.")

    def get_queryset(self):
        qs = Ticket.objects.all().select_related('categoria', 'usuario_creador', 'tecnico_asignado')
        
        # Filtro de asignación
        vista = self.request.GET.get('vista', 'todos')
        if vista == 'mis_tickets':
            qs = qs.filter(tecnico_asignado=self.request.user)
        elif vista == 'sin_asignar':
            qs = qs.filter(tecnico_asignado__isnull=True)

        # Filtro de estado
        estado = self.request.GET.get('estado')
        if estado:
            qs = qs.filter(estado=estado)

        # Filtro de prioridad
        prioridad = self.request.GET.get('prioridad')
        if prioridad:
            qs = qs.filter(prioridad=prioridad)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Métricas de soporte para el Gestor
        context['total_pendientes'] = Ticket.objects.filter(estado__in=[Ticket.Estado.ABIERTO, Ticket.Estado.EN_PROCESO]).count()
        context['sin_asignar_count'] = Ticket.objects.filter(tecnico_asignado__isnull=True).exclude(estado=Ticket.Estado.CERRADO).count()
        context['mis_asignados_count'] = Ticket.objects.filter(tecnico_asignado=user).exclude(estado=Ticket.Estado.CERRADO).count()
        context['resueltos_count'] = Ticket.objects.filter(estado=Ticket.Estado.RESUELTO).count()
        
        context['vista_actual'] = self.request.GET.get('vista', 'todos')
        context['estado_filtro'] = self.request.GET.get('estado', '')
        context['prioridad_filtro'] = self.request.GET.get('prioridad', '')
        context['estados_disponibles'] = Ticket.Estado.choices
        context['prioridades_disponibles'] = Ticket.Prioridad.choices
        return context


class GestorAsignarTicketView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Acción rápida para que un Gestor se autoasigne una solicitud o la asigne a otro técnico.
    """
    def test_func(self):
        return self.request.user.rol in [CustomUser.Rol.GESTOR, CustomUser.Rol.ADMINISTRADOR]

    def post(self, request, pk, *args, **kwargs):
        ticket = get_object_or_404(Ticket, pk=pk)
        tecnico_id = request.POST.get('tecnico_id')

        if tecnico_id:
            tecnico = get_object_or_404(CustomUser, pk=tecnico_id)
            ticket.tecnico_asignado = tecnico
            nombre_tecnico = tecnico.get_full_name() or tecnico.username
        else:
            # Autoasignarse a sí mismo
            ticket.tecnico_asignado = request.user
            nombre_tecnico = "ti mismo"

        # Al asignarse, si el estado estaba en ABIERTO pasa a EN_PROCESO automáticamente
        if ticket.estado == Ticket.Estado.ABIERTO:
            ticket.estado = Ticket.Estado.EN_PROCESO

        ticket.save()

        # Registro de comentario del sistema
        Comentario.objects.create(
            ticket=ticket,
            autor=request.user,
            mensaje=f"📌 Solicitud asignada al técnico: {ticket.tecnico_asignado.username}.",
            es_interno=True
        )

        messages.success(request, f"Ticket #{ticket.id:04d} asignado a {nombre_tecnico}.")
        return redirect('tickets:ticket_detail', pk=ticket.pk)


class GestorCambiarEstadoView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Permite al Gestor cambiar el estado del ticket (Abierto, En Diagnóstico / Proceso, Resuelto, Cerrado).
    """
    def test_func(self):
        return self.request.user.rol in [CustomUser.Rol.GESTOR, CustomUser.Rol.ADMINISTRADOR]

    def post(self, request, pk, *args, **kwargs):
        ticket = get_object_or_404(Ticket, pk=pk)
        nuevo_estado = request.POST.get('estado')
        nota_tecnica = request.POST.get('nota_tecnica', '').strip()
        es_interno = request.POST.get('es_interno') == 'on'

        if nuevo_estado in dict(Ticket.Estado.choices):
            estado_anterior = ticket.get_estado_display()
            ticket.estado = nuevo_estado
            ticket.save()

            mensaje_log = f"🔄 Estado cambiado de [{estado_anterior}] a [{ticket.get_estado_display()}]."
            if nota_tecnica:
                mensaje_log += f"\nObservación técnica: {nota_tecnica}"

            Comentario.objects.create(
                ticket=ticket,
                autor=request.user,
                mensaje=mensaje_log,
                es_interno=es_interno
            )

            messages.success(request, f"Estado del Ticket #{ticket.id:04d} actualizado a '{ticket.get_estado_display()}'.")
        else:
            messages.error(request, "Estado inválido seleccionado.")

        return redirect('tickets:ticket_detail', pk=ticket.pk)


class TicketDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Permite a Administradores y Gestores eliminar un ticket permanentemente del sistema.
    """
    def test_func(self):
        return self.request.user.rol in [CustomUser.Rol.GESTOR, CustomUser.Rol.ADMINISTRADOR]

    def post(self, request, pk, *args, **kwargs):
        ticket = get_object_or_404(Ticket, pk=pk)
        ticket_id = ticket.id
        titulo = ticket.titulo
        ticket.delete()
        messages.success(request, f"🗑️ El Ticket #{ticket_id:04d} ('{titulo}') ha sido eliminado exitosamente.")
        
        # Redirigir a la vista de origen o al panel gestor
        next_url = request.POST.get('next')
        if next_url and f'/tickets/{pk}/' not in next_url:
            return redirect(next_url)
        return redirect('tickets:gestor_dashboard')


class TicketBulkDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Barra de acciones: Permite a Administradores y Gestores eliminar múltiples tickets en lote.
    """
    def test_func(self):
        return self.request.user.rol in [CustomUser.Rol.GESTOR, CustomUser.Rol.ADMINISTRADOR]

    def post(self, request, *args, **kwargs):
        ticket_ids = request.POST.getlist('ticket_ids')
        if ticket_ids:
            tickets_a_eliminar = Ticket.objects.filter(id__in=ticket_ids)
            cantidad = tickets_a_eliminar.count()
            tickets_a_eliminar.delete()
            messages.success(request, f"🗑️ Se han eliminado {cantidad} ticket(s) exitosamente del sistema.")
        else:
            messages.warning(request, "No seleccionaste ningún ticket para eliminar.")
        return redirect('tickets:gestor_dashboard')


# ============================================================================
# 6. REGISTRO DE COMENTARIOS Y NOTAS INTERNAS
# ============================================================================

class ComentarioCreateView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Agrega comentarios e intervenciones a un ticket.
    Soporta notas técnicas internas para gestores.
    """
    def test_func(self):
        ticket = get_object_or_404(Ticket, pk=self.kwargs['pk'])
        user = self.request.user
        return (
            ticket.usuario_creador == user or
            ticket.tecnico_asignado == user or
            user.is_gestor or
            user.is_admin_rol
        )

    def post(self, request, pk, *args, **kwargs):
        ticket = get_object_or_404(Ticket, pk=pk)
        mensaje = request.POST.get('mensaje', '').strip()
        es_gestor_o_admin = request.user.is_gestor or request.user.is_admin_rol
        es_interno = (request.POST.get('es_interno') == 'on') if es_gestor_o_admin else False

        if mensaje:
            Comentario.objects.create(
                ticket=ticket,
                autor=request.user,
                mensaje=mensaje,
                es_interno=es_interno
            )
            messages.success(request, "Comentario añadido correctamente.")
        else:
            messages.warning(request, "El mensaje no puede estar vacío.")

        return redirect('tickets:ticket_detail', pk=ticket.pk)

