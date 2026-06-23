import BuscadorSeccion from "@/components/ui/BuscadorSeccion";
import FadeIn from "@/components/ui/FadeIn";
import { useHeroOscuro } from "@/hooks/useHeroOscuro";

const EXTRAS = [
  { nombre: "Seguro a todo riesgo", desc: "Cobertura completa sin franquicia para viajar tranquilo." },
  { nombre: "Conductor adicional", desc: "Añade conductores autorizados a tu reserva." },
  { nombre: "GPS / Navegador", desc: "Navegador con mapas actualizados." },
  { nombre: "Silla infantil", desc: "Homologadas para distintas edades." },
  { nombre: "Kit camping", desc: "Mesa, sillas y menaje para tus escapadas." },
  { nombre: "Kilometraje ilimitado", desc: "Sin límite de kilómetros durante tu alquiler." },
];

export default function Extras() {
  useHeroOscuro();
  return (
    <div>
      <BuscadorSeccion titulo="Extras" subtitulo="Personaliza tu alquiler con todo lo que necesites." />
      <section className="max-w-container mx-auto px-6 py-12">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {EXTRAS.map((e, i) => (
            <FadeIn key={e.nombre} delay={(i % 3) * 80}>
              <div className="bg-bg-2 border border-border rounded-2xl p-6 h-full hover:shadow-soft hover:-translate-y-1 transition-all duration-300">
                <span className="w-11 h-11 rounded-xl bg-accent-dim flex items-center justify-center text-accent mb-3">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M12 5v14M5 12h14" /></svg>
                </span>
                <p className="font-display font-medium text-lg">{e.nombre}</p>
                <p className="text-[13px] text-text-2 mt-1 leading-relaxed">{e.desc}</p>
              </div>
            </FadeIn>
          ))}
        </div>
      </section>
    </div>
  );
}
