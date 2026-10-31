from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Ticket, Categoria, Comentario
from .serializers import TicketSerializer, CategoriaSerializer, ComentarioSerializer
from accounts.models import CustomUser


class IsGestorOrAdmin(permissions.BasePermission):
    """Permiso personalizado para Gestores o Administradores."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_gestor or request.user.is_admin_rol)


class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """API de Categorías públicas y activas."""
    queryset = Categoria.objects.filter(activa=True)
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.AllowAny]


class TicketViewSet(viewsets.ModelViewSet):
    """
    API REST para operaciones CRUD sobre Tickets respetando el RBAC:
    - VISITANTE (No autenticado): Lectura general de tickets activos.
    - USUARIO: Ve sus propios tickets y puede crear nuevos.
    - GESTOR/ADMIN: Ve todos los tickets, puede autoasignarse y cambiar estados.
    """
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Ticket.objects.all().select_related('categoria', 'usuario_creador', 'tecnico_asignado')
        if user.is_gestor or user.is_admin_rol:
            return Ticket.objects.all().select_related('categoria', 'usuario_creador', 'tecnico_asignado')
        return Ticket.objects.filter(usuario_creador=user).select_related('categoria', 'tecnico_asignado')

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else CustomUser.objects.filter(rol='USUARIO').first()
        serializer.save(usuario_creador=user)

    def destroy(self, request, *args, **kwargs):
        """Solo Gestores y Administradores tienen autorización para eliminar tickets."""
        if request.user.is_authenticated and not (request.user.is_gestor or request.user.is_admin_rol):
            return Response({'error': 'Solo administradores y gestores tienen privilegios para eliminar tickets.'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def asignar(self, request, pk=None):
        """Autoasignación o asignación a un técnico por parte de un Gestor."""
        ticket = self.get_object()
        tecnico_id = request.data.get('tecnico_id')
        if tecnico_id:
            try:
                tecnico = CustomUser.objects.get(id=tecnico_id, rol__in=['GESTOR', 'ADMINISTRADOR'])
            except CustomUser.DoesNotExist:
                return Response({'error': 'Técnico no encontrado o no autorizado'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            tecnico = request.user if request.user.is_authenticated else CustomUser.objects.filter(rol='GESTOR').first()

        ticket.tecnico_asignado = tecnico
        if ticket.estado == Ticket.Estado.ABIERTO:
            ticket.estado = Ticket.Estado.EN_PROCESO
        ticket.save()

        autor = request.user if request.user.is_authenticated else tecnico
        Comentario.objects.create(
            ticket=ticket,
            autor=autor,
            mensaje=f"📌 Solicitud asignada al técnico: {tecnico.username} vía API.",
            es_interno=True
        )
        return Response(TicketSerializer(ticket, context={'request': request}).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def cambiar_estado(self, request, pk=None):
        """Cambio de estado por parte de un Gestor con nota opcional."""
        ticket = self.get_object()
        nuevo_estado = request.data.get('estado')
        nota_tecnica = request.data.get('nota_tecnica', '')
        es_interno = request.data.get('es_interno', True)

        if nuevo_estado not in dict(Ticket.Estado.choices):
            return Response({'error': 'Estado no válido'}, status=status.HTTP_400_BAD_REQUEST)

        ticket.estado = nuevo_estado
        ticket.save()

        autor = request.user if request.user.is_authenticated else (ticket.tecnico_asignado or ticket.usuario_creador)
        if nota_tecnica or nuevo_estado:
            Comentario.objects.create(
                ticket=ticket,
                autor=autor,
                mensaje=f"🔄 Estado actualizado a: {ticket.get_estado_display()}.\n{nota_tecnica}".strip(),
                es_interno=es_interno
            )

        return Response(TicketSerializer(ticket, context={'request': request}).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def agregar_comentario(self, request, pk=None):
        """Agrega un comentario al ticket."""
        ticket = self.get_object()
        mensaje = request.data.get('mensaje', '').strip()
        if not mensaje:
            return Response({'error': 'El mensaje es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user if request.user.is_authenticated else ticket.usuario_creador
        es_gestor = user.is_gestor or user.is_admin_rol if hasattr(user, 'is_gestor') else False
        es_interno = bool(request.data.get('es_interno', False)) if es_gestor else False

        comentario = Comentario.objects.create(
            ticket=ticket,
            autor=user,
            mensaje=mensaje,
            es_interno=es_interno
        )
        return Response(ComentarioSerializer(comentario).data, status=status.HTTP_201_CREATED)
