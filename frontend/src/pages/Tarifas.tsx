import BuscadorSeccion from "@/components/ui/BuscadorSeccion";
import FadeIn from "@/components/ui/FadeIn";
import { useHeroOscuro } from "@/hooks/useHeroOscuro";

const INCLUYE = [
  { t: "Seguro de Protección Parcial (CDW)", d: "Responsabilidad civil obligatoria frente a terceros y daños por colisión (sujeto a franquicia)." },
  { t: "Asistencia en Carretera 24/7", d: "Cobertura total de grúa y asistencia en todo el territorio nacional." },
  { t: "Flota 100% garantizada", d: "Mantenimiento preventivo, higienización profesional e ITV al día antes de cada entrega." },
  { t: "Impuestos incluidos", d: "Todos los precios muestran el 21% de IVA desglosado. Sin tasas extrañas." },
  { t: "Gestión ágil", d: "Check-in digital para pasar el menor tiempo posible en la oficina." },
];

const MODALIDADES = [
  {
    nombre: "Essential",
    claim: "La opción más económica. Ideal si eres conductor experimentado y buscas el mejor precio base.",
    destacada: false,
    puntos: ["Kilometraje: límite diario", "Franquicia estándar (400€–800€ según grupo)", "Fianza: retención estándar", "Modificaciones hasta 48h antes"],
  },
  {
    nombre: "Comfort",
    claim: "El equilibrio perfecto. Viaja protegido sin duplicar el precio del alquiler.",
    destacada: true,
    puntos: ["Kilometraje ampliado", "Franquicia reducida al 50%", "Segundo conductor GRATIS", "Modificaciones flexibles hasta 24h antes"],
  },
  {
    nombre: "Premium (Super-Relax)",
    claim: "Cero estrés. Recoge las llaves, disfruta y devuélvelo sin mirar los arañazos con lupa.",
    destacada: false,
    puntos: ["Kilometraje ILIMITADO", "Franquicia 0€ (todo riesgo SCDW)", "Fianza cero o simbólica (100€)", "Asistencia VIP: llaves y repostaje", "Cancelación gratuita hasta 12h antes"],
  },
];

const EXTRAS = [
  "Conductor adicional — para turnaros al volante en viajes largos.",
  "Sillitas y elevadores (ISOFIX) — higienizadas tras cada uso.",
  "Pack kilometraje ilimitado — si cruzas la península.",
  "Cadenas de nieve — imprescindibles en invierno.",
  "Permiso de salida al extranjero — Carta Verde para viajar por la UE.",
];

const COMPROMISO = [
  { t: "Política de combustible justa (lleno / lleno)", d: "Te entregamos el depósito al 100% y lo devuelves al 100%. No cobramos por el llenado si lo traes igual." },
  { t: "El precio de la web manda", d: "El algoritmo calcula el precio según estacionalidad, días y ocupación. El precio que bloqueas hoy es definitivo." },
  { t: "Fianzas rápidas", d: "Ordenamos el desbloqueo de tu fianza en un máximo de 48h tras verificar el estado del vehículo." },
];

export default function Tarifas() {
  useHeroOscuro();
  return (
    <div>
      <BuscadorSeccion
        titulo="Tarifas claras. Cero sorpresas en el mostrador."
        subtitulo="El precio que calculas en nuestra web es el precio exacto que pagas. Sin cargos ocultos de última hora."
      />

      {/* Lo que incluye + imagen */}
      <section className="max-w-container mx-auto px-6 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_360px] gap-10 items-start">
          <FadeIn>
            <div>
              <h2 className="text-2xl font-medium mb-1">Lo que siempre incluye tu reserva</h2>
              <p className="text-text-2 mb-6">Sea una camper para una semana o una furgoneta para una tarde.</p>
              <div className="space-y-3">
                {INCLUYE.map((i) => (
                  <div key={i.t} className="flex items-start gap-3 bg-bg-2 border border-border rounded-xl p-4">
                    <span className="w-7 h-7 rounded-full bg-accent-dim text-accent flex items-center justify-center shrink-0 mt-0.5">
                      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M20 6L9 17l-5-5" /></svg>
                    </span>
                    <div>
                      <p className="font-medium text-sm">{i.t}</p>
                      <p className="text-[13px] text-text-2 mt-0.5">{i.d}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </FadeIn>

          <FadeIn delay={120}>
            <div className="lg:sticky lg:top-24 rounded-2xl overflow-hidden bg-accent-dim aspect-[3/4]">
              <img
                src="/images/tarifas.jpg"
                alt="Vehículos AutoRent"
                className="w-full h-full object-cover"
                onError={(e) => { (e.currentTarget as HTMLImageElement).style.display = "none"; }}
              />
            </div>
          </FadeIn>
        </div>
      </section>

      {/* Modalidades de seguro en 3 columnas */}
      <section className="bg-bg-2 border-y border-border py-16">
        <div className="max-w-container mx-auto px-6">
          <FadeIn>
            <div className="text-center mb-10">
              <h2 className="text-2xl font-medium">Elige tu nivel de tranquilidad</h2>
              <p className="text-text-2 mt-2">Tres modalidades para adaptar el viaje a tu perfil de conductor.</p>
            </div>
          </FadeIn>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-start">
            {MODALIDADES.map((m, i) => (
              <FadeIn key={m.nombre} delay={i * 100}>
                <div className={`relative rounded-2xl p-6 h-full border ${m.destacada ? "border-accent shadow-soft bg-bg" : "border-border bg-bg"}`}>
                  {m.destacada && (
                    <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-accent text-white text-[11px] font-medium px-3 py-1 rounded-full">
                      ⭐ Recomendada
                    </span>
                  )}
                  <p className="font-display font-medium text-lg mt-2">{m.nombre}</p>
                  <p className="text-[13px] text-text-2 mt-1 mb-4 leading-relaxed">{m.claim}</p>
                  <ul className="space-y-2">
                    {m.puntos.map((p) => (
                      <li key={p} className="flex items-start gap-2 text-[13px]">
                        <span className="text-accent mt-0.5 shrink-0">
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M20 6L9 17l-5-5" /></svg>
                        </span>
                        {p}
                      </li>
                    ))}
                  </ul>
                </div>
              </FadeIn>
            ))}
          </div>
        </div>
      </section>

      {/* Extras */}
      <section className="max-w-container mx-auto px-6 py-16">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
          <FadeIn>
            <div>
              <h2 className="text-2xl font-medium mb-1">Adapta el vehículo a tu medida</h2>
              <p className="text-text-2 mb-6">Configura tu reserva en el último paso del buscador añadiendo solo lo que necesitas.</p>
              <ul className="space-y-3">
                {EXTRAS.map((e) => (
                  <li key={e} className="flex items-start gap-3 text-sm">
                    <span className="w-6 h-6 rounded-full bg-accent-dim text-accent flex items-center justify-center shrink-0 mt-0.5">
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 5v14M5 12h14" /></svg>
                    </span>
                    {e}
                  </li>
                ))}
              </ul>
            </div>
          </FadeIn>

          <FadeIn delay={120}>
            <div>
              <h2 className="text-2xl font-medium mb-1">Nuestro compromiso de transparencia</h2>
              <p className="text-text-2 mb-6">Tres reglas de oro para que hagas tus números con tranquilidad.</p>
              <div className="space-y-3">
                {COMPROMISO.map((c, i) => (
                  <div key={c.t} className="bg-bg-2 border border-border rounded-xl p-4 flex gap-3">
                    <span className="w-7 h-7 rounded-full bg-accent text-white font-display text-sm flex items-center justify-center shrink-0">{i + 1}</span>
                    <div>
                      <p className="font-medium text-sm">{c.t}</p>
                      <p className="text-[13px] text-text-2 mt-0.5">{c.d}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </FadeIn>
        </div>

        <FadeIn>
          <div className="text-center mt-12">
            <a href="/modelos" className="inline-block bg-accent text-white font-medium px-8 py-3 rounded-lg hover:opacity-90 transition">
              Reserva tu vehículo ahora
            </a>
          </div>
        </FadeIn>
      </section>
    </div>
  );
}
