const BASE = import.meta.env.VITE_API_URL ?? "/api";
const BUILD_COMMIT = String(import.meta.env.VITE_DEPLOY_COMMIT ?? "unknown");
const CHAVE_ULTIMA_RECARGA = "corvia.freshness.reload";
const INTERVALO_MINIMO_CHECK_MS = 5000;

let verificando = false;
let recargaPendente = false;
let ultimoCheckEm = 0;

function streamAtivo() {
  return Boolean((window as unknown as { __streamAtivo?: boolean }).__streamAtivo);
}

async function limparCachesDoApp() {
  if (!("caches" in window)) return;
  const nomes = await caches.keys();
  await Promise.all(
    nomes
      .filter((nome) => nome.startsWith("corvia-") || nome.startsWith("workbox-"))
      .map((nome) => caches.delete(nome)),
  );
}

async function prepararNovaVersao(commit: string) {
  const agora = Date.now();
  const ultimo = Number(sessionStorage.getItem(CHAVE_ULTIMA_RECARGA) || "0");
  if (agora - ultimo < 5000) return;

  if (streamAtivo()) {
    recargaPendente = true;
    return;
  }

  sessionStorage.setItem(CHAVE_ULTIMA_RECARGA, String(agora));
  try {
    await limparCachesDoApp();
    if ("serviceWorker" in navigator) {
      const registro = await navigator.serviceWorker.getRegistration();
      await registro?.update().catch(() => undefined);
    }
  } finally {
    const url = new URL(window.location.href);
    url.searchParams.set("__corvia_build", commit.slice(0, 12));
    window.location.replace(url.toString());
  }
}

export async function verificarVersaoAtual(forcar = false) {
  const agora = Date.now();
  if (verificando || BUILD_COMMIT === "unknown") return;
  if (!forcar && agora - ultimoCheckEm < INTERVALO_MINIMO_CHECK_MS) return;
  ultimoCheckEm = agora;
  verificando = true;
  try {
    const res = await fetch(`${BASE}/version?_=${agora}`, {
      cache: "no-store",
      credentials: "include",
      headers: { "Cache-Control": "no-cache" },
    });
    if (!res.ok) return;
    const body = await res.json() as { commit?: string };
    const servidor = String(body.commit ?? "unknown");
    if (servidor !== "unknown" && servidor !== BUILD_COMMIT) {
      await prepararNovaVersao(servidor);
    }
  } catch {
    // Sem rede: mantém o app utilizável e tenta novamente na próxima interação.
  } finally {
    verificando = false;
  }
}

export function liberarRecargaPendente() {
  if (!recargaPendente) return;
  recargaPendente = false;
  void verificarVersaoAtual(true);
}
