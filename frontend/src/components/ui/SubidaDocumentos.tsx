import { useState } from "react";
import { subirDocumento } from "@/lib/api";

interface Props {
  localizador: string;
}

const TIPOS = [
  { tipo: "dni_anverso", label: "DNI / NIE (anverso)" },
  { tipo: "dni_reverso", label: "DNI / NIE (reverso)" },
  { tipo: "carnet", label: "Carnet de conducir" },
];

const MAX_MB = 10;
const FORMATOS = ["image/jpeg", "image/png", "image/webp", "application/pdf"];

export default function SubidaDocumentos({ localizador }: Props) {
  const [estados, setEstados] = useState<Record<string, "idle" | "subiendo" | "ok" | "error">>({});
  const [errores, setErrores] = useState<Record<string, string>>({});

  async function manejarArchivo(tipo: string, file: File | null) {
    if (!file) return;
    setErrores((e) => ({ ...e, [tipo]: "" }));

    if (file.size > MAX_MB * 1024 * 1024) {
      setErrores((e) => ({ ...e, [tipo]: `El archivo supera los ${MAX_MB} MB.` }));
      return;
    }
    if (file.type && !FORMATOS.includes(file.type)) {
      setErrores((e) => ({ ...e, [tipo]: "Formato no válido (usa JPG, PNG, WEBP o PDF)." }));
      return;
    }

    setEstados((s) => ({ ...s, [tipo]: "subiendo" }));
    try {
      await subirDocumento(localizador, tipo, file);
      setEstados((s) => ({ ...s, [tipo]: "ok" }));
    } catch {
      setEstados((s) => ({ ...s, [tipo]: "error" }));
      setErrores((e) => ({ ...e, [tipo]: "No se pudo subir. Inténtalo de nuevo." }));
    }
  }

  return (
    <div className="space-y-3">
      {TIPOS.map((t) => {
        const estado = estados[t.tipo] ?? "idle";
        return (
          <div key={t.tipo} className="flex items-center gap-3 bg-bg border border-border rounded-xl p-4">
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
              <p className="text-sm font-medium">{t.label}</p>
              {estado === "ok" && <p className="text-[12px] text-accent">Subido correctamente</p>}
              {estado === "subiendo" && <p className="text-[12px] text-text-2">Subiendo…</p>}
              {errores[t.tipo] && <p className="text-[12px] text-red-600">{errores[t.tipo]}</p>}
              {estado === "idle" && !errores[t.tipo] && (
                <p className="text-[12px] text-text-2">JPG, PNG, WEBP o PDF (máx. {MAX_MB} MB)</p>
              )}
            </div>
            <label className="shrink-0 text-[13px] px-3 py-2 border border-border-2 rounded-lg cursor-pointer hover:bg-surface-2 transition">
              {estado === "ok" ? "Cambiar" : "Subir"}
              <input
                type="file"
                accept=".jpg,.jpeg,.png,.webp,.pdf"
                className="hidden"
                onChange={(e) => manejarArchivo(t.tipo, e.target.files?.[0] ?? null)}
              />
            </label>
          </div>
        );
      })}
    </div>
  );
}
