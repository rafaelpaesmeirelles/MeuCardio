const BASE = import.meta.env.VITE_API_URL ?? "/api";
const BUILD_COMMIT = String(import.meta.env.VITE_DEPLOY_COMMIT ?? "unknown");
const CHAVE_ATUALIZACAO_PENDENTE = "corvia.freshness.pending";
const INTERVALO_MINIMO_CHECK_MS = 60_000;

let verificando = false;
let ultimoCheckEm = 0;

async function prepararNovaVersao(commit: string) {
  // Nunca interrompe uma consulta, digitação ou fluxo clínico com reload automático.
  // A nova versão será usada na próxima navegação/reabertura normal da página.
  if (sessionStorage.getItem(CHAVE_ATUALIZACAO_PENDENTE) === commit) return;
  sessionStorage.setItem(CHAVE_ATUALIZACAO_PENDENTE, commit);
  try {
    // A página aberta ainda depende dos chunks desta versão. Preserve seu cache.
    if ("serviceWorker" in navigator) {
      const registro = await navigator.serviceWorker.getRegistration();
      await registro?.update().catch(() => undefined);
    }
  } catch {
    // Falha ao preparar atualização não pode interromper o uso atual.
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
  // Mantido por compatibilidade com streams existentes; não força recarga.
}
