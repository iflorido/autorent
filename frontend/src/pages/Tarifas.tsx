import BuscadorSeccion from "@/components/ui/BuscadorSeccion";
import FadeIn from "@/components/ui/FadeIn";
import { useHeroOscuro } from "@/hooks/useHeroOscuro";

const INCLUYE = [
  "Kilometraje según tarifa contratada",
  "Seguro básico a terceros",
  "Asistencia en carretera 24/7",
  "Mantenimiento e ITV al día",
];

export default function Tarifas() {
  useHeroOscuro();
  return (
    <div>
      <BuscadorSeccion titulo="Tarifas" subtitulo="Precios claros, sin sorpresas. El precio por día baja cuanto más larga es tu reserva." />
      <section className="max-w-container mx-auto px-6 py-12">
        <FadeIn>
          <div className="bg-bg-2 border border-border rounded-2xl p-8 max-w-2xl">
            <h2 className="text-xl font-medium mb-4">Qué incluye tu alquiler</h2>
            <ul className="space-y-3">
              {INCLUYE.map((t) => (
                <li key={t} className="flex items-center gap-3 text-sm">
                  <span className="w-6 h-6 rounded-full bg-accent-dim text-accent flex items-center justify-center shrink-0">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M20 6L9 17l-5-5" /></svg>
                  </span>
                  {t}
                </li>
              ))}
            </ul>
            <p className="text-[13px] text-text-2 mt-6">
              Las tarifas exactas se calculan según el vehículo y las fechas. Usa el buscador para ver el precio de tu reserva.
            </p>
          </div>
        </FadeIn>
      </section>
    </div>
  );
}
