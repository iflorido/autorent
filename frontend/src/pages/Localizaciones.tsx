import { useEffect, useState } from "react";
import BuscadorSeccion from "@/components/ui/BuscadorSeccion";
import FadeIn from "@/components/ui/FadeIn";
import { getSedes } from "@/lib/api";
import { useHeroOscuro } from "@/hooks/useHeroOscuro";
import type { Sede } from "@/types";

function MapaSede({ sede }: { sede: Sede }) {
  if (!sede.latitud || !sede.longitud) return null;
  const lat = parseFloat(sede.latitud);
  const lon = parseFloat(sede.longitud);
  // bbox pequeño alrededor del punto + marcador, vía OpenStreetMap (sin API key).
  const d = 0.008;
  const bbox = `${lon - d}%2C${lat - d}%2C${lon + d}%2C${lat + d}`;
  const src = `https://www.openstreetmap.org/export/embed.html?bbox=${bbox}&layer=mapnik&marker=${lat}%2C${lon}`;
  return (
    <div className="rounded-xl overflow-hidden border border-border mt-4">
      <iframe
        title={`Mapa de ${sede.nombre}`}
        src={src}
        className="w-full h-64 block"
        loading="lazy"
      />
    </div>
  );
}

export default function Localizaciones() {
  useHeroOscuro();
  const [sedes, setSedes] = useState<Sede[]>([]);
  useEffect(() => { getSedes().then(setSedes).catch(() => {}); }, []);

  return (
    <div>
      <BuscadorSeccion titulo="Localizaciones" subtitulo="Recoge y entrega tu vehículo en nuestras sedes." />
      <section className="max-w-container mx-auto px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {sedes.map((s, i) => (
            <FadeIn key={s.id} delay={(i % 2) * 100}>
              <div className="bg-bg-2 border border-border rounded-2xl p-6">
                <div className="flex items-start gap-4">
                  <span className="shrink-0 w-12 h-12 rounded-lg bg-accent flex items-center justify-center text-white">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                      <path d="M21 10c0 7-9 12-9 12s-9-5-9-12a9 9 0 0118 0z" /><circle cx="12" cy="10" r="3" />
                    </svg>
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="font-display font-medium text-lg">{s.nombre}</p>
                    <p className="text-[13px] text-text-2 mt-1">
                      {s.direccion}
                      {s.direccion && (s.poblacion || s.cp) ? <br /> : null}
                      {[s.poblacion, s.provincia, s.cp].filter(Boolean).join(", ")}
                    </p>
                    {s.telefono && <p className="text-[13px] text-text-2 mt-2">Tel: {s.telefono}</p>}
                    {s.horario && <p className="text-[13px] text-text-2 mt-1 whitespace-pre-line">{s.horario}</p>}
                  </div>
                </div>
                <MapaSede sede={s} />
              </div>
            </FadeIn>
          ))}
        </div>
        {sedes.length === 0 && <p className="text-text-2">Cargando sedes…</p>}
      </section>
    </div>
  );
}
