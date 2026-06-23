import { useEffect } from "react";
import { api } from "@/lib/api";

interface FrontendConfig {
  tokens: Record<string, string>;
  fuentes_google: string[];
  font_display: string;
  font_body: string;
}

/**
 * Lee /api/frontend-config/ al arrancar y aplica:
 *   - los tokens de color/fuente como variables CSS en :root
 *   - las fuentes de Google necesarias (inyecta el <link>)
 *
 * Si el endpoint falla, se mantienen los valores por defecto del CSS,
 * así que la web nunca se queda sin estilos.
 */
export function useFrontendConfig() {
  useEffect(() => {
    let cancelado = false;

    api
      .get<FrontendConfig>("/frontend-config/")
      .then(({ data }) => {
        if (cancelado) return;

        // 1) Aplicar tokens como variables CSS.
        const root = document.documentElement;
        Object.entries(data.tokens).forEach(([clave, valor]) => {
          root.style.setProperty(clave, valor);
        });

        // 2) Cargar las fuentes de Google necesarias.
        if (data.fuentes_google?.length) {
          const familias = data.fuentes_google
            .map((f) => `family=${f.replace(/ /g, "+")}:wght@400;500;600;700`)
            .join("&");
          const href = `https://fonts.googleapis.com/css2?${familias}&display=swap`;

          // Evitar duplicar el link si ya existe.
          const existente = document.getElementById("ar-google-fonts");
          if (existente) existente.setAttribute("href", href);
          else {
            const link = document.createElement("link");
            link.id = "ar-google-fonts";
            link.rel = "stylesheet";
            link.href = href;
            document.head.appendChild(link);
          }
        }
      })
      .catch(() => {
        // Silencioso: se mantienen los defaults del CSS.
      });

    return () => {
      cancelado = true;
    };
  }, []);
}
