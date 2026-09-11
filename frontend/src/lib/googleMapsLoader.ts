// One shared SDK load for the Home preview and the expanded map. A failed
// network request must not poison the promise for the rest of the session.
export const MAPS_AUTH_ERROR = "corvia:maps-auth-error";
type MapsWindow = Window & { google?: any; gm_authFailure?: () => void; corviaMapsReady?: () => void };
let pending: Promise<any> | null = null;
let authHookInstalled = false;
let authFailed = false;

export function loadGoogleMaps(apiKey: string): Promise<any> {
  const host = window as MapsWindow;
  if (!authHookInstalled) {
    const previous = host.gm_authFailure;
    host.gm_authFailure = () => {
      authFailed = true;
      window.dispatchEvent(new Event(MAPS_AUTH_ERROR));
      previous?.();
    };
    authHookInstalled = true;
  }
  if (authFailed) return Promise.reject(new Error("O Google Maps não autorizou a exibição neste endereço. Revise a configuração do serviço."));
  if (typeof host.google?.maps?.Map === "function") return Promise.resolve(host.google);
  if (pending) return pending;
  pending = new Promise((resolve, reject) => {
    const existing = document.querySelector<HTMLScriptElement>('script[data-corvia-google-maps="true"]');
    const script = existing || document.createElement("script");
    let finished = false;
    const cleanup = () => {
      window.clearTimeout(timeout);
      script.removeEventListener("load", ready);
      script.removeEventListener("error", failed);
      window.removeEventListener(MAPS_AUTH_ERROR, unauthorized);
      if (host.corviaMapsReady === ready) delete host.corviaMapsReady;
    };
    const complete = (error?: Error) => {
      if (finished) return;
      finished = true;
      cleanup();
      if (error) { script.remove(); reject(error); }
      else resolve(host.google);
    };
    const ready = () => {
      if (typeof host.google?.maps?.Map === "function") complete();
    };
    const failed = () => complete(new Error("Não foi possível carregar o mapa. Verifique a conexão e tente novamente."));
    const unauthorized = () => complete(new Error("O Google Maps não autorizou a exibição neste endereço. Revise a configuração do serviço."));
    const timeout = window.setTimeout(() => complete(new Error("O mapa demorou para responder. Tente carregar novamente.")), 15000);
    // Listeners are registered BEFORE insertion: cached scripts can load fast.
    script.addEventListener("load", ready);
    script.addEventListener("error", failed);
    window.addEventListener(MAPS_AUTH_ERROR, unauthorized);
    host.corviaMapsReady = ready;
    if (!existing) {
      script.src = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(apiKey)}&v=weekly&language=pt-BR&region=BR&loading=async&callback=corviaMapsReady`;
      script.async = true;
      script.dataset.corviaGoogleMaps = "true";
      document.head.appendChild(script);
    }
    ready();
  }).catch((error: unknown) => { pending = null; throw error; });
  return pending;
}
