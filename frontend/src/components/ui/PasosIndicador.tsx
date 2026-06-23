interface Props {
  pasos: string[];
  actual: number; // índice 0-based del paso activo
}

export default function PasosIndicador({ pasos, actual }: Props) {
  return (
    <div className="flex items-center gap-2">
      {pasos.map((p, i) => {
        const completado = i < actual;
        const activo = i === actual;
        return (
          <div key={p} className="flex items-center gap-2 flex-1">
            <div className="flex items-center gap-2">
              <span
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium shrink-0 transition ${
                  completado
                    ? "bg-accent text-white"
                    : activo
                    ? "bg-accent text-white"
                    : "bg-surface-2 text-text-2"
                }`}
              >
                {completado ? (
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                    <path d="M20 6L9 17l-5-5" />
                  </svg>
                ) : (
                  i + 1
                )}
              </span>
              <span className={`text-[13px] hidden sm:block ${activo ? "font-medium text-text" : "text-text-2"}`}>
                {p}
              </span>
            </div>
            {i < pasos.length - 1 && (
              <div className={`flex-1 h-px ${completado ? "bg-accent" : "bg-border"}`} />
            )}
          </div>
        );
      })}
    </div>
  );
}
