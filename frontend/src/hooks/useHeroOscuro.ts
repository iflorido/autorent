import { useEffect } from "react";
import { useHero } from "./useHero";

/** Marca la página como con hero oscuro (header transparente) mientras vive. */
export function useHeroOscuro(activo = true) {
  const { setHeroOscuro } = useHero();
  useEffect(() => {
    setHeroOscuro(activo);
    return () => setHeroOscuro(false);
  }, [activo, setHeroOscuro]);
}
