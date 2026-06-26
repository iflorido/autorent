import FadeIn from "@/components/ui/FadeIn";
import { useHeroOscuro } from "@/hooks/useHeroOscuro";

/* Contenedores del despliegue (microservicios sobre un único dominio). */
const CONTENEDORES = [
  {
    nombre: "autorent-backend",
    rol: "API REST + Panel de gestión",
    desc: "Django 5 + Django REST Framework servido por Gunicorn. Expone la API pública del catálogo y reservas, y el panel de administración completo. Es el dueño del esquema de datos.",
    puerto: ":8072",
    icon: "M4 5h16v14H4z M4 9h16",
  },
  {
    nombre: "autorent-api",
    rol: "Ingesta GPS de alta frecuencia",
    desc: "Microservicio FastAPI asíncrono dedicado a recibir la telemetría de los dispositivos Teltonika. Inserta posiciones con asyncpg y delega el procesamiento, aislando la carga GPS de la web.",
    puerto: ":8073",
    icon: "M12 2a10 10 0 100 20 10 10 0 000-20z M2 12h20",
  },
  {
    nombre: "autorent-frontend",
    rol: "Aplicación web (SPA)",
    desc: "React 18 + TypeScript compilado con Vite y estilado con Tailwind. Catálogo, asistente de reserva multipaso, tarifas y subida de documentación. Servido como single-page application.",
    puerto: ":8074",
    icon: "M3 3h18v14H3z M8 21h8 M12 17v4",
  },
  {
    nombre: "autorent-celery",
    rol: "Procesamiento en segundo plano",
    desc: "Worker de Celery que ejecuta tareas pesadas sin bloquear la web: generación de contratos PDF, análisis de telemetría (driver score, eventos de conducción) y envío de correos.",
    puerto: "worker",
    icon: "M12 8v4l3 3 M12 2a10 10 0 100 20 10 10 0 000-20z",
  },
  {
    nombre: "autorent-celery-beat",
    rol: "Tareas programadas",
    desc: "Planificador que dispara tareas periódicas (recordatorios, comprobaciones de mantenimiento por fecha) en los momentos configurados.",
    puerto: "scheduler",
    icon: "M12 6v6l4 2 M12 2a10 10 0 100 20 10 10 0 000-20z",
  },
  {
    nombre: "autorent-redis",
    rol: "Broker de mensajes y caché",
    desc: "Cola que conecta los servicios: el API y el backend encolan tareas que el worker consume. Es la columna vertebral de la comunicación asíncrona.",
    puerto: ":6379",
    icon: "M4 7c0-2 4-3 8-3s8 1 8 3-4 3-8 3-8-1-8-3z M4 7v10c0 2 4 3 8 3s8-1 8-3V7",
  },
];

/* Capas del stack tecnológico. */
const CAPAS = [
  {
    titulo: "Backend",
    items: ["Python 3.12", "Django 5.1", "Django REST Framework", "FastAPI", "Celery", "Gunicorn / Uvicorn"],
  },
  {
    titulo: "Frontend",
    items: ["React 18", "TypeScript", "Vite", "Tailwind CSS", "React Router", "Axios"],
  },
  {
    titulo: "Datos e infraestructura",
    items: ["PostgreSQL", "Redis", "Docker", "GitHub Actions (CI/CD)", "Nginx / Plesk", "asyncpg"],
  },
  {
    titulo: "Telemetría y mapas",
    items: ["Teltonika FMC130 / FMC003", "Protocolo Codec 8", "Leaflet", "OpenStreetMap / CARTO", "reportlab (PDF)"],
  },
];

/* Módulos funcionales desarrollados. */
const MODULOS = [
  {
    titulo: "Motor de reservas",
    desc: "Asistente multipaso con conductores adicionales, validación de requisitos por categoría, extras con precio congelado y recálculo de precio siempre en servidor dentro de una transacción atómica.",
  },
  {
    titulo: "Verificación documental",
    desc: "Subida de documentación mediante enlace mágico sin necesidad de registro, almacenamiento seguro fuera del alcance público, y flujo de revisión con aprobación o rechazo y aviso automático al cliente.",
  },
  {
    titulo: "Contratos automáticos",
    desc: "Generación del contrato en PDF al confirmar la reserva, con todas las condiciones legales, firma del contrato y huella de integridad. Revisión previa antes del envío al cliente.",
  },
  {
    titulo: "Seguimiento GPS de flota",
    desc: "Dispositivos Teltonika enlazados por IMEI que reportan posición, velocidad, odómetro y combustible. Dashboard con mapa en tiempo real integrado en el panel de gestión.",
  },
  {
    titulo: "Driver score y alertas",
    desc: "Detección de frenazos, acelerones, curvas bruscas y excesos de velocidad mediante acelerómetro, con puntuación de conducción por vehículo y por reserva, y alertas en tiempo real.",
  },
  {
    titulo: "Mantenimiento predictivo",
    desc: "Reglas de mantenimiento por kilometraje real (odómetro) y por fecha (ITV) que generan avisos automáticos cuando un vehículo alcanza el umbral programado.",
  },
];

/* Diagrama de arquitectura: navegador -> proxy -> servicios -> datos. */
function DiagramaArquitectura() {
  return (
    <div className="w-full rounded-2xl border p-4" style={{ borderColor: "var(--border)", background: "var(--surface)" }}>
      <svg viewBox="0 0 460 360" className="w-full h-auto" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Diagrama de arquitectura">
        <defs>
          <marker id="ar" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
            <path d="M0 0L6 3L0 6Z" fill="var(--accent)" />
          </marker>
        </defs>

        {/* Cliente */}
        <g>
          <rect x="170" y="14" width="120" height="40" rx="9" fill="var(--accent)" />
          <text x="230" y="39" textAnchor="middle" fontSize="13" fontWeight="600" fill="#fff">Navegador / Cliente</text>
        </g>
        <line x1="230" y1="54" x2="230" y2="78" stroke="var(--accent)" strokeWidth="2" markerEnd="url(#ar)" />

        {/* Proxy */}
        <g>
          <rect x="150" y="80" width="160" height="40" rx="9" fill="var(--accent-dim)" stroke="var(--accent)" strokeWidth="1.2" />
          <text x="230" y="99" textAnchor="middle" fontSize="12.5" fontWeight="600" fill="var(--text)">Nginx / Plesk</text>
          <text x="230" y="113" textAnchor="middle" fontSize="9.5" fill="var(--text-2)">proxy inverso · un dominio</text>
        </g>

        {/* Tres servicios desde el proxy */}
        {/* Conexiones */}
        <line x1="180" y1="120" x2="90" y2="158" stroke="var(--accent)" strokeWidth="1.6" markerEnd="url(#ar)" />
        <line x1="230" y1="120" x2="230" y2="158" stroke="var(--accent)" strokeWidth="1.6" markerEnd="url(#ar)" />
        <line x1="280" y1="120" x2="370" y2="158" stroke="var(--accent)" strokeWidth="1.6" markerEnd="url(#ar)" />

        {/* frontend */}
        <g>
          <rect x="22" y="160" width="130" height="46" rx="9" fill="var(--bg)" stroke="var(--border)" />
          <text x="87" y="180" textAnchor="middle" fontSize="11" fontWeight="600" fill="var(--text)">frontend</text>
          <text x="87" y="195" textAnchor="middle" fontSize="9" fill="var(--text-2)">React · /</text>
        </g>
        {/* backend */}
        <g>
          <rect x="165" y="160" width="130" height="46" rx="9" fill="var(--bg)" stroke="var(--border)" />
          <text x="230" y="180" textAnchor="middle" fontSize="11" fontWeight="600" fill="var(--text)">backend</text>
          <text x="230" y="195" textAnchor="middle" fontSize="9" fill="var(--text-2)">Django · /api /admin</text>
        </g>
        {/* api */}
        <g>
          <rect x="308" y="160" width="130" height="46" rx="9" fill="var(--bg)" stroke="var(--border)" />
          <text x="373" y="180" textAnchor="middle" fontSize="11" fontWeight="600" fill="var(--text)">api</text>
          <text x="373" y="195" textAnchor="middle" fontSize="9" fill="var(--text-2)">FastAPI · /gps</text>
        </g>

        {/* Worker + beat (segunda fila, ligados por redis) */}
        <line x1="230" y1="206" x2="230" y2="230" stroke="var(--accent)" strokeWidth="1.6" markerEnd="url(#ar)" />
        <line x1="373" y1="206" x2="270" y2="230" stroke="var(--accent)" strokeWidth="1.6" markerEnd="url(#ar)" />
        <g>
          <rect x="160" y="232" width="150" height="40" rx="9" fill="var(--accent-dim)" stroke="var(--accent)" strokeWidth="1.1" />
          <text x="235" y="251" textAnchor="middle" fontSize="11" fontWeight="600" fill="var(--text)">redis</text>
          <text x="235" y="264" textAnchor="middle" fontSize="9" fill="var(--text-2)">broker de mensajes</text>
        </g>
        <line x1="160" y1="252" x2="92" y2="288" stroke="var(--accent)" strokeWidth="1.6" markerEnd="url(#ar)" />
        <line x1="235" y1="272" x2="235" y2="288" stroke="var(--accent)" strokeWidth="1.6" markerEnd="url(#ar)" />
        <g>
          <rect x="22" y="290" width="135" height="42" rx="9" fill="var(--bg)" stroke="var(--border)" />
          <text x="89" y="310" textAnchor="middle" fontSize="10.5" fontWeight="600" fill="var(--text)">celery</text>
          <text x="89" y="323" textAnchor="middle" fontSize="8.5" fill="var(--text-2)">worker · tareas</text>
        </g>
        <g>
          <rect x="168" y="290" width="135" height="42" rx="9" fill="var(--bg)" stroke="var(--border)" />
          <text x="235" y="310" textAnchor="middle" fontSize="10.5" fontWeight="600" fill="var(--text)">celery-beat</text>
          <text x="235" y="323" textAnchor="middle" fontSize="8.5" fill="var(--text-2)">programador</text>
        </g>

        {/* PostgreSQL a la derecha, conectada a backend y api */}
        <g>
          <rect x="318" y="244" width="120" height="46" rx="9" fill="var(--accent)" />
          <text x="378" y="264" textAnchor="middle" fontSize="11" fontWeight="600" fill="#fff">PostgreSQL</text>
          <text x="378" y="278" textAnchor="middle" fontSize="8.5" fill="rgba(255,255,255,0.8)">datos compartidos</text>
        </g>
        <line x1="295" y1="183" x2="318" y2="250" stroke="var(--border-2)" strokeWidth="1.4" strokeDasharray="3 3" />
        <line x1="400" y1="206" x2="385" y2="244" stroke="var(--border-2)" strokeWidth="1.4" strokeDasharray="3 3" />
      </svg>
    </div>
  );
}

/* Diagrama de CI/CD (ancho): permite scroll horizontal dentro del marco. */
function DiagramaCICD() {
  return (
    <div
      className="w-full rounded-2xl border overflow-x-auto"
      style={{ borderColor: "var(--border)", background: "var(--surface)" }}
    >
      <svg viewBox="0 0 900 200" width="900" className="h-56 max-w-none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Flujo de integración y despliegue continuo">
        <defs>
          <marker id="ci" markerWidth="9" markerHeight="9" refX="6" refY="3" orient="auto">
            <path d="M0 0L6 3L0 6Z" fill="var(--accent)" />
          </marker>
        </defs>

        {[
          { x: 20, t1: "git push", t2: "Cambio en el código", ic: "M6 3v12a3 3 0 003 3 M18 9a3 3 0 100-6 3 3 0 000 6z M6 6a3 3 0 100-3" },
          { x: 195, t1: "GitHub Actions", t2: "Construye la imagen", ic: "M4 6h16v12H4z M4 10h16" },
          { x: 370, t1: "Registro GHCR", t2: "Publica la imagen", ic: "M12 2l9 4.9V17L12 22 3 17V7z" },
          { x: 545, t1: "Plesk", t2: "Recoge y recarga", ic: "M3 13l9-9 9 9 M5 11v9h14v-9" },
          { x: 720, t1: "entrypoint", t2: "Migra y arranca", ic: "M5 3l14 9-14 9z" },
        ].map((p, i) => (
          <g key={i}>
            <rect x={p.x} y="60" width="150" height="80" rx="12" fill="var(--bg)" stroke="var(--border)" />
            <circle cx={p.x + 30} cy="90" r="15" fill="var(--accent-dim)" />
            <svg x={p.x + 21} y="81" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="1.7">
              <path d={p.ic} />
            </svg>
            <text x={p.x + 16} y="120" fontSize="12" fontWeight="600" fill="var(--text)">{p.t1}</text>
            <text x={p.x + 16} y="134" fontSize="9.5" fill="var(--text-2)">{p.t2}</text>
            {i < 4 && (
              <line x1={p.x + 150} y1="100" x2={p.x + 175} y2="100" stroke="var(--accent)" strokeWidth="2" markerEnd="url(#ci)" />
            )}
          </g>
        ))}
        <text x="20" y="34" fontSize="13" fontWeight="600" fill="var(--text)">Despliegue continuo — de un push a producción sin intervención manual</text>
      </svg>
    </div>
  );
}

export default function Stack() {
  useHeroOscuro();

  return (
    <div className="bg-bg text-text">
      {/* Hero */}
      <section className="relative pt-32 pb-20 px-6 overflow-hidden" style={{ background: "linear-gradient(160deg, #0c1c2c 0%, #103040 60%, #0891b2 160%)" }}>
        <div className="max-w-container mx-auto">
          <FadeIn>
            <p className="text-accent-dim font-medium tracking-widest text-xs uppercase mb-4" style={{ color: "rgba(255,255,255,0.6)" }}>
              Arquitectura & Tecnología
            </p>
            <h1 className="font-display text-4xl md:text-5xl font-semibold text-white max-w-3xl leading-tight">
              Una plataforma de alquiler construida como software profesional
            </h1>
            <p className="text-white/70 text-lg mt-6 max-w-2xl">
              AutoRent no es una web de reservas: es un sistema completo de gestión de flota con
              microservicios, seguimiento GPS en tiempo real y automatización de extremo a extremo,
              desplegado de forma continua sobre un único dominio.
            </p>
          </FadeIn>
        </div>
      </section>

      {/* Visión general / diagrama */}
      <section className="py-20 px-6">
        <div className="max-w-container mx-auto">
          <FadeIn>
            <div className="grid md:grid-cols-2 gap-12 items-center">
              <div>
                <h2 className="font-display text-3xl font-semibold mb-5">Arquitectura de microservicios</h2>
                <p className="text-text-2 leading-relaxed mb-4">
                  En lugar de una aplicación monolítica, AutoRent reparte el trabajo entre servicios
                  independientes que colaboran. Cada uno corre en su propio contenedor Docker, se
                  despliega de forma automática y cumple una responsabilidad concreta.
                </p>
                <p className="text-text-2 leading-relaxed">
                  Esta separación permite que la web de reservas siga respondiendo con fluidez aunque
                  lleguen miles de tramas GPS por minuto, porque cada carga vive en su propio servicio
                  y no compiten entre sí.
                </p>
              </div>
              {/* Diagrama de arquitectura */}
              <DiagramaArquitectura />
            </div>
          </FadeIn>
        </div>
      </section>

      {/* Contenedores */}
      <section className="py-20 px-6" style={{ background: "var(--bg-2)" }}>
        <div className="max-w-container mx-auto">
          <FadeIn>
            <h2 className="font-display text-3xl font-semibold mb-3 text-center">Seis servicios, un solo dominio</h2>
            <p className="text-text-2 text-center max-w-2xl mx-auto mb-14">
              Todos los servicios conviven tras un proxy inverso que enruta cada petición al contenedor
              correcto según su ruta, presentando una experiencia unificada bajo el mismo dominio.
            </p>
          </FadeIn>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {CONTENEDORES.map((c, i) => (
              <FadeIn key={c.nombre} delay={i * 60}>
                <div className="h-full rounded-2xl border p-6 transition hover:shadow-soft" style={{ borderColor: "var(--border)", background: "var(--bg)" }}>
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-11 h-11 rounded-xl flex items-center justify-center" style={{ background: "var(--accent-dim)" }}>
                      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="1.6">
                        <path d={c.icon} />
                      </svg>
                    </div>
                    <code className="text-xs px-2 py-1 rounded-md text-text-2" style={{ background: "var(--surface-2)" }}>{c.puerto}</code>
                  </div>
                  <h3 className="font-mono text-sm font-semibold text-accent mb-1">{c.nombre}</h3>
                  <p className="font-medium text-[15px] mb-2">{c.rol}</p>
                  <p className="text-text-2 text-sm leading-relaxed">{c.desc}</p>
                </div>
              </FadeIn>
            ))}
          </div>
        </div>
      </section>

      {/* Flujo de la telemetría GPS (diferenciador) */}
      <section className="py-20 px-6">
        <div className="max-w-container mx-auto">
          <FadeIn>
            <div className="grid md:grid-cols-2 gap-12 items-center">
              {/* Captura del dashboard de flota (sube la imagen a public/images/) */}
              <img
                src="/images/dashboard-flota.jpg"
                alt="Dashboard de flota con mapa en tiempo real"
                className="w-full h-80 object-cover rounded-2xl border shadow-soft"
                style={{ borderColor: "var(--border)" }}
              />
              <div>
                <p className="text-accent font-medium tracking-widest text-xs uppercase mb-3">El diferenciador</p>
                <h2 className="font-display text-3xl font-semibold mb-5">Telemetría en tiempo real de la flota</h2>
                <p className="text-text-2 leading-relaxed mb-4">
                  Los vehículos llevan dispositivos Teltonika que reportan su estado constantemente.
                  La trama llega al microservicio FastAPI, que la guarda al instante y encola su
                  análisis para no frenar la ingesta.
                </p>
                <p className="text-text-2 leading-relaxed">
                  El worker procesa cada posición: calcula la puntuación de conducción, detecta
                  excesos de velocidad según el límite de cada categoría de vehículo, y comprueba si
                  toca mantenimiento según el kilometraje real. Todo se refleja en el mapa del panel
                  de gestión, sin intervención manual.
                </p>
              </div>
            </div>
          </FadeIn>
        </div>
      </section>

      {/* Módulos desarrollados */}
      <section className="py-20 px-6" style={{ background: "var(--bg-2)" }}>
        <div className="max-w-container mx-auto">
          <FadeIn>
            <h2 className="font-display text-3xl font-semibold mb-14 text-center">Qué hace la plataforma</h2>
          </FadeIn>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {MODULOS.map((m, i) => (
              <FadeIn key={m.titulo} delay={i * 60}>
                <div className="h-full rounded-2xl p-6" style={{ background: "var(--bg)", border: "1px solid var(--border)" }}>
                  <div className="w-8 h-8 rounded-lg flex items-center justify-center mb-4 text-accent font-semibold" style={{ background: "var(--accent-dim)" }}>
                    {i + 1}
                  </div>
                  <h3 className="font-medium text-[15px] mb-2">{m.titulo}</h3>
                  <p className="text-text-2 text-sm leading-relaxed">{m.desc}</p>
                </div>
              </FadeIn>
            ))}
          </div>
        </div>
      </section>

      {/* Stack tecnológico por capas */}
      <section className="py-20 px-6">
        <div className="max-w-container mx-auto">
          <FadeIn>
            <h2 className="font-display text-3xl font-semibold mb-3 text-center">El stack completo</h2>
            <p className="text-text-2 text-center max-w-2xl mx-auto mb-14">
              Tecnologías modernas y probadas, elegidas por su rendimiento, fiabilidad y mantenibilidad.
            </p>
          </FadeIn>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {CAPAS.map((capa, i) => (
              <FadeIn key={capa.titulo} delay={i * 60}>
                <div className="rounded-2xl border p-6 h-full" style={{ borderColor: "var(--border)" }}>
                  <h3 className="font-display text-lg font-semibold mb-4 text-accent">{capa.titulo}</h3>
                  <ul className="space-y-2">
                    {capa.items.map((it) => (
                      <li key={it} className="text-text-2 text-sm flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full" style={{ background: "var(--accent)" }} />
                        {it}
                      </li>
                    ))}
                  </ul>
                </div>
              </FadeIn>
            ))}
          </div>
        </div>
      </section>

      {/* CI/CD */}
      <section className="py-20 px-6" style={{ background: "var(--bg-2)" }}>
        <div className="max-w-container mx-auto">
          <FadeIn>
            <div className="grid md:grid-cols-2 gap-12 items-center">
              <div>
                <h2 className="font-display text-3xl font-semibold mb-5">Despliegue continuo automatizado</h2>
                <p className="text-text-2 leading-relaxed mb-4">
                  Cada cambio en el código dispara un flujo de integración continua que construye las
                  imágenes de los contenedores y las publica automáticamente. El servidor recoge la
                  nueva versión y recarga los servicios sin intervención manual.
                </p>
                <p className="text-text-2 leading-relaxed">
                  Las migraciones de base de datos se aplican solas al arrancar, garantizando que el
                  esquema esté siempre sincronizado con el código en producción.
                </p>
              </div>
              {/* Diagrama de CI/CD (ancho, con scroll dentro del marco) */}
              <DiagramaCICD />
            </div>
          </FadeIn>
        </div>
      </section>

      {/* Cierre */}
      <section className="py-24 px-6 text-center">
        <div className="max-w-container mx-auto">
          <FadeIn>
            <h2 className="font-display text-3xl md:text-4xl font-semibold mb-5 max-w-2xl mx-auto">
              Software a medida, pensado para crecer
            </h2>
            <p className="text-text-2 text-lg max-w-2xl mx-auto">
              AutoRent demuestra cómo una plataforma de alquiler puede integrar reservas, verificación
              documental, contratos y seguimiento de flota en un sistema único, robusto y escalable.
            </p>
          </FadeIn>
        </div>
      </section>
    </div>
  );
}
