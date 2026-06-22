import { useEffect, useMemo, useState } from "react";
import { useParams, useSearchParams, Link } from "react-router-dom";
import { getVehiculo, getPrecio } from "@/lib/api";
import type { PrecioCalculo, VehiculoDetail } from "@/types";
import { formatoCorto, toISODate } from "@/lib/fechas";
import CalendarioRango from "@/components/ui/CalendarioRango";

export default function Vehiculo() {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const [vehiculo, setVehiculo] = useState<VehiculoDetail | null>(null);
  const [fotoActiva, setFotoActiva] = useState(0);

  // Fechas (desde la URL si vienen del buscador).
  const [inicio, setInicio] = useState<Date | null>(
    searchParams.get("fecha_inicio") ? new Date(searchParams.get("fecha_inicio")!) : null,
  );
  const [fin, setFin] = useState<Date | null>(
    searchParams.get("fecha_fin") ? new Date(searchParams.get("fecha_fin")!) : null,
  );
  const [calOpen, setCalOpen] = useState(false);
  const [precio, setPrecio] = useState<PrecioCalculo | null>(null);
  const [calculandoPrecio, setCalculandoPrecio] = useState(false);

  useEffect(() => {
    if (!id) return;
    getVehiculo(Number(id)).then(setVehiculo).catch(() => {});
  }, [id]);

  // Recalcula el precio cuando hay fechas válidas.
  useEffect(() => {
    if (!id || !inicio || !fin) {
      setPrecio(null);
      return;
    }
    setCalculandoPrecio(true);
    getPrecio(Number(id), toISODate(inicio), toISODate(fin))
      .then(setPrecio)
      .catch(() => setPrecio(null))
      .finally(() => setCalculandoPrecio(false));
  }, [id, inicio, fin]);

  const fotos = vehiculo?.fotos ?? [];
  const fotoPrincipal = useMemo(() => fotos[fotoActiva] ?? fotos[0], [fotos, fotoActiva]);

  if (!vehiculo) {
    return <div className="pt-28 max-w-container mx-auto px-6 py-20 text-text-2">Cargando…</div>;
  }

  const caracteristicas = [
    { label: "Plazas", valor: vehiculo.plazas },
    { label: "Puertas", valor: vehiculo.puertas },
    { label: "Combustible", valor: vehiculo.combustible_display },
    { label: "Cambio", valor: vehiculo.cambio_display },
    { label: "Carga", valor: vehiculo.capacidad_carga || "—" },
    { label: "Categoría", valor: vehiculo.categoria_display },
  ];

  return (
    <div className="pt-16">
      <div className="max-w-container mx-auto px-6 py-8">
        <Link to="/modelos" className="text-sm text-text-2 hover:text-accent inline-flex items-center gap-1 mb-6">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M15 18l-6-6 6-6" />
          </svg>
          Volver a modelos
        </Link>

        <div className="grid grid-cols-1 lg:grid-cols-[1fr_360px] gap-8 items-start">
          {/* Columna principal */}
          <div>
            {/* Galería */}
            <div className="rounded-xl overflow-hidden bg-accent-dim aspect-[16/10] flex items-center justify-center">
              {fotoPrincipal?.imagen ? (
                <img src={fotoPrincipal.imagen} alt={vehiculo.nombre} className="w-full h-full object-cover" />
              ) : (
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.2" className="text-accent">
                  <path d="M3 13h18v4H3zM5 13V8h11l3 5" />
                </svg>
              )}
            </div>
            {fotos.length > 1 && (
              <div className="flex gap-2 mt-3 overflow-x-auto pb-1">
                {fotos.map((f, i) => (
                  <button
                    key={f.id}
                    onClick={() => setFotoActiva(i)}
                    className={`shrink-0 w-24 h-16 rounded-lg overflow-hidden border-2 transition ${
                      i === fotoActiva ? "border-accent" : "border-transparent"
                    }`}
                  >
                    {f.imagen && <img src={f.imagen} alt="" className="w-full h-full object-cover" />}
                  </button>
                ))}
              </div>
            )}

            {/* Título y descripción */}
            <div className="mt-8">
              <h1 className="text-3xl font-medium">{vehiculo.nombre}</h1>
              <p className="text-text-2 mt-1">{vehiculo.marca} {vehiculo.modelo}{vehiculo.anio ? ` · ${vehiculo.anio}` : ""}</p>
              {vehiculo.descripcion && (
                <p className="text-text-2 mt-4 leading-relaxed">{vehiculo.descripcion}</p>
              )}
            </div>

            {/* Características */}
            <div className="mt-8">
              <h2 className="text-lg font-medium mb-4">Características</h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                {caracteristicas.map((c) => (
                  <div key={c.label} className="bg-bg-2 border border-border rounded-lg p-4">
                    <p className="text-[12px] uppercase tracking-wide text-text-2">{c.label}</p>
                    <p className="font-medium mt-1">{c.valor}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Extras disponibles */}
            {vehiculo.extras.length > 0 && (
              <div className="mt-8">
                <h2 className="text-lg font-medium mb-4">Extras disponibles</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {vehiculo.extras.map((e) => (
                    <div key={e.id} className="flex items-center justify-between bg-bg-2 border border-border rounded-lg px-4 py-3">
                      <div>
                        <p className="text-sm font-medium">{e.nombre}</p>
                        {e.descripcion && <p className="text-[12px] text-text-2">{e.descripcion}</p>}
                      </div>
                      <p className="text-sm text-accent font-medium whitespace-nowrap">
                        {e.precio} € <span className="text-text-2 font-normal">/ {e.tipo_cobro === "por_dia" ? "día" : "ud."}</span>
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar sticky de reserva */}
          <aside className="lg:sticky lg:top-24">
            <div className="bg-bg-2 border border-border rounded-xl shadow-soft p-5">
              <p className="font-medium">{vehiculo.nombre}</p>
              {vehiculo.sede && (
                <p className="text-[13px] text-text-2 mt-0.5">{vehiculo.sede.nombre}</p>
              )}

              {/* Selector de fechas */}
              <div className="mt-4 relative">
                <label className="text-[11px] uppercase tracking-wide text-text-2 font-medium">Fechas</label>
                <button
                  onClick={() => setCalOpen((v) => !v)}
                  className="w-full mt-1 h-10 px-3 border border-border-2 rounded-lg text-sm flex items-center gap-2 text-left"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="text-accent">
                    <rect x="3" y="4" width="18" height="18" rx="2" /><path d="M16 2v4M8 2v4M3 10h18" />
                  </svg>
                  <span className={inicio ? "text-text" : "text-text-2"}>
                    {inicio && fin
                      ? `${formatoCorto(inicio)} – ${formatoCorto(fin)}`
                      : "Selecciona fechas"}
                  </span>
                </button>
                {calOpen && (
                  <div className="absolute right-0 top-full mt-2 z-[999] w-[640px] max-w-[80vw]">
                    <CalendarioRango
                      inicio={inicio}
                      fin={fin}
                      onChange={(i, f) => {
                        setInicio(i);
                        setFin(f);
                        if (i && f) setCalOpen(false);
                      }}
                    />
                  </div>
                )}
              </div>

              {/* Desglose de precio */}
              <div className="mt-5 border-t border-border pt-4">
                {!inicio || !fin ? (
                  <p className="text-[13px] text-text-2">Selecciona fechas para ver el precio.</p>
                ) : calculandoPrecio ? (
                  <p className="text-[13px] text-text-2">Calculando…</p>
                ) : precio ? (
                  <div className="space-y-2 text-sm">
                    {!precio.disponible && (
                      <p className="text-red-600 text-[13px] mb-2">
                        No disponible en estas fechas.
                      </p>
                    )}
                    <div className="flex justify-between text-text-2">
                      <span>{precio.num_dias} días × {precio.precio_dia_base} €</span>
                      <span>{precio.subtotal_vehiculo} €</span>
                    </div>
                    <div className="flex justify-between text-text-2">
                      <span>Fianza (depósito)</span>
                      <span>{precio.fianza} €</span>
                    </div>
                    <div className="flex justify-between font-medium text-base border-t border-border pt-2 mt-2">
                      <span>Total alquiler</span>
                      <span>{precio.subtotal_vehiculo} €</span>
                    </div>
                  </div>
                ) : (
                  <p className="text-[13px] text-text-2">No se pudo calcular el precio.</p>
                )}
              </div>

              <button
                disabled={!precio?.disponible}
                className="w-full mt-5 h-11 bg-accent text-white rounded-lg font-medium hover:opacity-90 transition disabled:opacity-40 disabled:cursor-not-allowed"
              >
                Continuar con la reserva
              </button>
              <p className="text-[11px] text-text-2 text-center mt-2">
                Sin cargo hasta confirmar la reserva.
              </p>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}
