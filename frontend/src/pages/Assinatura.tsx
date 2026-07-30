import { useEffect, useState } from "react";
import { api, ApiError } from "../lib/api";

type StatusAssinatura = {
  status: string;
  current_period_end: string | null;
  plano: string | null;
};

type Plano = {
  id: "basico" | "completo";
  nome: string;
  preco: string;
  descricao: string;
  itens: string[];
};

const PLANOS: Plano[] = [
  {
    id: "basico",
    nome: "Acesso Completo à Plataforma",
    preco: "R$ 20,00/mês",
    descricao: "sem CorvIA Mail",
    itens: [
      "Biblioteca científica, fluxogramas e calculadoras completos",
      "Assistente de IA clínica",
      "Round, agenda e modelos de documento",
    ],
  },
  {
    id: "completo",
    nome: "Acesso Completo + CorvIA Mail",
    preco: "R$ 30,00/mês",
    descricao: "com CorvIA Mail incluso",
    itens: [
      "Tudo do plano Acesso Completo à Plataforma",
      "Caixa de e-mail própria @corvia.med.br com webmail integrado",
      "Sem cobrança adicional pelo CorvIA Mail",
    ],
  },
];

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
  const [processando, setProcessando] = useState<string | null>(null);
  const [status, setStatus] = useState<StatusAssinatura | null>(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    api
      .get<StatusAssinatura>("/billing/status")
      .then(setStatus)
      .catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível carregar sua assinatura."))
      .finally(() => setCarregando(false));
  }, []);

  async function assinar(planoId: string) {
    setProcessando(planoId);
    setErro("");
    try {
      const { checkout_url } = await api.post<{ checkout_url: string }>(`/billing/checkout?plano=${planoId}`);
      window.location.assign(checkout_url);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível iniciar o pagamento.");
      setProcessando(null);
    }
  }

  const ativa = status ? STATUS_COM_ACESSO.includes(status.status) : false;

  return (
    <div className="pagina">
      <h1>Assinatura</h1>

      {carregando ? (
        <p>Carregando…</p>
      ) : (
        <>
          <div className="cartao" style={{ maxWidth: "560px", marginBottom: "1.5rem" }}>
            <p>
              Status atual: <strong>{status ? ROTULOS[status.status] ?? status.status : "—"}</strong>
              {ativa && status?.plano && (
                <> — plano <strong>{PLANOS.find((p) => p.id === status.plano)?.nome ?? status.plano}</strong></>
              )}
            </p>

            {status?.current_period_end && (
              <p style={{ fontSize: "0.86rem", opacity: 0.8 }}>
                Renovação em: {new Date(status.current_period_end).toLocaleDateString("pt-BR")}
              </p>
            )}

            {erro && (
              <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>
                {erro}
              </p>
            )}

            {ativa && <p style={{ color: "var(--sucesso)" }}>Sua assinatura está ativa.</p>}
          </div>

          {!ativa && (
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
                gap: "1rem",
                maxWidth: "760px",
              }}
            >
              {PLANOS.map((plano) => (
                <div key={plano.id} className="cartao">
                  <h2 style={{ marginTop: 0 }}>{plano.nome}</h2>
                  <p style={{ fontSize: "1.3rem", margin: "0.2rem 0" }}>
                    <strong>{plano.preco}</strong>
                  </p>
                  <p style={{ fontSize: "0.86rem", opacity: 0.8, marginTop: 0 }}>{plano.descricao}</p>
                  <ul style={{ paddingLeft: "1.1rem", fontSize: "0.92rem" }}>
                    {plano.itens.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                  <button
                    className="botao"
                    style={{ width: "100%", marginTop: "0.5rem" }}
                    onClick={() => assinar(plano.id)}
                    disabled={processando !== null}
                  >
                    {processando === plano.id ? "Redirecionando…" : "Assinar este plano"}
                  </button>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
