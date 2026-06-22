import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Buscador from "@/components/ui/Buscador";
import CarruselVehiculos from "@/components/ui/CarruselVehiculos";
import OficinasCercanas from "@/components/ui/OficinasCercanas";
import FadeIn from "@/components/ui/FadeIn";
import { getSedes, getVehiculos } from "@/lib/api";
import type { Sede, VehiculoList } from "@/types";

const VENTAJAS = [
  { icon: "M5 13h14v4H5zM7 13V9h7l3 4", titulo: "Flota moderna", texto: "Vehículos revisados y equipados para cada viaje." },
  { icon: "M12 2v20M2 12h20", titulo: "Kilometraje generoso", texto: "Tarifas claras sin sorpresas de última hora." },
  { icon: "M20 6L9 17l-5-5", titulo: "Reserva sencilla", texto: "En pocos pasos y con confirmación inmediata." },
  { icon: "M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z", titulo: "Soporte cercano", texto: "Te acompañamos antes, durante y después." },
];

const CATEGORIAS = [
  { slug: "turismo", label: "Turismo", desc: "Espacio y confort para la familia." },
  { slug: "camper", label: "Camper", desc: "Tu casa sobre ruedas para escapadas." },
  { slug: "industrial", label: "Industrial", desc: "Carga y volumen para profesionales." },
];

export default function Home() {
  const [vehiculos, setVehiculos] = useState<VehiculoList[]>([]);
  const [sedes, setSedes] = useState<Sede[]>([]);

  useEffect(() => {
    getVehiculos().then(setVehiculos).catch(() => {});
    getSedes().then(setSedes).catch(() => {});
  }, []);

  return (
    <div>
      {/* Hero a pantalla con imagen de fondo (el header transparente va encima) */}
      <section className="relative min-h-[88vh] flex items-center">
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage:
              "linear-gradient(160deg, rgba(15,36,51,0.92), rgba(8,145,178,0.78)), url('/images/hero.jpg')",
            backgroundColor: "#0f2433",
          }}
        />
        <div className="relative max-w-container mx-auto px-6 w-full pt-24 pb-40">
          <FadeIn>
            <div className="max-w-xl">
              <h1 className="text-white text-4xl md:text-6xl font-medium leading-[1.1]">
                Tu próxima aventura sobre ruedas
              </h1>
              <p className="text-white/85 mt-5 text-lg">
                Furgonetas, campers y vehículos para cada viaje. Reserva en minutos.
              </p>
            </div>
          </FadeIn>
        </div>

        {/* Buscador superpuesto en el borde inferior del hero */}
        <div className="absolute left-0 right-0 bottom-0 translate-y-1/2 z-[20]">
          <div className="max-w-container mx-auto px-6">
            <FadeIn delay={150}>
              <Buscador />
            </FadeIn>
          </div>
        </div>
      </section>

      {/* Carrusel de vehículos */}
      <section className="max-w-container mx-auto px-6 pt-28 pb-8">
        <FadeIn>
          <CarruselVehiculos vehiculos={vehiculos} />
        </FadeIn>
      </section>

      {/* Ventajas */}
      <section className="max-w-container mx-auto px-6 py-12">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {VENTAJAS.map((v, i) => (
            <FadeIn key={v.titulo} delay={i * 80}>
              <div className="flex flex-col gap-2">
                <span className="w-11 h-11 rounded-xl bg-accent-dim flex items-center justify-center text-accent">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                    <path d={v.icon} />
                  </svg>
                </span>
                <p className="font-medium mt-1">{v.titulo}</p>
                <p className="text-[13px] text-text-2 leading-relaxed">{v.texto}</p>
              </div>
            </FadeIn>
          ))}
        </div>
      </section>

      {/* Categorías */}
      <section className="bg-bg-2 border-y border-border py-16">
        <div className="max-w-container mx-auto px-6">
          <FadeIn>
            <h2 className="text-2xl font-medium mb-8 text-center">Elige tu tipo de vehículo</h2>
          </FadeIn>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {CATEGORIAS.map((c, i) => (
              <FadeIn key={c.slug} delay={i * 100}>
                <Link
                  to={`/modelos?categoria=${c.slug}`}
                  className="group block bg-bg border border-border rounded-xl p-6 hover:border-accent transition"
                >
                  <div className="h-32 rounded-lg bg-accent-dim mb-4 flex items-center justify-center text-accent">
                    <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.3">
                      <path d="M3 13h18v4H3zM5 13V8h11l3 5" />
                    </svg>
                  </div>
                  <p className="font-medium text-lg group-hover:text-accent transition">{c.label}</p>
                  <p className="text-[13px] text-text-2 mt-1">{c.desc}</p>
                </Link>
              </FadeIn>
            ))}
          </div>
        </div>
      </section>

      {/* Oficinas cercanas */}
      <section className="max-w-container mx-auto px-6 py-16">
        <FadeIn>
          <OficinasCercanas sedes={sedes} />
        </FadeIn>
      </section>

      {/* CTA final */}
      <section className="max-w-container mx-auto px-6 pb-20">
        <FadeIn>
          <div
            className="rounded-2xl px-8 py-14 text-center bg-cover bg-center"
            style={{ backgroundImage: "linear-gradient(160deg, #0f2433, #0891b2)" }}
          >
            <h2 className="text-white text-2xl md:text-3xl font-medium">¿Listo para tu próximo viaje?</h2>
            <p className="text-white/80 mt-3 max-w-md mx-auto">
              Encuentra el vehículo perfecto y reserva en minutos.
            </p>
            <Link
              to="/modelos"
              className="inline-block mt-6 bg-white text-accent font-medium px-6 py-3 rounded-lg hover:opacity-90 transition"
            >
              Ver todos los modelos
            </Link>
          </div>
        </FadeIn>
      </section>
    </div>
  );
}
