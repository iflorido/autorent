import { Link } from "react-router-dom";
import type { VehiculoList } from "@/types";

interface Props {
  v: VehiculoList;
  fechaInicio?: string;
  fechaFin?: string;
}

export default function VehiculoCard({ v, fechaInicio, fechaFin }: Props) {
  // Propaga las fechas seleccionadas a la ficha del vehículo.
  const query = new URLSearchParams();
  if (fechaInicio) query.set("fecha_inicio", fechaInicio);
  if (fechaFin) query.set("fecha_fin", fechaFin);
  const qs = query.toString();
  const to = `/vehiculo/${v.slug}${qs ? `?${qs}` : ""}`;

  return (
    <div className="bg-bg-2 border border-border rounded-xl overflow-hidden flex flex-col group">
      <div className="h-44 bg-accent-dim flex items-center justify-center overflow-hidden">
        {v.foto_principal ? (
          <img
            src={v.foto_principal}
            alt={v.nombre}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
        ) : (
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-accent">
            <path d="M3 13h18v4H3zM5 13V8h11l3 5" />
          </svg>
        )}
      </div>
      <div className="p-4 flex flex-col flex-1">
        <p className="font-display font-medium text-[15px]">{v.nombre}</p>
        <p className="text-[13px] text-text-2 mt-0.5">
          {v.categoria_display} · {v.plazas} plazas
        </p>
        {v.precio_desde && (
          <p className="text-sm mt-2 mb-3">
            <span className="font-medium text-accent">desde {v.precio_desde} €</span> / día
          </p>
        )}
        <div className="flex gap-2 mt-auto pt-2">
          <Link
            to={to}
            className="flex-1 text-center text-[13px] py-2 border border-border-2 rounded-lg hover:bg-surface-2 transition"
          >
            Más información
          </Link>
          <Link
            to={to}
            className="flex-1 text-center text-[13px] py-2 rounded-lg bg-accent text-white hover:opacity-90 transition"
          >
            Reservar
          </Link>
        </div>
      </div>
    </div>
  );
}
