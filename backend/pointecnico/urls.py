"""
URL Configuration principal para PoinTécnico.
Sistema de Gestión y Asignación de Soporte Técnico para Técnicos.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Personalización visual del Django Admin con Branding PoinTécnico
admin.site.site_header = "PoinTécnico | Administración Central"
admin.site.site_title = "PoinTécnico Portal Administrativo"
admin.site.index_title = "Gestión y Asignación de Soporte Técnico"

urlpatterns = [
    # Panel de Administración de Django (Rol: ADMINISTRADOR)
    path('admin/', admin.site.urls),

    # Autenticación y Cuentas de Usuario (RBAC)
    path('accounts/', include('accounts.urls', namespace='accounts')),

    # Módulo de Tickets, Landing, FAQ y Paneles por Rol
    path('', include('tickets.urls', namespace='tickets')),
]

# Servir archivos estáticos y media en entorno de desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

