import { useEffect, useState } from "react";
import { api, ApiError } from "../lib/api";
import { Carregando, Vazio } from "../components/Estado";

type Template = { id: number; title: string; doc_type: string; body: string };
type Gerado = { id: number; title: string; doc_type: string; created_at: string };

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
function GerarDocumento({ template, onFechar, onGerado }: {
  template: Template; onFechar: () => void; onGerado: () => void;
}) {
  const variaveis = variaveisDoModelo(template.body);
  const [valores, setValores] = useState<Record<string, string>>({});
  const [endereco, setEndereco] = useState<"" | "residencial" | "profissional">("");
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
        template_id: template.id, variables: valores, endereco: endereco || null,
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
      const blob = await api.blob(`/document-templates/gerados/${geradoId}/pdf`);
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
          <button className="botao" onClick={baixar}>Baixar PDF</button>

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
  const [gerados, setGerados] = useState<Gerado[] | null>(null);

  const recarregar = () => api.get<Template[]>("/document-templates").then(setLista);
  const recarregarGerados = () => api.get<Gerado[]>("/document-templates/gerados").then(setGerados);
  useEffect(() => { recarregar(); recarregarGerados(); }, []);

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
            <div key={t.id} className="cartao" style={{ marginBottom: "0.5rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <p className="eyebrow" style={{ margin: 0 }}>{RÓTULO[t.doc_type] ?? t.doc_type}</p>
                  <strong>{t.title}</strong>
                </div>
                <div style={{ display: "flex", gap: 6 }}>
                  <button className="botao" style={{ padding: "0.3rem 0.6rem" }}
                          onClick={() => setGerandoDe(gerandoDe?.id === t.id ? null : t)}>
                    Usar
                  </button>
                  <button className="botao botao--secundario" style={{ padding: "0.3rem 0.6rem" }}
                          onClick={() => setEditando(t)}>Editar</button>
                  <button className="botao botao--secundario" style={{ padding: "0.3rem 0.6rem" }}
                          onClick={() => apagar(t.id)}>Apagar</button>
                </div>
              </div>
              {gerandoDe?.id === t.id && (
                <GerarDocumento template={t} onFechar={() => setGerandoDe(null)} onGerado={recarregarGerados} />
              )}
            </div>
          ))
        )}
      </div>

      <h2 style={{ marginTop: "2rem" }}>Documentos gerados</h2>
      {gerados === null ? (
        <Carregando />
      ) : gerados.length === 0 ? (
        <Vazio titulo="Nenhum documento gerado ainda" />
      ) : (
        gerados.map((g) => (
          <div key={g.id} className="cartao" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
            <div>
              <p className="eyebrow" style={{ margin: 0 }}>{RÓTULO[g.doc_type] ?? g.doc_type}</p>
              <strong>{g.title}</strong>
              <p style={{ margin: 0, fontSize: "0.8rem", color: "var(--texto-secundario)" }}>
                {new Date(g.created_at).toLocaleString("pt-BR")}
              </p>
            </div>
            <button className="botao botao--secundario" style={{ padding: "0.3rem 0.6rem" }}
                    onClick={async () => {
                      const blob = await api.blob(`/document-templates/gerados/${g.id}/pdf`);
                      baixarBlob(blob, `${g.doc_type}-${g.id}.pdf`);
                    }}>
              Baixar PDF
            </button>
          </div>
        ))
      )}
    </>
  );
}
