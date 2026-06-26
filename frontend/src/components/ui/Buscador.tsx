import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import CalendarioRango from "./CalendarioRango";
import { getSedes } from "@/lib/api";
import type { Sede } from "@/types";
import { formatoRango, toISODate } from "@/lib/fechas";

export default function Buscador() {
  const navigate = useNavigate();
  const [sedes, setSedes] = useState<Sede[]>([]);
  const [sedeRecogida, setSedeRecogida] = useState<number | "">("");
  const [sedeEntrega, setSedeEntrega] = useState<number | "">("");
  const [inicio, setInicio] = useState<Date | null>(null);
  const [fin, setFin] = useState<Date | null>(null);
  const [calOpen, setCalOpen] = useState(false);
  const calRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getSedes().then((s) => {
      setSedes(s);
      if (s.length > 0) {
        setSedeRecogida(s[0].id);
        setSedeEntrega(s[0].id);
      }
    });
  }, []);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (calRef.current && !calRef.current.contains(e.target as Node)) {
        setCalOpen(false);
      }
    }
    if (calOpen) document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [calOpen]);

  function buscar() {
    const params = new URLSearchParams();
    if (sedeRecogida) params.set("sede", String(sedeRecogida));
    if (sedeEntrega) params.set("sede_entrega", String(sedeEntrega));
    if (inicio) params.set("fecha_inicio", toISODate(inicio));
    if (fin) params.set("fecha_fin", toISODate(fin));
    navigate(`/modelos?${params.toString()}`);
  }

  return (
    <div className={`relative ${calOpen ? "z-[999]" : ""}`}>
      <div className="bg-bg-2 rounded-xl shadow-soft p-4 grid grid-cols-1 md:grid-cols-[1fr_1fr_1fr_auto] gap-3 items-end">
        {/* Recogida */}
        <div className="flex flex-col gap-1">
          <label className="text-[11px] uppercase tracking-wide text-text-2 font-medium">Recogida</label>
          <select
            value={sedeRecogida}
            onChange={(e) => setSedeRecogida(e.target.value ? Number(e.target.value) : "")}
            className="h-10 px-3 border border-border-2 rounded-lg text-sm bg-bg-2"
          >
            {sedes.length === 0 && <option>Cargando…</option>}
            {sedes.map((s) => (
              <option key={s.id} value={s.id}>{s.nombre}</option>
            ))}
          </select>
        </div>

        {/* Entrega: ahora funcional con su propio desplegable */}
        <div className="flex flex-col gap-1">
          <label className="text-[11px] uppercase tracking-wide text-text-2 font-medium">Entrega</label>
          <select
            value={sedeEntrega}
            onChange={(e) => setSedeEntrega(e.target.value ? Number(e.target.value) : "")}
            className="h-10 px-3 border border-border-2 rounded-lg text-sm bg-bg-2"
          >
            {sedes.length === 0 && <option>Cargando…</option>}
            {sedes.map((s) => (
              <option key={s.id} value={s.id}>{s.nombre}</option>
            ))}
          </select>
        </div>

        {/* Fechas */}
        <div className="flex flex-col gap-1">
          <label className="text-[11px] uppercase tracking-wide text-text-2 font-medium">Cuándo</label>
          <button
            onClick={() => setCalOpen((v) => !v)}
            className="h-10 px-3 border border-border-2 rounded-lg text-sm flex items-center gap-2 text-left bg-bg-2"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="text-accent">
              <rect x="3" y="4" width="18" height="18" rx="2" />
              <path d="M16 2v4M8 2v4M3 10h18" />
            </svg>
            <span className={inicio ? "text-text" : "text-text-2"}>
              {formatoRango(inicio, fin)}
            </span>
          </button>
        </div>

        {/* Botón buscar */}
        <button
          onClick={buscar}
          className="h-10 px-5 bg-accent text-white rounded-lg text-sm font-medium flex items-center gap-2 justify-center hover:opacity-90 transition"
        >
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="7" /><path d="M21 21l-4-4" />
          </svg>
          Buscar
        </button>
      </div>

      {/* Calendario: centrado, ancho, z-index alto, por encima de todo */}
      {calOpen && (
        <div
          ref={calRef}
          className="absolute left-1/2 -translate-x-1/2 top-full mt-3 w-full max-w-[720px] z-[999]"
        >
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
  );
}
