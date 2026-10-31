import React, { useState, useEffect } from 'react'

function App() {
  const [tickets, setTickets] = useState([])
  const [categorias, setCategorias] = useState([])
  const [loading, setLoading] = useState(true)
  const [filtroEstado, setFiltroEstado] = useState('TODOS')
  const [mostrarModal, setMostrarModal] = useState(false)
  const [nuevoTicket, setNuevoTicket] = useState({
    titulo: '',
    categoria: '',
    prioridad: 'MEDIA',
    descripcion: ''
  })

  // Cargar datos desde Django REST Framework (o fallback con datos iniciales)
  useEffect(() => {
    fetchTickets()
    fetchCategorias()
  }, [])

  const fetchTickets = async () => {
    try {
      const res = await fetch('/api/tickets/')
      if (res.ok) {
        const data = await res.json()
        setTickets(data.results || data)
      } else {
        cargarMockTickets()
      }
    } catch (err) {
      cargarMockTickets()
    } finally {
      setLoading(false)
    }
  }

  const fetchCategorias = async () => {
    try {
      const res = await fetch('/api/categorias/')
      if (res.ok) {
        const data = await res.json()
        setCategorias(data.results || data)
      } else {
        setCategorias([
          { id: 1, nombre: 'Hardware y Equipos' },
          { id: 2, nombre: 'Redes y Conectividad' },
          { id: 3, nombre: 'Software y Aplicaciones' },
          { id: 4, nombre: 'Telefonía e Impresión' },
        ])
      }
    } catch (err) {
      setCategorias([
        { id: 1, nombre: 'Hardware y Equipos' },
        { id: 2, nombre: 'Redes y Conectividad' },
        { id: 3, nombre: 'Software y Aplicaciones' },
        { id: 4, nombre: 'Telefonía e Impresión' },
      ])
    }
  }

  const cargarMockTickets = () => {
    setTickets([
      {
        id: 1,
        titulo: 'Impresora fiscal de contabilidad no responde en red',
        descripcion: 'La impresora arrojó código de error E-04 tras reinicio del switch principal.',
        prioridad: 'ALTA',
        estado: 'EN_PROCESO',
        categoria_detalle: { nombre: 'Telefonía e Impresión' },
        usuario_creador: { username: 'ana.finanzas', first_name: 'Ana Valenzuela' },
        tecnico_asignado: { username: 'tecnico_carlos', first_name: 'Carlos Mendoza' },
        fecha_creacion: '2026-10-30T10:00:00Z',
      },
      {
        id: 2,
        titulo: 'Falla al conectar VPN corporativa para trabajo remoto',
        descripcion: 'Error TLS Handshake Failed al validar certificado en cliente OpenVPN.',
        prioridad: 'CRITICA',
        estado: 'ABIERTO',
        categoria_detalle: { nombre: 'Redes y Conectividad' },
        usuario_creador: { username: 'mario.lopez', first_name: 'Mario López' },
        tecnico_asignado: null,
        fecha_creacion: '2026-10-30T10:25:00Z',
      },
      {
        id: 3,
        titulo: 'Instalación de paquete estadístico y PowerBI',
        descripcion: 'Se requiere actualización de paquete de análisis y licencias en equipo portátil.',
        prioridad: 'MEDIA',
        estado: 'RESUELTO',
        categoria_detalle: { nombre: 'Software y Aplicaciones' },
        usuario_creador: { username: 'sofia.mercadeo', first_name: 'Sofía Rivas' },
        tecnico_asignado: { username: 'tecnica_laura', first_name: 'Laura Gómez' },
        fecha_creacion: '2026-10-30T08:15:00Z',
      }
    ])
  }

  const handleCrearTicket = async (e) => {
    e.preventDefault()
    if (!nuevoTicket.titulo || !nuevoTicket.descripcion) return

    const categoriaSeleccionada = categorias.find(c => c.id === parseInt(nuevoTicket.categoria)) || { nombre: 'General' }
    const nuevo = {
      id: tickets.length + 1,
      titulo: nuevoTicket.titulo,
      descripcion: nuevoTicket.descripcion,
      prioridad: nuevoTicket.prioridad,
      estado: 'ABIERTO',
      categoria_detalle: categoriaSeleccionada,
      usuario_creador: { username: 'usuario_activo', first_name: 'Usuario Solicitante' },
      tecnico_asignado: null,
      fecha_creacion: new Date().toISOString(),
    }

    setTickets([nuevo, ...tickets])
    setNuevoTicket({ titulo: '', categoria: '', prioridad: 'MEDIA', descripcion: '' })
    setMostrarModal(false)

    try {
      await fetch('/api/tickets/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          titulo: nuevoTicket.titulo,
          descripcion: nuevoTicket.descripcion,
          prioridad: nuevoTicket.prioridad,
          categoria: nuevoTicket.categoria || 1
        })
      })
    } catch (error) { }
  }

  const handleAutoasignar = async (ticketId) => {
    setTickets(tickets.map(t => {
      if (t.id === ticketId) {
        return {
          ...t,
          tecnico_asignado: { username: 'carlos_mendoza', first_name: 'Carlos Mendoza' },
          estado: t.estado === 'ABIERTO' ? 'EN_PROCESO' : t.estado
        }
      }
      return t
    }))
    try {
      await fetch(`/api/tickets/${ticketId}/asignar/`, { method: 'POST' })
    } catch (err) { }
  }

  const handleCambiarEstado = async (ticketId, nuevoEstado) => {
    setTickets(tickets.map(t => {
      if (t.id === ticketId) return { ...t, estado: nuevoEstado }
      return t
    }))
    try {
      await fetch(`/api/tickets/${ticketId}/cambiar_estado/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ estado: nuevoEstado, nota_tecnica: 'Estado modificado desde el panel interactivo.' })
      })
    } catch (err) { }
  }

  const handleEliminarTicket = async (ticketId, titulo) => {
    if (!window.confirm(`¿Estás seguro de que deseas eliminar permanentemente el Ticket #${ticketId} ("${titulo}")?`)) return
    setTickets(tickets.filter(t => t.id !== ticketId))
    try {
      await fetch(`/api/tickets/${ticketId}/`, { method: 'DELETE' })
    } catch (err) { }
  }

  // Filtrado de tickets
  const ticketsFiltrados = tickets.filter(t => {
    if (filtroEstado === 'TODOS') return true
    return t.estado === filtroEstado
  })

  // Helper: label legible de estado
  const estadoLabel = (estado) => {
    if (estado === 'EN_PROCESO') return 'En Diagnóstico'
    if (estado === 'ABIERTO') return 'Abierto'
    if (estado === 'RESUELTO') return 'Resuelto'
    return 'Cerrado'
  }

  // ─────────────────────────────────────────────────────────
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: '#0a0a0a' }}>

      {/* ══════════════ NAVBAR OSCURO + ROJO ══════════════ */}
      <nav className="spa-navbar">
        <div className="container d-flex align-items-center justify-content-between">
          <div className="d-flex align-items-center gap-3">
            <img
              src="/logo.jpg"
              alt="PoinTécnico Logo"
              style={{
                height: '44px', borderRadius: '10px', background: 'white', padding: '2px',
                border: '1px solid rgba(220,38,38,0.5)',
                boxShadow: '0 0 12px rgba(220,38,38,0.3)'
              }}
            />
            <div>
              <span style={{
                fontFamily: "'Poppins', sans-serif", fontWeight: 800,
                fontSize: '1.3rem', color: '#fff', letterSpacing: '-0.03em'
              }}>
                Poin<span style={{ color: '#dc2626' }}>técnico</span>
              </span>
              <span style={{
                display: 'block', fontSize: '0.72rem',
                color: 'rgba(255,255,255,0.35)', marginTop: '-2px', fontWeight: 600
              }}>
                Gestión y Asignación de Soporte
              </span>
            </div>
          </div>

          <div className="d-flex align-items-center gap-2">
            <button
              style={{
                display: 'inline-flex', alignItems: 'center', gap: '7px',
                background: 'linear-gradient(135deg, #dc2626, #991b1b)',
                color: '#fff', border: 'none', borderRadius: '10px',
                padding: '9px 18px', fontWeight: 800, fontSize: '0.875rem',
                cursor: 'pointer', boxShadow: '0 4px 14px rgba(220,38,38,0.4)'
              }}
              onClick={() => setMostrarModal(true)}
            >
              <i className="bi bi-plus-lg"></i>
              <span>Reportar Incidencia</span>
            </button>
            <a
              href="http://localhost:8000"
              style={{
                display: 'inline-flex', alignItems: 'center', gap: '6px',
                background: 'rgba(255,255,255,0.05)', color: 'rgba(255,255,255,0.7)',
                border: '1px solid rgba(255,255,255,0.12)', borderRadius: '10px',
                padding: '9px 16px', fontWeight: 700, fontSize: '0.875rem',
                textDecoration: 'none'
              }}
            >
              <i className="bi bi-box-arrow-up-right"></i> Portal Web
            </a>
          </div>
        </div>
      </nav>

      {/* ══════════════ CONTENIDO PRINCIPAL ══════════════ */}
      <div className="container py-4" style={{ flex: 1 }}>

        {/* BANNER OSCURO CON ACENTO ROJO */}
        <div className="spa-banner mb-4">
          <div className="row align-items-center justify-content-between g-3">
            <div className="col-lg-8">
              <span style={{
                display: 'inline-flex', alignItems: 'center', gap: '7px',
                background: 'rgba(220,38,38,0.1)', border: '1px solid rgba(220,38,38,0.25)',
                color: '#f87171', padding: '4px 14px', borderRadius: '999px',
                fontSize: '0.72rem', fontWeight: 800, letterSpacing: '0.5px',
                textTransform: 'uppercase', marginBottom: '14px'
              }}>
                📍 Panel de Control de Incidencias
              </span>
              <h2 style={{
                fontFamily: "'Poppins', sans-serif", fontWeight: 900, color: '#fff',
                fontSize: '2rem', letterSpacing: '-0.04em', marginBottom: '10px'
              }}>
                Centro de Gestión y Soporte Técnico
              </h2>
              <p style={{ color: 'rgba(255,255,255,0.45)', fontSize: '1rem', lineHeight: 1.65, margin: 0 }}>
                Monitoreo en tiempo real, asignación de técnicos especializados y flujo ágil
                de diagnóstico y resolución de requerimientos.
              </p>
            </div>
            <div className="col-lg-4 text-lg-end">
              <div className="banner-stat-box d-inline-flex gap-4">
                <div>
                  <div style={{ fontSize: '0.68rem', fontWeight: 800, textTransform: 'uppercase', color: 'rgba(255,255,255,0.35)', letterSpacing: '0.5px' }}>
                    Total Tickets
                  </div>
                  <div style={{ fontFamily: "'Poppins', sans-serif", fontSize: '1.8rem', fontWeight: 900, color: '#fff', lineHeight: 1 }}>
                    {tickets.length}
                  </div>
                </div>
                <div style={{ borderLeft: '1px solid rgba(255,255,255,0.08)', paddingLeft: '20px' }}>
                  <div style={{ fontSize: '0.68rem', fontWeight: 800, textTransform: 'uppercase', color: '#fbbf24', letterSpacing: '0.5px' }}>
                    Sin Asignar
                  </div>
                  <div style={{ fontFamily: "'Poppins', sans-serif", fontSize: '1.8rem', fontWeight: 900, color: '#fcd34d', lineHeight: 1 }}>
                    {tickets.filter(t => !t.tecnico_asignado).length}
                  </div>
                </div>
                <div style={{ borderLeft: '1px solid rgba(255,255,255,0.08)', paddingLeft: '20px' }}>
                  <div style={{ fontSize: '0.68rem', fontWeight: 800, textTransform: 'uppercase', color: '#34d399', letterSpacing: '0.5px' }}>
                    Resueltos
                  </div>
                  <div style={{ fontFamily: "'Poppins', sans-serif", fontSize: '1.8rem', fontWeight: 900, color: '#6ee7b7', lineHeight: 1 }}>
                    {tickets.filter(t => t.estado === 'RESUELTO').length}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* FILTROS SEGMENTADOS */}
        <div className="d-flex flex-wrap align-items-center justify-content-between gap-3 mb-4">
          <div className="filter-segmented">
            {[
              { id: 'TODOS', label: 'Todos los Tickets' },
              { id: 'ABIERTO', label: 'Abiertos' },
              { id: 'EN_PROCESO', label: 'En Diagnóstico' },
              { id: 'RESUELTO', label: 'Resueltos' },
              { id: 'CERRADO', label: 'Cerrados' }
            ].map(item => (
              <button
                key={item.id}
                type="button"
                className={`filter-segmented-btn ${filtroEstado === item.id ? 'active' : ''}`}
                onClick={() => setFiltroEstado(item.id)}
              >
                {item.label}
              </button>
            ))}
          </div>
          <div style={{ fontSize: '0.82rem', color: 'rgba(255,255,255,0.35)', fontWeight: 700 }}>
            Mostrando <span style={{ color: '#fff' }}>{ticketsFiltrados.length}</span> ticket(s)
          </div>
        </div>

        {/* GRID DE TICKETS */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: '80px 0', color: 'rgba(255,255,255,0.25)' }}>
            <div className="spinner-border" role="status" style={{ color: '#dc2626' }}></div>
            <p style={{ marginTop: '16px', fontSize: '0.875rem' }}>Cargando tickets...</p>
          </div>
        ) : (
          <div className="row g-4">
            {ticketsFiltrados.map(ticket => (
              <div key={ticket.id} className="col-lg-6">
                <div className="ticket-card-modern p-4 h-100" style={{ display: 'flex', flexDirection: 'column' }}>

                  {/* Header: ID + fecha + badges */}
                  <div className="d-flex justify-content-between align-items-center mb-3">
                    <div className="d-flex align-items-center gap-2">
                      <span className="ticket-id-pill">#{String(ticket.id).padStart(4, '0')}</span>
                      <span style={{ fontSize: '0.74rem', color: 'rgba(255,255,255,0.3)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <i className="bi bi-calendar3"></i>
                        {new Date(ticket.fecha_creacion).toLocaleDateString('es-ES', { day: '2-digit', month: 'short' })}
                      </span>
                    </div>
                    <div className="d-flex align-items-center gap-1">
                      <span className={`pill-priority pill-priority-${ticket.prioridad.toLowerCase()}`}>
                        {ticket.prioridad}
                      </span>
                      <span className={`pill-status pill-status-${ticket.estado.toLowerCase()}`}>
                        <span style={{
                          display: 'inline-block', width: '6px', height: '6px', borderRadius: '50%',
                          background:
                            ticket.estado === 'ABIERTO' ? '#60a5fa' :
                              ticket.estado === 'EN_PROCESO' ? '#fbbf24' :
                                ticket.estado === 'RESUELTO' ? '#34d399' : '#6b7280'
                        }}></span>
                        {estadoLabel(ticket.estado)}
                      </span>
                    </div>
                  </div>

                  {/* Título y descripción */}
                  <h5 style={{ fontWeight: 800, color: '#e5e7eb', fontSize: '1.02rem', lineHeight: 1.35, marginBottom: '10px' }}>
                    {ticket.titulo}
                  </h5>
                  <p style={{ color: 'rgba(255,255,255,0.45)', fontSize: '0.87rem', lineHeight: 1.6, marginBottom: '16px', flexGrow: 1 }}>
                    {ticket.descripcion}
                  </p>

                  {/* Metadata row */}
                  <div className="card-meta-row mb-3">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <i className="bi bi-tag-fill" style={{ color: '#dc2626' }}></i>
                      <span>{ticket.categoria_detalle?.nombre || 'General'}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <i className="bi bi-person-circle" style={{ color: 'rgba(255,255,255,0.35)' }}></i>
                      <span>{ticket.usuario_creador?.first_name || ticket.usuario_creador?.username}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <i className="bi bi-tools" style={{ color: 'rgba(255,255,255,0.35)' }}></i>
                      {ticket.tecnico_asignado ? (
                        <span style={{ color: '#93c5fd', fontWeight: 700 }}>
                          {ticket.tecnico_asignado?.first_name || ticket.tecnico_asignado?.username}
                        </span>
                      ) : (
                        <span style={{ color: '#fbbf24', fontWeight: 700 }}>Sin Asignar</span>
                      )}
                    </div>
                  </div>

                  {/* Botones de acción */}
                  <div style={{
                    display: 'flex', flexWrap: 'wrap', gap: '8px',
                    paddingTop: '12px', borderTop: '1px solid rgba(255,255,255,0.06)'
                  }}>
                    {!ticket.tecnico_asignado && (
                      <button
                        className="btn-action-modern btn-action-assign"
                        onClick={() => handleAutoasignar(ticket.id)}
                      >
                        <i className="bi bi-person-check-fill"></i>
                        <span>Asignarme</span>
                      </button>
                    )}
                    {ticket.estado !== 'RESUELTO' && ticket.estado !== 'CERRADO' && (
                      <button
                        className="btn-action-modern btn-action-resolve"
                        onClick={() => handleCambiarEstado(ticket.id, 'RESUELTO')}
                      >
                        <i className="bi bi-check2-circle"></i>
                        <span>Marcar Resuelto</span>
                      </button>
                    )}
                    {ticket.estado === 'ABIERTO' && (
                      <button
                        className="btn-action-modern btn-action-diagnose"
                        onClick={() => handleCambiarEstado(ticket.id, 'EN_PROCESO')}
                      >
                        <i className="bi bi-gear-fill"></i>
                        <span>Iniciar Diagnóstico</span>
                      </button>
                    )}
                    <button
                      className="btn-action-modern btn-action-delete-spa"
                      onClick={() => handleEliminarTicket(ticket.id, ticket.titulo)}
                      title="Eliminar ticket"
                    >
                      <i className="bi bi-trash3-fill"></i>
                      <span>Eliminar</span>
                    </button>
                  </div>
                </div>
              </div>
            ))}

            {ticketsFiltrados.length === 0 && (
              <div style={{ padding: '80px 0', textAlign: 'center', color: 'rgba(255,255,255,0.2)' }}>
                <i className="bi bi-ticket-perforated" style={{ fontSize: '3rem', display: 'block', marginBottom: '16px' }}></i>
                <h5 style={{ color: 'rgba(255,255,255,0.5)', fontWeight: 700, marginBottom: '8px' }}>
                  No hay tickets en esta categoría
                </h5>
                <p style={{ fontSize: '0.875rem' }}>Prueba otro filtro o reporta una nueva incidencia.</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* ══════════════ MODAL OSCURO ══════════════ */}
      {mostrarModal && (
        <div
          className="modal show d-block modal-dark"
          style={{ backgroundColor: 'rgba(0,0,0,0.78)', backdropFilter: 'blur(6px)' }}
        >
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content">
              <div className="modal-header">
                <div>
                  <h5 style={{
                    fontFamily: "'Poppins', sans-serif", fontWeight: 800,
                    color: '#fff', marginBottom: '2px'
                  }}>
                    Reportar Incidencia Técnica
                  </h5>
                  <p style={{ color: 'rgba(255,255,255,0.4)', fontSize: '0.82rem', margin: 0 }}>
                    Describe el problema para asignarlo al equipo especializado
                  </p>
                </div>
                <button
                  type="button"
                  style={{
                    background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)',
                    color: 'rgba(255,255,255,0.5)', borderRadius: '8px',
                    padding: '6px 10px', cursor: 'pointer', fontSize: '1rem', lineHeight: 1
                  }}
                  onClick={() => setMostrarModal(false)}
                >✕</button>
              </div>
              <form onSubmit={handleCrearTicket}>
                <div className="modal-body p-4">
                  <div className="mb-3">
                    <label className="form-label">Título Resumido *</label>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="Ej: Impresora contable no responde en red"
                      value={nuevoTicket.titulo}
                      onChange={e => setNuevoTicket({ ...nuevoTicket, titulo: e.target.value })}
                      required
                    />
                  </div>
                  <div className="row g-3 mb-3">
                    <div className="col-6">
                      <label className="form-label">Categoría *</label>
                      <select
                        className="form-select"
                        value={nuevoTicket.categoria}
                        onChange={e => setNuevoTicket({ ...nuevoTicket, categoria: e.target.value })}
                        required
                      >
                        <option value="">Seleccione...</option>
                        {categorias.map(cat => (
                          <option key={cat.id} value={cat.id}>{cat.nombre}</option>
                        ))}
                      </select>
                    </div>
                    <div className="col-6">
                      <label className="form-label">Nivel de Prioridad *</label>
                      <select
                        className="form-select"
                        value={nuevoTicket.prioridad}
                        onChange={e => setNuevoTicket({ ...nuevoTicket, prioridad: e.target.value })}
                      >
                        <option value="BAJA">Baja</option>
                        <option value="MEDIA">Media</option>
                        <option value="ALTA">Alta</option>
                        <option value="CRITICA">Crítica</option>
                      </select>
                    </div>
                  </div>
                  <div>
                    <label className="form-label">Descripción Detallada *</label>
                    <textarea
                      className="form-control"
                      rows="4"
                      placeholder="Indica síntomas del fallo, equipo afectado y mensajes de error..."
                      value={nuevoTicket.descripcion}
                      onChange={e => setNuevoTicket({ ...nuevoTicket, descripcion: e.target.value })}
                      required
                    ></textarea>
                  </div>
                </div>
                <div className="modal-footer">
                  <button
                    type="button"
                    style={{
                      background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)',
                      color: 'rgba(255,255,255,0.6)', padding: '9px 20px', borderRadius: '10px',
                      fontWeight: 700, cursor: 'pointer'
                    }}
                    onClick={() => setMostrarModal(false)}
                  >Cancelar</button>
                  <button
                    type="submit"
                    style={{
                      background: 'linear-gradient(135deg, #dc2626, #991b1b)',
                      color: '#fff', border: 'none', padding: '9px 24px', borderRadius: '10px',
                      fontWeight: 800, cursor: 'pointer', boxShadow: '0 4px 14px rgba(220,38,38,0.4)'
                    }}
                  >
                    <i className="bi bi-send-fill" style={{ marginRight: '6px' }}></i>
                    Registrar Incidencia
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* ══════════════ FOOTER ══════════════ */}
      <footer className="spa-footer">
        PoinTécnico &bull; Sistema de Gestión y Asignación de Soporte para Técnicos &copy; 2026
      </footer>
    </div>
  )
}

export default App
