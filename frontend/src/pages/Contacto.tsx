import { useEffect, useState } from "react";
import FadeIn from "@/components/ui/FadeIn";
import OficinasCercanas from "@/components/ui/OficinasCercanas";
import { useHeroOscuro } from "@/hooks/useHeroOscuro";
import { getSedes, enviarContacto } from "@/lib/api";
import { EMPRESA } from "@/lib/empresa";
import type { Sede } from "@/types";

interface FormData {
  nombre: string;
  email: string;
  telefono: string;
  mensaje: string;
}

export default function Contacto() {
  useHeroOscuro();
  const [sedes, setSedes] = useState<Sede[]>([]);
  const [form, setForm] = useState<FormData>({ nombre: "", email: "", telefono: "", mensaje: "" });
  const [enviado, setEnviado] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => { getSedes().then(setSedes).catch(() => {}); }, []);

  function actualizar(campo: keyof FormData, valor: string) {
    setForm((f) => ({ ...f, [campo]: valor }));
  }

  async function enviar() {
    setError(null);
    if (!form.nombre.trim() || !form.email.trim() || !form.mensaje.trim()) {
      setError("Por favor, completa nombre, email y mensaje.");
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
      setError("El email no parece válido.");
      return;
    }
    setEnviando(true);
    try {
      await enviarContacto({
        nombre: form.nombre.trim(),
        email: form.email.trim(),
        telefono: form.telefono.trim(),
        mensaje: form.mensaje.trim(),
      });
      setEnviado(true);
    } catch {
      setError("No se pudo enviar el mensaje. Inténtalo de nuevo en unos minutos.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div>
      {/* Cabecera */}
      <div className="border-b border-border" style={{ background: "linear-gradient(160deg, #0f2433, #0891b2)" }}>
        <div className="max-w-container mx-auto px-6 pt-28 pb-10">
          <h1 className="text-white text-3xl md:text-4xl font-medium">Contacto</h1>
          <p className="text-white/80 mt-2 max-w-xl">¿Tienes dudas sobre tu reserva o nuestros vehículos? Escríbenos.</p>
        </div>
      </div>

      <section className="max-w-container mx-auto px-6 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_360px] gap-10 items-start">
          {/* Formulario */}
          <FadeIn>
            <div className="bg-bg-2 border border-border rounded-2xl p-6 md:p-8">
              {enviado ? (
                <div className="text-center py-10">
                  <span className="w-14 h-14 rounded-full bg-accent-dim text-accent flex items-center justify-center mx-auto mb-4">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M20 6L9 17l-5-5" /></svg>
                  </span>
                  <p className="font-display font-medium text-lg">¡Mensaje enviado!</p>
                  <p className="text-text-2 mt-1 text-sm">Te responderemos lo antes posible.</p>
                </div>
              ) : (
                <>
                  <h2 className="text-xl font-medium mb-5">Envíanos un mensaje</h2>
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div className="flex flex-col gap-1">
                        <label className="text-[13px] font-medium">Nombre *</label>
                        <input
                          value={form.nombre}
                          onChange={(e) => actualizar("nombre", e.target.value)}
                          className="h-10 px-3 border border-border-2 rounded-lg text-sm bg-bg-2"
                          placeholder="Tu nombre"
                        />
                      </div>
                      <div className="flex flex-col gap-1">
                        <label className="text-[13px] font-medium">Teléfono</label>
                        <input
                          value={form.telefono}
                          onChange={(e) => actualizar("telefono", e.target.value)}
                          className="h-10 px-3 border border-border-2 rounded-lg text-sm bg-bg-2"
                          placeholder="Opcional"
                        />
                      </div>
                    </div>
                    <div className="flex flex-col gap-1">
                      <label className="text-[13px] font-medium">Email *</label>
                      <input
                        value={form.email}
                        onChange={(e) => actualizar("email", e.target.value)}
                        className="h-10 px-3 border border-border-2 rounded-lg text-sm bg-bg-2"
                        placeholder="tucorreo@ejemplo.com"
                      />
                    </div>
                    <div className="flex flex-col gap-1">
                      <label className="text-[13px] font-medium">Mensaje *</label>
                      <textarea
                        value={form.mensaje}
                        onChange={(e) => actualizar("mensaje", e.target.value)}
                        rows={5}
                        className="px-3 py-2 border border-border-2 rounded-lg text-sm bg-bg-2 resize-none"
                        placeholder="Cuéntanos en qué podemos ayudarte"
                      />
                    </div>

                    {error && <p className="text-red-600 text-[13px]">{error}</p>}

                    <button
                      onClick={enviar}
                      disabled={enviando}
                      className="h-11 px-6 bg-accent text-white rounded-lg font-medium hover:opacity-90 transition disabled:opacity-60 disabled:cursor-not-allowed"
                    >
                      {enviando ? "Enviando…" : "Enviar mensaje"}
                    </button>
                    <p className="text-[12px] text-text-2">
                      Al enviar aceptas nuestra{" "}
                      <a href="/privacidad" className="text-accent hover:underline">Política de Privacidad</a>.
                    </p>
                  </div>
                </>
              )}
            </div>
          </FadeIn>

          {/* Datos de la empresa */}
          <FadeIn delay={120}>
            <div className="bg-bg-2 border border-border rounded-2xl p-6 space-y-4">
              <p className="font-display font-medium text-lg">{EMPRESA.nombreComercial}</p>
              <div className="space-y-3 text-sm">
                <a href={`tel:${EMPRESA.telefono.replace(/ /g, "")}`} className="flex items-center gap-3 text-text-2 hover:text-accent transition">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="text-accent shrink-0">
                    <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72c.13.96.36 1.9.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0122 16.92z" />
                  </svg>
                  {EMPRESA.telefono}
                </a>
                <a href={`mailto:${EMPRESA.email}`} className="flex items-center gap-3 text-text-2 hover:text-accent transition">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="text-accent shrink-0">
                    <rect x="2" y="4" width="20" height="16" rx="2" /><path d="M22 7l-10 5L2 7" />
                  </svg>
                  {EMPRESA.email}
                </a>
                <div className="flex items-start gap-3 text-text-2">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="text-accent shrink-0 mt-0.5">
                    <path d="M21 10c0 7-9 12-9 12s-9-5-9-12a9 9 0 0118 0z" /><circle cx="12" cy="10" r="3" />
                  </svg>
                  {EMPRESA.domicilio}
                </div>
              </div>
            </div>
          </FadeIn>
        </div>

        {/* Bloque de sedes */}
        <div className="mt-16">
          <FadeIn>
            <OficinasCercanas sedes={sedes} />
          </FadeIn>
        </div>
      </section>
    </div>
  );
}
