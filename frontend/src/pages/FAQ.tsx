import { useState } from "react";
import BuscadorSeccion from "@/components/ui/BuscadorSeccion";
import FadeIn from "@/components/ui/FadeIn";
import { useHeroOscuro } from "@/hooks/useHeroOscuro";

const PREGUNTAS = [
  { q: "¿Qué necesito para alquilar?", a: "DNI o pasaporte en vigor, carnet de conducir con la antigüedad requerida y una tarjeta para la fianza." },
  { q: "¿Cómo funciona la fianza?", a: "Se retiene un depósito al recoger el vehículo y se devuelve tras la entrega si todo está correcto." },
  { q: "¿Puedo cancelar mi reserva?", a: "Sí, según las condiciones de cancelación que verás al confirmar la reserva." },
  { q: "¿El kilometraje es ilimitado?", a: "Depende de la tarifa. Puedes añadir kilometraje ilimitado como extra." },
  { q: "¿Cómo pago la reserva?", a: "Por ahora la reserva se confirma mediante transferencia bancaria; recibirás los datos por email." },
];

export default function FAQ() {
  useHeroOscuro();
  const [abierta, setAbierta] = useState<number | null>(0);
  return (
    <div>
      <BuscadorSeccion titulo="Preguntas frecuentes" subtitulo="Resolvemos las dudas más habituales." />
      <section className="max-w-container mx-auto px-6 py-12">
        <div className="max-w-2xl space-y-3">
          {PREGUNTAS.map((p, i) => (
            <FadeIn key={i} delay={i * 60}>
              <div className="bg-bg-2 border border-border rounded-xl overflow-hidden">
                <button
                  onClick={() => setAbierta(abierta === i ? null : i)}
                  className="w-full flex items-center justify-between px-5 py-4 text-left"
                >
                  <span className="font-medium text-sm">{p.q}</span>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
                    className="transition-transform shrink-0" style={{ transform: abierta === i ? "rotate(180deg)" : "none" }}>
                    <path d="M6 9l6 6 6-6" />
                  </svg>
                </button>
                {abierta === i && (
                  <p className="px-5 pb-4 text-[13px] text-text-2 leading-relaxed">{p.a}</p>
                )}
              </div>
            </FadeIn>
          ))}
        </div>
      </section>
    </div>
  );
}
