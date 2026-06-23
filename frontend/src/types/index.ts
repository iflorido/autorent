// Tipos que reflejan los serializers del backend (autorent/serializers.py)

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
  fianza: string;
}

// Respuesta paginada de DRF
export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
