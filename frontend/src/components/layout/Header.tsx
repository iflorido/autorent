import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useHero } from "@/hooks/useHero";

const CATEGORIAS = [
  { slug: "turismo", label: "Turismo", icon: "M3 13l2-5h14l2 5M5 13h14v4H5z" },
  { slug: "industrial", label: "Industrial", icon: "M3 17h13V7H3zM16 10h4l1 3v4h-5z" },
  { slug: "camper", label: "Camper", icon: "M3 13h18v4H3zM5 13V8h11l3 5" },
  { slug: "todos", label: "Todos los modelos", icon: "M4 6h16M4 12h16M4 18h16" },
];

const ENLACES = [
  { to: "/localizaciones", label: "Localizaciones" },
  { to: "/tarifas", label: "Tarifas" },
  { to: "/extras", label: "Extras" },
  { to: "/faq", label: "Preguntas frecuentes" },
];

export default function Header() {
  const { tieneHeroOscuro } = useHero();
  const [megaOpen, setMegaOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  // El header es transparente solo si la página tiene hero oscuro detrás.
  const tieneHero = tieneHeroOscuro;

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Sólido si: no hay hero, o se ha hecho scroll, o el megamenú está abierto.
  const solido = !tieneHero || scrolled || megaOpen;

  return (
    <header
      className="fixed top-0 inset-x-0 z-[900] transition-colors duration-300"
      style={{
        background: solido ? "var(--bg-2)" : "transparent",
        borderBottom: solido ? "1px solid var(--border)" : "1px solid transparent",
        boxShadow: solido ? "0 1px 12px rgba(15,23,42,0.05)" : "none",
      }}
    >
      <div className="max-w-container mx-auto px-6 h-16 flex items-center gap-8">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 shrink-0">
          <span className="inline-flex w-8 h-8 rounded-lg bg-accent items-center justify-center text-white font-medium">
            A
          </span>
          <span
            className="font-display text-lg font-medium tracking-tight transition-colors"
            style={{ color: solido ? "var(--text)" : "#fff" }}
          >
            AutoRent
          </span>
        </Link>

        {/* Navegación a la izquierda, junto al logo */}
        <nav
          className="flex items-center gap-6 text-sm transition-colors"
          style={{ color: solido ? "var(--text)" : "rgba(255,255,255,0.92)" }}
        >
          <div
            className="relative"
            onMouseEnter={() => setMegaOpen(true)}
            onMouseLeave={() => setMegaOpen(false)}
          >
            {/* Botón Alquilar: sin fondo hover, solo cambia color de texto */}
            <button
              className="flex items-center gap-1.5 py-5 bg-transparent transition-colors"
              style={{ color: solido ? "var(--accent)" : "#fff" }}
            >
              Alquilar
              <svg
                width="14" height="14" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" strokeWidth="2"
                className="transition-transform duration-200"
                style={{ transform: megaOpen ? "rotate(180deg)" : "none" }}
              >
                <path d="M6 9l6 6 6-6" />
              </svg>
            </button>

            {megaOpen && (
              <div className="absolute left-0 top-full w-[560px] bg-bg-2 border border-border rounded-xl shadow-soft p-5 grid grid-cols-2 gap-6 text-text">
                <div className="grid grid-cols-2 gap-2.5">
                  {CATEGORIAS.map((c) => (
                    <Link
                      key={c.slug}
                      to={`/modelos${c.slug !== "todos" ? `?categoria=${c.slug}` : ""}`}
                      onClick={() => setMegaOpen(false)}
                      className={`flex items-center gap-2.5 px-3 py-2.5 rounded-lg transition ${
                        c.slug === "todos"
                          ? "bg-accent text-white"
                          : "bg-accent-dim text-text hover:bg-surface-2"
                      }`}
                    >
                      <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                        <path d={c.icon} />
                      </svg>
                      <span className="text-[13px]">{c.label}</span>
                    </Link>
                  ))}
                </div>
                <div className="flex flex-col gap-2 border-l border-border pl-6">
                  {ENLACES.map((e) => (
                    <Link
                      key={e.to}
                      to={e.to}
                      onClick={() => setMegaOpen(false)}
                      className="text-[13px] text-text hover:text-accent transition"
                    >
                      {e.label}
                    </Link>
                  ))}
                </div>
              </div>
            )}
          </div>

          <Link to="/modelos" className="hover:text-accent transition" style={{ color: "inherit" }}>Modelos</Link>
          <Link to="/reservas" className="hover:text-accent transition" style={{ color: "inherit" }}>Reservas</Link>
          <Link to="/contacto" className="hover:text-accent transition" style={{ color: "inherit" }}>Contacto</Link>
        </nav>

        {/* Iconos usuario / admin a la derecha */}
        <div className="ml-auto flex items-center gap-2">
          <Link
            to="/reservas"
            title="Mi cuenta"
            className="w-9 h-9 rounded-full flex items-center justify-center transition"
            style={{
              color: solido ? "var(--text)" : "#fff",
              background: solido ? "var(--surface-2)" : "rgba(255,255,255,0.15)",
            }}
          >
            <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
              <circle cx="12" cy="8" r="4" /><path d="M4 21c0-4 4-6 8-6s8 2 8 6" />
            </svg>
          </Link>
          <a
            href="/admin/"
            title="Administración"
            className="w-9 h-9 rounded-full flex items-center justify-center transition"
            style={{
              color: solido ? "var(--text)" : "#fff",
              background: solido ? "var(--surface-2)" : "rgba(255,255,255,0.15)",
            }}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
              <path d="M12 15a3 3 0 100-6 3 3 0 000 6z" />
              <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 11-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 11-2.83-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 112.83-2.83l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 112.83 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z" />
            </svg>
          </a>
        </div>
      </div>
    </header>
  );
}
