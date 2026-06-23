import PaginaLegal from "@/components/ui/PaginaLegal";
import { EMPRESA } from "@/lib/empresa";

export default function Condiciones() {
  return (
    <PaginaLegal titulo="Condiciones generales de contratación" actualizado="junio de 2026">
      <p>
        Las presentes Condiciones Generales de Contratación (en adelante, las «Condiciones»)
        regulan la relación jurídica derivada del contrato de arrendamiento de vehículos sin
        conductor celebrado entre <strong>{EMPRESA.razonSocial}</strong>, con NIF {EMPRESA.nif} y
        domicilio en {EMPRESA.domicilio} (en adelante, el «Arrendador»), y la persona física o
        jurídica que contrata el servicio (en adelante, el «Arrendatario»). La confirmación de
        la reserva implica la aceptación expresa, íntegra y sin reservas de estas Condiciones.
      </p>

      <h2>Cláusula 1: Objeto del contrato</h2>
      <p>
        El Arrendador cede al Arrendatario el uso del vehículo especificado en el contrato
        particular, por el plazo, precio y condiciones estipulados. El vehículo es propiedad
        exclusiva del Arrendador; este contrato no configura título de adquisición, usufructo o
        disposición sobre el mismo.
      </p>

      <h2>Cláusula 2: Conductores autorizados</h2>
      <p>
        Solo están autorizados a conducir el vehículo el «Conductor Principal» y los
        «Conductores Adicionales» designados en el contrato. El Arrendatario y los conductores
        adicionales deberán ser mayores de 21 años para turismos y 23 para vehículos
        industriales y campers, con permiso de conducción B en vigor homologado en España y una
        antigüedad mínima de 2 años.
      </p>
      <p>
        Queda terminantemente prohibida la cesión del volante a personas no autorizadas. Su
        incumplimiento anulará de forma inmediata y automática la totalidad de las coberturas
        del seguro, respondiendo el Arrendatario de los daños ocasionados.
      </p>

      <h2>Cláusula 3: Perfección de la reserva y modalidad de pago</h2>
      <p>
        Al solicitar un vehículo, el sistema emitirá un bloqueo temporal de 24 horas. El
        contrato no se considerará perfeccionado hasta que el Arrendador verifique el ingreso
        del importe total del alquiler en la cuenta bancaria indicada ({EMPRESA.iban}). Si
        transcurridas 24 horas no se ha recibido el comprobante en {EMPRESA.emailReservas}, el
        sistema liberará el vehículo automáticamente.
      </p>

      <h2>Cláusula 4: Depósito de garantía (fianza)</h2>
      <p>
        Antes de la entrega, el Arrendatario constituirá un depósito de garantía mediante
        tarjeta a su nombre (orientativo: 400 € para turismos y 800 € para industriales y
        campers). El Arrendatario autoriza a aplicar cargos contra la fianza para liquidar
        franquicias por daños, faltas de combustible y penalizaciones de repostaje, kilometraje
        excedido, retrasos en la devolución, gestión de multas y limpieza extrema. El bloqueo se
        liberará en un máximo de 48 horas tras la inspección de fin de contrato, sujeto a los
        plazos de la entidad bancaria del cliente.
      </p>

      <h2>Cláusula 5: Estado del vehículo, entrega y devolución</h2>
      <p>
        El vehículo se entrega en perfecto estado de funcionamiento, limpieza y conservación, y
        se firmará un Acta de Entrega (Check-out) reflejando los desperfectos preexistentes. El
        Arrendatario se obliga a devolverlo en las mismas condiciones, en el lugar, fecha y hora
        estipulados. Se concede un periodo de cortesía de 30 minutos; superado, se penalizará el
        retraso o se facturará un día completo a tarifa de mostrador si supera las 3 horas, más
        una penalización por perjuicios logísticos.
      </p>

      <h2>Cláusula 6: Utilización del vehículo y usos prohibidos</h2>
      <p>El Arrendatario conducirá de forma diligente respetando la Ley de Seguridad Vial. Queda prohibido:</p>
      <ul>
        <li>Destinar el vehículo al transporte comercial de pasajeros o de mercancías ilegales, peligrosas o inflamables.</li>
        <li>Empujar o remolcar otros vehículos o remolques.</li>
        <li>Participar en competiciones, carreras o conducción en circuitos.</li>
        <li>Circular por vías no pavimentadas, playas o pistas forestales (off-road).</li>
        <li>Subarrendar, hipotecar, pignorar o vender el vehículo o sus piezas.</li>
        <li>Conducir bajo los efectos del alcohol, drogas o fatiga extrema.</li>
        <li>Manipular el cuentakilómetros (en cuyo caso se abonarán 1.000 km por cada día de alquiler).</li>
        <li>Fumar en el interior (penalización de 150 € por tratamiento de ozono).</li>
        <li>En campers: usar gas o fuego con el vehículo en marcha; verter aguas grises o negras en lugares no habilitados.</li>
      </ul>

      <h2>Cláusula 7: Seguros, coberturas y exclusiones</h2>
      <p>
        El precio incluye Seguro de Responsabilidad Civil Obligatoria y Cobertura de Daños
        Propios con franquicia (CDW). El Arrendatario perderá toda cobertura (incluso con el
        extra Super-Relax/SCDW de franquicia 0 €) y responderá del 100 % de la reparación en
        supuestos de negligencia manifiesta: error en el repostaje; pérdida, robo o rotura de
        llaves; daños en techos o voladizos por colisión con puentes, túneles o garajes de
        altura insuficiente; daños en los bajos por desniveles o bordillos; o quemar el embrague
        por uso negligente.
      </p>

      <h2>Cláusula 8: Averías y accidentes</h2>
      <p>
        En caso de accidente, el Arrendatario no reconocerá responsabilidad, obtendrá los datos
        de la parte contraria mediante el Parte Amistoso y lo remitirá al Arrendador en un máximo
        de 24 horas, avisando a las autoridades si hay heridos. No podrá ordenar reparaciones en
        talleres no concertados sin autorización expresa, debiendo contactar con el teléfono de
        Asistencia en Carretera.
      </p>

      <h2>Cláusula 9: Infracciones de tráfico</h2>
      <p>
        El Arrendatario es el único responsable legal de multas, peajes y sanciones impuestas
        durante el alquiler. El Arrendador identificará al conductor ante la DGT u organismo
        sancionador y cargará un coste de gestión administrativa (35 € + IVA) por cada
        expediente, independiente del importe de la multa.
      </p>

      <h2>Cláusula 10: Política de cancelación y desistimiento</h2>
      <p>
        Conforme al artículo 103.l) del Real Decreto Legislativo 1/2007, queda excluido el
        derecho de desistimiento de 14 días. Las cancelaciones se rigen por el siguiente
        escalado:
      </p>
      <ul>
        <li>Más de 48 horas antes de la recogida: reembolso del 100 %.</li>
        <li>Entre 48 y 24 horas: reembolso del 50 %.</li>
        <li>Menos de 24 horas o no presentarse (No-Show): pérdida del 100 % del importe.</li>
      </ul>

      <h2>Cláusula 11: Dispositivos de geolocalización (GPS)</h2>
      <p>
        El Arrendatario queda informado y consiente que el vehículo puede incorporar un
        dispositivo de geolocalización y telemetría. El Arrendador solo accederá a los datos de
        posición en caso de: alerta por robo o apropiación indebida; accidente grave; faltas de
        comunicación reiteradas superada la fecha de devolución; o sospecha fundada de paso de
        frontera no autorizado.
      </p>

      <h2>Cláusula 12: Jurisdicción aplicable</h2>
      <p>
        Si el cliente es consumidor (particular), serán competentes los Juzgados y Tribunales de
        su domicilio. Si el cliente es empresa o autónomo, las partes se someten a la
        jurisdicción de los Juzgados y Tribunales de {EMPRESA.ciudad}, con renuncia expresa a su
        fuero propio.
      </p>
    </PaginaLegal>
  );
}
