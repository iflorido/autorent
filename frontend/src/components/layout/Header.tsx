import { useState } from "react";
import { Link } from "react-router-dom";

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
  const [megaOpen, setMegaOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 bg-bg-2 border-b border-border">
      <div className="max-w-container mx-auto px-6 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <span className="inline-flex w-8 h-8 rounded-lg bg-accent items-center justify-center text-white font-medium">
            A
          </span>
          <span className="text-lg font-medium tracking-tight">AutoRent</span>
        </Link>

        <nav className="flex items-center gap-7 text-sm">
          <div
            className="relative"
            onMouseEnter={() => setMegaOpen(true)}
            onMouseLeave={() => setMegaOpen(false)}
          >
            <button className="flex items-center gap-1.5 text-accent py-5">
              Alquilar
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M6 9l6 6 6-6" />
              </svg>
            </button>

            {megaOpen && (
              <div className="absolute left-0 top-full w-[560px] bg-bg-2 border border-border rounded-xl shadow-soft p-5 grid grid-cols-2 gap-6">
                <div className="grid grid-cols-2 gap-2.5">
                  {CATEGORIAS.map((c) => (
                    <Link
                      key={c.slug}
                      to={`/modelos${c.slug !== "todos" ? `?categoria=${c.slug}` : ""}`}
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
                    <Link key={e.to} to={e.to} className="text-[13px] text-text hover:text-accent transition">
                      {e.label}
                    </Link>
                  ))}
                </div>
              </div>
            )}
          </div>

          <Link to="/modelos" className="hover:text-accent transition">Modelos</Link>
          <Link to="/reservas" className="hover:text-accent transition">Reservas</Link>
          <Link to="/contacto" className="hover:text-accent transition">Contacto</Link>
        </nav>
      </div>
    </header>
  );
}
