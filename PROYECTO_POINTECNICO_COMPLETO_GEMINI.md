# 🛠️ DOSSIER TÉCNICO COMPLETO: PROYECTO POINTÉCNICO
> **Documento para alimentar a Gemini en Google Chrome**  
> *Fecha de compilación:* Octubre 2026  
> *Sistema:* PoinTécnico - Plataforma de Gestión, Asignación y Soporte Técnico

---

## 📌 1. RESUMEN EJECUTIVO Y PROPÓSITO DEL PROYECTO
**PoinTécnico** es un sistema web integral diseñado para resolver el desorden y la falta de trazabilidad en los departamentos de soporte de tecnologías de información (TI). 

Permite centralizar el levantamiento de incidencias técnicas por parte de los empleados o clientes, automatizar el flujo de autoasignación por técnicos especializados (gestores), dar seguimiento al diagnóstico y resolución en tiempo real, resguardar notas internas confidenciales y proporcionar a los administradores herramientas de auditoría, control y depuración de tickets.

---

## ⚙️ 2. STACK TECNOLÓGICO Y ARQUITECTURA
El proyecto implementa una arquitectura desacoplada y robusta basada en microservicios contenerizados:

* **Backend:** Python 3.11+ con **Django 5.0.14** y **Django REST Framework (DRF)**.
* **Base de Datos:** SQLite 3 relacional integrada mediante el ORM de Django con integridad referencial, transacciones y cascadas.
* **Frontend SSR (Server-Side Rendering):** Django Templates con componentes dinámicos en HTML5/CSS3 moderno y Bootstrap 5.3 + Bootstrap Icons.
* **Frontend SPA (Single Page Application):** React 18 sobre **Vite.js** conectado mediante llamadas asíncronas (`fetch`) a la API REST.
* **Diseño e Identidad Visual:** Tema oscuro (*Dark Mode*) de alta legibilidad con paleta basada en rojo carmesí (`#dc2626` / `#ef4444`) como color de acento principal, acompañado de fondos oscuros profundos (`#0a0a0a` / `#121212`) y tipografía blanca y ámbar de máximo contraste.
* **Contenerización y Despliegue:** **Docker** y **Docker Compose**:
  * Servicio `backend` (Django en `http://localhost:8000`).
  * Servicio `frontend` (Vite SPA en `http://localhost:5173`).
  * Script de arranque `entrypoint.sh` con migraciones automáticas y carga de datos iniciales (`seed_data`).

---

## 🔐 3. CONTROL DE ACCESO BASADO EN ROLES (RBAC)
El sistema utiliza un modelo de usuario extendido (`CustomUser` derivado de `AbstractUser` en la app `accounts`).

| Rol | Privilegios y Capacidades | Vistas y Rutas Principales |
| :--- | :--- | :--- |
| **VISITANTE** | Usuario no autenticado. Visualización pública de la propuesta de valor y preguntas frecuentes. | Landing Page (`/`), FAQ (`/faq/`), Login/Registro. |
| **USUARIO** | Empleado solicitante. Puede crear tickets, ver únicamente sus propios casos, revisar respuestas y comentar. | Portal de Usuario (`/portal/tickets/`), Nuevo Ticket (`/portal/tickets/nuevo/`), Detalle (`/tickets/<id>/`). |
| **GESTOR** | Técnico de soporte informático. Visualiza cola de tickets entrantes sin asignar, se autoasigna incidencias, modifica estados con diagnóstico técnico, redacta notas internas y elimina tickets. | Mesa de Soporte y Asignación (`/gestor/panel/`), Autoasignación (`/gestor/tickets/<id>/asignar/`), Diagnóstico (`/gestor/tickets/<id>/cambiar-estado/`). |
| **ADMINISTRADOR** | Superusuario con privilegios globales. Acceso a métricas, panel gestor, depuración masiva y administración de la base de datos. | Django Admin (`/admin/`), Panel Gestor (`/gestor/panel/`), Eliminación masiva en lote. |

---

## 🗄️ 4. ESTRUCTURA DE BASE DE DATOS Y MODELOS

### Módulo `accounts`:
* **`CustomUser`**:
  * `rol`: Selector choices (`VISITANTE`, `USUARIO`, `GESTOR`, `ADMINISTRADOR`).
  * `telefono`, `departamento`, `especialidad`.
  * Validación de correo electrónico: Restricción obligatoria a dominios `@gmail.com` y `@hotmail.com` (en modelo y formulario).
  * Métodos booleanos: `is_gestor`, `is_usuario`, `is_admin_rol`, `is_visitante`.

### Módulo `tickets`:
* **`Categoria`**: Categorización técnica (`nombre`, `descripcion`, `activa`, `created_at`).
* **`Ticket`**:
  * `titulo`, `descripcion`.
  * `prioridad`: `BAJA`, `MEDIA`, `ALTA`, `CRITICA`.
  * `estado`: `ABIERTO`, `EN_PROCESO` (En Diagnóstico), `RESUELTO`, `CERRADO`.
  * `usuario_creador` (`ForeignKey` a `CustomUser`).
  * `tecnico_asignado` (`ForeignKey` a `CustomUser`, nullable).
  * `categoria` (`ForeignKey` a `Categoria`).
  * `fecha_creacion`, `fecha_actualizacion`.
* **`Comentario`**:
  * `ticket` (`ForeignKey` a `Ticket`), `autor` (`ForeignKey` a `CustomUser`).
  * `mensaje`: Texto del seguimiento técnico o respuesta.
  * `es_interno`: Booleano para notas confidenciales visibles únicamente entre gestores y administradores.
  * `fecha_creacion`.

---

## 🚀 5. FUNCIONALIDADES Y MEJORAS CLAVE IMPLEMENTADAS

1. **Rediseño Visual Moderno y Pulcro (Tema Rojo / Oscuro):**
   * Eliminación de fondos blancos y grises de bajo contraste.
   * Tablas y badges con textos blancos, amarillos y verdes de alta legibilidad.
   * Tarjetas métricas dinámicas en el panel de control técnico (*Total en Cola*, *Cola Sin Asignar*, *Mis Casos Asignados*, *Total Resueltos*).

2. **Barra de Eliminación en Lote (Bulk Action Bar):**
   * Incorporada para Administradores y Gestores en la mesa de soporte.
   * Al seleccionar uno o varios tickets con las casillas de verificación (checkboxes), se despliega una barra flotante roja con el conteo en tiempo real (`X ticket(s) seleccionado(s)`).
   * Botón de desmarcar todos y botón de confirmación en modal de seguridad para borrado masivo permanente.

3. **Botones de Eliminación Individual:**
   * Botón `[ 🗑️ Eliminar ]` en la columna de `ACCIONES` de cada fila del panel de gestores con modal de confirmación por ticket.
   * Botón de eliminación en la barra lateral de operaciones del detalle del ticket (`/tickets/<id>/`).
   * Botón de eliminación con confirmación en las tarjetas interactivas de la SPA React.

4. **Reglas de Seguridad y Validación de Correo:**
   * Validación estricta en el formulario de registro (`clean_email`) y en el modelo (`clean()`): solo se aceptan registros con `@gmail.com` o `@hotmail.com`.
   * Protección RBAC en vistas backend con `UserPassesTestMixin` y en la API REST con `IsGestorOrAdmin`.

5. **Limpieza de Interfaz:**
   * Retiradas las etiquetas "Frontend Vite.js" y "Simular Rol" del encabezado para una apariencia corporativa limpia.
   * Retirado el bloque redundante de roles en el formulario de login y sustituido por una tarjeta elegante de consejos y recomendaciones del sistema.

---

## 🔑 6. CREDENCIALES PRECONFIGURADAS DE PRUEBA
(Contraseña común para todas las cuentas: `admin1234`)

* **Administrador:**
  * Usuario: `admin`
  * Correo: `admin.pointecnico@gmail.com`
  * Destino: Panel Django Admin (`/admin/`) y Panel Gestor (`/gestor/panel/`)
* **Gestor Técnico 1:**
  * Usuario: `tecnico_carlos`
  * Correo: `carlos.soporte@gmail.com`
  * Destino: Mesa de Soporte y Asignación (`/gestor/panel/`)
* **Gestor Técnico 2:**
  * Usuario: `tecnica_laura`
  * Correo: `laura.soporte@hotmail.com`
  * Destino: Mesa de Soporte y Asignación (`/gestor/panel/`)
* **Usuario Solicitante:**
  * Usuario: `empleado_ana`
  * Correo: `ana.valenzuela@gmail.com`
  * Destino: Portal de Mis Tickets (`/portal/tickets/`)

---

## 📐 7. MARCO METODOLÓGICO: MODELO EN V (INGENIERÍA DE SOFTWARE)

### Rama Descendente (Fase de Verificación):
1. **Análisis de Requisitos (Requirement Gathering):** Levantamiento de necesidades por rol (Visitante, Usuario, Gestor, Administrador) y especificación de Requisitos Funcionales (RF-01 a RF-05) y No Funcionales (RNF-01 a RNF-03 de seguridad, contraste y contenerización).
2. **Análisis del Sistema (System Analysis):** Modelado del flujo de vida de incidencias (`ABIERTO` $\rightarrow$ `EN_PROCESO` $\rightarrow$ `RESUELTO` $\rightarrow$ `CERRADO`), reglas de negocio de confidencialidad en notas técnicas y validación de dominios permitidos.
3. **Diseño de Software / Arquitectura (Software Design):** Arquitectura híbrida desacoplada MVT + REST API, stack Python/Django + React/Vite, servicios Docker Compose vinculados en puertos 8000 y 5173.
4. **Diseño de Módulos (Module Design):**
   * Módulo `accounts`: Modelo `CustomUser`, métodos RBAC, despachador inteligente post-login (`DashboardDispatcherRedirectView`) y validadores de email.
   * Módulo `tickets`: Modelos relacionales `Categoria`, `Ticket`, `Comentario`, vistas `GestorDashboardView`, `TicketDeleteView`, `TicketBulkDeleteView`, serializers y ViewSets REST.

### Punto de Inflexión:
5. **Codificación (Coding):** Implementación del código bajo normas PEP 8, protección contra CSRF, inyecciones SQL y XSS, automatización de migraciones y script generador de datos semilla (`seed_data.py`).

