import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "@/components/layout/Layout";
import Home from "@/pages/Home";

// Páginas pendientes de desarrollar (placeholders para que el router no falle).
function Placeholder({ titulo }: { titulo: string }) {
  return (
    <div className="max-w-container mx-auto px-6 py-20">
      <h1 className="text-2xl font-medium">{titulo}</h1>
      <p className="text-text-2 mt-2">Esta sección está en construcción.</p>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="modelos" element={<Placeholder titulo="Modelos" />} />
          <Route path="vehiculo/:id" element={<Placeholder titulo="Ficha de vehículo" />} />
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
