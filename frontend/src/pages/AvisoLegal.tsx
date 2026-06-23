import PaginaLegal from "@/components/ui/PaginaLegal";
import { EMPRESA } from "@/lib/empresa";

export default function AvisoLegal() {
  return (
    <PaginaLegal titulo="Aviso legal" actualizado="junio de 2026">
      <p>
        En cumplimiento del artículo 10 de la Ley 34/2002, de 11 de julio, de Servicios
        de la Sociedad de la Información y del Comercio Electrónico (LSSICE),{" "}
        <strong>{EMPRESA.razonSocial}</strong> (en adelante, «{EMPRESA.nombreComercial}»),
        responsable de este sitio web, pone a disposición de los usuarios la presente
        información para definir sus condiciones de uso.
      </p>
      <p>
        Los aspectos relativos a la protección de datos personales y la privacidad se
        desarrollan en las páginas de Política de Privacidad y Política de Cookies.
      </p>

      <h2>Identidad del responsable</h2>
      <ul>
        <li><strong>Denominación social:</strong> {EMPRESA.razonSocial}</li>
        <li><strong>Nombre comercial:</strong> {EMPRESA.nombreComercial}</li>
        <li><strong>NIF:</strong> {EMPRESA.nif}</li>
        <li><strong>Domicilio:</strong> {EMPRESA.domicilio}</li>
        <li><strong>Actividad:</strong> {EMPRESA.actividad}</li>
        <li><strong>Teléfono:</strong> {EMPRESA.telefono}</li>
        <li><strong>Email:</strong> {EMPRESA.email}</li>
        <li><strong>Dominio:</strong> {EMPRESA.dominio}</li>
      </ul>

      <h2>Finalidad de la web</h2>
      <ul>
        <li>Informar a clientes y potenciales clientes sobre los vehículos, servicios, tarifas y datos de contacto.</li>
        <li>Permitir la consulta de disponibilidad y la solicitud de reservas de alquiler de vehículos.</li>
        <li>Gestionar las comunicaciones con los usuarios que contacten a través de la web.</li>
      </ul>

      <h2>Marco normativo</h2>
      <p>La actividad de esta web está sujeta al marco legal español y europeo, en particular:</p>
      <ul>
        <li>Reglamento General de Protección de Datos (RGPD) (UE) 2016/679.</li>
        <li>Ley Orgánica 3/2018, de Protección de Datos Personales y Garantía de los Derechos Digitales (LOPDGDD).</li>
        <li>Ley 34/2002, de Servicios de la Sociedad de la Información y del Comercio Electrónico (LSSICE).</li>
      </ul>

      <h2>Condiciones de uso y responsabilidades</h2>
      <p>
        Toda persona que acceda a este sitio asume el papel de usuario y se compromete a la
        observancia de las condiciones aquí dispuestas. {EMPRESA.nombreComercial} no se
        responsabiliza de los daños, propios o a terceros, derivados del uso inadecuado del
        sitio. Queda prohibido introducir virus o sistemas que dañen los equipos, reproducir
        sin autorización los contenidos, acceder a zonas restringidas o eludir los sistemas de
        reserva y pago establecidos.
      </p>
      <p>
        El sitio se revisa para funcionar correctamente, si bien no se descarta la existencia
        de errores puntuales o falta de disponibilidad por mantenimiento o causas de fuerza
        mayor. {EMPRESA.nombreComercial} se reserva el derecho a modificar la información de la
        web en cualquier momento sin previo aviso.
      </p>

      <h2>Propiedad intelectual</h2>
      <p>
        El sitio web, su programación, diseño, logotipos, textos y gráficos son propiedad de{" "}
        {EMPRESA.nombreComercial} o cuenta con la autorización de sus autores. No se permite la
        reproducción, distribución o transformación, total o parcial, sin permiso previo y por
        escrito. Las marcas o logotipos de terceros que pudieran aparecer pertenecen a sus
        respectivos propietarios.
      </p>

      <h2>Enlaces de terceros</h2>
      <p>
        Este sitio puede contener enlaces a páginas de terceros. {EMPRESA.nombreComercial} no
        asume responsabilidad sobre su contenido, veracidad o licitud, y retirará de inmediato
        cualquier redirección que contravenga la legislación vigente.
      </p>

      <h2>Ley aplicable y jurisdicción</h2>
      <p>
        El idioma de redacción e interpretación de este aviso legal es el español. La relación
        entre {EMPRESA.nombreComercial} y el usuario se rige por la ley española, a la que ambas
        partes se someten ante cualquier controversia relacionada con el sitio web o las
        actividades en él desarrolladas.
      </p>
    </PaginaLegal>
  );
}
