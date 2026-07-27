import { useEffect, useState } from "react";
import { api, ApiError } from "../lib/api";

type StatusAssinatura = {
  status: string;
  current_period_end: string | null;
};

const ROTULOS: Record<string, string> = {
  ativo: "Ativa",
  teste: "Período de teste",
  inativo: "Inativa",
  pendente: "Pendente",
  inadimplente: "Pagamento pendente",
  suspenso: "Suspensa por falta de pagamento",
  cancelado: "Cancelada",
  pausado: "Pausada",
};

// Mesmo conjunto de ACESSO_LIBERADO em backend/app/core/security.py.
const STATUS_COM_ACESSO = ["ativo", "teste", "inadimplente"];

export default function Assinatura() {
  const [carregando, setCarregando] = useState(true);
  const [processando, setProcessando] = useState(false);
  const [status, setStatus] = useState<StatusAssinatura | null>(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    api
      .get<StatusAssinatura>("/billing/status")
      .then(setStatus)
      .catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível carregar sua assinatura."))
      .finally(() => setCarregando(false));
  }, []);

  async function assinar() {
    setProcessando(true);
    setErro("");
    try {
      const { checkout_url } = await api.post<{ checkout_url: string }>("/billing/checkout");
      window.location.assign(checkout_url);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível iniciar o pagamento.");
      setProcessando(false);
    }
  }

  const ativa = status ? STATUS_COM_ACESSO.includes(status.status) : false;

  return (
    <div className="pagina">
      <h1>Assinatura</h1>

      {carregando ? (
        <p>Carregando…</p>
      ) : (
        <div className="cartao" style={{ maxWidth: "480px" }}>
          <p>
            Status atual: <strong>{status ? ROTULOS[status.status] ?? status.status : "—"}</strong>
          </p>

          {status?.current_period_end && (
            <p style={{ fontSize: "0.86rem", opacity: 0.8 }}>
              Renovação em: {new Date(status.current_period_end).toLocaleDateString("pt-BR")}
            </p>
          )}

          <div className="fio-dourado" style={{ margin: "1rem 0" }} />

          <p>
            <strong>R$ 20,00/mês</strong> — acesso completo à plataforma CardioBenê.
          </p>

          {erro && (
            <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>
              {erro}
            </p>
          )}

          {!ativa && (
            <button className="botao" style={{ width: "100%", marginTop: "1rem" }} onClick={assinar} disabled={processando}>
              {processando ? "Redirecionando…" : "Assinar agora"}
            </button>
          )}

          {ativa && <p style={{ color: "var(--sucesso, #0a5)", marginTop: "1rem" }}>Sua assinatura está ativa.</p>}
        </div>
      )}
    </div>
  );
}
