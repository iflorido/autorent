import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Buscador from "@/components/ui/Buscador";
import CarruselVehiculos from "@/components/ui/CarruselVehiculos";
import HeroScrollFrames from "@/components/ui/HeroScrollFrames";
import OficinasCercanas from "@/components/ui/OficinasCercanas";
import FadeIn from "@/components/ui/FadeIn";
import PasosReserva from "@/components/ui/PasosReserva";
import { getSedes, getVehiculos } from "@/lib/api";
import { useHeroOscuro } from "@/hooks/useHeroOscuro";
import type { Sede, VehiculoList } from "@/types";

const VENTAJAS = [
  { icon: "M5 13h14v4H5zM7 13V9h7l3 4", titulo: "Flota moderna", texto: "Vehículos revisados y equipados para cada viaje." },
  { icon: "M12 2v20M2 12h20", titulo: "Kilometraje generoso", texto: "Tarifas claras sin sorpresas de última hora." },
  { icon: "M20 6L9 17l-5-5", titulo: "Reserva sencilla", texto: "En pocos pasos y con confirmación inmediata." },
  { icon: "M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z", titulo: "Soporte cercano", texto: "Te acompañamos antes, durante y después." },
];

const CATEGORIAS = [
  { slug: "turismo", label: "Turismo", desc: "Espacio y confort para la familia.", img: "/images/cat-turismo.jpg" },
  { slug: "camper", label: "Camper", desc: "Tu casa sobre ruedas para escapadas.", img: "/images/cat-camper.jpg" },
  { slug: "industrial", label: "Industrial", desc: "Carga y volumen para profesionales.", img: "/images/cat-industrial.jpg" },
];

export default function Home() {
  useHeroOscuro(); // header transparente sobre el hero
  const [vehiculos, setVehiculos] = useState<VehiculoList[]>([]);
  const [sedes, setSedes] = useState<Sede[]>([]);

  useEffect(() => {
    getVehiculos().then(setVehiculos).catch(() => {});
    getSedes().then(setSedes).catch(() => {});
  }, []);

  return (
    <div>
      {/* Hero con animación scroll-driven (secuencia de frames) */}
      <HeroScrollFrames primerFrame={30} ultimoFrame={65} alturaScroll={3}>
        <div className="max-w-xl">
          <h1 className="text-white text-4xl md:text-6xl font-medium leading-[1.1]">
            Tu próxima aventura sobre ruedas
          </h1>
          <p className="text-white/85 mt-5 text-lg">
            Furgonetas, campers y vehículos para cada viaje. Reserva en minutos.
          </p>
        </div>
      </HeroScrollFrames>

      {/* Buscador justo después de la animación */}
      <section className="max-w-container mx-auto px-6 -mt-16 md:-mt-20 relative z-[20]">
        <FadeIn>
          <Buscador />
        </FadeIn>
      </section>

      {/* Carrusel de vehículos */}
      <section className="max-w-container mx-auto px-6 pt-12 md:pt-16 pb-8">
        <FadeIn>
          <CarruselVehiculos vehiculos={vehiculos} />
        </FadeIn>
      </section>

      {/* Ventajas — versión más vistosa: tarjetas con fondo, icono destacado y hover */}
      <section className="max-w-container mx-auto px-6 py-12">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {VENTAJAS.map((v, i) => (
            <FadeIn key={v.titulo} delay={i * 80}>
              <div className="group h-full bg-bg-2 border border-border rounded-2xl p-6 hover:shadow-soft hover:-translate-y-1 transition-all duration-300">
                <span className="w-12 h-12 rounded-xl bg-accent flex items-center justify-center text-white mb-4 group-hover:scale-110 transition-transform">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                    <path d={v.icon} />
                  </svg>
                </span>
                <p className="font-display font-medium text-lg">{v.titulo}</p>
                <p className="text-[13px] text-text-2 leading-relaxed mt-1">{v.texto}</p>
              </div>
            </FadeIn>
          ))}
        </div>
      </section>

      {/* Cómo funciona — pasos numerados (componente reutilizable) */}
      <section className="bg-bg-2 border-y border-border py-16">
        <div className="max-w-container mx-auto px-6">
          <PasosReserva />
        </div>
      </section>

      {/* Categorías */}
      <section className="max-w-container mx-auto px-6 py-16">
        <FadeIn>
          <h2 className="text-2xl font-medium mb-8 text-center">Elige tu tipo de vehículo</h2>
        </FadeIn>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {CATEGORIAS.map((c, i) => (
            <FadeIn key={c.slug} delay={i * 100}>
              <Link
                to={`/modelos?categoria=${c.slug}`}
                className="group relative block rounded-2xl overflow-hidden h-56"
              >
                {/* Imagen de fondo */}
                <div
                  className="absolute inset-0 bg-cover bg-center transition-transform duration-500 group-hover:scale-105"
                  style={{ backgroundImage: `url('${c.img}')`, backgroundColor: "#0f2433" }}
                />
                {/* Capa azul: opaca por defecto (0.85), se aclara al hover (0.30) para ver la foto */}
                <div
                  className="absolute inset-0 transition-opacity duration-300 opacity-[0.85] group-hover:opacity-30"
                  style={{ background: "linear-gradient(160deg, #0f2433, #0891b2)" }}
                />
                {/* Contenido */}
                <div className="relative h-full flex flex-col justify-end p-6">
                  <p className="font-display font-medium text-lg text-white">{c.label}</p>
                  <p className="text-[13px] text-white/85 mt-1">{c.desc}</p>
                </div>
              </Link>
            </FadeIn>
          ))}
        </div>
      </section>

      {/* Oficinas cercanas */}
      <section className="bg-bg-2 border-y border-border py-16">
        <div className="max-w-container mx-auto px-6">
          <FadeIn>
            <OficinasCercanas sedes={sedes} />
          </FadeIn>
        </div>
      </section>

      {/* CTA final */}
      <section className="max-w-container mx-auto px-6 py-20">
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
