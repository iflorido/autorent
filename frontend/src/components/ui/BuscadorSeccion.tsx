import Buscador from "./Buscador";

interface Props {
  titulo: string;
  subtitulo?: string;
}

/**
 * Cabecera de sección con el buscador integrado.
 * Se usa en Modelos, Extras, Tarifas, Localizaciones y FAQ para que el
 * usuario nunca pierda la opción de buscar.
 */
export default function BuscadorSeccion({ titulo, subtitulo }: Props) {
  return (
    <div
      className="border-b border-border"
      style={{ background: "linear-gradient(160deg, #0f2433, #0891b2)" }}
    >
      <div className="max-w-container mx-auto px-6 pt-28 pb-8">
        <h1 className="text-white text-3xl md:text-4xl font-medium">{titulo}</h1>
        {subtitulo && <p className="text-white/80 mt-2 max-w-xl">{subtitulo}</p>}
        <div className="mt-6">
          <Buscador />
        </div>
      </div>
    </div>
  );
}
