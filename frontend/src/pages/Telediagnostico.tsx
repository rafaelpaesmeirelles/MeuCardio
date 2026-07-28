import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import { useAuth } from "../lib/auth";

type Preco = {
  servico: string; servico_rotulo: string;
  urgencia: string; urgencia_rotulo: string;
  preco_centavos: number;
};
type Tabela = { precos: Preco[]; exames_aceitos: { codigo: string; rotulo: string }[] };

type Pedido = {
  id: number;
  servico: string; servico_rotulo: string;
  urgencia: string; urgencia_rotulo: string;
  exame: string | null;
  preco_centavos: number;
  status: string;
  duvida: string | null;
  tem_arquivo: boolean;
  arquivo_nome_original: string | null;
  prazo_em: string | null;
  atendido_em: string | null;
  resposta: string | null;
  created_at: string;
};

const STATUS: Record<string, string> = {
  aguardando_pagamento: "Aguardando pagamento",
  pago: "Em atendimento",
  cancelado: "Cancelado",
};

function reais(centavos: number) {
  return (centavos / 100).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function TabelaPrecos({ tabela }: { tabela: Tabela }) {
  const servicos = [...new Set(tabela.precos.map((p) => p.servico))];
  const urgencias = [...new Set(tabela.precos.map((p) => p.urgencia))];
  const valor = (s: string, u: string) =>
    tabela.precos.find((p) => p.servico === s && p.urgencia === u)?.preco_centavos;

  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.88rem" }}>
        <thead>
          <tr style={{ textAlign: "left", color: "var(--texto-secundario)" }}>
            <th style={{ padding: "0.3rem 0.6rem 0.3rem 0" }}>Serviço</th>
            {urgencias.map((u) => (
              <th key={u} style={{ padding: "0.3rem 0.6rem" }}>
                {tabela.precos.find((p) => p.urgencia === u)?.urgencia_rotulo}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {servicos.map((s) => (
            <tr key={s} style={{ borderTop: "1px solid var(--borda)" }}>
              <td style={{ padding: "0.45rem 0.6rem 0.45rem 0" }}>
                {tabela.precos.find((p) => p.servico === s)?.servico_rotulo}
              </td>
              {urgencias.map((u) => (
                <td key={u} className="dado" style={{ padding: "0.45rem 0.6rem" }}>
                  {valor(s, u) !== undefined ? reais(valor(s, u)!) : "—"}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Solicitar({ tabela, aoCriar }: { tabela: Tabela; aoCriar: () => void }) {
  const { usuario } = useAuth();
  const [form, setForm] = useState({
    exame: "", duvida: "", servico: "consultoria", urgencia: "eletivo",
    contato_email: usuario?.email ?? "", contato_whatsapp: "",
    paciente_nome: "", paciente_cpf: "", consentimento: false,
  });
  const [arquivo, setArquivo] = useState<File | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState("");

  function set<K extends keyof typeof form>(campo: K, valor: (typeof form)[K]) {
    setForm((f) => ({ ...f, [campo]: valor }));
  }

  const precoAtual = tabela.precos.find(
    (p) => p.servico === form.servico && p.urgencia === form.urgencia
  )?.preco_centavos;

  const ehLaudo = form.servico === "laudo";
  const completo =
    form.exame && form.duvida.trim().length >= 10 && arquivo && form.consentimento &&
    (!ehLaudo || (form.paciente_nome.trim() && form.paciente_cpf.replace(/\D/g, "").length === 11));

  async function enviar() {
    if (!arquivo) return;
    setErro("");
    setEnviando(true);
    try {
      // A ordem importa: o pedido precisa existir para receber os dados
      // clínicos e o arquivo, e só então o usuário vai para o pagamento.
      const { pedido, checkout_url } = await api.post<{ pedido: Pedido; checkout_url: string }>(
        "/pedidos/checkout",
        { servico: form.servico, urgencia: form.urgencia, exame: form.exame }
      );
      await api.patch(`/pedidos/${pedido.id}`, {
        duvida: form.duvida,
        contato_email: form.contato_email || null,
        contato_whatsapp: form.contato_whatsapp || null,
        paciente_nome: ehLaudo ? form.paciente_nome : null,
        paciente_cpf: ehLaudo ? form.paciente_cpf : null,
        consentimento: true,
      });
      await api.upload(`/pedidos/${pedido.id}/exame`, "arquivo", arquivo);
      aoCriar();
      window.location.assign(checkout_url);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível registrar a solicitação.");
      setEnviando(false);
    }
  }

  return (
    <div className="cartao">
      <h2 style={{ marginTop: 0 }}>Solicitar laudo ou consultoria</h2>

      <p className="aviso" style={{ borderTop: "none", marginTop: 0, paddingTop: 0 }}>
        Este exame contém dados de saúde do seu paciente. Envie apenas exames para os quais
        você já obteve o consentimento, conforme o Termo de Consentimento Livre e Esclarecido.
      </p>

      <label htmlFor="td-exame">Tipo de exame</label>
      <select id="td-exame" value={form.exame} onChange={(e) => set("exame", e.target.value)}>
        <option value="">Selecione</option>
        {tabela.exames_aceitos.map((x) => (
          <option key={x.codigo} value={x.codigo}>{x.rotulo}</option>
        ))}
      </select>

      <label htmlFor="td-arquivo" style={{ marginTop: "0.8rem" }}>Foto ou PDF do exame</label>
      <input id="td-arquivo" type="file" accept="image/jpeg,image/png,application/pdf"
             onChange={(e) => setArquivo(e.target.files?.[0] ?? null)} />
      <p style={{ fontSize: "0.8rem", color: "var(--texto-secundario)", margin: "0.25rem 0 0" }}>
        JPEG, PNG ou PDF, até 20 MB. O arquivo é guardado cifrado e só você e o cardiologista
        responsável têm acesso.
      </p>

      <label htmlFor="td-duvida" style={{ marginTop: "0.8rem" }}>Sua dúvida específica</label>
      <textarea id="td-duvida" rows={3} value={form.duvida}
                onChange={(e) => set("duvida", e.target.value)}
                placeholder="Descreva o que você precisa esclarecer neste exame." />

      <div className="grade grade--2" style={{ marginTop: "0.8rem" }}>
        <div>
          <label htmlFor="td-servico">Tipo de serviço</label>
          <select id="td-servico" value={form.servico} onChange={(e) => set("servico", e.target.value)}>
            <option value="consultoria">Consultoria — interpretação, sem laudo assinado</option>
            <option value="laudo">Laudo completo assinado</option>
          </select>
        </div>
        <div>
          <label htmlFor="td-urgencia">Urgência</label>
          <select id="td-urgencia" value={form.urgencia} onChange={(e) => set("urgencia", e.target.value)}>
            <option value="eletivo">Eletivo — até 12h</option>
            <option value="urgente">Urgente/Plantão — até 2h</option>
          </select>
        </div>
      </div>

      {form.urgencia === "urgente" && (
        <p style={{ fontSize: "0.8rem", color: "var(--texto-secundario)", marginTop: "0.4rem" }}>
          O prazo de 2h vale para pedidos pagos entre 7h e 22h. Fora dessa janela, o pedido é
          atendido no prazo eletivo de 12h.
        </p>
      )}

      {ehLaudo && (
        <div className="grade grade--2" style={{ marginTop: "0.8rem" }}>
          <div>
            <label htmlFor="td-pac-nome">Nome completo do paciente</label>
            <input id="td-pac-nome" value={form.paciente_nome}
                   onChange={(e) => set("paciente_nome", e.target.value)} />
          </div>
          <div>
            <label htmlFor="td-pac-cpf">CPF do paciente</label>
            <input id="td-pac-cpf" value={form.paciente_cpf} inputMode="numeric"
                   placeholder="000.000.000-00"
                   onChange={(e) => set("paciente_cpf", e.target.value)} />
          </div>
        </div>
      )}

      <div className="grade grade--2" style={{ marginTop: "0.8rem" }}>
        <div>
          <label htmlFor="td-email">E-mail para resposta</label>
          <input id="td-email" type="email" value={form.contato_email}
                 onChange={(e) => set("contato_email", e.target.value)} />
        </div>
        <div>
          <label htmlFor="td-whats">WhatsApp <span className="eyebrow">(opcional)</span></label>
          <input id="td-whats" value={form.contato_whatsapp}
                 onChange={(e) => set("contato_whatsapp", e.target.value)} />
        </div>
      </div>

      <label style={{ display: "flex", gap: "0.5rem", marginTop: "1rem", fontWeight: 400, alignItems: "start" }}>
        <input type="checkbox" checked={form.consentimento} style={{ width: "auto", marginTop: 3 }}
               onChange={(e) => set("consentimento", e.target.checked)} />
        <span style={{ fontSize: "0.86rem" }}>
          Confirmo que obtive o consentimento do paciente (ou responsável legal) para o envio
          deste exame e destes dados à Corvia, conforme o TCLE.
        </span>
      </label>

      <div className="fio" style={{ margin: "1rem 0", borderTop: "1px solid var(--borda)" }} />

      <p style={{ margin: 0 }}>
        Valor: <strong className="dado">{precoAtual !== undefined ? reais(precoAtual) : "—"}</strong>
      </p>

      {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erro}</p>}

      <button className="botao" style={{ marginTop: "0.8rem" }} onClick={enviar} disabled={!completo || enviando}>
        {enviando ? "Registrando…" : "Enviar e pagar"}
      </button>
      {!completo && (
        <p style={{ fontSize: "0.8rem", color: "var(--texto-secundario)", marginTop: "0.4rem" }}>
          Preencha exame, arquivo, dúvida{ehLaudo ? ", dados do paciente" : ""} e o consentimento.
        </p>
      )}
    </div>
  );
}

export function BotaoExame({ pedidoId }: { pedidoId: number }) {
  const [abrindo, setAbrindo] = useState(false);
  const [erro, setErro] = useState("");

  async function abrir() {
    setErro("");
    setAbrindo(true);
    try {
      const blob = await api.blob(`/pedidos/${pedidoId}/exame`);
      const url = URL.createObjectURL(blob);
      window.open(url, "_blank", "noopener");
      // Libera a memória sem fechar a aba recém-aberta.
      setTimeout(() => URL.revokeObjectURL(url), 60_000);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível abrir o exame.");
    } finally {
      setAbrindo(false);
    }
  }

  return (
    <>
      <button className="botao botao--secundario" style={{ marginTop: "0.5rem" }}
              onClick={abrir} disabled={abrindo}>
        {abrindo ? "Abrindo…" : "Ver o exame"}
      </button>
      {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.82rem" }}>{erro}</p>}
    </>
  );
}

function MeusPedidos({ pedidos, aoAtualizar }: { pedidos: Pedido[]; aoAtualizar: () => void }) {
  const [conferindo, setConferindo] = useState<number | null>(null);

  async function conferirPagamento(id: number) {
    setConferindo(id);
    try {
      await api.post(`/pedidos/${id}/reconciliar`);
      aoAtualizar();
    } catch {
      /* silencioso: é uma reconferência, não uma ação principal */
    } finally {
      setConferindo(null);
    }
  }

  if (pedidos.length === 0) {
    return (
      <div className="cartao">
        <h2 style={{ marginTop: 0 }}>Meus pedidos</h2>
        <p style={{ margin: 0, color: "var(--texto-secundario)" }}>Você ainda não fez nenhum pedido.</p>
      </div>
    );
  }

  return (
    <div className="cartao">
      <h2 style={{ marginTop: 0 }}>Meus pedidos</h2>
      <div style={{ display: "flex", flexDirection: "column", gap: "0.8rem" }}>
        {pedidos.map((p) => (
          <div key={p.id} style={{ borderTop: "1px solid var(--borda)", paddingTop: "0.7rem" }}>
            <p className="eyebrow" style={{ margin: 0 }}>
              #{p.id} · {p.servico_rotulo} · {p.urgencia_rotulo} · {p.exame ?? "—"}
            </p>
            <p style={{ margin: "0.2rem 0" }}>
              <strong>{STATUS[p.status] ?? p.status}</strong>
              {p.prazo_em && !p.atendido_em && (
                <span style={{ color: "var(--texto-secundario)" }}>
                  {" "}· prazo até {new Date(p.prazo_em).toLocaleString("pt-BR")}
                </span>
              )}
            </p>
            {p.duvida && (
              <p style={{ margin: "0.2rem 0", fontSize: "0.86rem", color: "var(--texto-secundario)" }}>
                {p.duvida}
              </p>
            )}
            {p.atendido_em && p.resposta && (
              <div className="cartao cartao--clinico" style={{ marginTop: "0.5rem" }}>
                <p className="eyebrow" style={{ margin: 0 }}>Resposta</p>
                <p style={{ margin: "0.3rem 0 0", whiteSpace: "pre-wrap" }}>{p.resposta}</p>
              </div>
            )}
            {p.tem_arquivo && <BotaoExame pedidoId={p.id} />}
            {p.status === "aguardando_pagamento" && (
              <button className="botao botao--secundario" style={{ marginTop: "0.5rem" }}
                      onClick={() => conferirPagamento(p.id)} disabled={conferindo === p.id}>
                {conferindo === p.id ? "Conferindo…" : "Já paguei — conferir"}
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default function Telediagnostico() {
  const [params] = useSearchParams();
  const [tabela, setTabela] = useState<Tabela | null>(null);
  const [pedidos, setPedidos] = useState<Pedido[]>([]);

  function carregarPedidos() {
    api.get<{ pedidos: Pedido[] }>("/pedidos").then((d) => setPedidos(d.pedidos)).catch(() => {});
  }

  useEffect(() => {
    api.get<Tabela>("/pedidos/precos").then(setTabela).catch(() => {});
    carregarPedidos();
  }, []);

  // Volta do Stripe: confere o pagamento em vez de esperar o webhook, que é
  // entrega assíncrona e pode demorar ou falhar.
  useEffect(() => {
    const id = params.get("pedido");
    if (id && params.get("status") === "sucesso") {
      api.post(`/pedidos/${id}/reconciliar`).then(carregarPedidos).catch(() => {});
    }
  }, [params]);

  return (
    <div className="pagina">
      <p className="eyebrow">Telediagnóstico</p>
      <h1>Laudo e consultoria à distância</h1>

      {params.get("status") === "sucesso" && (
        <div className="cartao" style={{ borderLeft: "3px solid var(--sucesso)" }}>
          <strong>Pagamento recebido.</strong> Seu pedido entrou na fila e você recebe a resposta
          pelo contato informado, dentro do prazo escolhido.
        </div>
      )}
      {params.get("status") === "cancelado" && (
        <div className="cartao" style={{ borderLeft: "3px solid var(--alerta)" }}>
          Pagamento cancelado. O pedido continua salvo — você pode concluí-lo em "Meus pedidos".
        </div>
      )}

      <div style={{ display: "grid", gap: "1rem", maxWidth: 620, marginTop: "1rem" }}>
        {tabela && (
          <div className="cartao">
            <h2 style={{ marginTop: 0 }}>Como funciona o preço</h2>
            <p style={{ marginTop: 0, color: "var(--texto-secundario)", fontSize: "0.88rem" }}>
              Exames aceitos nesta fase: {tabela.exames_aceitos.map((e) => e.rotulo).join(", ")}.
            </p>
            <TabelaPrecos tabela={tabela} />
          </div>
        )}

        {tabela && <Solicitar tabela={tabela} aoCriar={carregarPedidos} />}

        <MeusPedidos pedidos={pedidos} aoAtualizar={carregarPedidos} />
      </div>
    </div>
  );
}
