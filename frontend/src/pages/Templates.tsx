import { useEffect, useState } from "react";
import { api, ApiError } from "../lib/api";
import { useAuth } from "../lib/auth";
import { Carregando, Vazio } from "../components/Estado";

type Template = { id: number; title: string; doc_type: string; body: string };
type Gerado = { id: number; title: string; doc_type: string; created_at: string; patient_name: string | null };
// GET /document-templates/gerados/{gid} — usado só por "Recriar baseado
// neste" (Tarefa 4): busca o modelo de origem e os valores usados, pra
// pré-preencher em vez de começar do zero.
type GeradoDetalhe = {
  template_id: number | null;
  variables: Record<string, string> | null;
};

// Catálogo de métodos de assinatura (Tarefa 4) — GET /assinatura/provedores.
// Escolhido no MOMENTO DO DOWNLOAD, não ao gerar: `GeneratedDocument` nasce
// só como texto (endereço é a exceção histórica, gravado ao gerar); quem
// decide se vira PDF assinado ou manual é o primeiro `GET .../pdf`.
type Provedor = { codigo: string; nome: string; nivel: string; familia: string; disponivel: boolean; motivo: string | null };

const RÓTULO: Record<string, string> = { atestado: "Atestado", laudo: "Laudo", outro: "Outro" };

function variaveisDoModelo(body: string): string[] {
  const encontradas = new Set<string>();
  for (const m of body.matchAll(/\{\{(\w+)\}\}/g)) encontradas.add(m[1]);
  return [...encontradas];
}

function baixarBlob(blob: Blob, nomeArquivo: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = nomeArquivo;
  a.click();
  URL.revokeObjectURL(url);
}

/** Formulário de "gerar documento" a partir de um modelo — preenche as
 * variáveis, gera, e a partir daí baixa PDF ou envia por e-mail (link
 * seguro, nunca o PDF anexado — ver Tarefa 29 no CLAUDE.md). */
function GerarDocumento({ template, provedores, valoresIniciais, onFechar, onGerado }: {
  template: Template; provedores: Provedor[] | null; valoresIniciais?: Record<string, string>;
  onFechar: () => void; onGerado: () => void;
}) {
  const { usuario } = useAuth();
  const variaveis = variaveisDoModelo(template.body);
  const [valores, setValores] = useState<Record<string, string>>(valoresIniciais ?? {});
  const [endereco, setEndereco] = useState<"" | "residencial" | "profissional">("");
  const [patientName, setPatientName] = useState(valoresIniciais?.nome_paciente ?? valoresIniciais?.paciente ?? valoresIniciais?.nome ?? "");
  const [metodo, setMetodo] = useState(usuario?.assinatura_metodo_preferido ?? "MANUAL");
  const [gerando, setGerando] = useState(false);
  const [erro, setErro] = useState("");
  const [geradoId, setGeradoId] = useState<number | null>(null);
  const [email, setEmail] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [resultadoEnvio, setResultadoEnvio] = useState<{ enviado: boolean; link: string | null } | null>(null);

  const faltando = variaveis.filter((v) => !valores[v]?.trim());

  async function gerar() {
    setGerando(true);
    setErro("");
    try {
      const r = await api.post<{ id: number }>("/document-templates/gerar", {
        template_id: template.id, variables: valores, endereco: endereco || null, patient_name: patientName.trim() || null,
      });
      setGeradoId(r.id);
      onGerado();
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível gerar o documento.");
    } finally {
      setGerando(false);
    }
  }

  async function baixar() {
    if (!geradoId) return;
    try {
      // `metodo` só tem efeito no PRIMEIRO download — depois disso o
      // documento já foi emitido e sempre serve os mesmos bytes.
      const blob = await api.blob(`/document-templates/gerados/${geradoId}/pdf?metodo=${encodeURIComponent(metodo)}`);
      baixarBlob(blob, `${template.doc_type}-${geradoId}.pdf`);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível baixar o PDF.");
    }
  }

  async function enviar() {
    if (!geradoId || !email) return;
    setEnviando(true);
    setErro("");
    try {
      const r = await api.post<{ enviado: boolean; link: string | null }>(
        `/document-templates/gerados/${geradoId}/enviar-email`, { email },
      );
      setResultadoEnvio(r);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível enviar o e-mail.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="cartao" style={{ marginTop: "0.8rem" }}>
      <p className="eyebrow" style={{ margin: 0 }}>Gerar a partir de "{template.title}"</p>

      {!geradoId ? (
        <>
          <label>Nome do paciente/destinatário</label>
          <input value={patientName} onChange={(e) => setPatientName(e.target.value)} placeholder="Usado para organizar e pesquisar o histórico" />
          {variaveis.length === 0 && <p style={{ fontSize: "0.86rem" }}>Este modelo não tem variáveis a preencher.</p>}
          {variaveis.map((v) => (
            <div key={v} style={{ marginTop: "0.5rem" }}>
              <label>{v}</label>
              <input value={valores[v] ?? ""} onChange={(e) => setValores({ ...valores, [v]: e.target.value })} />
            </div>
          ))}
          <div style={{ marginTop: "0.6rem" }}>
            <label>Endereço no cabeçalho/rodapé (opcional)</label>
            <select value={endereco} onChange={(e) => setEndereco(e.target.value as typeof endereco)}>
              <option value="">Nenhum</option>
              <option value="profissional">Profissional (consultório)</option>
              <option value="residencial">Residencial</option>
            </select>
          </div>
          {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erro}</p>}
          <div style={{ display: "flex", gap: 8, marginTop: "0.8rem" }}>
            <button className="botao" onClick={gerar} disabled={gerando || faltando.length > 0}>
              {gerando ? "Gerando…" : "Gerar documento"}
            </button>
            <button className="botao botao--secundario" onClick={onFechar}>Cancelar</button>
          </div>
        </>
      ) : (
        <>
          <p style={{ color: "var(--sucesso)" }}>Documento gerado.</p>

          <div style={{ marginTop: "0.4rem" }}>
            <label>Método de assinatura</label>
            <select value={metodo} onChange={(e) => setMetodo(e.target.value)}>
              {(provedores ?? []).map((p) => (
                <option key={p.codigo} value={p.codigo} disabled={!p.disponivel}>
                  {p.nome}{!p.disponivel ? " — indisponível" : ""}
                </option>
              ))}
            </select>
            {(() => {
              const escolhido = provedores?.find((p) => p.codigo === metodo);
              if (!escolhido || escolhido.disponivel) return null;
              return <p style={{ color: "var(--alerta)", fontSize: "0.82rem", margin: "0.3rem 0 0" }}>{escolhido.motivo}</p>;
            })()}
          </div>
          <button className="botao" style={{ marginTop: "0.6rem" }} onClick={baixar}>Baixar PDF</button>

          <div style={{ marginTop: "0.8rem" }}>
            <label>Enviar por e-mail ao paciente (link seguro, válido por 7 dias)</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                   placeholder="paciente@exemplo.com" />
            <button className="botao" style={{ marginTop: "0.4rem" }}
                    onClick={enviar} disabled={enviando || !email}>
              {enviando ? "Enviando…" : "Enviar por e-mail"}
            </button>
          </div>

          {resultadoEnvio && (
            resultadoEnvio.enviado ? (
              <p style={{ color: "var(--sucesso)", fontSize: "0.86rem" }}>E-mail enviado.</p>
            ) : (
              <p style={{ fontSize: "0.86rem" }}>
                O envio automático não está disponível agora. Copie o link e envie manualmente:{" "}
                <code style={{ wordBreak: "break-all" }}>{resultadoEnvio.link}</code>
              </p>
            )
          )}

          {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erro}</p>}
          <button className="botao botao--secundario" style={{ marginTop: "0.8rem" }} onClick={onFechar}>Fechar</button>
        </>
      )}
    </div>
  );
}

export default function Templates() {
  const [lista, setLista] = useState<Template[] | null>(null);
  const [editando, setEditando] = useState<Partial<Template> | null>(null);
  const [salvando, setSalvando] = useState(false);
  const [gerandoDe, setGerandoDe] = useState<Template | null>(null);
  const [valoresIniciais, setValoresIniciais] = useState<Record<string, string> | undefined>(undefined);
  const [gerados, setGerados] = useState<Gerado[] | null>(null);
  const [provedores, setProvedores] = useState<Provedor[] | null>(null);
  const [erroGerados, setErroGerados] = useState("");
  const [buscaGerados, setBuscaGerados] = useState("");
  const [tipoGerados, setTipoGerados] = useState("");

  const recarregar = () => api.get<Template[]>("/document-templates").then(setLista);
  const recarregarGerados = () => {
    const p = new URLSearchParams();
    if (buscaGerados.trim()) p.set("nome", buscaGerados.trim());
    if (tipoGerados) p.set("tipo", tipoGerados);
    return api.get<Gerado[]>(`/document-templates/gerados${p.toString() ? `?${p}` : ""}`).then(setGerados);
  };
  useEffect(() => {
    recarregar();
    recarregarGerados();
    // Falha aqui não trava a tela — GerarDocumento cai para o `<select>`
    // vazio e o default "MANUAL", que é o método que sempre funciona.
    api.get<Provedor[]>("/assinatura/provedores").then(setProvedores).catch(() => {});
  }, []);
  useEffect(() => { recarregarGerados(); }, [buscaGerados, tipoGerados]);

  async function salvar() {
    if (!editando?.title || !editando.doc_type || !editando.body) return;
    setSalvando(true);
    try {
      if (editando.id) {
        await api.put(`/document-templates/${editando.id}`, editando);
      } else {
        await api.post("/document-templates", editando);
      }
      setEditando(null);
      recarregar();
    } finally {
      setSalvando(false);
    }
  }

  async function apagar(id: number) {
    await api.delete(`/document-templates/${id}`);
    recarregar();
  }

  // "Recriar baseado neste" (Tarefa 4) — busca de qual modelo o documento
  // veio e com quais valores, e reabre o formulário de gerar já preenchido
  // (o médico edita o que precisar e gera um `GeneratedDocument` novo,
  // independente do antigo). Modelo apagado ou documento sem `template_id`
  // (gerado antes desta tarefa) não tem como recriar — avisa em vez de falhar
  // silenciosamente.
  async function recriarBaseadoEm(gid: number) {
    setErroGerados("");
    try {
      const detalhe = await api.get<GeradoDetalhe>(`/document-templates/gerados/${gid}`);
      if (!detalhe.template_id) {
        setErroGerados("Este documento foi gerado antes desta função existir — não dá pra recriar automaticamente.");
        return;
      }
      const template = lista?.find((t) => t.id === detalhe.template_id);
      if (!template) {
        setErroGerados("O modelo original não existe mais.");
        return;
      }
      setValoresIniciais(detalhe.variables ?? {});
      setGerandoDe(template);
      document.getElementById(`modelo-${template.id}`)?.scrollIntoView({ behavior: "smooth", block: "center" });
    } catch (e) {
      setErroGerados(e instanceof ApiError ? e.message : "Não foi possível recriar este documento.");
    }
  }

  return (
    <>
      <p className="eyebrow">Documentos</p>
      <h1>Modelos de atestado e laudo</h1>
      <p style={{ color: "var(--texto-secundario)", maxWidth: "60ch" }}>
        Crie modelos com variáveis entre chaves duplas — ex.: <code>{"{{dias_afastamento}}"}</code> —
        preenchidas na hora de gerar o documento.
      </p>

      <button className="botao" style={{ marginTop: "0.8rem" }}
              onClick={() => setEditando({ title: "", doc_type: "atestado", body: "" })}>
        + Novo modelo
      </button>

      {editando && (
        <div className="cartao" style={{ marginTop: "0.8rem" }}>
          <label>Título</label>
          <input value={editando.title ?? ""} onChange={(e) => setEditando({ ...editando, title: e.target.value })} />
          <label style={{ marginTop: "0.5rem" }}>Tipo</label>
          <select value={editando.doc_type ?? "atestado"}
                  onChange={(e) => setEditando({ ...editando, doc_type: e.target.value })}>
            <option value="atestado">Atestado</option>
            <option value="laudo">Laudo</option>
            <option value="outro">Outro</option>
          </select>
          <label style={{ marginTop: "0.5rem" }}>Corpo do documento</label>
          <textarea rows={8} value={editando.body ?? ""}
                    placeholder={"Atesto que o(a) paciente {{nome}} necessita de afastamento de suas atividades por {{dias_afastamento}} dias, a partir de {{data_inicio}}, por motivo de {{motivo}}."}
                    onChange={(e) => setEditando({ ...editando, body: e.target.value })} />
          <div style={{ display: "flex", gap: 8, marginTop: "0.6rem" }}>
            <button className="botao" onClick={salvar} disabled={salvando}>
              {salvando ? "Salvando…" : "Salvar modelo"}
            </button>
            <button className="botao botao--secundario" onClick={() => setEditando(null)}>Cancelar</button>
          </div>
        </div>
      )}

      <div style={{ marginTop: "1.2rem" }}>
        {lista === null ? (
          <Carregando />
        ) : lista.length === 0 ? (
          <Vazio titulo="Nenhum modelo ainda" acao="Crie o primeiro modelo acima." />
        ) : (
          lista.map((t) => (
            <div key={t.id} id={`modelo-${t.id}`} className="cartao" style={{ marginBottom: "0.5rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <p className="eyebrow" style={{ margin: 0 }}>{RÓTULO[t.doc_type] ?? t.doc_type}</p>
                  <strong>{t.title}</strong>
                </div>
                <div style={{ display: "flex", gap: 6 }}>
                  <button className="botao" style={{ padding: "0.3rem 0.6rem" }}
                          onClick={() => { setGerandoDe(gerandoDe?.id === t.id ? null : t); setValoresIniciais(undefined); }}>
                    Usar
                  </button>
                  <button className="botao botao--secundario" style={{ padding: "0.3rem 0.6rem" }}
                          onClick={() => setEditando(t)}>Editar</button>
                  <button className="botao botao--secundario" style={{ padding: "0.3rem 0.6rem" }}
                          onClick={() => apagar(t.id)}>Apagar</button>
                </div>
              </div>
              {gerandoDe?.id === t.id && (
                <GerarDocumento template={t} provedores={provedores} valoresIniciais={valoresIniciais}
                                onFechar={() => { setGerandoDe(null); setValoresIniciais(undefined); }}
                                onGerado={recarregarGerados} />
              )}
            </div>
          ))
        )}
      </div>

      <h2 style={{ marginTop: "2rem" }}>Documentos gerados</h2>
      <div className="grade grade--2" style={{ marginBottom: "0.8rem" }}>
        <div><label>Procurar pelo paciente</label><input value={buscaGerados} onChange={(e) => setBuscaGerados(e.target.value)} placeholder="Nome completo ou parte do nome" /></div>
        <div><label>Tipo de documento</label><select value={tipoGerados} onChange={(e) => setTipoGerados(e.target.value)}><option value="">Todos</option><option value="atestado">Atestado</option><option value="laudo">Laudo</option><option value="outro">Outro</option></select></div>
      </div>
      {erroGerados && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erroGerados}</p>}
      {gerados === null ? (
        <Carregando />
      ) : gerados.length === 0 ? (
        <Vazio titulo="Nenhum documento gerado ainda" />
      ) : (
        gerados.map((g) => (
          <div key={g.id} className="cartao" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
            <div>
              <p className="eyebrow" style={{ margin: 0 }}>{RÓTULO[g.doc_type] ?? g.doc_type}</p>
              <strong>{g.patient_name ?? "Paciente não informado"}</strong>
              <div style={{ fontSize: "0.86rem" }}>{g.title}</div>
              <p style={{ margin: 0, fontSize: "0.8rem", color: "var(--texto-secundario)" }}>
                {new Date(g.created_at).toLocaleString("pt-BR")}
              </p>
            </div>
            <div style={{ display: "flex", gap: 6 }}>
              <button className="botao botao--secundario" style={{ padding: "0.3rem 0.6rem" }}
                      onClick={() => recriarBaseadoEm(g.id)}>
                Recriar baseado neste
              </button>
              <button className="botao botao--secundario" style={{ padding: "0.3rem 0.6rem" }}
                      onClick={async () => {
                        const blob = await api.blob(`/document-templates/gerados/${g.id}/pdf`);
                        baixarBlob(blob, `${g.doc_type}-${g.id}.pdf`);
                      }}>
                Baixar PDF
              </button>
            </div>
          </div>
        ))
      )}
    </>
  );
}
