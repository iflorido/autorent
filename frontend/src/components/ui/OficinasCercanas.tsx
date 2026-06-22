import { Link } from "react-router-dom";
import type { Sede } from "@/types";

export default function OficinasCercanas({ sedes }: { sedes: Sede[] }) {
  if (sedes.length === 0) return null;

  return (
    <div>
      <h2 className="text-2xl font-medium mb-6">Oficinas cercanas</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {sedes.map((s) => (
          <Link
            key={s.id}
            to="/localizaciones"
            className="group flex items-center gap-4 bg-bg-2 border border-border rounded-xl p-5 hover:border-accent transition"
          >
            <span className="shrink-0 w-12 h-12 rounded-lg bg-accent flex items-center justify-center text-white">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                <path d="M21 10c0 7-9 12-9 12s-9-5-9-12a9 9 0 0118 0z" />
                <circle cx="12" cy="10" r="3" />
              </svg>
            </span>
            <div className="flex-1 min-w-0">
              <p className="font-medium">{s.nombre}</p>
              <p className="text-[13px] text-text-2 mt-0.5">
                {s.direccion}
                {s.direccion && (s.poblacion || s.cp) ? <br /> : null}
                {[s.poblacion, s.provincia, s.cp].filter(Boolean).join(", ")}
              </p>
            </div>
            <svg
              width="20" height="20" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" strokeWidth="2"
              className="text-text-2 group-hover:text-accent transition shrink-0"
            >
              <path d="M9 18l6-6-6-6" />
            </svg>
          </Link>
        ))}
      </div>
    </div>
  );
}
