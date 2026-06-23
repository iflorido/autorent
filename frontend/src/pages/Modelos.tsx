import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import VehiculoCard from "@/components/ui/VehiculoCard";
import BuscadorSeccion from "@/components/ui/BuscadorSeccion";
import PasosReserva from "@/components/ui/PasosReserva";
import FadeIn from "@/components/ui/FadeIn";
import { getVehiculos } from "@/lib/api";
import { useHeroOscuro } from "@/hooks/useHeroOscuro";
import type { VehiculoList } from "@/types";

const FILTROS = [
  { slug: "", label: "Todos" },
  { slug: "turismo", label: "Turismo" },
  { slug: "camper", label: "Camper" },
  { slug: "industrial", label: "Industrial" },
];

export default function Modelos() {
  useHeroOscuro();
  const [searchParams, setSearchParams] = useSearchParams();
  const [vehiculos, setVehiculos] = useState<VehiculoList[]>([]);
  const [cargando, setCargando] = useState(true);

  const categoria = searchParams.get("categoria") || "";
  const fechaInicio = searchParams.get("fecha_inicio") || undefined;
  const fechaFin = searchParams.get("fecha_fin") || undefined;
  const sede = searchParams.get("sede") || undefined;

  useEffect(() => {
    setCargando(true);
    getVehiculos({
      categoria: categoria || undefined,
      fecha_inicio: fechaInicio,
      fecha_fin: fechaFin,
      sede: sede ? Number(sede) : undefined,
    })
      .then(setVehiculos)
      .catch(() => setVehiculos([]))
      .finally(() => setCargando(false));
  }, [categoria, fechaInicio, fechaFin, sede]);

  function cambiarCategoria(slug: string) {
    const params = new URLSearchParams(searchParams);
    if (slug) params.set("categoria", slug);
    else params.delete("categoria");
    setSearchParams(params);
  }

  const hayFechas = fechaInicio && fechaFin;

  return (
    <div>
      {/* Cabecera con buscador integrado */}
      <BuscadorSeccion
        titulo="Nuestros modelos"
        subtitulo={
          hayFechas
            ? `Vehículos disponibles del ${fechaInicio} al ${fechaFin}.`
            : "Explora toda nuestra flota. Selecciona fechas para ver disponibilidad."
        }
      />

      {/* Filtros de categoría */}
      <div className="max-w-container mx-auto px-6 pt-8">
        <div className="flex flex-wrap gap-2">
          {FILTROS.map((f) => (
            <button
              key={f.slug}
              onClick={() => cambiarCategoria(f.slug)}
              className={`px-4 py-2 rounded-lg text-sm transition ${
                categoria === f.slug
                  ? "bg-accent text-white"
                  : "bg-surface-2 text-text hover:bg-surface-3"
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {/* Listado */}
      <div className="max-w-container mx-auto px-6 py-10">
        {cargando && <p className="text-text-2">Cargando vehículos…</p>}

        {!cargando && vehiculos.length === 0 && (
          <div className="text-center py-16">
            <p className="text-lg font-medium">No hay vehículos disponibles</p>
            <p className="text-text-2 mt-1">
              Prueba con otras fechas o quita los filtros.
            </p>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {vehiculos.map((v, i) => (
            <FadeIn key={v.id} delay={(i % 3) * 80}>
              <VehiculoCard v={v} fechaInicio={fechaInicio} fechaFin={fechaFin} />
            </FadeIn>
          ))}
        </div>
      </div>

      {/* Bloque de pasos antes del footer */}
      <section className="bg-bg-2 border-t border-border py-16 mt-8">
        <div className="max-w-container mx-auto px-6">
          <PasosReserva />
        </div>
      </section>
    </div>
  );
}
