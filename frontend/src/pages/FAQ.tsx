import { useState } from "react";
import BuscadorSeccion from "@/components/ui/BuscadorSeccion";
import FadeIn from "@/components/ui/FadeIn";
import { useHeroOscuro } from "@/hooks/useHeroOscuro";

interface Pregunta { q: string; a: string }
interface Bloque { titulo: string; preguntas: Pregunta[] }

const BLOQUES: Bloque[] = [
  {
    titulo: "Requisitos y documentación",
    preguntas: [
      {
        q: "¿Qué documentación necesito para recoger el vehículo?",
        a: "El conductor principal y los adicionales deben presentar físicamente en la entrega: DNI o pasaporte en vigor (no se aceptan denuncias de pérdida ni documentos caducados), permiso de conducir válido en España con la antigüedad requerida (si no es de la UE, además el Permiso Internacional de Conducción) y una tarjeta de crédito o débito a nombre del titular para la fianza.",
      },
      {
        q: "¿Hay edad mínima o antigüedad de carnet?",
        a: "Sí, según el segmento: turismos estándar desde 21 años y 2 de antigüedad; furgonetas industriales y campers desde 23 años y 2 de antigüedad. Los menores de 25 años pueden estar sujetos a un suplemento de conductor joven por cobertura del seguro.",
      },
    ],
  },
  {
    titulo: "Reservas, pagos y fianza",
    preguntas: [
      {
        q: "¿Cómo se formaliza el pago de la reserva?",
        a: "Por ahora las reservas se confirman por transferencia bancaria o ingreso. Al terminar el proceso recibirás un correo con un localizador y los datos bancarios, y el vehículo queda pre-reservado 24 horas. La reserva pasa a confirmada en firme cuando recibimos el justificante, momento en que se habilita tu contrato digital.",
      },
      {
        q: "¿En qué consiste la fianza y cuándo se devuelve?",
        a: "Es una pre-autorización bancaria (un bloqueo de saldo, no un cargo) que cubre posibles franquicias por daños, combustible o días extra. El importe varía según categoría (orientativo: turismos 400 €, industriales y campers 800 €). Se libera en un máximo de 48 horas tras la devolución y el check-in; según tu banco, el dinero vuelve a estar disponible en 3 a 10 días laborables.",
      },
    ],
  },
  {
    titulo: "Seguros y coberturas",
    preguntas: [
      {
        q: "¿Qué seguro incluye mi tarifa?",
        a: "Todas las tarifas incluyen el seguro obligatorio de responsabilidad civil frente a terceros y una cobertura de daños propios con franquicia (CDW). La franquicia es el importe máximo del que respondes en caso de daño con culpa, vandalismo o robo. Puedes contratar la cobertura Super-Relax (SCDW) para reducir la franquicia a 0 €.",
      },
      {
        q: "¿Qué supuestos no cubre el seguro?",
        a: "Como en todo el sector, no se cubren negligencias graves: errores de repostaje (combustible equivocado), pérdida o rotura de llaves, daños en bajos o techos por vías no asfaltadas o de altura restringida, y conducir bajo los efectos del alcohol o drogas o ceder el volante a un conductor no registrado.",
      },
    ],
  },
  {
    titulo: "Recogida, devolución y kilometraje",
    preguntas: [
      {
        q: "¿Cuál es la política de combustible?",
        a: "Lleno / lleno: entregamos el depósito al 100 % y debes devolverlo igual. Si lo devuelves con menos, se factura el combustible faltante más una penalización de repostaje por el desplazamiento de nuestro personal.",
      },
      {
        q: "¿El kilometraje es ilimitado?",
        a: "Depende del vehículo y la duración, y lo verás desglosado al elegir modelo. Puedes adquirir el pack de kilometraje ilimitado durante la reserva, o abonar el exceso a la entrega según la tarifa por kilómetro adicional.",
      },
      {
        q: "¿Qué pasa si me retraso en la devolución?",
        a: "Hay un margen de cortesía de 30 minutos. Superado, se factura un día extra a tarifa de mostrador, más una posible penalización logística si el vehículo estaba comprometido con otro cliente. Si vas a llegar tarde, avísanos.",
      },
    ],
  },
  {
    titulo: "Uso del vehículo y normativa",
    preguntas: [
      {
        q: "¿Puedo viajar fuera de España?",
        a: "Sí, a países fronterizos del espacio Schengen (Portugal, Francia, Andorra), pero es obligatorio notificarlo en la reserva para emitir la Carta Verde y activar la asistencia transfronteriza. Viajar al extranjero sin autorización invalida las coberturas.",
      },
      {
        q: "¿Qué ocurre si recibo una multa durante el alquiler?",
        a: "Por ley, el arrendatario es responsable de las infracciones cometidas durante el contrato. Cuando la administración nos requiere la identificación del conductor, estamos obligados a facilitarla; este trámite conlleva un cargo de gestión administrativa, independiente del importe de la multa, que el organismo te notificará directamente.",
      },
    ],
  },
  {
    titulo: "Cancelaciones y cambios",
    preguntas: [
      {
        q: "¿Cuál es la política de cancelación?",
        a: "Con más de 48 horas de antelación, reembolso del 100 %. Entre 48 y 24 horas, reembolso del 50 %. Con menos de 24 horas o no presentarse, no hay reembolso. El derecho de desistimiento de 14 días no aplica a los alquileres de vehículo con fecha de ejecución específica (Art. 103.l del RDL 1/2007).",
      },
    ],
  },
];

export default function FAQ() {
  useHeroOscuro();
  // Clave única "bloque-pregunta" para el acordeón.
  const [abierta, setAbierta] = useState<string | null>("0-0");

  return (
    <div>
      <BuscadorSeccion titulo="Preguntas frecuentes" subtitulo="Resolvemos las dudas más habituales sobre el alquiler." />
      <section className="max-w-container mx-auto px-6 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_360px] gap-10 items-start">
          {/* Columna de preguntas */}
          <div className="space-y-8">
            {BLOQUES.map((bloque, bi) => (
              <FadeIn key={bi}>
                <div>
                  <h2 className="text-lg font-medium mb-3">{bloque.titulo}</h2>
                  <div className="space-y-3">
                    {bloque.preguntas.map((p, pi) => {
                      const clave = `${bi}-${pi}`;
                      const open = abierta === clave;
                      return (
                        <div key={clave} className="bg-bg-2 border border-border rounded-xl overflow-hidden">
                          <button
                            onClick={() => setAbierta(open ? null : clave)}
                            className="w-full flex items-center justify-between gap-3 px-5 py-4 text-left"
                          >
                            <span className="font-medium text-sm">{p.q}</span>
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
                              className="transition-transform shrink-0 text-text-2"
                              style={{ transform: open ? "rotate(180deg)" : "none" }}>
                              <path d="M6 9l6 6 6-6" />
                            </svg>
                          </button>
                          {open && <p className="px-5 pb-4 text-[13px] text-text-2 leading-relaxed">{p.a}</p>}
                        </div>
                      );
                    })}
                  </div>
                </div>
              </FadeIn>
            ))}
          </div>

          {/* Columna imagen (sticky en desktop) */}
          <FadeIn delay={150}>
            <div className="lg:sticky lg:top-24">
              <div className="rounded-2xl overflow-hidden bg-accent-dim aspect-[3/4]">
                <img
                  src="/images/faq.jpg"
                  alt="Atención al cliente AutoRent"
                  className="w-full h-full object-cover"
                  onError={(e) => { (e.currentTarget as HTMLImageElement).style.display = "none"; }}
                />
              </div>
              <div className="mt-4 bg-bg-2 border border-border rounded-2xl p-5">
                <p className="font-display font-medium">¿No encuentras tu respuesta?</p>
                <p className="text-[13px] text-text-2 mt-1">Escríbenos y te ayudamos con tu reserva.</p>
                <a href="/contacto" className="inline-block mt-3 text-sm text-accent font-medium hover:underline">
                  Ir a contacto →
                </a>
              </div>
            </div>
          </FadeIn>
        </div>
      </section>
    </div>
  );
}
