import { useEffect } from "react";

const BASE = import.meta.env.VITE_API_URL ?? "/api";

/** Presença agregada: apenas sessão autenticada e página visível. */
export function useActivityHeartbeat(userId: number | undefined) {
  useEffect(() => {
    if (userId === undefined) return;
    let inFlight = false;
    let stopped = false;
    let lastSent = 0;
    const controller = new AbortController();
    async function heartbeat() {
      if (stopped || inFlight || document.visibilityState !== "visible" || Date.now() - lastSent < 25_000) return;
      inFlight = true;
      lastSent = Date.now();
      try {
        const response = await fetch(`${BASE}/presence/heartbeat`, {
          method: "POST",
          credentials: "include",
          cache: "no-store",
          signal: controller.signal,
        });
        // A chamada em segundo plano não redireciona nem interfere no login.
        if (response.status === 401 || response.status === 403) stopped = true;
      } catch {
        // Falha de rede será tentada no próximo intervalo visível.
      } finally {
        inFlight = false;
      }
    }
    const onVisibility = () => { void heartbeat(); };
    void heartbeat();
    const timer = window.setInterval(onVisibility, 30_000);
    document.addEventListener("visibilitychange", onVisibility);
    return () => {
      stopped = true;
      controller.abort();
      window.clearInterval(timer);
      document.removeEventListener("visibilitychange", onVisibility);
    };
  }, [userId]);
}
