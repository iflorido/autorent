import { useEffect, useMemo, useState } from "react";
import { useParams, useSearchParams, Link, useNavigate } from "react-router-dom";
import { getVehiculo, getVehiculos, getPrecio } from "@/lib/api";
import type { Extra, PrecioCalculo, VehiculoDetail, VehiculoList } from "@/types";
import { formatoCorto, toISODate } from "@/lib/fechas";
import CarruselVehiculos from "@/components/ui/CarruselVehiculos";
import FadeIn from "@/components/ui/FadeIn";
import CalendarioRango from "@/components/ui/CalendarioRango";

export default function Vehiculo() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [vehiculo, setVehiculo] = useState<VehiculoDetail | null>(null);
  const [fotoActiva, setFotoActiva] = useState(0);

  const [inicio, setInicio] = useState<Date | null>(
    searchParams.get("fecha_inicio") ? new Date(searchParams.get("fecha_inicio")!) : null,
  );
  const [fin, setFin] = useState<Date | null>(
    searchParams.get("fecha_fin") ? new Date(searchParams.get("fecha_fin")!) : null,
  );
  const [calOpen, setCalOpen] = useState(false);
  const [precio, setPrecio] = useState<PrecioCalculo | null>(null);
  const [calculandoPrecio, setCalculandoPrecio] = useState(false);

  // Extras seleccionados (set de ids).
  const [extrasSel, setExtrasSel] = useState<Set<number>>(new Set());

  // Otros vehículos para el slider del final.
  const [otros, setOtros] = useState<VehiculoList[]>([]);

  useEffect(() => {
    if (!slug) return;
    getVehiculo(slug).then(setVehiculo).catch(() => {});
  }, [slug]);

  // Cargar otros vehículos (excluyendo el actual) para "Otras opciones".
  useEffect(() => {
    getVehiculos()
      .then((lista) => setOtros(lista.filter((v) => v.slug !== slug).slice(0, 8)))
      .catch(() => setOtros([]));
  }, [slug]);

  useEffect(() => {
    if (!vehiculo || !inicio || !fin) {
      setPrecio(null);
      return;
    }
    setCalculandoPrecio(true);
    getPrecio(vehiculo.id, toISODate(inicio), toISODate(fin))
      .then(setPrecio)
      .catch(() => setPrecio(null))
      .finally(() => setCalculandoPrecio(false));
  }, [vehiculo, inicio, fin]);

  const fotos = vehiculo?.fotos ?? [];
  const fotoPrincipal = useMemo(() => fotos[fotoActiva] ?? fotos[0], [fotos, fotoActiva]);

  function toggleExtra(extraId: number) {
    setExtrasSel((prev) => {
      const n = new Set(prev);
      if (n.has(extraId)) n.delete(extraId);
      else n.add(extraId);
      return n;
    });
  }

  // Precio de un extra según su tipo de cobro y los días de la reserva.
  function precioExtra(e: Extra): number {
    const dias = precio?.num_dias ?? 0;
    const base = parseFloat(e.precio);
    return e.tipo_cobro === "por_dia" ? base * dias : base;
  }

  // Lista de extras seleccionados con su subtotal calculado.
  const extrasCalculados = useMemo(() => {
    if (!vehiculo) return [];
    return vehiculo.extras
      .filter((e) => extrasSel.has(e.id))
      .map((e) => ({ extra: e, subtotal: precioExtra(e) }));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [vehiculo, extrasSel, precio?.num_dias]);

  const totalExtras = extrasCalculados.reduce((s, x) => s + x.subtotal, 0);
  const subtotalVehiculo = precio ? parseFloat(precio.subtotal_vehiculo) : 0;
  const totalAlquiler = subtotalVehiculo + totalExtras;

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

  const fmt = (n: number) => n.toLocaleString("es-ES", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

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

            {/* Extras seleccionables */}
            {vehiculo.extras.length > 0 && (
              <div className="mt-8">
                <h2 className="text-lg font-medium mb-1">Extras</h2>
                <p className="text-[13px] text-text-2 mb-4">
                  Marca los que quieras añadir; se sumarán al total.
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {vehiculo.extras.map((e) => {
                    const sel = extrasSel.has(e.id);
                    return (
                      <button
                        key={e.id}
                        onClick={() => toggleExtra(e.id)}
                        className={`flex items-center justify-between gap-3 rounded-lg px-4 py-3 border text-left transition ${
                          sel ? "border-accent bg-accent-dim" : "border-border bg-bg-2 hover:border-border-2"
                        }`}
                      >
                        <div className="flex items-center gap-3 min-w-0">
                          <span
                            className={`shrink-0 w-5 h-5 rounded border flex items-center justify-center transition ${
                              sel ? "bg-accent border-accent" : "border-border-2"
                            }`}
                          >
                            {sel && (
                              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="3">
                                <path d="M20 6L9 17l-5-5" />
                              </svg>
                            )}
                          </span>
                          <div className="min-w-0">
                            <p className="text-sm font-medium truncate">{e.nombre}</p>
                            {e.descripcion && <p className="text-[12px] text-text-2 truncate">{e.descripcion}</p>}
                          </div>
                        </div>
                        <p className="text-sm text-accent font-medium whitespace-nowrap">
                          {e.precio} € <span className="text-text-2 font-normal">/ {e.tipo_cobro === "por_dia" ? "día" : "ud."}</span>
                        </p>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar sticky de reserva */}
          <aside className="lg:sticky lg:top-24">
            <div className="bg-bg-2 border border-border rounded-xl shadow-soft p-5">
              <p className="font-display font-medium">{vehiculo.nombre}</p>
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
                      <p className="text-red-600 text-[13px] mb-2">No disponible en estas fechas.</p>
                    )}
                    <div className="flex justify-between text-text-2">
                      <span>{precio.num_dias} días × {precio.precio_dia_base} €</span>
                      <span>{fmt(subtotalVehiculo)} €</span>
                    </div>

                    {/* Líneas de extras seleccionados */}
                    {extrasCalculados.map(({ extra, subtotal }) => (
                      <div key={extra.id} className="flex justify-between text-text-2">
                        <span className="truncate pr-2">
                          {extra.nombre}
                          {extra.tipo_cobro === "por_dia" && (
                            <span className="text-[12px]"> ({precio.num_dias}d)</span>
                          )}
                        </span>
                        <span className="whitespace-nowrap">{fmt(subtotal)} €</span>
                      </div>
                    ))}

                    <div className="flex justify-between text-text-2">
                      <span>Fianza (depósito)</span>
                      <span>{precio.fianza} €</span>
                    </div>
                    <p className="text-[11px] text-text-2 leading-snug">
                      La fianza se retiene en la recogida con tarjeta de crédito a nombre del titular.
                    </p>

                    <div className="flex justify-between font-medium text-base border-t border-border pt-2 mt-2">
                      <span>Total alquiler</span>
                      <span>{fmt(totalAlquiler)} €</span>
                    </div>
                    {totalExtras > 0 && (
                      <p className="text-[11px] text-text-2">
                        Incluye {fmt(totalExtras)} € en extras.
                      </p>
                    )}
                  </div>
                ) : (
                  <p className="text-[13px] text-text-2">No se pudo calcular el precio.</p>
                )}
              </div>

              <button
                disabled={!precio?.disponible}
                onClick={() => {
                  if (!vehiculo || !inicio || !fin) return;
                  const params = new URLSearchParams();
                  params.set("fecha_inicio", toISODate(inicio));
                  params.set("fecha_fin", toISODate(fin));
                  if (extrasSel.size > 0) {
                    params.set("extras", Array.from(extrasSel).join(","));
                  }
                  navigate(`/reserva/${vehiculo.slug}?${params.toString()}`);
                }}
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

      {/* Otros vehículos disponibles */}
      {otros.length > 0 && (
        <section className="bg-bg-2 border-t border-border py-16 mt-8">
          <div className="max-w-container mx-auto px-6">
            <FadeIn>
              <CarruselVehiculos vehiculos={otros} titulo="Otros vehículos disponibles" />
            </FadeIn>
          </div>
        </section>
      )}
    </div>
  );
}
