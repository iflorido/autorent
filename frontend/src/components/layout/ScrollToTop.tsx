import { useEffect } from "react";
import { useLocation } from "react-router-dom";

/**
 * Sube la página al inicio cuando cambia la RUTA (pathname).
 * Reacciona solo al pathname, no a la query string, para no saltar
 * arriba al cambiar filtros en la misma página (p. ej. /modelos?categoria=...).
 */
export default function ScrollToTop() {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo({ top: 0, left: 0, behavior: "auto" });
  }, [pathname]);

  return null;
}
