import type { ReactNode } from "react";
import { useEnViewport } from "@/hooks/useEnViewport";

interface Props {
  children: ReactNode;
  delay?: number; // ms
  className?: string;
}

/** Envuelve contenido para que entre con fade + desplazamiento al hacer scroll. */
export default function FadeIn({ children, delay = 0, className = "" }: Props) {
  const { ref, visible } = useEnViewport();
  return (
    <div
      ref={ref}
      className={className}
      style={{
        opacity: visible ? 1 : 0,
        transform: visible ? "translateY(0)" : "translateY(24px)",
        transition: `opacity 0.6s ease ${delay}ms, transform 0.6s ease ${delay}ms`,
      }}
    >
      {children}
    </div>
  );
}
