import { useEffect, useState } from "react";
import { api, ApiError } from "../lib/api";

type StatusAssinatura = {
  status: string;
  current_period_end: string | null;
  plano: string | null;
  periodicidade: string | null;
};

type Periodicidade = "mensal" | "semestral" | "anual";

type Plano = {
  id: "basico" | "completo";
  nome: string;
  descricao: string;
  itens: string[];
  precos: Record<Periodicidade, string>;
};

// Preços confirmados pelo Rafael em 08/08/2026 — mensal sem mudança de valor,
// semestral/anual novos. A fonte de verdade real é o servidor
// (PRECO_CENTAVOS em billing.py); isto aqui é só o texto de vitrine.
const PLANOS: Plano[] = [
  {
    id: "basico",
    nome: "Assinatura Básica",
    descricao: "Acesso ao Site — sem CorvIA Mail",
    itens: [
      "Biblioteca científica, fluxogramas e calculadoras completos",
      "Assistente de IA clínica",
      "Round, agenda e modelos de documento",
    ],
    precos: { mensal: "R$ 49,90/mês", semestral: "R$ 269,90 a cada 6 meses", anual: "R$ 479,90/ano" },
  },
  {
    id: "completo",
    nome: "Assinatura Completa",
    descricao: "Acesso ao Site + CorvIA Mail",
    itens: [
      "Tudo da Assinatura Básica",
      "Caixa de e-mail própria @corvia.med.br com webmail integrado",
      "Sem cobrança adicional pelo CorvIA Mail",
    ],
    precos: { mensal: "R$ 59,90/mês", semestral: "R$ 323,90 a cada 6 meses", anual: "R$ 575,90/ano" },
  },
];

const ROTULO_PERIODICIDADE: Record<Periodicidade, string> = {
  mensal: "Mensal", semestral: "Semestral", anual: "Anual",
};

// Desconto em relação ao mensal × 6 ou × 12 — só texto de vitrine, calculado
// a partir dos mesmos valores fixos acima (mantidos em sincronia manual com
// PRECO_CENTAVOS do backend, única fonte real de cobrança).
const DESCONTO: Record<string, string> = {
  "basico-semestral": "≈10% de desconto vs. mensal",
  "basico-anual": "≈20% de desconto vs. mensal",
  "completo-semestral": "≈10% de desconto vs. mensal",
  "completo-anual": "≈20% de desconto vs. mensal",
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
  const [processando, setProcessando] = useState<string | null>(null);
  const [status, setStatus] = useState<StatusAssinatura | null>(null);
  const [erro, setErro] = useState("");
  const [mensagemConvidado, setMensagemConvidado] = useState("");
  const [periodicidade, setPeriodicidade] = useState<Periodicidade>("mensal");
  const [trocando, setTrocando] = useState<string | null>(null);
  const [avisoTroca, setAvisoTroca] = useState("");

  function carregarStatus() {
    return api
      .get<StatusAssinatura>("/billing/status")
      .then(setStatus)
      .catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível carregar sua assinatura."))
      .finally(() => setCarregando(false));
  }

  useEffect(() => {
    carregarStatus();
  }, []);

  async function assinar(planoId: string) {
    setProcessando(`${planoId}-${periodicidade}`);
    setErro("");
    try {
      const resultado = await api.post<{ checkout_url: string | null; convidado?: boolean; mensagem?: string }>(
        `/billing/checkout?plano=${planoId}&periodicidade=${periodicidade}`
      );
      if (resultado.convidado) {
        // Médico convidado (08/08/2026): sem Stripe, a assinatura já foi
        // liberada no servidor — só recarrega o status em vez de redirecionar.
        setMensagemConvidado(resultado.mensagem || "Médico Convidado — Acesso Completo Liberado.");
        await carregarStatus();
        setProcessando(null);
        return;
      }
      window.location.assign(resultado.checkout_url as string);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível iniciar o pagamento.");
      setProcessando(null);
    }
  }

  async function trocarPlano(planoId: string, novaPeriodicidade: Periodicidade) {
    setAvisoTroca("");
    setErro("");
    setTrocando(`${planoId}-${novaPeriodicidade}`);
    try {
      const resultado = await api.post<{ nota: string }>(
        `/billing/trocar-plano?plano=${planoId}&periodicidade=${novaPeriodicidade}`
      );
      setAvisoTroca(resultado.nota);
      await carregarStatus();
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível trocar de plano.");
    } finally {
      setTrocando(null);
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
          {mensagemConvidado && (
            <div className="cartao cartao--clinico" style={{ maxWidth: "560px", marginBottom: "1rem", borderLeftColor: "var(--sucesso)" }}>
              <p className="eyebrow" style={{ color: "var(--sucesso)" }}>Médico Convidado</p>
              <p style={{ margin: 0, fontWeight: 700 }}>{mensagemConvidado}</p>
              <p style={{ margin: "0.4rem 0 0", fontSize: "0.86rem", color: "var(--texto-secundario)" }}>
                Nenhuma cobrança foi feita. Seu acesso já está liberado.
              </p>
            </div>
          )}

          <div className="cartao" style={{ maxWidth: "560px", marginBottom: "1.5rem" }}>
            <p>
              Status atual: <strong>{status ? ROTULOS[status.status] ?? status.status : "—"}</strong>
              {ativa && status?.plano && (
                <>
                  {" "}
                  — plano <strong>{PLANOS.find((p) => p.id === status.plano)?.nome ?? status.plano}</strong>
                  {status.periodicidade && (
                    <> ({ROTULO_PERIODICIDADE[status.periodicidade as Periodicidade] ?? status.periodicidade})</>
                  )}
                </>
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
            {avisoTroca && (
              <p style={{ color: "var(--sucesso)", fontSize: "0.86rem" }}>{avisoTroca}</p>
            )}

            {ativa && <p style={{ color: "var(--sucesso)" }}>Sua assinatura está ativa.</p>}
          </div>

          {!ativa && (
            <>
              <div className="grade" style={{ gridTemplateColumns: "repeat(3, auto)", display: "inline-grid", gap: "0.4rem", marginBottom: "1rem" }}>
                {(["mensal", "semestral", "anual"] as Periodicidade[]).map((p) => (
                  <button
                    key={p}
                    className={p === periodicidade ? "botao" : "botao botao--secundario"}
                    onClick={() => setPeriodicidade(p)}
                  >
                    {ROTULO_PERIODICIDADE[p]}
                  </button>
                ))}
              </div>

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
                      <strong>{plano.precos[periodicidade]}</strong>
                    </p>
                    {periodicidade !== "mensal" && (
                      <p style={{ fontSize: "0.82rem", color: "var(--sucesso)", margin: "0 0 0.4rem" }}>
                        {DESCONTO[`${plano.id}-${periodicidade}`]}
                      </p>
                    )}
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
                      {processando === `${plano.id}-${periodicidade}` ? "Redirecionando…" : "Assinar este plano"}
                    </button>
                  </div>
                ))}
              </div>
            </>
          )}

          {ativa && status?.plano && (
            <div style={{ maxWidth: "760px", marginTop: "1rem" }}>
              <h2 style={{ fontSize: "1.05rem" }}>Trocar plano ou periodicidade</h2>
              <p style={{ fontSize: "0.86rem", color: "var(--texto-secundario)", maxWidth: "60ch" }}>
                A troca é aplicada direto na sua assinatura no Stripe, com ajuste proporcional ao
                tempo já pago no ciclo atual. Confirmamos assim que o Stripe processar.
              </p>
              <div className="grade" style={{ gridTemplateColumns: "repeat(3, auto)", display: "inline-grid", gap: "0.4rem", margin: "0.6rem 0" }}>
                {(["mensal", "semestral", "anual"] as Periodicidade[]).map((p) => (
                  <button
                    key={p}
                    className={p === periodicidade ? "botao" : "botao botao--secundario"}
                    onClick={() => setPeriodicidade(p)}
                  >
                    {ROTULO_PERIODICIDADE[p]}
                  </button>
                ))}
              </div>
              <div style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap" }}>
                {PLANOS.map((plano) => {
                  const jaEsteMesmo = plano.id === status.plano && periodicidade === status.periodicidade;
                  return (
                    <button
                      key={plano.id}
                      className="botao botao--secundario"
                      disabled={jaEsteMesmo || trocando !== null}
                      onClick={() => trocarPlano(plano.id, periodicidade)}
                    >
                      {trocando === `${plano.id}-${periodicidade}`
                        ? "Trocando…"
                        : jaEsteMesmo
                        ? `Já está no ${plano.nome} ${ROTULO_PERIODICIDADE[periodicidade]}`
                        : `Mudar para ${plano.nome} (${ROTULO_PERIODICIDADE[periodicidade]})`}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
