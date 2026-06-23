import PaginaLegal from "@/components/ui/PaginaLegal";
import { EMPRESA } from "@/lib/empresa";

export default function Cookies() {
  return (
    <PaginaLegal titulo="Política de cookies" actualizado="junio de 2026">
      <p>
        Esta web, titularidad de {EMPRESA.razonSocial} («{EMPRESA.nombreComercial}»), utiliza
        cookies y tecnologías similares para garantizar su correcto funcionamiento y mejorar la
        experiencia de navegación. A continuación te explicamos qué son y cómo las usamos.
      </p>

      <h2>¿Qué es una cookie?</h2>
      <p>
        Una cookie es un pequeño archivo de texto que un sitio web almacena en tu navegador
        cuando lo visitas. Permite recordar información sobre tu visita, como tus preferencias,
        para facilitar la navegación y hacerla más útil.
      </p>

      <h2>Tipos de cookies que utilizamos</h2>
      <ul>
        <li>
          <strong>Técnicas o necesarias:</strong> imprescindibles para el funcionamiento del
          sitio (por ejemplo, mantener tu sesión o tu proceso de reserva). No requieren
          consentimiento.
        </li>
        <li>
          <strong>De preferencias:</strong> recuerdan tus elecciones, como el idioma o la sede
          seleccionada.
        </li>
        <li>
          <strong>De análisis o estadística:</strong> nos ayudan a entender cómo se usa la web
          de forma agregada y anónima, para mejorarla. Requieren tu consentimiento.
        </li>
      </ul>

      <h2>Gestión de cookies</h2>
      <p>
        Puedes permitir, bloquear o eliminar las cookies instaladas configurando las opciones
        de tu navegador. Ten en cuenta que desactivar las cookies técnicas puede afectar al
        funcionamiento de algunas partes de la web, como el proceso de reserva.
      </p>
      <p>
        Encontrarás cómo gestionar las cookies en la ayuda de los principales navegadores:
        Google Chrome, Mozilla Firefox, Safari y Microsoft Edge.
      </p>

      <h2>Actualizaciones</h2>
      <p>
        Podemos actualizar esta política de cookies para adaptarla a cambios normativos o
        técnicos. Te recomendamos revisarla periódicamente. Para cualquier duda, escríbenos a{" "}
        {EMPRESA.email}.
      </p>
    </PaginaLegal>
  );
}
