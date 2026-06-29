// Tipos que reflejan los serializers del backend (autorent/serializers.py)

export interface FranjaHoraria {
  dia_semana: number;
  dia_semana_display: string;
  hora_apertura: string;
  hora_cierre: string;
}

export interface Sede {
  id: number;
  nombre: string;
  slug: string;
  direccion: string;
  poblacion: string;
  cp: string;
  provincia: string;
  pais: string;
  latitud: string | null;
  longitud: string | null;
  telefono: string;
  email: string;
  horario: string;
  suplemento_fuera_horario: string;
  franjas: FranjaHoraria[];
}

export interface Extra {
  id: number;
  nombre: string;
  descripcion: string;
  precio: string;
  tipo_cobro: "por_dia" | "unico";
  tipo_cobro_display: string;
}

export interface FotoVehiculo {
  id: number;
  imagen: string | null;
  principal: boolean;
  orden: number;
  titulo: string;
}

export interface RangoPrecio {
  dias_min: number;
  dias_max: number | null;
  precio_dia: string;
}

export interface VehiculoList {
  id: number;
  slug: string;
  nombre: string;
  marca: string;
  modelo: string;
  categoria: string;
  categoria_display: string;
  plazas: number;
  puertas: number;
  combustible: string;
  cambio: string;
  capacidad_carga: string;
  foto_principal: string | null;
  precio_desde: number | null;
}

export interface VehiculoDetail extends VehiculoList {
  anio: number | null;
  combustible_display: string;
  cambio_display: string;
  descripcion: string;
  fianza: string;
  fotos: FotoVehiculo[];
  rangos_precio: RangoPrecio[];
  extras: Extra[];
  sede: Sede | null;
}

export interface PrecioCalculo {
  vehiculo_id: number;
  fecha_inicio: string;
  fecha_fin: string;
  disponible: boolean;
  num_dias: number;
  precio_dia_base: string;
  subtotal_vehiculo: string;
  suplemento_fuera_horario?: string;
  suplemento_detalle?: { recogida_fuera: boolean; entrega_fuera: boolean };
  fianza: string;
}

// Respuesta paginada de DRF
export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// --- Asistente de reserva ---

export interface ClienteEntrada {
  nombre: string;
  apellidos?: string;
  nif: string;
  email: string;
  telefono: string;
  fecha_nacimiento?: string | null;
  direccion?: string;
  poblacion?: string;
  cp?: string;
  provincia?: string;
  pais?: string;
  carnet_numero?: string;
  carnet_caducidad?: string | null;
}

export interface ExtraEntrada {
  extra_id: number;
  cantidad: number;
}

export interface ConductorAdicionalEntrada {
  nombre: string;
  apellidos: string;
  nif: string;
  fecha_nacimiento: string;
  carnet_numero: string;
  carnet_caducidad: string;
}

export interface CrearReservaPayload {
  vehiculo_id: number;
  fecha_inicio: string;
  fecha_fin: string;
  hora_recogida?: string | null;
  hora_entrega?: string | null;
  sede_recogida_id?: number | null;
  sede_entrega_id?: number | null;
  metodo_pago: "transferencia" | "tarjeta" | "efectivo";
  cliente: ClienteEntrada;
  extras: ExtraEntrada[];
  conductores_adicionales: ConductorAdicionalEntrada[];
  acepta_condiciones: boolean;
}

export interface ReservaCreada {
  localizador: string;
  estado: string;
  estado_display: string;
  vehiculo_nombre: string;
  fecha_inicio: string;
  fecha_fin: string;
  num_dias: number;
  precio_dia_base: string;
  subtotal_vehiculo: string;
  subtotal_extras: string;
  fianza: string;
  total: string;
  metodo_pago: string;
  token_subida?: string;
}
