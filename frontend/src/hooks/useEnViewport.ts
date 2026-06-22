import { useEffect, useRef, useState } from "react";

/**
 * Hook para animaciones de entrada al hacer scroll.
 * Devuelve una ref y un booleano `visible` que pasa a true cuando el
 * elemento entra en el viewport (una sola vez).
 */
export function useEnViewport<T extends HTMLElement = HTMLDivElement>(
  margen = "0px 0px -80px 0px",
) {
  const ref = useRef<T>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          obs.disconnect();
        }
      },
      { rootMargin: margen, threshold: 0.1 },
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, [margen]);

  return { ref, visible };
}
