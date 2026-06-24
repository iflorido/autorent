import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import {
  getInfoSubida, subirDocumentoToken, finalizarSubida, type InfoSubida,
} from "@/lib/api";

const MAX_MB = 10;
const FORMATOS = ["image/jpeg", "image/png", "image/webp", "application/pdf"];

// Documentos requeridos por persona.
const DOCS_TITULAR = [
  { tipo: "dni_anverso", label: "DNI / NIE (anverso)" },
  { tipo: "dni_reverso", label: "DNI / NIE (reverso)" },
  { tipo: "carnet", label: "Carnet de conducir" },
];

interface Persona {
  conductorId: number | null;
  nombre: string;
  rol: string;
}

export default function SubirDocumentos() {
  const { token } = useParams();
  const [info, setInfo] = useState<InfoSubida | null>(null);
  const [cargando, setCargando] = useState(true);
  const [errorCarga, setErrorCarga] = useState<string | null>(null);

  const [personas, setPersonas] = useState<Persona[]>([]);
  const [pasoActual, setPasoActual] = useState(0);
  const [subidos, setSubidos] = useState<Record<string, "ok" | "subiendo" | "error">>({});
  const [errores, setErrores] = useState<Record<string, string>>({});
  const [finalizado, setFinalizado] = useState(false);
  const [enviandoFinal, setEnviandoFinal] = useState(false);

  useEffect(() => {
    if (!token) return;
    getInfoSubida(token)
      .then((d) => {
        setInfo(d);
        const lista: Persona[] = [
          { conductorId: null, nombre: d.titular, rol: "Conductor titular" },
          ...d.conductores_adicionales.map((c) => ({
            conductorId: c.id, nombre: c.nombre_completo, rol: "Conductor adicional",
          })),
        ];
        setPersonas(lista);
        // Marcar ya-subidos.
        const yaSub: Record<string, "ok"> = {};
        d.documentos_subidos.forEach((doc) => {
          yaSub[`${doc.conductor_id ?? "tit"}_${doc.tipo}`] = "ok";
        });
        setSubidos(yaSub);
      })
      .catch((e) => {
        const err = e as { response?: { data?: { detail?: string; estado?: string } } };
        setErrorCarga(err.response?.data?.detail ?? "No se pudo abrir el enlace.");
      })
      .finally(() => setCargando(false));
  }, [token]);

  function clave(p: Persona, tipo: string) {
    return `${p.conductorId ?? "tit"}_${tipo}`;
  }

  async function manejarArchivo(p: Persona, tipo: string, file: File | null) {
    if (!file || !token) return;
    const k = clave(p, tipo);
    setErrores((e) => ({ ...e, [k]: "" }));
    if (file.size > MAX_MB * 1024 * 1024) {
      setErrores((e) => ({ ...e, [k]: `Supera los ${MAX_MB} MB.` }));
      return;
    }
    if (file.type && !FORMATOS.includes(file.type)) {
      setErrores((e) => ({ ...e, [k]: "Formato no válido (JPG, PNG, WEBP o PDF)." }));
      return;
    }
    setSubidos((s) => ({ ...s, [k]: "subiendo" }));
    try {
      await subirDocumentoToken(token, tipo, file, p.conductorId);
      setSubidos((s) => ({ ...s, [k]: "ok" }));
    } catch (e) {
      const err = e as { response?: { data?: { detail?: string } } };
      setSubidos((s) => ({ ...s, [k]: "error" }));
      setErrores((er) => ({ ...er, [k]: err.response?.data?.detail ?? "No se pudo subir." }));
    }
  }

  const personaActual = personas[pasoActual];
  const docsCompletos = (p: Persona) => DOCS_TITULAR.every((d) => subidos[clave(p, d.tipo)] === "ok");
  const todoCompleto = personas.every((p) => docsCompletos(p));

  async function finalizar() {
    if (!token) return;
    setEnviandoFinal(true);
    try {
      await finalizarSubida(token);
      setFinalizado(true);
    } catch {
      setEnviandoFinal(false);
    }
  }

  if (cargando) {
    return <div className="pt-28 max-w-container mx-auto px-6 py-20 text-text-2 text-center">Cargando…</div>;
  }

  if (errorCarga) {
    return (
      <div className="pt-28 max-w-md mx-auto px-6 py-20 text-center">
        <span className="w-14 h-14 rounded-full bg-red-50 text-red-500 flex items-center justify-center mx-auto mb-4">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10" /><path d="M12 8v4M12 16h.01" /></svg>
        </span>
        <h1 className="text-xl font-medium">Enlace no disponible</h1>
        <p className="text-text-2 mt-2">{errorCarga}</p>
        <p className="text-[13px] text-text-2 mt-4">
          Si tu documentación fue rechazada, revisa tu correo: te habremos enviado un enlace nuevo.
          Para cualquier duda, contacta con nosotros.
        </p>
      </div>
    );
  }

  if (finalizado) {
    return (
      <div className="pt-28 max-w-md mx-auto px-6 py-20 text-center">
        <span className="w-16 h-16 rounded-full bg-accent-dim text-accent flex items-center justify-center mx-auto mb-4">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M20 6L9 17l-5-5" /></svg>
        </span>
        <h1 className="text-xl font-medium">¡Documentación enviada!</h1>
        <p className="text-text-2 mt-2">
          Hemos recibido tus documentos. Nuestro equipo los revisará y te confirmaremos la reserva.
          Si hubiera algún problema, te avisaremos por correo.
        </p>
      </div>
    );
  }

  return (
    <div className="pt-20">
      <div className="max-w-2xl mx-auto px-6 py-8">
        <h1 className="text-2xl font-medium">Sube tu documentación</h1>
        <p className="text-text-2 mt-1">
          Reserva <strong>{info?.localizador}</strong> · {info?.vehiculo}
        </p>

        {/* Progreso de personas */}
        <div className="flex items-center gap-2 mt-6 mb-8 flex-wrap">
          {personas.map((p, i) => (
            <button
              key={i}
              onClick={() => setPasoActual(i)}
              className={`text-[13px] px-3 py-1.5 rounded-full border transition ${
                i === pasoActual
                  ? "border-accent bg-accent text-white"
                  : docsCompletos(p)
                  ? "border-accent text-accent"
                  : "border-border text-text-2"
              }`}
            >
              {docsCompletos(p) && i !== pasoActual ? "✓ " : ""}{p.nombre}
            </button>
          ))}
        </div>

        {personaActual && (
          <div className="bg-bg-2 border border-border rounded-2xl p-6">
            <p className="text-[13px] text-accent font-medium">{personaActual.rol}</p>
            <h2 className="text-lg font-medium mb-1">{personaActual.nombre}</h2>
            <p className="text-[13px] text-text-2 mb-5">Sube los tres documentos en JPG, PNG, WEBP o PDF (máx. {MAX_MB} MB).</p>

            <div className="space-y-3">
              {DOCS_TITULAR.map((d) => {
                const k = clave(personaActual, d.tipo);
                const estado = subidos[k];
                return (
                  <div key={d.tipo} className="flex items-center gap-3 bg-bg border border-border rounded-xl p-4">
                    <span className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 ${
                      estado === "ok" ? "bg-accent text-white" : "bg-accent-dim text-accent"
                    }`}>
                      {estado === "ok" ? (
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M20 6L9 17l-5-5" /></svg>
                      ) : (
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" /><path d="M14 2v6h6" /></svg>
                      )}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium">{d.label}</p>
                      {estado === "ok" && <p className="text-[12px] text-accent">Subido correctamente</p>}
                      {estado === "subiendo" && <p className="text-[12px] text-text-2">Subiendo…</p>}
                      {errores[k] && <p className="text-[12px] text-red-600">{errores[k]}</p>}
                    </div>
                    <label className="shrink-0 text-[13px] px-3 py-2 border border-border-2 rounded-lg cursor-pointer hover:bg-surface-2 transition">
                      {estado === "ok" ? "Cambiar" : "Subir"}
                      <input type="file" accept=".jpg,.jpeg,.png,.webp,.pdf" className="hidden"
                        onChange={(e) => manejarArchivo(personaActual, d.tipo, e.target.files?.[0] ?? null)} />
                    </label>
                  </div>
                );
              })}
            </div>

            <div className="flex justify-between mt-6">
              <button
                onClick={() => setPasoActual((p) => Math.max(0, p - 1))}
                disabled={pasoActual === 0}
                className="h-10 px-4 border border-border-2 rounded-lg text-sm disabled:opacity-40"
              >
                Anterior
              </button>
              {pasoActual < personas.length - 1 ? (
                <button
                  onClick={() => setPasoActual((p) => p + 1)}
                  className="h-10 px-5 bg-accent text-white rounded-lg text-sm font-medium hover:opacity-90"
                >
                  Siguiente persona
                </button>
              ) : (
                <button
                  onClick={finalizar}
                  disabled={!todoCompleto || enviandoFinal}
                  className="h-10 px-5 bg-accent text-white rounded-lg text-sm font-medium hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  {enviandoFinal ? "Enviando…" : "Finalizar envío"}
                </button>
              )}
            </div>
            {pasoActual === personas.length - 1 && !todoCompleto && (
              <p className="text-[12px] text-text-2 text-right mt-2">
                Sube todos los documentos de cada persona para finalizar.
              </p>
            )}
          </div>
        )}

        <p className="text-[12px] text-text-2 mt-4 text-center">
          🔒 Tus documentos se almacenan de forma segura y solo son accesibles por nuestro personal autorizado.
          Este enlace es personal y caduca a los 7 días.
        </p>
      </div>
    </div>
  );
}
