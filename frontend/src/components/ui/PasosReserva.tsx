import FadeIn from "./FadeIn";

const PASOS = [
  { n: "1", titulo: "Elige fechas y vehículo", texto: "Busca por fechas y compara nuestra flota disponible." },
  { n: "2", titulo: "Añade tus extras", texto: "Personaliza tu alquiler con seguros, GPS y más." },
  { n: "3", titulo: "Confirma y viaja", texto: "Reserva en minutos y recoge tu vehículo." },
];

export default function PasosReserva() {
  return (
    <div>
      <FadeIn>
        <div className="text-center mb-10">
          <h2 className="text-2xl font-medium">Reservar es muy fácil</h2>
          <p className="text-text-2 mt-2">En tres pasos tienes tu vehículo listo.</p>
        </div>
      </FadeIn>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {PASOS.map((p, i) => (
          <FadeIn key={p.n} delay={i * 100}>
            <div className="relative bg-bg-2 border border-border rounded-2xl p-6 h-full">
              <span className="absolute -top-4 left-6 w-9 h-9 rounded-full bg-accent text-white font-display font-medium flex items-center justify-center shadow-soft">
                {p.n}
              </span>
              <p className="font-display font-medium text-lg mt-3">{p.titulo}</p>
              <p className="text-[13px] text-text-2 leading-relaxed mt-1">{p.texto}</p>
            </div>
          </FadeIn>
        ))}
      </div>
    </div>
  );
}
