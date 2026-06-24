import axios from "axios";
import type {
  CrearReservaPayload,
  Extra,
  Paginated,
  PrecioCalculo,
  ReservaCreada,
  Sede,
  VehiculoDetail,
  VehiculoList,
} from "@/types";

// En producción el frontend y la API comparten dominio (mismo origen),
// así que basta con rutas relativas. En desarrollo, el proxy de Vite
// redirige /api al backend local.
export const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
});

export interface VehiculoFiltros {
  categoria?: string;
  sede?: number;
  fecha_inicio?: string;
  fecha_fin?: string;
}

export async function getSedes(): Promise<Sede[]> {
  const { data } = await api.get<Paginated<Sede>>("/sedes/");
  return data.results;
}

export async function getExtras(): Promise<Extra[]> {
  const { data } = await api.get<Extra[]>("/extras/");
  return data;
}

export async function getVehiculos(
  filtros: VehiculoFiltros = {},
): Promise<VehiculoList[]> {
  const params = new URLSearchParams();
  if (filtros.categoria) params.set("categoria", filtros.categoria);
  if (filtros.sede) params.set("sede", String(filtros.sede));
  if (filtros.fecha_inicio) params.set("fecha_inicio", filtros.fecha_inicio);
  if (filtros.fecha_fin) params.set("fecha_fin", filtros.fecha_fin);

  const { data } = await api.get<Paginated<VehiculoList>>("/vehiculos/", { params });
  return data.results;
}

export async function getVehiculo(slug: string): Promise<VehiculoDetail> {
  const { data } = await api.get<VehiculoDetail>(`/vehiculos/${slug}/`);
  return data;
}

export async function getPrecio(
  id: number,
  fechaInicio: string,
  fechaFin: string,
): Promise<PrecioCalculo> {
  const { data } = await api.get<PrecioCalculo>(`/vehiculos/${id}/precio/`, {
    params: { fecha_inicio: fechaInicio, fecha_fin: fechaFin },
  });
  return data;
}

export async function crearReserva(payload: CrearReservaPayload): Promise<ReservaCreada> {
  const { data } = await api.post<ReservaCreada>("/reservas/", payload);
  return data;
}

export async function subirDocumento(
  localizador: string,
  tipo: string,
  archivo: File,
): Promise<{ id: number; tipo: string; estado: string }> {
  const fd = new FormData();
  fd.append("tipo", tipo);
  fd.append("archivo", archivo);
  const { data } = await api.post(`/reservas/${localizador}/documentos/`, fd, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}
