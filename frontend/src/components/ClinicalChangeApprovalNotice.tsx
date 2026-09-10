import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import { useAuth } from "../lib/auth";

/** One owner-only counter per mounted shell; never fetch proposal bodies here. */
export default function ClinicalChangeApprovalNotice() {
  const { usuario } = useAuth();
  const userId = usuario?.id;
  const isAdmin = usuario?.role === "admin";
  const [result, setResult] = useState<{ userId: number; pending: number } | null>(null);
  useEffect(() => {
    let active = true, sequence = 0;
    setResult(null);
    if (!isAdmin || !userId) return;
    async function refresh() {
      if (document.visibilityState === "hidden") return;
      const current = ++sequence;
      try {
        const value = await api.get<{ pending: number }>("/clinical-change-approvals/count");
        if (active && current === sequence) setResult({ userId: userId!, pending: value.pending });
      } catch (error) {
        if (active && current === sequence) setResult(null);
        // 403 is expected for administrators who are not the existing owner.
        if (error instanceof ApiError && error.status === 403) stopPolling();
      }
    }
    let timer: ReturnType<typeof setInterval> | null = null;
    function stopPolling() { if (timer) clearInterval(timer); timer = null; }
    const changed = (event: Event) => { if ((event as CustomEvent<{ userId: number }>).detail?.userId === userId) void refresh(); };
    const visible = () => { if (document.visibilityState !== "hidden") void refresh(); };
    timer = setInterval(() => void refresh(), 60000);
    void refresh();
    document.addEventListener("visibilitychange", visible);
    window.addEventListener("corvia:clinical-approvals-changed", changed);
    return () => { active = false; sequence++; stopPolling(); document.removeEventListener("visibilitychange", visible); window.removeEventListener("corvia:clinical-approvals-changed", changed); };
  }, [userId, isAdmin]);
  if (!isAdmin || result?.userId !== userId || !result?.pending) return null;
  return <aside className="clinical-change-notice" aria-label="Mudanças de conduta pendentes" style={{ padding: "12px", marginBlock: "8px", border: "1px solid currentColor", borderRadius: 10 }}>
    <Link to="/admin/mudancas-clinicas"><strong>{result.pending} mudança{result.pending === 1 ? " de conduta aguarda" : "s de conduta aguardam"} sua aprovação</strong></Link>
    <p style={{ margin: "4px 0 0", fontSize: ".85rem" }}>Novas sugestões baseadas em evidências estão disponíveis para sua revisão.</p>
  </aside>;
}
