from django.core.management.base import BaseCommand
from accounts.models import CustomUser
from tickets.models import Categoria, Ticket, Comentario


class Command(BaseCommand):
    help = 'Pobla la base de datos de PoinTécnico con datos iniciales de demostración para todos los roles (RBAC).'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Iniciando inicialización de datos para PoinTécnico..."))

        # 1. Crear Categorías
        categorias_data = [
            ("Hardware y Equipos", "Reparación, mantenimiento y reemplazo de estaciones de trabajo, laptops y periféricos."),
            ("Redes y Conectividad", "Fallas de red LAN, Wi-Fi, switches, routers o VPN institucional."),
            ("Software y Aplicaciones", "Instalación de paquetes de software, soporte a ERP, suites ofimáticas y errores de sistema operativo."),
            ("Cuentas y Accesos", "Restablecimiento de contraseñas, permisos de red y creación de cuentas de correo."),
            ("Telefonía e Impresión", "Configuración de impresoras térmicas/láser de red y telefonía IP."),
        ]

        categorias_map = {}
        for nombre, descripcion in categorias_data:
            cat, created = Categoria.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': descripcion, 'activa': True}
            )
            categorias_map[nombre] = cat
            if created:
                self.stdout.write(f"  + Categoría creada: {nombre}")

        # 2. Crear / Actualizar Usuarios por Rol (RBAC) con correos @gmail.com y @hotmail.com
        # Administrador
        admin_user, created = CustomUser.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin.pointecnico@gmail.com',
                'first_name': 'Administrador',
                'last_name': 'Principal',
                'rol': CustomUser.Rol.ADMINISTRADOR,
                'is_staff': True,
                'is_superuser': True,
                'departamento': 'Gerencia de TI'
            }
        )
        admin_user.email = 'admin.pointecnico@gmail.com'
        if created:
            admin_user.set_password('admin123')
            self.stdout.write(self.style.SUCCESS("  + Superusuario ADMIN creado (admin / admin123)"))
        admin_user.save()

        # Gestor (Técnico de soporte 1)
        gestor_user, created = CustomUser.objects.get_or_create(
            username='tecnico_carlos',
            defaults={
                'email': 'carlos.soporte@gmail.com',
                'first_name': 'Carlos',
                'last_name': 'Mendoza',
                'rol': CustomUser.Rol.GESTOR,
                'departamento': 'Mesa de Ayuda Nivel 2',
                'especialidad': 'Hardware y Redes'
            }
        )
        gestor_user.email = 'carlos.soporte@gmail.com'
        if created:
            gestor_user.set_password('gestor123')
            self.stdout.write(self.style.SUCCESS("  + Usuario GESTOR creado (tecnico_carlos / gestor123)"))
        gestor_user.save()

        # Gestor (Técnica de soporte 2)
        gestor_user2, created = CustomUser.objects.get_or_create(
            username='tecnica_laura',
            defaults={
                'email': 'laura.soporte@hotmail.com',
                'first_name': 'Laura',
                'last_name': 'Gómez',
                'rol': CustomUser.Rol.GESTOR,
                'departamento': 'Mesa de Ayuda Nivel 1',
                'especialidad': 'Software y Accesos'
            }
        )
        gestor_user2.email = 'laura.soporte@hotmail.com'
        if created:
            gestor_user2.set_password('gestor123')
            self.stdout.write(self.style.SUCCESS("  + Usuario GESTOR creado (tecnica_laura / gestor123)"))
        gestor_user2.save()

        # Usuario Solicitante (Cliente/Empleado)
        solicitante_user, created = CustomUser.objects.get_or_create(
            username='empleado_ana',
            defaults={
                'email': 'ana.valenzuela@gmail.com',
                'first_name': 'Ana',
                'last_name': 'Valenzuela',
                'rol': CustomUser.Rol.USUARIO,
                'departamento': 'Departamento de Finanzas',
                'telefono': '+58 412 1234567'
            }
        )
        solicitante_user.email = 'ana.valenzuela@gmail.com'
        if created:
            solicitante_user.set_password('usuario123')
            self.stdout.write(self.style.SUCCESS("  + Usuario USUARIO creado (empleado_ana / usuario123)"))
        solicitante_user.save()

        # Asegurar que cualquier otro usuario de prueba tenga exclusivamente @gmail.com o @hotmail.com
        for u in CustomUser.objects.all():
            if '@' in u.email:
                domain = u.email.split('@')[-1].lower()
                if domain not in ['gmail.com', 'hotmail.com']:
                    prefix = u.email.split('@')[0]
                    u.email = f"{prefix}@gmail.com"
                    u.save()

        # 3. Crear Tickets de Ejemplo
        if not Ticket.objects.exists():
            t1 = Ticket.objects.create(
                titulo="Impresora de facturación fiscal no responde",
                descripcion="La impresora conectada al puerto de red en el dpto de finanzas dejó de responder tras el apagón de ayer. Arroja código de error E-04.",
                prioridad=Ticket.Prioridad.ALTA,
                estado=Ticket.Estado.EN_PROCESO,
                usuario_creador=solicitante_user,
                tecnico_asignado=gestor_user,
                categoria=categorias_map["Telefonía e Impresión"]
            )
            Comentario.objects.create(
                ticket=t1,
                autor=solicitante_user,
                mensaje="El incidente ocurrió a las 09:00 AM al intentar emitir el balance diario.",
                es_interno=False
            )
            Comentario.objects.create(
                ticket=t1,
                autor=gestor_user,
                mensaje="Revisado ping a IP 192.168.1.150. Se detectó fusible de la fuente de poder alterado. Se procede a cambio de repuesto.",
                es_interno=True
            )

            t2 = Ticket.objects.create(
                titulo="Imposibilidad de conectar a la VPN corporativa desde casa",
                descripcion="Al ingresar credenciales en el cliente OpenVPN indica 'TLS Handshake Failed'. Requiere soporte urgente para trabajo remoto.",
                prioridad=Ticket.Prioridad.CRITICA,
                estado=Ticket.Estado.ABIERTO,
                usuario_creador=solicitante_user,
                tecnico_asignado=None,
                categoria=categorias_map["Redes y Conectividad"]
            )

            t3 = Ticket.objects.create(
                titulo="Solicitud de instalación de Excel avanzado y complementos PowerQuery",
                descripcion="Requiero actualización de licencia y complementos de análisis de datos para nueva analista.",
                prioridad=Ticket.Prioridad.MEDIA,
                estado=Ticket.Estado.RESUELTO,
                usuario_creador=solicitante_user,
                tecnico_asignado=gestor_user2,
                categoria=categorias_map["Software y Aplicaciones"]
            )
            Comentario.objects.create(
                ticket=t3,
                autor=gestor_user2,
                mensaje="Instalación completada y verificada mediante asistencia remota.",
                es_interno=False
            )

            self.stdout.write(self.style.SUCCESS("  + 3 tickets de demostración generados con comentarios."))

        self.stdout.write(self.style.SUCCESS("\n¡Datos iniciales de PoinTécnico inicializados correctamente!"))

