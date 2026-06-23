import { useEffect, useState } from "react";
import BuscadorSeccion from "@/components/ui/BuscadorSeccion";
import ExtraCard from "@/components/ui/ExtraCard";
import FadeIn from "@/components/ui/FadeIn";
import { getExtras } from "@/lib/api";
import { useHeroOscuro } from "@/hooks/useHeroOscuro";
import type { Extra } from "@/types";

export default function Extras() {
  useHeroOscuro();
  const [extras, setExtras] = useState<Extra[]>([]);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    getExtras()
      .then(setExtras)
      .catch(() => setExtras([]))
      .finally(() => setCargando(false));
  }, []);

  return (
    <div>
      <BuscadorSeccion titulo="Extras" subtitulo="Personaliza tu alquiler con todo lo que necesites." />
      <section className="max-w-container mx-auto px-6 py-12">
        {cargando && <p className="text-text-2">Cargando extras…</p>}
        {!cargando && extras.length === 0 && (
          <p className="text-text-2">No hay extras disponibles por ahora.</p>
        )}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {extras.map((e, i) => (
            <FadeIn key={e.id} delay={(i % 3) * 80}>
              <ExtraCard extra={e} />
            </FadeIn>
          ))}
        </div>
      </section>
    </div>
  );
}
