from django.contrib import admin
from django.utils.html import format_html
from .models import Categoria, Ticket, Comentario


class ComentarioInline(admin.TabularInline):
    """
    Permite visualizar y registrar comentarios directamente en la vista del ticket.
    """
    model = Comentario
    extra = 1
    fields = ('autor', 'mensaje', 'es_interno', 'timestamp')
    readonly_fields = ('timestamp',)
    autocomplete_fields = ('autor',)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """
    Administración de Categorías de soporte técnico.
    """
    list_display = ('nombre', 'descripcion_corta', 'total_tickets', 'activa', 'created_at')
    list_filter = ('activa', 'created_at')
    search_fields = ('nombre', 'descripcion')
    ordering = ('nombre',)

    @admin.display(description='Descripción')
    def descripcion_corta(self, obj):
        return obj.descripcion[:60] + '...' if len(obj.descripcion) > 60 else obj.descripcion

    @admin.display(description='Total Tickets')
    def total_tickets(self, obj):
        count = obj.tickets.count()
        return format_html('<strong>{}</strong>', count)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """
    Administración avanzada de Tickets para el Administrador de PoinTécnico.
    """
    list_display = (
        'codigo_ticket',
        'titulo',
        'categoria',
        'prioridad_badge',
        'estado_badge',
        'usuario_creador',
        'tecnico_asignado',
        'fecha_creacion',
    )
    list_filter = (
        'estado',
        'prioridad',
        'categoria',
        'fecha_creacion',
        'tecnico_asignado',
    )
    search_fields = (
        'titulo',
        'descripcion',
        'usuario_creador__username',
        'usuario_creador__email',
        'tecnico_asignado__username',
    )
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    autocomplete_fields = ('usuario_creador', 'tecnico_asignado', 'categoria')
    inlines = [ComentarioInline]
    date_hierarchy = 'fecha_creacion'
    actions = ['marcar_como_en_proceso', 'marcar_como_resueltos', 'asignarme_a_mi']

    fieldsets = (
        ('Datos Principales de la Incidencia', {
            'fields': ('titulo', 'categoria', 'descripcion')
        }),
        ('Clasificación y Estado', {
            'fields': (('prioridad', 'estado'),)
        }),
        ('Actores del Proceso', {
            'fields': (('usuario_creador', 'tecnico_asignado'),)
        }),
        ('Tiempos de Registro', {
            'classes': ('collapse',),
            'fields': (('fecha_creacion', 'fecha_actualizacion'),)
        }),
    )

    @admin.display(description='ID')
    def codigo_ticket(self, obj):
        return f"#{obj.id:04d}"

    @admin.display(description='Prioridad')
    def prioridad_badge(self, obj):
        colors = {
            Ticket.Prioridad.BAJA: '#2a9d8f',       # Verde
            Ticket.Prioridad.MEDIA: '#0084ff',      # Azul Eléctrico
            Ticket.Prioridad.ALTA: '#f4a261',       # Naranja
            Ticket.Prioridad.CRITICA: '#e63946',    # Rojo Alerta
        }
        color = colors.get(obj.prioridad, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 4px; font-weight: 600; font-size: 0.8rem;">{}</span>',
            color,
            obj.get_prioridad_display()
        )

    @admin.display(description='Estado')
    def estado_badge(self, obj):
        colors = {
            Ticket.Estado.ABIERTO: '#0b224e',       # Azul Marino PoinTécnico
            Ticket.Estado.EN_PROCESO: '#0084ff',    # Azul Eléctrico
            Ticket.Estado.RESUELTO: '#2a9d8f',      # Verde Éxito
            Ticket.Estado.CERRADO: '#6c757d',       # Gris Neutral
        }
        color = colors.get(obj.estado, '#333')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 4px; font-weight: 600; font-size: 0.8rem;">{}</span>',
            color,
            obj.get_estado_display()
        )

    @admin.action(description='Cambiar estado a: En Diagnóstico / Proceso')
    def marcar_como_en_proceso(self, request, queryset):
        filas = queryset.update(estado=Ticket.Estado.EN_PROCESO)
        self.message_user(request, f"{filas} tickets actualizados a 'En Diagnóstico / Proceso'.")

    @admin.action(description='Cambiar estado a: Resuelto')
    def marcar_como_resueltos(self, request, queryset):
        filas = queryset.update(estado=Ticket.Estado.RESUELTO)
        self.message_user(request, f"{filas} tickets actualizados a 'Resuelto'.")

    @admin.action(description='Asignar tickets seleccionados a mi usuario')
    def asignarme_a_mi(self, request, queryset):
        filas = queryset.update(tecnico_asignado=request.user)
        self.message_user(request, f"{filas} tickets asignados al técnico {request.user.username}.")


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    """
    Administración de comentarios e intervenciones técnicas.
    """
    list_display = ('id', 'ticket', 'autor', 'mensaje_corto', 'es_interno_badge', 'timestamp')
    list_filter = ('es_interno', 'timestamp', 'autor')
    search_fields = ('mensaje', 'ticket__titulo', 'autor__username')
    ordering = ('-timestamp',)

    @admin.display(description='Mensaje')
    def mensaje_corto(self, obj):
        return obj.mensaje[:70] + '...' if len(obj.mensaje) > 70 else obj.mensaje

    @admin.display(description='Tipo')
    def es_interno_badge(self, obj):
        if obj.es_interno:
            return format_html(
                '<span style="background-color: #ffd166; color: #1f2937; padding: 2px 6px; border-radius: 3px; font-weight: bold; font-size: 0.75rem;">🔒 NOTA TÉCNICA INTERNA</span>'
            )
        return format_html(
            '<span style="background-color: #e9ecef; color: #495057; padding: 2px 6px; border-radius: 3px; font-size: 0.75rem;">Público</span>'
        )

