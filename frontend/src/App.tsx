import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "@/components/layout/Layout";
import Home from "@/pages/Home";
import Modelos from "@/pages/Modelos";
import Vehiculo from "@/pages/Vehiculo";
import { useFrontendConfig } from "@/hooks/useFrontendConfig";

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
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="modelos" element={<Modelos />} />
          <Route path="vehiculo/:id" element={<Vehiculo />} />
          <Route path="reservas" element={<Placeholder titulo="Reservas" />} />
          <Route path="contacto" element={<Placeholder titulo="Contacto" />} />
          <Route path="localizaciones" element={<Placeholder titulo="Localizaciones" />} />
          <Route path="tarifas" element={<Placeholder titulo="Tarifas" />} />
          <Route path="extras" element={<Placeholder titulo="Extras" />} />
          <Route path="faq" element={<Placeholder titulo="Preguntas frecuentes" />} />
          <Route path="aviso-legal" element={<Placeholder titulo="Aviso legal" />} />
          <Route path="privacidad" element={<Placeholder titulo="Privacidad" />} />
          <Route path="condiciones" element={<Placeholder titulo="Condiciones de contratación" />} />
          <Route path="*" element={<Placeholder titulo="Página no encontrada" />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
