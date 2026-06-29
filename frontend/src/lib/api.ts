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

export interface CategoriaItem {
  slug: string;
  nombre: string;
}

export async function getCategorias(): Promise<CategoriaItem[]> {
  const { data } = await api.get<CategoriaItem[]>("/categorias/");
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
  opciones?: {
    horaRecogida?: string;
    horaEntrega?: string;
    sedeRecogida?: number;
    sedeEntrega?: number;
  },
): Promise<PrecioCalculo> {
  const params: Record<string, string> = {
    fecha_inicio: fechaInicio,
    fecha_fin: fechaFin,
  };
  if (opciones?.horaRecogida) params.hora_recogida = opciones.horaRecogida;
  if (opciones?.horaEntrega) params.hora_entrega = opciones.horaEntrega;
  if (opciones?.sedeRecogida) params.sede_recogida = String(opciones.sedeRecogida);
  if (opciones?.sedeEntrega) params.sede_entrega = String(opciones.sedeEntrega);
  const { data } = await api.get<PrecioCalculo>(`/vehiculos/${id}/precio/`, { params });
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

// --- Enlace mágico de subida de documentos (sin login) ---

export interface InfoSubida {
  localizador: string;
  titular: string;
  vehiculo: string;
  conductores_adicionales: { id: number; nombre_completo: string }[];
  documentos_subidos: { tipo: string; conductor_id: number | null }[];
  expira_at: string;
}

export async function getInfoSubida(token: string): Promise<InfoSubida> {
  const { data } = await api.get<InfoSubida>(`/subida/${token}/`);
  return data;
}

export async function subirDocumentoToken(
  token: string, tipo: string, archivo: File, conductorId?: number | null,
): Promise<{ id: number; tipo: string; conductor_id: number | null }> {
  const fd = new FormData();
  fd.append("tipo", tipo);
  fd.append("archivo", archivo);
  if (conductorId) fd.append("conductor_id", String(conductorId));
  const { data } = await api.post(`/subida/${token}/documento/`, fd, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function finalizarSubida(token: string): Promise<{ finalizado: boolean }> {
  const { data } = await api.post(`/subida/${token}/finalizar/`);
  return data;
}
