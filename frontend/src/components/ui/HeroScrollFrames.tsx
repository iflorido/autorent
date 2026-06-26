import { useEffect, useRef, useState } from "react";

/**
 * HeroScrollFrames — Hero con animación "scroll-driven".
 *
 * Una secuencia de fotogramas avanza según el scroll. La sección es alta
 * (varias pantallas); mientras se recorre, el lienzo queda anclado (sticky)
 * ocupando la ventana y se va dibujando el frame correspondiente a la posición
 * del scroll. El contenido (children) se muestra encima.
 *
 * Técnica: precarga de imágenes + dibujo en <canvas> + requestAnimationFrame,
 * que es lo más fluido (evita recargar src en cada frame).
 */
interface Props {
  primerFrame: number;        // p.ej. 30
  ultimoFrame: number;        // p.ej. 65
  ruta?: (n: number) => string;  // construye la URL de cada frame
  alturaScroll?: number;      // múltiplo de la altura de ventana que dura la animación
  children?: React.ReactNode; // contenido superpuesto (título, etc.)
}

function rutaPorDefecto(n: number) {
  const num = String(n).padStart(4, "0");
  return `/images/frames/frame_${num}.webp`;
}

export default function HeroScrollFrames({
  primerFrame,
  ultimoFrame,
  ruta = rutaPorDefecto,
  alturaScroll = 3,
  children,
}: Props) {
  const total = ultimoFrame - primerFrame + 1;
  const seccionRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imagenesRef = useRef<HTMLImageElement[]>([]);
  const frameActualRef = useRef<number>(-1);
  const [listo, setListo] = useState(false);

  // Precargar todos los frames.
  useEffect(() => {
    let cargadas = 0;
    const imgs: HTMLImageElement[] = [];
    for (let i = 0; i < total; i++) {
      const img = new Image();
      img.src = ruta(primerFrame + i);
      img.onload = img.onerror = () => {
        cargadas++;
        if (cargadas === total) setListo(true);
      };
      imgs[i] = img;
    }
    imagenesRef.current = imgs;
  }, [primerFrame, total, ruta]);

  // Dibujar un frame concreto en el canvas, cubriendo el lienzo (object-fit: cover).
  function dibujar(indice: number) {
    const canvas = canvasRef.current;
    const img = imagenesRef.current[indice];
    if (!canvas || !img || !img.complete || img.naturalWidth === 0) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const cw = canvas.width;
    const ch = canvas.height;
    const ir = img.naturalWidth / img.naturalHeight;
    const cr = cw / ch;
    let dw = cw, dh = ch, dx = 0, dy = 0;
    if (ir > cr) {
      dh = ch; dw = ch * ir; dx = (cw - dw) / 2;
    } else {
      dw = cw; dh = cw / ir; dy = (ch - dh) / 2;
    }
    ctx.clearRect(0, 0, cw, ch);
    ctx.drawImage(img, dx, dy, dw, dh);
  }

  // Ajustar el tamaño real del canvas a su tamaño en pantalla (nitidez).
  function redimensionar() {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = canvas.clientWidth * dpr;
    canvas.height = canvas.clientHeight * dpr;
    const ctx = canvas.getContext("2d");
    if (ctx) ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    // Forzar redibujado del frame actual.
    if (frameActualRef.current >= 0) dibujar(frameActualRef.current);
  }

  useEffect(() => {
    if (!listo) return;
    redimensionar();
    dibujar(0);
    frameActualRef.current = 0;

    let ticking = false;
    function alScroll() {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => {
        const sec = seccionRef.current;
        if (sec) {
          const rect = sec.getBoundingClientRect();
          const recorrido = sec.offsetHeight - window.innerHeight;
          // Progreso 0..1 según cuánto se ha scrolleado dentro de la sección.
          const progreso = Math.min(1, Math.max(0, -rect.top / recorrido));
          const indice = Math.min(total - 1, Math.round(progreso * (total - 1)));
          if (indice !== frameActualRef.current) {
            frameActualRef.current = indice;
            dibujar(indice);
          }
        }
        ticking = false;
      });
    }

    window.addEventListener("scroll", alScroll, { passive: true });
    window.addEventListener("resize", redimensionar);
    return () => {
      window.removeEventListener("scroll", alScroll);
      window.removeEventListener("resize", redimensionar);
    };
  }, [listo, total]);

  return (
    <section
      ref={seccionRef}
      className="relative"
      style={{ height: `${alturaScroll * 100}vh` }}
    >
      {/* Lienzo anclado que ocupa la ventana mientras dura el scroll. */}
      <div className="sticky top-0 h-screen w-full overflow-hidden" style={{ background: "#0f2433" }}>
        <canvas ref={canvasRef} className="absolute inset-0 w-full h-full" />
        {/* Velo para legibilidad del texto encima. */}
        <div
          className="absolute inset-0"
          style={{ background: "linear-gradient(160deg, rgba(15,36,51,0.30), rgba(8,145,178,0.55))" }}
        />
        {/* Imagen de respaldo mientras precargan los frames. */}
        {!listo && (
          <div
            className="absolute inset-0 bg-cover bg-center"
            style={{ backgroundImage: "url('/images/hero.jpg')" }}
          />
        )}
        {/* Contenido superpuesto (título, etc.) */}
        <div className="relative h-full flex items-center">
          <div className="max-w-container mx-auto px-6 w-full">{children}</div>
        </div>
      </div>
    </section>
  );
}
