import { useEffect, useState } from "react";
import { api } from "../lib/api";

export const RX_QUEUE_CHANGED = "corvia:rx-queue-changed";

export default function usePrescriptionQueueBadge(isAdmin: boolean) {
  const [count, setCount] = useState<number>();

  useEffect(() => {
    if (!isAdmin) return;
    let active = true;
    const refresh = async () => {
      try {
        const capabilities = await api.get<{ rafael_signer: boolean }>("/prescricao-especial/capacidades");
        if (!active) return;
        if (!capabilities.rafael_signer) return setCount(undefined);
        const pending = await api.get<unknown[]>("/prescricao-especial/pendentes");
        if (active) setCount(pending.length);
      } catch { /* menu permanece fail-closed */ }
    };
    const changed = (event: Event) => setCount((event as CustomEvent<number>).detail);
    void refresh();
    window.addEventListener(RX_QUEUE_CHANGED, changed);
    const timer = window.setInterval(refresh, 60_000);
    return () => { active = false; window.clearInterval(timer); window.removeEventListener(RX_QUEUE_CHANGED, changed); };
  }, [isAdmin]);

  return count;
}
