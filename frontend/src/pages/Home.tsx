import { useEffect, useState } from "react";
import { getVehiculos } from "@/lib/api";
import type { VehiculoList } from "@/types";

export default function Home() {
  const [vehiculos, setVehiculos] = useState<VehiculoList[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getVehiculos()
      .then(setVehiculos)
      .catch(() => setError("No se pudieron cargar los vehículos."))
      .finally(() => setCargando(false));
  }, []);

  return (
    <div>
      {/* Hero provisional (se desarrollará con el buscador en la siguiente fase) */}
      <section className="bg-gradient-to-br from-[#0f2433] to-accent py-20 px-6">
        <div className="max-w-container mx-auto">
          <h1 className="text-white text-3xl md:text-4xl font-medium max-w-xl leading-tight">
            Tu próxima aventura sobre ruedas
          </h1>
          <p className="text-white/80 mt-3 max-w-lg">
            Furgonetas, campers y vehículos para cada viaje. Reserva en minutos.
          </p>
        </div>
      </section>

      {/* Listado provisional para verificar la conexión con la API */}
      <section className="max-w-container mx-auto px-6 py-12">
        <h2 className="text-xl font-medium mb-6">Nuestros vehículos</h2>

        {cargando && <p className="text-text-2">Cargando…</p>}
        {error && <p className="text-red-600">{error}</p>}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {vehiculos.map((v) => (
            <div key={v.id} className="bg-bg-2 border border-border rounded-xl overflow-hidden">
              <div className="h-44 bg-accent-dim flex items-center justify-center">
                {v.foto_principal ? (
                  <img src={v.foto_principal} alt={v.nombre} className="w-full h-full object-cover" />
                ) : (
                  <span className="text-accent text-sm">Sin foto</span>
                )}
              </div>
              <div className="p-4">
                <p className="font-medium">{v.nombre}</p>
                <p className="text-[13px] text-text-2 mt-0.5">
                  {v.categoria_display} · {v.plazas} plazas
                </p>
                {v.precio_desde && (
                  <p className="text-sm mt-2">
                    <span className="font-medium text-accent">desde {v.precio_desde} €</span> / día
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
