import { useEffect, useMemo, useRef, useState } from "react";
import Icone from "./Icone";

export type RotaDeslocamento = {
  rank: number;
  provider_rank?: number;
  recommended?: boolean;
  duration_seconds: number;
  typical_duration_seconds?: number | null;
  traffic_delay_seconds: number;
  extra_time_seconds?: number;
  distance_meters: number;
  congestion: "normal" | "leve" | "moderado" | "intenso" | string;
  summary: string;
  labels?: string[];
  geometry?: { format: "encoded_polyline"; value: string; precision: number };
  traffic_segments?: Array<{ start_index: number; end_index?: number | null; speed: string }>;
  incidents?: Array<{ type?: string; description?: string }>;
};

type Coordenada = [number, number];
type Origem = { latitude: number; longitude: number } | null;
type Destino = { latitude: number | null; longitude: number | null; name: string };

const CORES_ROTAS = ["#22d3ee", "#a78bfa", "#f8c35c"];
let carregamentoGoogleMaps: Promise<any> | null = null;

function carregarGoogleMaps(apiKey: string): Promise<any> {
  const janela = window as typeof window & { google?: any };
  if (janela.google?.maps) return Promise.resolve(janela.google);
  if (carregamentoGoogleMaps) return carregamentoGoogleMaps;
  carregamentoGoogleMaps = new Promise((resolve, reject) => {
    const existente = document.querySelector<HTMLScriptElement>('script[data-corvia-google-maps="true"]');
    const script = existente || document.createElement("script");
    if (!existente) {
      script.src = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(apiKey)}&v=weekly&language=pt-BR&region=BR`;
      script.async = true;
      script.defer = true;
      script.dataset.corviaGoogleMaps = "true";
      document.head.appendChild(script);
    }
    script.addEventListener("load", () => janela.google?.maps ? resolve(janela.google) : reject(new Error("Google Maps indisponível.")), { once: true });
    script.addEventListener("error", () => reject(new Error("Falha ao carregar Google Maps.")), { once: true });
  });
  return carregamentoGoogleMaps;
}

function decodificarPolyline(valor: string, precisao = 5): Coordenada[] {
  const coordenadas: Coordenada[] = [];
  const fator = 10 ** precisao;
  let indice = 0;
  let latitude = 0;
  let longitude = 0;
  while (indice < valor.length) {
    let resultado = 0;
    let deslocamento = 0;
    let byte: number;
    do {
      byte = valor.charCodeAt(indice++) - 63;
      resultado |= (byte & 0x1f) << deslocamento;
      deslocamento += 5;
    } while (byte >= 0x20 && indice <= valor.length);
    latitude += resultado & 1 ? ~(resultado >> 1) : resultado >> 1;

    resultado = 0;
    deslocamento = 0;
    do {
      byte = valor.charCodeAt(indice++) - 63;
      resultado |= (byte & 0x1f) << deslocamento;
      deslocamento += 5;
    } while (byte >= 0x20 && indice <= valor.length);
    longitude += resultado & 1 ? ~(resultado >> 1) : resultado >> 1;
    coordenadas.push([latitude / fator, longitude / fator]);
  }
  return coordenadas;
}

function minutos(segundos: number) {
  return Math.max(1, Math.ceil(segundos / 60));
}

function quilometros(metros: number) {
  return (metros / 1000).toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
}

function nomeTransito(valor: string) {
  return ({
    normal: "Trânsito livre",
    leve: "Fluxo leve",
    moderado: "Trânsito moderado",
    intenso: "Trânsito intenso",
  } as Record<string, string>)[valor] || "Trânsito atualizado";
}

function corTrecho(velocidade: string) {
  if (velocidade === "traffic_jam") return "#fb7185";
  if (velocidade === "slow") return "#fbbf24";
  return "#34d399";
}

export default function MapaDeslocamento({
  rotas,
  origem,
  destino,
  provider,
  updatedAt,
  googleMapsApiKey,
}: {
  rotas: RotaDeslocamento[];
  origem: Origem;
  destino: Destino;
  provider?: string;
  updatedAt?: string;
  googleMapsApiKey?: string | null;
}) {
  const [selecionada, setSelecionada] = useState(0);
  const [estadoMapa, setEstadoMapa] = useState<"carregando" | "pronto" | "erro">("carregando");
  const mapaRef = useRef<HTMLDivElement>(null);
  const indiceSelecionado = Math.min(selecionada, Math.max(0, rotas.length - 1));
  const geometrias = useMemo(() => rotas.map((rota) => {
    const geometria = rota.geometry;
    return geometria?.value ? decodificarPolyline(geometria.value, geometria.precision) : [];
  }), [rotas]);
  const projetadas = useMemo(() => {
    const pontos = geometrias.flat();
    if (pontos.length < 2) return geometrias.map(() => [] as Array<[number, number]>);
    const mediaLatitude = pontos.reduce((total, ponto) => total + ponto[0], 0) / pontos.length;
    const fatorLongitude = Math.cos(mediaLatitude * Math.PI / 180);
    const cartesianas = geometrias.map((rota) => rota.map(([lat, lng]) => [lng * fatorLongitude, lat] as [number, number]));
    const todos = cartesianas.flat();
    const minX = Math.min(...todos.map((ponto) => ponto[0]));
    const maxX = Math.max(...todos.map((ponto) => ponto[0]));
    const minY = Math.min(...todos.map((ponto) => ponto[1]));
    const maxY = Math.max(...todos.map((ponto) => ponto[1]));
    const largura = 800;
    const altura = 340;
    const margem = 34;
    const escala = Math.min((largura - 2 * margem) / Math.max(maxX - minX, 0.00001), (altura - 2 * margem) / Math.max(maxY - minY, 0.00001));
    const conteudoLargura = (maxX - minX) * escala;
    const conteudoAltura = (maxY - minY) * escala;
    const deslocarX = (largura - conteudoLargura) / 2;
    const deslocarY = (altura - conteudoAltura) / 2;
    return cartesianas.map((rota) => rota.map(([x, y]) => ([
      deslocarX + (x - minX) * escala,
      altura - (deslocarY + (y - minY) * escala),
    ] as [number, number])));
  }, [geometrias]);

  const caminho = (pontos: Array<[number, number]>) => pontos
    .map(([x, y], indice) => `${indice ? "L" : "M"}${x.toFixed(1)} ${y.toFixed(1)}`)
    .join(" ");
  const rotaAtual = rotas[indiceSelecionado] || rotas[0];
  const pontosAtuais = projetadas[indiceSelecionado] || [];
  const inicio = pontosAtuais[0];
  const fim = pontosAtuais[pontosAtuais.length - 1];
  const destinoValido = destino.latitude != null && destino.longitude != null;
  const urlNavegacao = destinoValido
    ? `https://www.google.com/maps/dir/?api=1${origem ? `&origin=${origem.latitude},${origem.longitude}` : ""}&destination=${destino.latitude},${destino.longitude}&travelmode=driving&dir_action=navigate`
    : null;
  const deveUsarGoogleMap = provider === "Google Maps" || provider === "google_maps";
  const temGeometria = geometrias.some((rota) => rota.length > 1);

  useEffect(() => {
    if (!deveUsarGoogleMap || !googleMapsApiKey || !mapaRef.current || !destinoValido) return;
    let descartado = false;
    let sobreposicoes: any[] = [];
    setEstadoMapa("carregando");
    carregarGoogleMaps(googleMapsApiKey).then((google) => {
      if (descartado || !mapaRef.current || destino.latitude == null || destino.longitude == null) return;
      const destinoLatLng = { lat: destino.latitude, lng: destino.longitude };
      const map = new google.maps.Map(mapaRef.current, {
        center: destinoLatLng,
        zoom: 14,
        disableDefaultUI: true,
        zoomControl: true,
        gestureHandling: "cooperative",
        backgroundColor: "#092f3b",
        styles: [
          { elementType: "geometry", stylers: [{ color: "#173f49" }] },
          { elementType: "labels.text.fill", stylers: [{ color: "#c1d5d9" }] },
          { elementType: "labels.text.stroke", stylers: [{ color: "#173f49" }] },
          { featureType: "road", elementType: "geometry", stylers: [{ color: "#315963" }] },
          { featureType: "road.highway", elementType: "geometry", stylers: [{ color: "#456d75" }] },
          { featureType: "poi", stylers: [{ visibility: "off" }] },
          { featureType: "transit", stylers: [{ visibility: "off" }] },
          { featureType: "water", elementType: "geometry", stylers: [{ color: "#082b38" }] },
        ],
      });
      const limites = new google.maps.LatLngBounds();
      geometrias.flat().forEach(([lat, lng]) => limites.extend({ lat, lng }));
      const ordem = geometrias.map((_, indice) => indice).sort((a, b) => Number(a === indiceSelecionado) - Number(b === indiceSelecionado));
      ordem.forEach((indice) => {
        const pontos = geometrias[indice];
        if (pontos.length < 2) return;
        const polyline = new google.maps.Polyline({
          map,
          path: pontos.map(([lat, lng]) => ({ lat, lng })),
          strokeColor: CORES_ROTAS[indice] || "#94a3b8",
          strokeOpacity: indice === indiceSelecionado ? 1 : .55,
          strokeWeight: indice === indiceSelecionado ? 7 : 5,
          zIndex: indice === indiceSelecionado ? 20 : 10 + indice,
          clickable: true,
        });
        polyline.addListener("click", () => setSelecionada(indice));
        sobreposicoes.push(polyline);
      });
      (rotaAtual?.traffic_segments || []).forEach((trecho) => {
        const ate = trecho.end_index == null ? geometrias[indiceSelecionado].length : trecho.end_index + 1;
        const pontos = geometrias[indiceSelecionado].slice(trecho.start_index, ate);
        if (pontos.length < 2) return;
        sobreposicoes.push(new google.maps.Polyline({
          map,
          path: pontos.map(([lat, lng]) => ({ lat, lng })),
          strokeColor: corTrecho(trecho.speed),
          strokeOpacity: 1,
          strokeWeight: 8,
          zIndex: 30,
        }));
      });
      const principal = geometrias[indiceSelecionado] || [];
      if (principal.length) {
        const primeiro = principal[0];
        sobreposicoes.push(new google.maps.Marker({ map, position: { lat: primeiro[0], lng: primeiro[1] }, title: "Sua localização" }));
      } else if (origem) {
        limites.extend({ lat: origem.latitude, lng: origem.longitude });
        sobreposicoes.push(new google.maps.Marker({ map, position: { lat: origem.latitude, lng: origem.longitude }, title: "Sua localização" }));
      }
      limites.extend(destinoLatLng);
      sobreposicoes.push(new google.maps.Marker({ map, position: destinoLatLng, title: destino.name }));
      if (temGeometria || origem) map.fitBounds(limites, 42);
      else { map.setCenter(destinoLatLng); map.setZoom(14); }
      setEstadoMapa("pronto");
    }).catch(() => { if (!descartado) setEstadoMapa("erro"); });
    return () => {
      descartado = true;
      sobreposicoes.forEach((item) => item.setMap?.(null));
      sobreposicoes = [];
    };
  }, [deveUsarGoogleMap, destino.latitude, destino.longitude, destino.name, destinoValido, geometrias, googleMapsApiKey, indiceSelecionado, origem, rotaAtual, temGeometria]);

  return (
    <div className="deslocamento-painel">
      <div className="deslocamento-mapa" aria-label={temGeometria ? `Mapa do percurso até ${destino.name}` : `Mapa do destino ${destino.name}`}>
        {deveUsarGoogleMap && googleMapsApiKey && destinoValido ? (
          <>
            <div ref={mapaRef} className="deslocamento-mapa__google" />
            {estadoMapa === "carregando" && <div className="deslocamento-mapa__status">Carregando mapa{temGeometria ? " e trânsito" : " do destino"}…</div>}
            {estadoMapa === "erro" && <div className="deslocamento-mapa__status">O mapa não pôde ser carregado agora.</div>}
          </>
        ) : !deveUsarGoogleMap && pontosAtuais.length > 1 ? (
          <svg viewBox="0 0 800 340" role="img" aria-labelledby="mapa-deslocamento-titulo mapa-deslocamento-desc">
            <title id="mapa-deslocamento-titulo">Percurso e rotas alternativas</title>
            <desc id="mapa-deslocamento-desc">A rota selecionada e até duas alternativas, calculadas com trânsito em tempo real.</desc>
            <defs>
              <pattern id="mapa-grade" width="48" height="48" patternUnits="userSpaceOnUse">
                <path d="M48 0H0V48" fill="none" stroke="rgba(255,255,255,.055)" strokeWidth="1" />
              </pattern>
              <filter id="mapa-sombra" x="-30%" y="-30%" width="160%" height="160%">
                <feDropShadow dx="0" dy="3" stdDeviation="4" floodColor="#001820" floodOpacity=".45" />
              </filter>
            </defs>
            <rect width="800" height="340" fill="#092f3b" />
            <rect width="800" height="340" fill="url(#mapa-grade)" />
            <path d="M-20 82C125 24 188 154 330 94S575 58 830 120" fill="none" stroke="rgba(255,255,255,.055)" strokeWidth="18" />
            <path d="M72 365C118 210 300 255 412 162S585 115 710 -24" fill="none" stroke="rgba(255,255,255,.05)" strokeWidth="12" />
            {projetadas.map((pontos, indice) => indice === indiceSelecionado ? null : (
              <path key={`alternativa-${indice}`} d={caminho(pontos)} fill="none" stroke={CORES_ROTAS[indice] || "#94a3b8"} strokeWidth="7" strokeLinecap="round" strokeLinejoin="round" opacity=".48" />
            ))}
            <path d={caminho(pontosAtuais)} fill="none" stroke="rgba(0,16,23,.68)" strokeWidth="13" strokeLinecap="round" strokeLinejoin="round" />
            <path d={caminho(pontosAtuais)} fill="none" stroke={CORES_ROTAS[indiceSelecionado] || CORES_ROTAS[0]} strokeWidth="7" strokeLinecap="round" strokeLinejoin="round" />
            {(rotaAtual?.traffic_segments || []).map((trecho, indice) => {
              const ate = trecho.end_index == null ? pontosAtuais.length : trecho.end_index + 1;
              const pontos = pontosAtuais.slice(trecho.start_index, ate);
              return pontos.length > 1 ? <path key={`trafego-${indice}`} d={caminho(pontos)} fill="none" stroke={corTrecho(trecho.speed)} strokeWidth="8" strokeLinecap="round" /> : null;
            })}
            {inicio && <g transform={`translate(${inicio[0]} ${inicio[1]})`} filter="url(#mapa-sombra)"><circle r="13" fill="#f8fafc" /><circle r="6" fill="#0891b2" /></g>}
            {fim && <g transform={`translate(${fim[0]} ${fim[1]})`} filter="url(#mapa-sombra)"><path d="M0 15C-3 10-12 0-12-9A12 12 0 1 1 12-9C12 0 3 10 0 15Z" fill="#fb7185" /><circle cy="-9" r="4" fill="white" /></g>}
          </svg>
        ) : (
          <div className="deslocamento-mapa__indisponivel"><Icone nome="rota" /><span>{deveUsarGoogleMap ? "Configure a chave pública do Google Maps para exibir o mapa neste painel." : destinoValido ? "Mapa interativo indisponível para o provedor atual." : "Destino ainda sem coordenadas para exibir no mapa."}</span>{urlNavegacao && <a href={urlNavegacao} target="_blank" rel="noreferrer">Ver destino no Google Maps</a>}</div>
        )}
        <div className="deslocamento-mapa__legenda">
          <span><i className="livre" />Livre</span><span><i className="lento" />Lento</span><span><i className="parado" />Congestionado</span>
        </div>
        <div className="deslocamento-mapa__fonte">
          <span>{provider || "Mapa do destino"}</span>
          {updatedAt && <time dateTime={updatedAt}>Atualizado às {new Date(updatedAt).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}</time>}
        </div>
      </div>

      <div className="deslocamento-rotas" aria-label="Comparação das rotas">
        <div className="deslocamento-rotas__cabecalho">
          <div><strong>{rotas.length} {rotas.length === 1 ? "rota disponível" : "rotas disponíveis"}</strong><span>{rotas.length ? "Selecione para comparar no mapa" : "Use sua localização para calcular o percurso"}</span></div>
          {urlNavegacao && <a href={urlNavegacao} target="_blank" rel="noreferrer">Abrir navegação <Icone nome="seta" /></a>}
        </div>
        <div className="deslocamento-rotas__lista">
          {rotas.map((rota, indice) => (
            <button
              type="button"
              key={`${rota.provider_rank || rota.rank}-${rota.summary}`}
              className={indice === indiceSelecionado ? "selecionada" : ""}
              onClick={() => setSelecionada(indice)}
              aria-pressed={indice === indiceSelecionado}
            >
              <i style={{ background: CORES_ROTAS[indice] || "#94a3b8" }} />
              <span className="deslocamento-rota__nome">
                <strong>{rota.recommended ? "Mais rápida" : `Alternativa ${indice}`}</strong>
                <small>{rota.summary || `Rota ${indice + 1}`}</small>
              </span>
              <span className="deslocamento-rota__tempo"><strong>{minutos(rota.duration_seconds)} min</strong><small>{quilometros(rota.distance_meters)} km</small></span>
              <span className={`transito transito--${rota.congestion}`}>{nomeTransito(rota.congestion)}</span>
              <span className="deslocamento-rota__detalhe">
                {rota.extra_time_seconds ? `+${minutos(rota.extra_time_seconds)} min` : "Recomendada"}
                {rota.traffic_delay_seconds > 60 && ` · atraso de ${minutos(rota.traffic_delay_seconds)} min`}
                {rota.incidents?.length ? ` · ${rota.incidents.length} alerta${rota.incidents.length > 1 ? "s" : ""}` : ""}
              </span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
