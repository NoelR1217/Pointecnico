from rest_framework import serializers
from .models import Ticket, Categoria, Comentario
from accounts.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'rol', 'departamento', 'especialidad']


class CategoriaSerializer(serializers.ModelSerializer):
    total_tickets = serializers.IntegerField(source='tickets.count', read_only=True)

    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion', 'activa', 'total_tickets']


class ComentarioSerializer(serializers.ModelSerializer):
    autor = UserSerializer(read_only=True)

    class Meta:
        model = Comentario
        fields = ['id', 'ticket', 'autor', 'mensaje', 'es_interno', 'timestamp']
        read_only_fields = ['id', 'autor', 'timestamp']


class TicketSerializer(serializers.ModelSerializer):
    usuario_creador = UserSerializer(read_only=True)
    tecnico_asignado = UserSerializer(read_only=True)
    tecnico_asignado_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(rol__in=['GESTOR', 'ADMINISTRADOR']),
        source='tecnico_asignado',
        write_only=True,
        required=False,
        allow_null=True
    )
    categoria_detalle = CategoriaSerializer(source='categoria', read_only=True)
    comentarios = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id',
            'titulo',
            'descripcion',
            'prioridad',
            'prioridad_display',
            'estado',
            'estado_display',
            'fecha_creacion',
            'fecha_actualizacion',
            'usuario_creador',
            'tecnico_asignado',
            'tecnico_asignado_id',
            'categoria',
            'categoria_detalle',
            'comentarios',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion', 'usuario_creador']

    def get_comentarios(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if user and (user.is_authenticated and (user.is_gestor or user.is_admin_rol)):
            comentarios = obj.comentarios.all()
        else:
            comentarios = obj.comentarios.filter(es_interno=False)
        return ComentarioSerializer(comentarios, many=True).data

