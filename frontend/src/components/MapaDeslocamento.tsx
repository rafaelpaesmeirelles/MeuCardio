import { useEffect, useId, useMemo, useRef, useState } from "react";
import Icone from "./Icone";
import { coordinateValid, decodeRoutePolyline, geometryAvailable } from "../lib/mobilityGeometry";
import { loadGoogleMaps, MAPS_AUTH_ERROR } from "../lib/googleMapsLoader";
import { atelierMapPalette, atelierMapStyles } from "../lib/atelierMapStyle";
import { useCorviaTheme } from "../lib/corviaTheme";

export type RotaDeslocamento = {
  rank: number; provider_rank?: number; recommended?: boolean;
  duration_seconds: number; typical_duration_seconds?: number | null;
  traffic_delay_seconds: number; extra_time_seconds?: number; distance_meters: number;
  congestion: string; summary: string; labels?: string[]; geometry_available?: boolean;
  geometry?: { format: "encoded_polyline"; value: string; precision: number };
  traffic_segments?: Array<{ start_index: number; end_index?: number | null; speed: string }>;
  incidents?: Array<{ type?: string; description?: string }>;
};
type Coordinate = [number, number];
type Origin = { latitude: number; longitude: number } | null;
type Destination = { latitude: number | null; longitude: number | null; name: string };

function minutes(seconds: number) { return Number.isFinite(seconds) && seconds >= 0 ? Math.ceil(seconds / 60) : "—"; }
function kilometres(metres: number) { return Number.isFinite(metres) && metres >= 0 ? (metres / 1000).toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 }) : "—"; }
function trafficName(value: string) {
  return ({ normal: "Trânsito livre", leve: "Fluxo leve", moderado: "Trânsito moderado", intenso: "Trânsito intenso" } as Record<string, string>)[value] || "Trânsito não informado";
}
// Only non-Google geometry may use a schematic. Google Routes stays on a
// Google Map, with native logos/attribution intact and no invented streets.
function projectRoutes(routes: Coordinate[][]): Coordinate[][] {
  const all = routes.flat();
  if (all.length < 2) return routes.map(() => []);
  const factor = Math.cos(all.reduce((sum, p) => sum + p[0], 0) / all.length * Math.PI / 180);
  const xy = routes.map((route) => route.map(([lat, lng]) => [lng * factor, lat] as Coordinate));
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
  for (const route of xy) for (const [x, y] of route) { minX = Math.min(minX, x); maxX = Math.max(maxX, x); minY = Math.min(minY, y); maxY = Math.max(maxY, y); }
  const scale = Math.min(712 / Math.max(maxX - minX, 0.00001), 252 / Math.max(maxY - minY, 0.00001));
  const dx = (800 - (maxX - minX) * scale) / 2, dy = (340 - (maxY - minY) * scale) / 2;
  return xy.map((route) => route.map(([x, y]) => [dx + (x - minX) * scale, 340 - dy - (y - minY) * scale]));
}
const svgPath = (points: Coordinate[]) => points.map(([x, y], i) => `${i ? "L" : "M"}${x.toFixed(1)} ${y.toFixed(1)}`).join(" ");

export default function MapaDeslocamento({ rotas, origem, destino, provider, updatedAt, googleMapsApiKey, compact = false }: {
  rotas: RotaDeslocamento[]; origem: Origin; destino: Destination; provider?: string; updatedAt?: string; googleMapsApiKey?: string | null; compact?: boolean;
}) {
  const { theme } = useCorviaTheme();
  const dark = theme === "dark";
  const palette = useMemo(() => atelierMapPalette(dark), [dark]);
  const titleId = useId();
  const [selected, setSelected] = useState(0);
  const [mapState, setMapState] = useState<"loading" | "ready" | "error">("loading");
  const [mapError, setMapError] = useState("");
  const [retry, setRetry] = useState(0);
  const [version, setVersion] = useState(0);
  const canvasRef = useRef<HTMLDivElement>(null);
  const googleRef = useRef<any>(null);
  const mapRef = useRef<any>(null);
  const overlays = useRef<any[]>([]);
  const fitRef = useRef<(() => void) | null>(null);
  const signatureRef = useRef("");
  const index = Math.min(selected, Math.max(0, rotas.length - 1));
  const geometries = useMemo(() => rotas.map((route) => geometryAvailable(route)
    ? decodeRoutePolyline(route.geometry!.value, route.geometry!.precision) : []), [rotas]);
  const projected = useMemo(() => projectRoutes(geometries), [geometries]);
  const route = rotas[index];
  const activePoints = geometries[index] || [];
  const hasGeometry = geometries.some((points) => points.length > 1);
  const activeGeometry = activePoints.length > 1;
  const validDestination = coordinateValid(destino.latitude, destino.longitude);
  const validOrigin = origem && coordinateValid(origem.latitude, origem.longitude) ? origem : null;
  const isGoogle = ["google maps", "google_maps", "google_routes"].includes((provider || "").toLowerCase());
  const googleCanvas = isGoogle && Boolean(googleMapsApiKey) && validDestination;
  const navigationUrl = validDestination ? `https://www.google.com/maps/dir/?api=1${validOrigin ? `&origin=${validOrigin.latitude},${validOrigin.longitude}` : ""}&destination=${destino.latitude},${destino.longitude}&travelmode=driving&dir_action=navigate` : null;
  const updated = updatedAt ? new Date(updatedAt) : null;

  // One instance per mounted canvas. Updates below preserve its identity.
  useEffect(() => {
    if (!googleCanvas || !canvasRef.current || !googleMapsApiKey) return;
    let disposed = false;
    setMapState("loading"); setMapError("");
    const authFailure = () => { if (!disposed) { setMapState("error"); setMapError("O Google Maps não autorizou a exibição neste endereço. A configuração do serviço precisa ser revisada."); } };
    window.addEventListener(MAPS_AUTH_ERROR, authFailure);
    loadGoogleMaps(googleMapsApiKey).then((google) => {
      if (disposed || !canvasRef.current) return;
      googleRef.current = google;
      mapRef.current = new google.maps.Map(canvasRef.current, {
        center: { lat: destino.latitude, lng: destino.longitude }, zoom: 14,
        disableDefaultUI: true, zoomControl: true, controlSize: 44,
        gestureHandling: "cooperative", clickableIcons: false,
        mapTypeControl: false, streetViewControl: false, fullscreenControl: !compact,
        backgroundColor: palette.paper, styles: atelierMapStyles(dark),
      });
      setMapState("ready"); setVersion((v) => v + 1);
    }).catch((error: unknown) => {
      if (!disposed) { setMapState("error"); setMapError(error instanceof Error ? error.message : "O mapa não pôde ser carregado agora."); }
    });
    return () => {
      disposed = true;
      window.removeEventListener(MAPS_AUTH_ERROR, authFailure);
      overlays.current.forEach((item) => { item.setMap?.(null); googleRef.current?.maps.event.clearInstanceListeners(item); });
      overlays.current = [];
      if (mapRef.current) googleRef.current?.maps.event.clearInstanceListeners(mapRef.current);
      mapRef.current = null; googleRef.current = null; signatureRef.current = ""; fitRef.current = null;
    };
    // Initial center/style are updated below without recreation.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [googleCanvas, googleMapsApiKey, retry]);

  useEffect(() => {
    const google = googleRef.current, map = mapRef.current;
    if (!google || !map || !validDestination) return;
    map.setOptions({ styles: atelierMapStyles(dark), backgroundColor: palette.paper, fullscreenControl: !compact });
    overlays.current.forEach((item) => { item.setMap?.(null); google.maps.event.clearInstanceListeners(item); });
    overlays.current = [];
    const bounds = new google.maps.LatLngBounds();
    const target = { lat: destino.latitude, lng: destino.longitude };
    const addLine = (points: Coordinate[], color: string, weight: number, z: number, opacity = 1, onClick?: () => void) => {
      const line = new google.maps.Polyline({ map, path: points.map(([lat, lng]) => ({ lat, lng })), strokeColor: color, strokeWeight: weight, strokeOpacity: opacity, zIndex: z, clickable: Boolean(onClick) });
      if (onClick) line.addListener("click", onClick);
      overlays.current.push(line);
    };
    geometries.forEach((points, i) => {
      points.forEach(([lat, lng]) => bounds.extend({ lat, lng }));
      if (points.length > 1 && i !== index) addLine(points, palette.alternative, 5, 10, .9, () => setSelected(i));
    });
    if (activeGeometry) {
      addLine(activePoints, palette.halo, 11, 19);
      addLine(activePoints, palette.route, 6, 20);
      for (const segment of route?.traffic_segments || []) {
        if (!["slow", "traffic_jam"].includes(segment.speed) || !Number.isInteger(segment.start_index) || segment.start_index < 0) continue;
        const end = segment.end_index == null ? activePoints.length : segment.end_index + 1;
        const points = activePoints.slice(segment.start_index, end);
        if (points.length > 1) addLine(points, segment.speed === "slow" ? palette.slow : palette.jam, 7, 21);
      }
    }
    const first = activePoints[0];
    const origin = first ? { lat: first[0], lng: first[1] } : validOrigin ? { lat: validOrigin.latitude, lng: validOrigin.longitude } : null;
    const marker = (position: any, title: string, destination: boolean) => {
      overlays.current.push(new google.maps.Marker({ map, position, title, zIndex: 40,
        icon: { path: google.maps.SymbolPath.CIRCLE, fillColor: destination ? palette.route : palette.label, fillOpacity: 1, strokeColor: palette.halo, strokeWeight: 3, scale: destination ? 10 : 8 },
      }));
    };
    if (origin) { bounds.extend(origin); marker(origin, "Ponto de partida", false); }
    bounds.extend(target); marker(target, destino.name, true);
    fitRef.current = () => {
      if (!canvasRef.current?.clientWidth || !canvasRef.current.clientHeight) return;
      google.maps.event.trigger(map, "resize");
      if (hasGeometry || origin) map.fitBounds(bounds, compact ? 28 : 44);
      else { map.setCenter(target); map.setZoom(14); }
    };
    const signature = JSON.stringify([destino.latitude, destino.longitude, origin, geometries]);
    if (signature !== signatureRef.current) { signatureRef.current = signature; fitRef.current(); }
  }, [geometries, index, version, dark, palette, destino.latitude, destino.longitude, destino.name, validDestination, origem?.latitude, origem?.longitude, activeGeometry, activePoints, route, hasGeometry, compact]);

  // A preview can mount inside collapsed <details>; fit after real dimensions.
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || typeof ResizeObserver === "undefined") return;
    let frame = 0, size = "";
    const observer = new ResizeObserver(() => {
      const next = `${canvas.clientWidth}:${canvas.clientHeight}`;
      if (next === size || !canvas.clientWidth || !canvas.clientHeight) return;
      size = next; cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => fitRef.current?.());
    });
    observer.observe(canvas);
    return () => { observer.disconnect(); cancelAnimationFrame(frame); };
  }, [googleCanvas, version]);

  return <div className={`atelier-mobility deslocamento-painel${compact ? " deslocamento-painel--compact" : ""}${!rotas.length ? " deslocamento-painel--sem-rotas" : ""}`}>
    <div className="deslocamento-mapa" aria-label={`Mapa ${activeGeometry ? "do percurso até" : "do destino"} ${destino.name}`}>
      {googleCanvas ? <>
        <div ref={canvasRef} className="deslocamento-mapa__google" />
        {mapState === "loading" && <div className="deslocamento-mapa__status" role="status">Carregando cartografia…</div>}
        {mapState === "error" && <div className="deslocamento-mapa__status" role="status"><p>{mapError}</p><button type="button" onClick={() => setRetry((v) => v + 1)}>Tentar carregar novamente</button></div>}
      </> : !isGoogle && activeGeometry ? <svg viewBox="0 0 800 340" role="img" aria-labelledby={titleId}>
        <title id={titleId}>Geometria do percurso — representação esquemática, sem mapa de ruas</title>
        <rect width="800" height="340" fill={palette.paper} />
        {projected.map((points, i) => i !== index && points.length > 1 ? <path key={i} d={svgPath(points)} fill="none" stroke={palette.alternative} strokeWidth="5" opacity=".9" /> : null)}
        <path d={svgPath(projected[index] || [])} fill="none" stroke={palette.halo} strokeWidth="12" strokeLinecap="round" strokeLinejoin="round" />
        <path d={svgPath(projected[index] || [])} fill="none" stroke={palette.route} strokeWidth="6" strokeLinecap="round" strokeLinejoin="round" />
        {[projected[index]?.[0], projected[index]?.at(-1)].map((point, i) => point ? <circle key={i} cx={point[0]} cy={point[1]} r="9" fill={i ? palette.route : palette.label} stroke={palette.halo} strokeWidth="3" /> : null)}
      </svg> : <div className="deslocamento-mapa__indisponivel"><Icone nome="rota" /><strong>{validDestination ? "Destino localizado" : "Complete o destino"}</strong><span>{isGoogle ? "A exibição do mapa precisa de uma chave Google Maps autorizada para este site." : validDestination ? "Ainda não há um percurso geográfico disponível." : "Cadastre um local com endereço completo na Agenda."}</span></div>}
      <div className="deslocamento-mapa__legenda">
        {activeGeometry ? <><span><i style={{ background: palette.route }} />Percurso selecionado</span>{isGoogle && route?.traffic_segments?.length ? <><span><i className="lento" />Lento</span><span><i className="parado" />Congestionado</span></> : null}</> : <span>{rotas.length ? "Estimativa disponível; desenho desta rota indisponível." : "Destino cadastrado. Calcule a rota para visualizar o caminho."}</span>}
      </div>
      <div className="deslocamento-mapa__fonte">
        <span>{isGoogle ? "Google Maps" : `${provider || "Deslocamento"}${hasGeometry ? " · percurso esquemático" : ""}`}</span>
        {updated && Number.isFinite(updated.getTime()) && <time dateTime={updated.toISOString()}>Consulta às {updated.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}</time>}
        {navigationUrl && <a href={navigationUrl} target="_blank" rel="noreferrer">Abrir no Google Maps <Icone nome="seta" /></a>}
      </div>
    </div>
    {!compact && rotas.length > 0 && <div className="deslocamento-rotas" aria-label="Comparação das rotas">
      <div className="deslocamento-rotas__cabecalho"><div><strong>{rotas.length} {rotas.length === 1 ? "opção de percurso" : "opções de percurso"}</strong><span>Compare o trajeto, o tempo e o trânsito.</span></div></div>
      <div className="deslocamento-rotas__lista">{rotas.map((item, i) => <button type="button" key={`${item.provider_rank ?? item.rank}-${i}`} className={i === index ? "selecionada" : ""} aria-pressed={i === index} onClick={() => setSelected(i)}>
        <i style={{ background: i === index ? palette.route : palette.alternative }} />
        <span className="deslocamento-rota__nome"><strong>{item.recommended ? "Mais rápida" : `Percurso ${i + 1}`}</strong><small>{item.summary || `Opção ${i + 1}`}</small></span>
        <span className="deslocamento-rota__tempo"><strong>{minutes(item.duration_seconds)} min</strong><small>{kilometres(item.distance_meters)} km</small></span>
        <span className={`transito transito--${["normal", "leve", "moderado", "intenso"].includes(item.congestion) ? item.congestion : "indisponivel"}`}>{trafficName(item.congestion)}</span>
        <span className="deslocamento-rota__detalhe">{item.recommended ? "Recomendada pelo menor tempo" : item.extra_time_seconds ? `+${minutes(item.extra_time_seconds)} min em relação à mais rápida` : "Tempo equivalente à mais rápida"}{item.traffic_delay_seconds > 60 ? ` · ${minutes(item.traffic_delay_seconds)} min de trânsito adicional` : ""}{geometries[i]?.length < 2 ? " · desenho indisponível" : ""}</span>
      </button>)}</div>
    </div>}
  </div>;
}
