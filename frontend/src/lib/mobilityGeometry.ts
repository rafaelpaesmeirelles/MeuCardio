/** Provider geometry only: never interpolate an absent or incomplete route. */
type Coordinate = [number, number];
type UnknownRecord = Record<string, unknown>;

const MAX_POLYLINE_CHARACTERS = 200_000;
const MAX_POLYLINE_POINTS = 50_000;

function record(value: unknown): UnknownRecord | null {
  return typeof value === "object" && value !== null && !Array.isArray(value)
    ? value as UnknownRecord
    : null;
}

export function coordinateValid(latitude: unknown, longitude: unknown): boolean {
  return typeof latitude === "number" && typeof longitude === "number"
    && Number.isFinite(latitude) && Number.isFinite(longitude)
    && latitude >= -90 && latitude <= 90 && longitude >= -180 && longitude <= 180;
}

export function decodeRoutePolyline(value: unknown, precision = 5): Coordinate[] {
  if (typeof value !== "string" || !value.length || value.length > MAX_POLYLINE_CHARACTERS
      || (precision !== 5 && precision !== 6)) return [];
  const factor = 10 ** precision;
  const coordinates: Coordinate[] = [];
  let index = 0;
  let latitude = 0;
  let longitude = 0;
  while (index < value.length) {
    if (coordinates.length >= MAX_POLYLINE_POINTS) return [];
    const deltas: number[] = [];
    for (let dimension = 0; dimension < 2; dimension += 1) {
      let number = 0;
      let shift = 0;
      while (true) {
        // Six groups suffice for every valid coordinate delta at precision 6.
        if (index >= value.length || shift > 25) return [];
        const byte = value.charCodeAt(index) - 63;
        index += 1;
        if (byte < 0 || byte > 63) return [];
        number += (byte & 31) * 2 ** shift;
        if (byte < 32) break;
        shift += 5;
      }
      deltas.push(number % 2 ? -(Math.floor(number / 2) + 1) : number / 2);
    }
    latitude += deltas[0];
    longitude += deltas[1];
    const point: Coordinate = [latitude / factor, longitude / factor];
    if (!coordinateValid(point[0], point[1])) return [];
    coordinates.push(point);
  }
  return coordinates;
}

export function geometryAvailable(route: unknown): boolean {
  const candidate = record(route);
  if (!candidate || candidate.geometry_available === false) return false;
  const geometry = record(candidate.geometry);
  if (!geometry || geometry.format !== "encoded_polyline") return false;
  const precision = geometry.precision === undefined ? 5 : geometry.precision;
  if (typeof precision !== "number") return false;
  const points = decodeRoutePolyline(geometry.value, precision);
  return points.length >= 2 && points.some(([lat, lng]) => lat !== points[0][0] || lng !== points[0][1]);
}

const GEOMETRY_UNAVAILABLE = "O provedor retornou tempo e distância, mas não uma geometria utilizável para desenhar o trajeto. Os valores permanecem disponíveis; nenhum percurso foi inventado.";
const ROUTE_UNAVAILABLE = "A rota não pôde ser calculada agora. O destino continua disponível no mapa.";

export function mobilityResultError(result: unknown): string | null {
  const candidate = record(result);
  if (!candidate) return ROUTE_UNAVAILABLE;
  const detail = record(candidate.detail);
  const code = candidate.code ?? detail?.code;
  if (code === "traffic_provider_unavailable") return "O provedor de trânsito está temporariamente indisponível. Tente novamente em instantes.";
  if (code === "traffic_invalid_response") return "O provedor de trânsito retornou uma resposta inválida. Nenhum trajeto foi estimado; tente novamente.";
  if (code === "traffic_provider_error" || code === "unsupported_traffic_provider") return "Não foi possível consultar o provedor de trânsito. O destino continua disponível no mapa.";
  switch (candidate.status) {
    case "not_configured": return "O destino está pronto, mas o provedor de trânsito ainda não está configurado.";
    case "origin_not_geocoded": return "Não foi possível localizar com segurança o ponto de partida salvo.";
    case "destination_not_geocoded": return "Não foi possível localizar o endereço deste compromisso. Revise o local cadastrado na Agenda.";
    case "destination_without_location": return "Este compromisso ainda não possui um local cadastrado para a rota.";
    case "origin_without_location": return "O compromisso de partida ainda não possui um local cadastrado para a rota de retorno.";
    case "destination_mismatch": return "O destino selecionado não corresponde mais à Agenda. Atualize o próximo compromisso antes de calcular a rota.";
    case "origin_mismatch": return "O compromisso de partida não corresponde mais à Agenda. Atualize os compromissos antes de calcular o retorno.";
    case "no_upcoming_location": return "Nenhum próximo compromisso com local de deslocamento foi encontrado na Agenda.";
    case "no_route": return "O provedor não encontrou uma rota entre a origem e o destino. Nenhum percurso foi inventado.";
    case "geometry_unavailable": return GEOMETRY_UNAVAILABLE;
    case "live":
    case "ok": {
      const routes = Array.isArray(candidate.routes) ? candidate.routes : [];
      if (routes.some(geometryAvailable)) return null;
      return routes.length ? GEOMETRY_UNAVAILABLE : "O provedor respondeu, mas não retornou uma rota utilizável. Tente novamente.";
    }
    default: return ROUTE_UNAVAILABLE;
  }
}
