import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "@/components/layout/Layout";
import Home from "@/pages/Home";
import Modelos from "@/pages/Modelos";
import Vehiculo from "@/pages/Vehiculo";
import Localizaciones from "@/pages/Localizaciones";
import Extras from "@/pages/Extras";
import Tarifas from "@/pages/Tarifas";
import FAQ from "@/pages/FAQ";
import { useFrontendConfig } from "@/hooks/useFrontendConfig";
import { HeroProvider } from "@/hooks/useHero";

function Placeholder({ titulo }: { titulo: string }) {
  return (
    <div className="pt-16">
      <div className="max-w-container mx-auto px-6 py-20">
        <h1 className="text-2xl font-medium">{titulo}</h1>
        <p className="text-text-2 mt-2">Esta sección está en construcción.</p>
      </div>
    </div>
  );
}

export default function App() {
  useFrontendConfig();
  return (
    <BrowserRouter>
      <HeroProvider>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<Home />} />
            <Route path="modelos" element={<Modelos />} />
            <Route path="vehiculo/:id" element={<Vehiculo />} />
            <Route path="reservas" element={<Placeholder titulo="Reservas" />} />
            <Route path="contacto" element={<Placeholder titulo="Contacto" />} />
            <Route path="localizaciones" element={<Localizaciones />} />
            <Route path="tarifas" element={<Tarifas />} />
            <Route path="extras" element={<Extras />} />
            <Route path="faq" element={<FAQ />} />
            <Route path="aviso-legal" element={<Placeholder titulo="Aviso legal" />} />
            <Route path="privacidad" element={<Placeholder titulo="Privacidad" />} />
            <Route path="condiciones" element={<Placeholder titulo="Condiciones de contratación" />} />
            <Route path="*" element={<Placeholder titulo="Página no encontrada" />} />
          </Route>
        </Routes>
      </HeroProvider>
    </BrowserRouter>
  );
}
