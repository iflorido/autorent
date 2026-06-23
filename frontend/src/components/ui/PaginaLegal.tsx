import type { ReactNode } from "react";
import FadeIn from "@/components/ui/FadeIn";
import { useHeroOscuro } from "@/hooks/useHeroOscuro";

interface Props {
  titulo: string;
  actualizado?: string;
  children: ReactNode;
}

/** Layout común de las páginas legales: cabecera oscura + cuerpo de texto. */
export default function PaginaLegal({ titulo, actualizado, children }: Props) {
  useHeroOscuro();
  return (
    <div>
      <div
        className="border-b border-border"
        style={{ background: "linear-gradient(160deg, #0f2433, #0891b2)" }}
      >
        <div className="max-w-container mx-auto px-6 pt-28 pb-10">
          <h1 className="text-white text-3xl md:text-4xl font-medium">{titulo}</h1>
          {actualizado && (
            <p className="text-white/70 mt-2 text-sm">Última actualización: {actualizado}</p>
          )}
        </div>
      </div>

      <section className="max-w-3xl mx-auto px-6 py-12">
        <FadeIn>
          <div className="legal-content space-y-4 text-[15px] text-text-2 leading-relaxed">
            {children}
          </div>
        </FadeIn>
      </section>
    </div>
  );
}
