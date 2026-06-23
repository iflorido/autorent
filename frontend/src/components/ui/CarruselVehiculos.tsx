import { useRef } from "react";
import type { VehiculoList } from "@/types";
import VehiculoCard from "./VehiculoCard";

export default function CarruselVehiculos({ vehiculos, titulo = "Nuestros vehículos" }: { vehiculos: VehiculoList[]; titulo?: string }) {
  const scrollRef = useRef<HTMLDivElement>(null);

  function desplazar(dir: number) {
    if (!scrollRef.current) return;
    const ancho = scrollRef.current.clientWidth;
    scrollRef.current.scrollBy({ left: dir * ancho * 0.8, behavior: "smooth" });
  }

  if (vehiculos.length === 0) return null;

  return (
    <div className="relative">
      <div className="flex items-center justify-between mb-5">
        <h2 className="text-xl font-medium">{titulo}</h2>
        <div className="flex gap-2">
          <button
            onClick={() => desplazar(-1)}
            className="w-9 h-9 rounded-full border border-border-2 flex items-center justify-center hover:bg-surface-2 transition"
            aria-label="Anterior"
          >
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M15 18l-6-6 6-6" />
            </svg>
          </button>
          <button
            onClick={() => desplazar(1)}
            className="w-9 h-9 rounded-full bg-accent text-white flex items-center justify-center hover:opacity-90 transition"
            aria-label="Siguiente"
          >
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 18l6-6-6-6" />
            </svg>
          </button>
        </div>
      </div>

      <div
        ref={scrollRef}
        className="flex gap-4 overflow-x-auto scroll-smooth snap-x snap-mandatory pb-2"
        style={{ scrollbarWidth: "none" }}
      >
        {vehiculos.map((v) => (
          <div key={v.id} className="snap-start shrink-0 w-[calc(33.333%-11px)] min-w-[260px]">
            <VehiculoCard v={v} />
          </div>
        ))}
      </div>
    </div>
  );
}
