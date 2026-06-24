import { useEffect, useMemo, useState } from "react";
import { useParams, useSearchParams, Link } from "react-router-dom";
import PasosIndicador from "@/components/ui/PasosIndicador";
import { getVehiculo, getPrecio, crearReserva } from "@/lib/api";
import type {
  ClienteEntrada,
  ExtraEntrada,
  PrecioCalculo,
  ReservaCreada,
  VehiculoDetail,
} from "@/types";
import { formatoCorto } from "@/lib/fechas";

const PASOS = ["Tus datos", "Pago", "Confirmación"];

/** Extrae el primer mensaje de error legible de la respuesta del backend. */
function extraerError(data: unknown): string | null {
  if (!data) return null;
  if (typeof data === "string") return data;
  if (Array.isArray(data)) return data.length ? extraerError(data[0]) : null;
  if (typeof data === "object") {
    // Caso { detail: "..." }
    const obj = data as Record<string, unknown>;
    if (typeof obj.detail === "string") return obj.detail;
    // Recorrer campos (incluido anidado como { cliente: { campo: [...] } }).
    for (const valor of Object.values(obj)) {
      const msg = extraerError(valor);
      if (msg) return msg;
    }
  }
  return null;
}

const CLIENTE_INICIAL: ClienteEntrada = {
  nombre: "", apellidos: "", nif: "", email: "", telefono: "",
  fecha_nacimiento: "", direccion: "", poblacion: "", cp: "", provincia: "",
  carnet_numero: "", carnet_caducidad: "",
};

export default function Reserva() {
  const { slug } = useParams();
  const [searchParams] = useSearchParams();

  const fechaInicio = searchParams.get("fecha_inicio") || "";
  const fechaFin = searchParams.get("fecha_fin") || "";
  const extrasIds = useMemo(() => {
    const raw = searchParams.get("extras");
    return raw ? raw.split(",").map(Number).filter(Boolean) : [];
  }, [searchParams]);

  const [vehiculo, setVehiculo] = useState<VehiculoDetail | null>(null);
  const [precio, setPrecio] = useState<PrecioCalculo | null>(null);
  const [paso, setPaso] = useState(0);

  const [cliente, setCliente] = useState<ClienteEntrada>(CLIENTE_INICIAL);
  const [metodoPago, setMetodoPago] = useState<"transferencia" | "tarjeta" | "efectivo">("transferencia");
  const [aceptaCondiciones, setAceptaCondiciones] = useState(false);

  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reserva, setReserva] = useState<ReservaCreada | null>(null);

  useEffect(() => {
    if (!slug) return;
    getVehiculo(slug).then(setVehiculo).catch(() => {});
  }, [slug]);

  useEffect(() => {
    if (!vehiculo || !fechaInicio || !fechaFin) return;
    getPrecio(vehiculo.id, fechaInicio, fechaFin).then(setPrecio).catch(() => {});
  }, [vehiculo, fechaInicio, fechaFin]);

  // Extras elegidos con su cálculo para el resumen.
  const extrasElegidos = useMemo(() => {
    if (!vehiculo) return [];
    const dias = precio?.num_dias ?? 0;
    return vehiculo.extras
      .filter((e) => extrasIds.includes(e.id))
      .map((e) => ({
        extra: e,
        subtotal: e.tipo_cobro === "por_dia" ? parseFloat(e.precio) * dias : parseFloat(e.precio),
      }));
  }, [vehiculo, extrasIds, precio?.num_dias]);

  const totalExtras = extrasElegidos.reduce((s, x) => s + x.subtotal, 0);
  const subtotalVehiculo = precio ? parseFloat(precio.subtotal_vehiculo) : 0;
  const totalAlquiler = subtotalVehiculo + totalExtras;
  const fmt = (n: number) => n.toLocaleString("es-ES", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  function actualizar(campo: keyof ClienteEntrada, valor: string) {
    setCliente((c) => ({ ...c, [campo]: valor }));
  }

  function validarPaso1(): boolean {
    setError(null);
    if (!cliente.nombre.trim() || !cliente.nif.trim() || !cliente.email.trim() || !cliente.telefono.trim()) {
      setError("Completa al menos nombre, NIF, email y teléfono.");
      return false;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(cliente.email)) {
      setError("El email no parece válido.");
      return false;
    }
    if (!cliente.carnet_numero?.trim() || !cliente.carnet_caducidad) {
      setError("Indica el número y la caducidad de tu carnet de conducir.");
      return false;
    }
    // El carnet no puede estar caducado al inicio del alquiler.
    if (cliente.carnet_caducidad < fechaInicio) {
      setError("Tu carnet de conducir caduca antes del inicio del alquiler.");
      return false;
    }
    return true;
  }

  async function confirmarReserva() {
    setError(null);
    if (!aceptaCondiciones) {
      setError("Debes aceptar las Condiciones Generales de Contratación.");
      return;
    }
    if (!vehiculo) return;

    const extras: ExtraEntrada[] = extrasIds.map((id) => ({ extra_id: id, cantidad: 1 }));

    // Limpieza: no enviar cadenas vacías en los campos de fecha (el backend
    // espera fecha válida o ausencia del campo).
    const clienteLimpio: ClienteEntrada = { ...cliente };
    if (!clienteLimpio.fecha_nacimiento) delete clienteLimpio.fecha_nacimiento;
    if (!clienteLimpio.carnet_caducidad) delete clienteLimpio.carnet_caducidad;

    setEnviando(true);
    try {
      const creada = await crearReserva({
        vehiculo_id: vehiculo.id,
        fecha_inicio: fechaInicio,
        fecha_fin: fechaFin,
        metodo_pago: metodoPago,
        cliente: clienteLimpio,
        extras,
        acepta_condiciones: aceptaCondiciones,
      });
      setReserva(creada);
      setPaso(2);
    } catch (e: unknown) {
      const err = e as { response?: { data?: unknown; status?: number } };
      if (err.response?.status === 409) {
        setError("El vehículo ya no está disponible en esas fechas.");
      } else {
        // Extraer el primer mensaje de error legible que devuelva el backend.
        setError(extraerError(err.response?.data) ?? "No se pudo completar la reserva. Inténtalo de nuevo.");
      }
    } finally {
      setEnviando(false);
    }
  }

  // Falta de datos esenciales en la URL.
  if (!fechaInicio || !fechaFin) {
    return (
      <div className="pt-28 max-w-container mx-auto px-6 py-20 text-center">
        <p className="text-lg font-medium">Faltan las fechas de la reserva</p>
        <p className="text-text-2 mt-1">Vuelve a la ficha del vehículo y selecciona fechas.</p>
        <Link to="/modelos" className="inline-block mt-4 text-accent hover:underline">Ver modelos</Link>
      </div>
    );
  }

  if (!vehiculo) {
    return <div className="pt-28 max-w-container mx-auto px-6 py-20 text-text-2">Cargando…</div>;
  }

  return (
    <div className="pt-16">
      <div className="max-w-container mx-auto px-6 py-8">
        <h1 className="text-2xl font-medium mb-6">Completa tu reserva</h1>

        {paso < 2 && (
          <div className="mb-8 max-w-2xl">
            <PasosIndicador pasos={PASOS} actual={paso} />
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-[1fr_360px] gap-8 items-start">
          {/* Columna de pasos */}
          <div>
            {/* Paso 1: datos del cliente */}
            {paso === 0 && (
              <div className="bg-bg-2 border border-border rounded-2xl p-6">
                <h2 className="text-lg font-medium mb-5">Tus datos</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <Campo label="Nombre *" value={cliente.nombre} onChange={(v) => actualizar("nombre", v)} />
                  <Campo label="Apellidos" value={cliente.apellidos || ""} onChange={(v) => actualizar("apellidos", v)} />
                  <Campo label="NIF / DNI / Pasaporte *" value={cliente.nif} onChange={(v) => actualizar("nif", v)} />
                  <Campo label="Teléfono *" value={cliente.telefono} onChange={(v) => actualizar("telefono", v)} />
                  <Campo label="Email *" value={cliente.email} onChange={(v) => actualizar("email", v)} className="sm:col-span-2" />
                  <Campo label="Fecha de nacimiento" type="date" value={cliente.fecha_nacimiento || ""} onChange={(v) => actualizar("fecha_nacimiento", v)} />
                  <Campo label="Nº carnet de conducir *" value={cliente.carnet_numero || ""} onChange={(v) => actualizar("carnet_numero", v)} />
                  <Campo label="Caducidad del carnet *" type="date" value={cliente.carnet_caducidad || ""} onChange={(v) => actualizar("carnet_caducidad", v)} />
                  <Campo label="Dirección" value={cliente.direccion || ""} onChange={(v) => actualizar("direccion", v)} className="sm:col-span-2" />
                  <Campo label="Población" value={cliente.poblacion || ""} onChange={(v) => actualizar("poblacion", v)} />
                  <Campo label="Código postal" value={cliente.cp || ""} onChange={(v) => actualizar("cp", v)} />
                </div>
                {error && <p className="text-red-600 text-[13px] mt-4">{error}</p>}
                <div className="flex justify-end mt-6">
                  <button
                    onClick={() => { if (validarPaso1()) setPaso(1); }}
                    className="h-11 px-6 bg-accent text-white rounded-lg font-medium hover:opacity-90 transition"
                  >
                    Continuar
                  </button>
                </div>
              </div>
            )}

            {/* Paso 2: método de pago + condiciones */}
            {paso === 1 && (
              <div className="bg-bg-2 border border-border rounded-2xl p-6">
                <h2 className="text-lg font-medium mb-5">Método de pago</h2>
                <div className="space-y-3">
                  {[
                    { v: "transferencia", t: "Transferencia bancaria", d: "Recibirás los datos para hacer el ingreso y confirmar la reserva." },
                    { v: "efectivo", t: "Efectivo / en oficina", d: "Paga al recoger el vehículo en nuestra sede." },
                  ].map((m) => (
                    <button
                      key={m.v}
                      onClick={() => setMetodoPago(m.v as typeof metodoPago)}
                      className={`w-full flex items-start gap-3 p-4 rounded-xl border text-left transition ${
                        metodoPago === m.v ? "border-accent bg-accent-dim" : "border-border hover:border-border-2"
                      }`}
                    >
                      <span className={`w-5 h-5 rounded-full border-2 mt-0.5 shrink-0 flex items-center justify-center ${metodoPago === m.v ? "border-accent" : "border-border-2"}`}>
                        {metodoPago === m.v && <span className="w-2.5 h-2.5 rounded-full bg-accent" />}
                      </span>
                      <div>
                        <p className="font-medium text-sm">{m.t}</p>
                        <p className="text-[13px] text-text-2">{m.d}</p>
                      </div>
                    </button>
                  ))}
                </div>

                {/* Checkbox obligatorio de condiciones (NO premarcado) */}
                <label className="flex items-start gap-3 mt-6 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={aceptaCondiciones}
                    onChange={(e) => setAceptaCondiciones(e.target.checked)}
                    className="mt-0.5 w-4 h-4 accent-[color:var(--accent)]"
                  />
                  <span className="text-[13px] text-text-2">
                    He leído y acepto las{" "}
                    <Link to="/condiciones" target="_blank" className="text-accent hover:underline">
                      Condiciones Generales de Contratación
                    </Link>{" "}
                    y autorizo la retención de la fianza en mi tarjeta.
                  </span>
                </label>

                {error && <p className="text-red-600 text-[13px] mt-4">{error}</p>}

                <div className="flex justify-between mt-6">
                  <button onClick={() => setPaso(0)} className="h-11 px-5 border border-border-2 rounded-lg text-sm hover:bg-surface-2 transition">
                    Atrás
                  </button>
                  <button
                    onClick={confirmarReserva}
                    disabled={enviando || !aceptaCondiciones}
                    className="h-11 px-6 bg-accent text-white rounded-lg font-medium hover:opacity-90 transition disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    {enviando ? "Procesando…" : "Confirmar reserva"}
                  </button>
                </div>
              </div>
            )}

            {/* Paso 3: confirmación */}
            {paso === 2 && reserva && (
              <div className="bg-bg-2 border border-border rounded-2xl p-8 text-center">
                <span className="w-16 h-16 rounded-full bg-accent-dim text-accent flex items-center justify-center mx-auto mb-4">
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M20 6L9 17l-5-5" /></svg>
                </span>
                <h2 className="text-xl font-medium">¡Reserva registrada!</h2>
                <p className="text-text-2 mt-1">Tu localizador es:</p>
                <p className="text-2xl font-display font-medium text-accent mt-2 tracking-wide">{reserva.localizador}</p>

                <div className="bg-bg border border-border rounded-xl p-5 mt-6 text-left max-w-sm mx-auto">
                  <p className="text-sm"><strong>{reserva.vehiculo_nombre}</strong></p>
                  <p className="text-[13px] text-text-2 mt-1">{reserva.fecha_inicio} → {reserva.fecha_fin} ({reserva.num_dias} días)</p>
                  <div className="flex justify-between text-sm mt-3 pt-3 border-t border-border">
                    <span>Total alquiler</span><strong>{reserva.total} €</strong>
                  </div>
                  <div className="flex justify-between text-[13px] text-text-2 mt-1">
                    <span>Fianza (depósito)</span><span>{reserva.fianza} €</span>
                  </div>
                </div>

                {reserva.metodo_pago === "transferencia" && (
                  <p className="text-[13px] text-text-2 mt-5 max-w-sm mx-auto">
                    En breve recibirás un correo con los datos bancarios. Tu vehículo queda
                    pre-reservado durante 24 horas hasta recibir el justificante.
                  </p>
                )}

                <Link to="/" className="inline-block mt-6 bg-accent text-white font-medium px-6 py-3 rounded-lg hover:opacity-90 transition">
                  Volver al inicio
                </Link>
              </div>
            )}
          </div>

          {/* Resumen lateral */}
          <aside className="lg:sticky lg:top-24">
            <div className="bg-bg-2 border border-border rounded-2xl p-5">
              <p className="font-display font-medium">{vehiculo.nombre}</p>
              <p className="text-[13px] text-text-2 mt-0.5">
                {formatoCorto(new Date(fechaInicio))} – {formatoCorto(new Date(fechaFin))}
              </p>

              {precio && (
                <div className="mt-4 border-t border-border pt-4 space-y-2 text-sm">
                  <div className="flex justify-between text-text-2">
                    <span>{precio.num_dias} días × {precio.precio_dia_base} €</span>
                    <span>{fmt(subtotalVehiculo)} €</span>
                  </div>
                  {extrasElegidos.map(({ extra, subtotal }) => (
                    <div key={extra.id} className="flex justify-between text-text-2">
                      <span className="truncate pr-2">{extra.nombre}</span>
                      <span className="whitespace-nowrap">{fmt(subtotal)} €</span>
                    </div>
                  ))}
                  <div className="flex justify-between text-text-2">
                    <span>Fianza (depósito)</span>
                    <span>{precio.fianza} €</span>
                  </div>
                  <div className="flex justify-between font-medium text-base border-t border-border pt-2 mt-2">
                    <span>Total alquiler</span>
                    <span>{fmt(totalAlquiler)} €</span>
                  </div>
                </div>
              )}
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}

// Campo de formulario reutilizable
function Campo({
  label, value, onChange, type = "text", className = "",
}: {
  label: string; value: string; onChange: (v: string) => void; type?: string; className?: string;
}) {
  return (
    <div className={`flex flex-col gap-1 ${className}`}>
      <label className="text-[13px] font-medium">{label}</label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="h-10 px-3 border border-border-2 rounded-lg text-sm bg-bg-2"
      />
    </div>
  );
}