import { useEffect, useState } from "react";
import BuscadorSeccion from "@/components/ui/BuscadorSeccion";
import OficinasCercanas from "@/components/ui/OficinasCercanas";
import FadeIn from "@/components/ui/FadeIn";
import { getSedes } from "@/lib/api";
import { useHeroOscuro } from "@/hooks/useHeroOscuro";
import type { Sede } from "@/types";

export default function Localizaciones() {
  useHeroOscuro();
  const [sedes, setSedes] = useState<Sede[]>([]);
  useEffect(() => { getSedes().then(setSedes).catch(() => {}); }, []);

  return (
    <div>
      <BuscadorSeccion
        titulo="Localizaciones"
        subtitulo="Recoge y entrega tu vehículo en nuestras sedes."
      />
      <section className="max-w-container mx-auto px-6 py-12">
        <FadeIn><OficinasCercanas sedes={sedes} /></FadeIn>
      </section>
    </div>
  );
}
