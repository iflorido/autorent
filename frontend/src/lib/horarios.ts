import type { Sede, FranjaHoraria } from "@/types";

const DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"];

/** Día de la semana 0=lunes..6=domingo a partir de una fecha JS. */
export function diaSemanaLunes0(fecha: Date): number {
  return (fecha.getDay() + 6) % 7;
}

/** "HH:MM" o "HH:MM:SS" -> minutos desde medianoche. */
function aMinutos(hhmm: string): number {
  const [h, m] = hhmm.split(":").map(Number);
  return h * 60 + (m || 0);
}

/** ¿La hora ("HH:MM") cae dentro de alguna franja de la sede ese día? */
export function horaDentroDeHorario(sede: Sede, fecha: Date, hora: string): boolean {
  if (!hora) return true; // sin hora elegida, no marcamos nada
  const dia = diaSemanaLunes0(fecha);
  const min = aMinutos(hora);
  const franjas = sede.franjas.filter((f) => f.dia_semana === dia);
  return franjas.some((f) => min >= aMinutos(f.hora_apertura) && min <= aMinutos(f.hora_cierre));
}

/** Texto compacto del horario de una sede, agrupado por día. */
export function horarioPorDia(sede: Sede): { dia: string; franjas: string }[] {
  const porDia: Record<number, FranjaHoraria[]> = {};
  for (const f of sede.franjas) {
    if (!porDia[f.dia_semana]) porDia[f.dia_semana] = [];
    porDia[f.dia_semana].push(f);
  }
  const resultado: { dia: string; franjas: string }[] = [];
  for (let d = 0; d < 7; d++) {
    const fs = (porDia[d] ?? []).sort((a, b) => a.hora_apertura.localeCompare(b.hora_apertura));
    resultado.push({
      dia: DIAS[d],
      franjas: fs.length
        ? fs.map((f) => `${f.hora_apertura.slice(0, 5)}–${f.hora_cierre.slice(0, 5)}`).join(", ")
        : "Cerrado",
    });
  }
  return resultado;
}
