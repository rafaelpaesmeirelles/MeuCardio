import { useEffect, useState } from "react";
import { api, ApiError } from "../lib/api";
import { BotaoExame } from "./Telediagnostico";

type ItemFila = {
  id: number;
  servico: string; servico_rotulo: string;
  urgencia_rotulo: string;
  exame: string | null;
  duvida: string | null;
  contato_email: string | null;
  contato_whatsapp: string | null;
  tem_arquivo: boolean;
  consentimento_em: string | null;
  prazo_em: string | null;
  atendido_em: string | null;
  resposta: string | null;
  atrasado: boolean;
  minutos_restantes: number | null;
  solicitante: { nome?: string; conselho?: string | null; email?: string };
  paciente: { nome: string; cpf: string } | null;
};

function formatarCpf(cpf: string) {
  const d = cpf.replace(/\D/g, "");
  return d.length === 11 ? `${d.slice(0, 3)}.${d.slice(3, 6)}.${d.slice(6, 9)}-${d.slice(9)}` : cpf;
}

function Prazo({ item }: { item: ItemFila }) {
  if (item.atendido_em) {
    return (
      <span className="selo">
        Atendido em {new Date(item.atendido_em).toLocaleString("pt-BR")}
      </span>
    );
  }
  if (item.minutos_restantes === null) return <span className="selo">Sem prazo</span>;

  const m = item.minutos_restantes;
  const texto = item.atrasado
    ? `Atrasado há ${Math.abs(Math.floor(m / 60))}h${String(Math.abs(m % 60)).padStart(2, "0")}`
    : `Restam ${Math.floor(m / 60)}h${String(m % 60).padStart(2, "0")}`;

  return (
    <span className="selo" style={{
      borderColor: item.atrasado ? "var(--alerta)" : "var(--acento)",
      color: item.atrasado ? "var(--alerta)" : "var(--acento)",
      background: item.atrasado ? "var(--acao-tinta)" : "var(--acento-tinta)",
    }}>
      {texto}
    </span>
  );
}

function Atender({ item, aoResponder }: { item: ItemFila; aoResponder: () => void }) {
  const [texto, setTexto] = useState(item.resposta ?? "");
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState("");
  const [aviso, setAviso] = useState<string | null>(null);

  async function responder() {
    setErro("");
    setEnviando(true);
    try {
      const r = await api.post<{ aviso?: string }>(`/pedidos/${item.id}/responder`, { resposta: texto });
      setAviso(r.aviso ?? null);
      aoResponder();
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível registrar a resposta.");
    } finally {
      setEnviando(false);
    }
  }

  if (item.atendido_em) {
    return (
      <div className="cartao cartao--clinico" style={{ marginTop: "0.6rem" }}>
        <p className="eyebrow" style={{ margin: 0 }}>Resposta enviada</p>
        <p style={{ margin: "0.3rem 0 0", whiteSpace: "pre-wrap" }}>{item.resposta}</p>
      </div>
    );
  }

  return (
    <div style={{ marginTop: "0.6rem" }}>
      <label htmlFor={`resp-${item.id}`}>Resposta</label>
      <textarea id={`resp-${item.id}`} rows={4} value={texto}
                onChange={(e) => setTexto(e.target.value)}
                placeholder="Interpretação do exame e resposta à dúvida do solicitante." />
      {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.84rem" }}>{erro}</p>}
      {aviso && (
        <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.84rem", fontWeight: 600 }}>
          {aviso}
        </p>
      )}
      <button className="botao" style={{ marginTop: "0.5rem" }}
              onClick={responder} disabled={enviando || texto.trim().length < 10}>
        {enviando ? "Registrando…" : "Registrar resposta"}
      </button>
      {item.servico === "laudo" && (
        <p style={{ fontSize: "0.8rem", color: "var(--alerta)", marginTop: "0.4rem" }}>
          Pedido de <strong>laudo assinado</strong>: registrar a resposta aqui não emite o laudo.
          A assinatura digital (VIDAAS/Gov.br) ainda não está integrada.
        </p>
      )}
    </div>
  );
}

export default function FilaTelediagnostico() {
  const [fila, setFila] = useState<ItemFila[] | null>(null);
  const [incluirAtendidos, setIncluirAtendidos] = useState(false);
  const [erro, setErro] = useState("");

  function carregar() {
    api
      .get<{ fila: ItemFila[]; total: number }>(`/pedidos/fila?incluir_atendidos=${incluirAtendidos}`)
      .then((d) => setFila(d.fila))
      .catch((e) => {
        setErro(e instanceof ApiError ? e.message : "Não foi possível carregar a fila.");
        setFila([]);
      });
  }

  useEffect(carregar, [incluirAtendidos]);

  return (
    <div className="pagina">
      <p className="eyebrow">Telediagnóstico</p>
      <h1>Fila de atendimento</h1>

      <label style={{ display: "flex", gap: "0.4rem", alignItems: "center", fontWeight: 400 }}>
        <input type="checkbox" checked={incluirAtendidos} style={{ width: "auto" }}
               onChange={(e) => setIncluirAtendidos(e.target.checked)} />
        Mostrar também os já atendidos
      </label>

      {erro && <p role="alert" style={{ color: "var(--alerta)" }}>{erro}</p>}

      {fila === null ? (
        <p>Carregando…</p>
      ) : fila.length === 0 ? (
        <div className="cartao" style={{ marginTop: "1rem" }}>
          <h3 style={{ marginTop: 0 }}>Nada na fila</h3>
          <p style={{ margin: 0, color: "var(--texto-secundario)" }}>
            Só entram aqui os pedidos com pagamento confirmado.
          </p>
        </div>
      ) : (
        <div style={{ display: "grid", gap: "1rem", marginTop: "1rem", maxWidth: 720 }}>
          {fila.map((item) => (
            <div key={item.id} className="cartao">
              <div style={{ display: "flex", justifyContent: "space-between", gap: "0.5rem", flexWrap: "wrap" }}>
                <p className="eyebrow" style={{ margin: 0 }}>
                  #{item.id} · {item.servico_rotulo} · {item.urgencia_rotulo} · {item.exame ?? "—"}
                </p>
                <Prazo item={item} />
              </div>

              <p style={{ margin: "0.5rem 0 0", fontSize: "0.86rem" }}>
                <strong>Solicitante:</strong> {item.solicitante.nome}
                {item.solicitante.conselho && ` — ${item.solicitante.conselho}`}
                {item.contato_email && ` · ${item.contato_email}`}
                {item.contato_whatsapp && ` · ${item.contato_whatsapp}`}
              </p>

              {item.paciente && (
                <p style={{ margin: "0.2rem 0 0", fontSize: "0.86rem" }}>
                  <strong>Paciente:</strong> {item.paciente.nome} · CPF {formatarCpf(item.paciente.cpf)}
                </p>
              )}

              <p style={{ margin: "0.2rem 0 0", fontSize: "0.82rem", color: "var(--texto-secundario)" }}>
                Consentimento declarado em{" "}
                {item.consentimento_em
                  ? new Date(item.consentimento_em).toLocaleString("pt-BR")
                  : "— não registrado"}
              </p>

              {item.duvida && (
                <div className="cartao" style={{ marginTop: "0.6rem", background: "var(--fundo)" }}>
                  <p className="eyebrow" style={{ margin: 0 }}>Dúvida do solicitante</p>
                  <p style={{ margin: "0.3rem 0 0", whiteSpace: "pre-wrap" }}>{item.duvida}</p>
                </div>
              )}

              {item.tem_arquivo && <BotaoExame pedidoId={item.id} />}

              <Atender item={item} aoResponder={carregar} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
