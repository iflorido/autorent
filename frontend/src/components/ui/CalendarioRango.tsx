import { useState } from "react";
import {
  DIAS_SEMANA,
  MESES,
  diasDelMes,
  entreFechas,
  hoy,
  mismaFecha,
} from "@/lib/fechas";

interface Props {
  inicio: Date | null;
  fin: Date | null;
  onChange: (inicio: Date | null, fin: Date | null) => void;
}

export default function CalendarioRango({ inicio, fin, onChange }: Props) {
  const ahora = hoy();
  const [mesBase, setMesBase] = useState(() => new Date(ahora.getFullYear(), ahora.getMonth(), 1));

  function seleccionar(dia: Date) {
    // Primer clic, o reinicio si ya había un rango completo: nuevo inicio.
    if (!inicio || (inicio && fin)) {
      onChange(dia, null);
      return;
    }
    // Segundo clic: si es anterior al inicio, lo tomamos como nuevo inicio.
    if (dia <= inicio) {
      onChange(dia, null);
      return;
    }
    onChange(inicio, dia);
  }

  function mesSiguiente(base: Date, suma: number) {
    return new Date(base.getFullYear(), base.getMonth() + suma, 1);
  }

  function pintarMes(base: Date) {
    const celdas = diasDelMes(base.getFullYear(), base.getMonth());
    return (
      <div className="flex-1">
        <div className="text-center font-medium mb-3">
          {MESES[base.getMonth()]} {base.getFullYear()}
        </div>
        <div className="grid grid-cols-7 gap-y-1 text-center">
          {DIAS_SEMANA.map((d) => (
            <div key={d} className="text-[11px] text-text-2 font-medium py-1">{d}</div>
          ))}
          {celdas.map((dia, i) => {
            if (!dia) return <div key={i} />;
            const pasado = dia < ahora;
            const esInicio = mismaFecha(dia, inicio);
            const esFin = mismaFecha(dia, fin);
            const enRango = entreFechas(new Date(dia), inicio, fin);
            const seleccionado = esInicio || esFin;

            return (
              <button
                key={i}
                disabled={pasado}
                onClick={() => seleccionar(dia)}
                className={[
                  "h-9 text-sm rounded-lg transition mx-auto w-9 flex items-center justify-center",
                  pasado ? "text-text-2/40 cursor-not-allowed" : "hover:bg-accent-dim",
                  seleccionado ? "bg-accent text-white hover:bg-accent" : "",
                  enRango ? "bg-accent-dim" : "",
                ].join(" ")}
              >
                {dia.getDate()}
              </button>
            );
          })}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-bg-2 border border-border rounded-xl p-5 shadow-soft">
      <div className="flex items-center justify-between mb-1">
        <button
          onClick={() => setMesBase(mesSiguiente(mesBase, -1))}
          disabled={mesBase <= new Date(ahora.getFullYear(), ahora.getMonth(), 1)}
          className="w-8 h-8 rounded-full hover:bg-surface-2 flex items-center justify-center disabled:opacity-30 disabled:cursor-not-allowed"
          aria-label="Mes anterior"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M15 18l-6-6 6-6" />
          </svg>
        </button>
        <button
          onClick={() => setMesBase(mesSiguiente(mesBase, 1))}
          className="w-8 h-8 rounded-full hover:bg-surface-2 flex items-center justify-center"
          aria-label="Mes siguiente"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M9 18l6-6-6-6" />
          </svg>
        </button>
      </div>
      <div className="flex gap-8">
        {pintarMes(mesBase)}
        {pintarMes(mesSiguiente(mesBase, 1))}
      </div>
    </div>
  );
}
