from django.db import models
from django.conf import settings


class Categoria(models.Model):
    """
    Categoría para clasificar las incidencias y solicitudes de soporte técnico.
    Ej: Hardware, Redes y Conectividad, Software/Aplicaciones, Cuentas/Accesos, Telefonía.
    """
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre de la Categoría'
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    activa = models.BooleanField(
        default=True,
        verbose_name='Activa'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Registro'
    )

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Ticket(models.Model):
    """
    Modelo principal de Ticket / Incidencia de soporte en PoinTécnico.
    """

    class Prioridad(models.TextChoices):
        BAJA = 'BAJA', 'Baja'
        MEDIA = 'MEDIA', 'Media'
        ALTA = 'ALTA', 'Alta'
        CRITICA = 'CRITICA', 'Crítica'

    class Estado(models.TextChoices):
        ABIERTO = 'ABIERTO', 'Abierto'
        EN_PROCESO = 'EN_PROCESO', 'En Diagnóstico / En Proceso'
        RESUELTO = 'RESUELTO', 'Resuelto'
        CERRADO = 'CERRADO', 'Cerrado'

    titulo = models.CharField(
        max_length=200,
        verbose_name='Título de la Incidencia'
    )
    descripcion = models.TextField(
        verbose_name='Descripción Detallada'
    )
    prioridad = models.CharField(
        max_length=20,
        choices=Prioridad.choices,
        default=Prioridad.MEDIA,
        verbose_name='Prioridad'
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.ABIERTO,
        verbose_name='Estado del Ticket'
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )
    usuario_creador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tickets_creados',
        verbose_name='Usuario Creador'
    )
    tecnico_asignado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets_asignados',
        verbose_name='Técnico Asignado (Gestor)',
        limit_choices_to={'rol__in': ['GESTOR', 'ADMINISTRADOR']}
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='tickets',
        verbose_name='Categoría'
    )

    class Meta:
        verbose_name = 'Ticket de Soporte'
        verbose_name_plural = 'Tickets de Soporte'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"#{self.id:04d} - {self.titulo} [{self.get_estado_display()}]"

    @property
    def esta_asignado(self) -> bool:
        return self.tecnico_asignado is not None

    @property
    def puede_editar_estado(self) -> bool:
        return self.estado != self.Estado.CERRADO


class Comentario(models.Model):
    """
    Comentario o actualización en el hilo de seguimiento de un ticket.
    Permite notas internas exclusivas para Gestores (Técnicos) y administradores.
    """
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='comentarios',
        verbose_name='Ticket Asociado'
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comentarios_realizados',
        verbose_name='Autor'
    )
    mensaje = models.TextField(
        verbose_name='Mensaje / Nota Técnica'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha y Hora'
    )
    es_interno = models.BooleanField(
        default=False,
        verbose_name='Nota Interna (Solo Técnicos / Gestores)',
        help_text='Si está marcado, solo los Gestores y Administradores podrán visualizar este comentario.'
    )

    class Meta:
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        ordering = ['timestamp']

    def __str__(self):
        tipo = " [INTERNO]" if self.es_interno else ""
        return f"Comentario #{self.id} en #{self.ticket.id} por {self.autor.username}{tipo}"

