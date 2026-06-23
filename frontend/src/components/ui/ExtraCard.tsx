import type { Extra } from "@/types";

export default function ExtraCard({ extra }: { extra: Extra }) {
  return (
    <div className="bg-bg-2 border border-border rounded-2xl p-6 h-full hover:shadow-soft hover:-translate-y-1 transition-all duration-300">
      <div className="flex items-start justify-between gap-3">
        <span className="w-11 h-11 rounded-xl bg-accent-dim flex items-center justify-center text-accent shrink-0">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
            <path d="M12 5v14M5 12h14" />
          </svg>
        </span>
        <span className="text-sm font-medium text-accent whitespace-nowrap">
          {extra.precio} € <span className="text-text-2 font-normal">/ {extra.tipo_cobro === "por_dia" ? "día" : "ud."}</span>
        </span>
      </div>
      <p className="font-display font-medium text-lg mt-3">{extra.nombre}</p>
      {extra.descripcion && (
        <p className="text-[13px] text-text-2 mt-1 leading-relaxed">{extra.descripcion}</p>
      )}
    </div>
  );
}
