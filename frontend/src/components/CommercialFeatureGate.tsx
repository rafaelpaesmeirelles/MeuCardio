import { useEffect, useState, type ReactNode } from "react";
import { Link } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import { canUseCommercialFeature, type CommercialFeature, type CommercialStatus } from "../lib/commercialPlans";

export default function CommercialFeatureGate({ feature, children }: { feature: CommercialFeature; children: ReactNode }) {
  const [status, setStatus] = useState<CommercialStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    api.get<CommercialStatus>("/billing/status")
      .then((result) => { if (active) setStatus(result); })
      .catch((e) => { if (active) setError(e instanceof ApiError ? e.message : "Não foi possível verificar seu acesso."); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [attempt]);

  if (loading) return <div className="pagina"><p role="status">Verificando seu acesso…</p></div>;
  if (canUseCommercialFeature(status, feature)) return <>{children}</>;

  return (
    <div className="pagina">
      <div className="cartao" style={{ maxWidth: "640px" }}>
        <p className="eyebrow">{feature === "ai" ? "Recursos de IA" : "CorVIA Mail"}</p>
        <h1>{error ? "Não foi possível verificar o acesso" : "Conheça os planos que incluem este recurso"}</h1>
        {error ? <p role="alert">{error}</p> : (
          <p>{feature === "ai"
            ? "Assistentes, análise de exames e discussões com IA estão nos planos CorVIA IA e CorVIA Completo. A busca Tudo com Tudo e o acervo científico continuam incluídos em todos os planos."
            : "O CorVIA Mail está nos planos Básico + Mail e CorVIA Completo."}</p>
        )}
        <div style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap" }}>
          {error && <button className="botao" onClick={() => setAttempt((value) => value + 1)}>Tentar novamente</button>}
          <Link to="/assinatura" className="botao botao--secundario">Ver planos e acesso</Link>
          <Link to="/busca" className="botao botao--secundario">Buscar no Tudo com Tudo</Link>
        </div>
      </div>
    </div>
  );
}
