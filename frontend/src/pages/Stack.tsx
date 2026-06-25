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

function Hueco({ alto = "h-64", etiqueta = "Imagen" }: { alto?: string; etiqueta?: string }) {
  return (
    <div
      className={`w-full ${alto} rounded-2xl border-2 border-dashed flex items-center justify-center`}
      style={{ borderColor: "var(--border)", background: "var(--surface)" }}
    >
      <span className="text-text-2 text-sm flex items-center gap-2">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
          <rect x="3" y="3" width="18" height="18" rx="2" /><circle cx="9" cy="9" r="2" /><path d="M21 15l-5-5L5 21" />
        </svg>
        {etiqueta}
      </span>
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
              {/* Hueco para el diagrama de arquitectura */}
              <Hueco alto="h-80" etiqueta="Diagrama de arquitectura" />
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
              {/* Hueco para captura del dashboard de flota */}
              <Hueco alto="h-80" etiqueta="Dashboard de flota (mapa en vivo)" />
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
              {/* Hueco para diagrama de CI/CD */}
              <Hueco alto="h-64" etiqueta="Flujo CI/CD" />
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
