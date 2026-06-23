import PaginaLegal from "@/components/ui/PaginaLegal";
import { EMPRESA } from "@/lib/empresa";

export default function Privacidad() {
  return (
    <PaginaLegal titulo="Política de privacidad" actualizado="junio de 2026">
      <p>
        En {EMPRESA.razonSocial} («{EMPRESA.nombreComercial}») tratamos la información que nos
        facilitas con el fin de prestar y gestionar el servicio de alquiler de vehículos. A
        continuación te explicamos cómo y por qué tratamos tus datos personales, conforme al
        RGPD y a la LOPDGDD.
      </p>

      <h2>Responsable del tratamiento</h2>
      <ul>
        <li><strong>Titular:</strong> {EMPRESA.razonSocial}</li>
        <li><strong>NIF:</strong> {EMPRESA.nif}</li>
        <li><strong>Domicilio:</strong> {EMPRESA.domicilio}</li>
        <li><strong>Email:</strong> {EMPRESA.email}</li>
      </ul>

      <h2>Datos que tratamos</h2>
      <p>
        Según tu relación con nosotros, podemos tratar datos identificativos y de contacto
        (nombre, DNI o pasaporte, dirección, teléfono, email), datos del permiso de conducir,
        datos de la reserva y, en su caso, datos de pago. Recogemos únicamente los datos
        necesarios para gestionar el alquiler y cumplir nuestras obligaciones legales.
      </p>

      <h2>Finalidades y base legal</h2>
      <ul>
        <li><strong>Gestión de la reserva y el contrato de alquiler:</strong> ejecución del contrato.</li>
        <li><strong>Atención a consultas:</strong> consentimiento del interesado.</li>
        <li><strong>Obligaciones fiscales y de identificación ante autoridades:</strong> cumplimiento de obligaciones legales.</li>
        <li><strong>Comunicaciones comerciales propias:</strong> interés legítimo o consentimiento, según el caso.</li>
      </ul>

      <h2>Conservación</h2>
      <p>
        Conservamos tus datos mientras dure la relación contractual y, posteriormente, durante
        los plazos legalmente exigidos para atender posibles responsabilidades. Los datos de
        geolocalización de los vehículos se conservan el tiempo mínimo imprescindible según se
        detalla en las condiciones de contratación.
      </p>

      <h2>Destinatarios</h2>
      <p>
        Tus datos no se cederán a terceros salvo obligación legal (por ejemplo, identificación
        del conductor ante la DGT) o cuando sea necesario para la prestación del servicio
        (entidades de pago, compañía aseguradora, asistencia en carretera). No se realizan
        transferencias internacionales de datos.
      </p>

      <h2>Tus derechos</h2>
      <p>
        Puedes ejercer tus derechos de acceso, rectificación, supresión, oposición, limitación
        del tratamiento y portabilidad escribiendo a {EMPRESA.email}, indicando el derecho que
        deseas ejercer. También puedes presentar una reclamación ante la Agencia Española de
        Protección de Datos (www.aepd.es) si consideras que el tratamiento no se ajusta a la
        normativa.
      </p>
    </PaginaLegal>
  );
}
