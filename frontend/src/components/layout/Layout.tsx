import { Outlet } from "react-router-dom";
import Header from "./Header";
import Footer from "./Footer";

export default function Layout() {
  // El Header es fixed y transparente sobre el hero. Las páginas sin hero
  // (placeholders, modelos, etc.) deben compensar el alto del header; eso
  // se gestiona en cada página con un padding-top cuando no hay hero.
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
