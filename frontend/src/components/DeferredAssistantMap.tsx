import { type ComponentProps, type ComponentType, useEffect, useRef, useState } from "react";
import type MapaDeslocamento from "./MapaDeslocamento";

type MapProps = ComponentProps<typeof MapaDeslocamento>;
let loadedMap: ComponentType<MapProps> | null = null;

// Only the optional map is deferred. The assistant's state, requests and
// keyboard/focus lifecycle remain in its eagerly mounted parent.
export default function DeferredAssistantMap(props: MapProps) {
  const [Map, setMap] = useState(() => loadedMap);
  const [failed, setFailed] = useState(false);
  const [attempt, setAttempt] = useState(0);
  const slotRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (loadedMap) { setMap(() => loadedMap); return; }
    let active = true;
    import("./MapaDeslocamento").then((module) => {
      loadedMap = module.default;
      if (active) setMap(() => module.default);
    }).catch(() => { if (active) setFailed(true); });
    return () => { active = false; };
  }, [attempt]);

  return <div className="cos-assistant-map" ref={slotRef} tabIndex={-1} role="group" aria-label="Mapa do deslocamento">
    {Map ? <Map {...props} /> : <div className="atelier-mobility-empty">
      <p role={failed ? "alert" : "status"}>{failed ? "Não foi possível carregar o mapa. As outras funções do Apoio continuam disponíveis." : "Carregando mapa…"}</p>
      {failed && <button type="button" onClick={() => {
        // Keep keyboard focus inside the dialog when the retry button leaves.
        slotRef.current?.focus();
        setFailed(false);
        setAttempt((value) => value + 1);
      }}>Tentar carregar novamente</button>}
    </div>}
  </div>;
}
