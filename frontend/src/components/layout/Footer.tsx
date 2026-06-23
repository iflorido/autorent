import { Link } from "react-router-dom";

export default function Footer() {
  const year = new Date().getFullYear();
  return (
    <footer className="bg-bg-2 border-t border-border mt-20">
      <div className="max-w-container mx-auto px-6 py-12 grid grid-cols-2 md:grid-cols-4 gap-8">
        <div>
          <div className="flex items-center gap-2 mb-3">
            <span className="inline-flex w-7 h-7 rounded-lg bg-accent items-center justify-center text-white text-sm font-medium">
              A
            </span>
            <span className="font-medium">AutoRent</span>
          </div>
          <p className="text-[13px] text-text-2 leading-relaxed">
            Alquiler de furgonetas, campers y vehículos para cada viaje.
          </p>
        </div>

        <div>
          <h3 className="text-[13px] font-medium mb-3">Alquiler</h3>
          <ul className="space-y-2 text-[13px] text-text-2">
            <li><Link to="/modelos" className="hover:text-accent">Modelos</Link></li>
            <li><Link to="/tarifas" className="hover:text-accent">Tarifas</Link></li>
            <li><Link to="/extras" className="hover:text-accent">Extras</Link></li>
            <li><Link to="/localizaciones" className="hover:text-accent">Localizaciones</Link></li>
          </ul>
        </div>

        <div>
          <h3 className="text-[13px] font-medium mb-3">Empresa</h3>
          <ul className="space-y-2 text-[13px] text-text-2">
            <li><Link to="/contacto" className="hover:text-accent">Contacto</Link></li>
            <li>
              <Link to="/faq" className="inline-flex items-center gap-1.5 text-accent font-medium hover:underline">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10" /><path d="M9.1 9a3 3 0 015.8 1c0 2-3 3-3 3" /><path d="M12 17h.01" />
                </svg>
                Preguntas frecuentes
              </Link>
            </li>
          </ul>
        </div>

        <div>
          <h3 className="text-[13px] font-medium mb-3">Legal</h3>
          <ul className="space-y-2 text-[13px] text-text-2">
            <li><Link to="/aviso-legal" className="hover:text-accent">Aviso legal</Link></li>
            <li><Link to="/privacidad" className="hover:text-accent">Privacidad</Link></li>
            <li><Link to="/cookies" className="hover:text-accent">Política de cookies</Link></li>
            <li><Link to="/condiciones" className="hover:text-accent">Condiciones de contratación</Link></li>
          </ul>
        </div>
      </div>

      <div className="border-t border-border">
        <div className="max-w-container mx-auto px-6 py-4 text-[12px] text-text-2">
          © {year} AutoRent — AutomaWorks
        </div>
      </div>
    </footer>
  );
}
