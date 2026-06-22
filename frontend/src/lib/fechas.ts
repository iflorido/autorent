// Utilidades de fecha para el buscador y el calendario.

export const MESES = [
  "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
  "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
];

export const DIAS_SEMANA = ["LU", "MA", "MI", "JU", "VI", "SÁ", "DO"];

/** Devuelve una fecha en formato YYYY-MM-DD (para la API). */
export function toISODate(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

/** Formato legible: "22 jul 2026". */
export function formatoCorto(d: Date): string {
  const mesesCortos = [
    "ene", "feb", "mar", "abr", "may", "jun",
    "jul", "ago", "sep", "oct", "nov", "dic",
  ];
  return `${d.getDate()} ${mesesCortos[d.getMonth()]} ${d.getFullYear()}`;
}

/** Formato de rango: "22 – 25 jul 2026" o con meses distintos. */
export function formatoRango(inicio: Date | null, fin: Date | null): string {
  if (!inicio) return "Añadir fechas";
  if (!fin) return formatoCorto(inicio);
  return `${formatoCorto(inicio)} – ${formatoCorto(fin)}`;
}

/** Días de un mes para pintar la cuadrícula (lunes primero). */
export function diasDelMes(anio: number, mes: number): (Date | null)[] {
  const primero = new Date(anio, mes, 1);
  // getDay(): 0=domingo..6=sábado. Convertimos a lunes=0.
  const offset = (primero.getDay() + 6) % 7;
  const ultimoDia = new Date(anio, mes + 1, 0).getDate();

  const celdas: (Date | null)[] = [];
  for (let i = 0; i < offset; i++) celdas.push(null);
  for (let d = 1; d <= ultimoDia; d++) celdas.push(new Date(anio, mes, d));
  return celdas;
}

/** Compara solo año/mes/día (ignora hora). */
export function mismaFecha(a: Date | null, b: Date | null): boolean {
  if (!a || !b) return false;
  return (
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate()
  );
}

/** True si d está entre inicio y fin (exclusivo en extremos). */
export function entreFechas(d: Date, inicio: Date | null, fin: Date | null): boolean {
  if (!inicio || !fin) return false;
  const t = d.setHours(0, 0, 0, 0);
  return t > inicio.setHours(0, 0, 0, 0) && t < fin.setHours(0, 0, 0, 0);
}

/** Fecha de hoy a medianoche (para deshabilitar días pasados). */
export function hoy(): Date {
  const d = new Date();
  d.setHours(0, 0, 0, 0);
  return d;
}
