from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LandingPageView,
    FAQPageView,
    DashboardDispatcherRedirectView,
    UsuarioDashboardView,
    TicketCreateView,
    TicketDetailView,
    GestorDashboardView,
    GestorAsignarTicketView,
    GestorCambiarEstadoView,
    ComentarioCreateView,
    TicketDeleteView,
    TicketBulkDeleteView,
)
from .api_views import TicketViewSet, CategoriaViewSet

app_name = 'tickets'

# Router para Django REST Framework
api_router = DefaultRouter()
api_router.register(r'tickets', TicketViewSet, basename='api_ticket')
api_router.register(r'categorias', CategoriaViewSet, basename='api_categoria')

urlpatterns = [
    # 1. Rutas Públicas (Rol: VISITANTE)
    path('', LandingPageView.as_view(), name='landing'),
    path('faq/', FAQPageView.as_view(), name='faq'),

    # 2. Despachador de roles tras autenticación
    path('dashboard/', DashboardDispatcherRedirectView.as_view(), name='dashboard_dispatcher'),

    # 3. Panel y Operaciones de Solicitante (Rol: USUARIO)
    path('portal/tickets/', UsuarioDashboardView.as_view(), name='user_dashboard'),
    path('portal/tickets/nuevo/', TicketCreateView.as_view(), name='ticket_create'),

    # 4. Detalle y Comunicación de Incidencias (Compartido según permisos)
    path('tickets/<int:pk>/', TicketDetailView.as_view(), name='ticket_detail'),
    path('tickets/<int:pk>/comentar/', ComentarioCreateView.as_view(), name='comentario_create'),

    # 5. Panel de Control de Soporte y Operaciones de Técnico (Rol: GESTOR)
    path('gestor/panel/', GestorDashboardView.as_view(), name='gestor_dashboard'),
    path('gestor/tickets/<int:pk>/asignar/', GestorAsignarTicketView.as_view(), name='gestor_asignar'),
    path('gestor/tickets/<int:pk>/cambiar-estado/', GestorCambiarEstadoView.as_view(), name='gestor_cambiar_estado'),
    path('gestor/tickets/<int:pk>/eliminar/', TicketDeleteView.as_view(), name='ticket_delete'),
    path('gestor/tickets/eliminar-lote/', TicketBulkDeleteView.as_view(), name='ticket_bulk_delete'),

    # 6. Django REST Framework API Endpoints
    path('api/', include(api_router.urls)),
]

