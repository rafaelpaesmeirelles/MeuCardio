import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import { useAuth } from "../lib/auth";
import { Carregando, Vazio } from "../components/Estado";
import AssinaturaExternaITI from "../components/AssinaturaExternaITI";

// Trabalho 14 (06/08/2026) — mesmo conjunto de `provedor._MANUAL_EXTERNO`
// no backend: métodos que não têm API própria e passam pelo Assinador ITI.
const METODOS_MANUAL_EXTERNO = new Set(["GOVBR", "VIDAAS", "BIRDID", "SAFEID", "NEOID", "REMOTEID"]);

type Template = { id: number; title: string; doc_type: string; body: string };
type Gerado = { id: number; title: string; doc_type: string; created_at: string; patient_name: string | null };
type GeradosResposta = {
  items: Gerado[];
  page: number;
  page_size: number;
  has_more: boolean;
  total: number;
};
type GeradoDetalhe = {
  template_id: number | null;
  variables: Record<string, string> | null;
  patient_name: string | null;
};
type Provedor = {
  codigo: string;
  nome: string;
  nivel: string;
  familia: string;
  disponivel: boolean;
  motivo: string | null;
};

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

function GerarDocumento({ template, provedores, valoresIniciais, onFechar, onGerado }: {
  template: Template;
  provedores: Provedor[] | null;
  valoresIniciais?: Record<string, string>;
  onFechar: () => void;
  onGerado: () => void;
}) {
  const { usuario } = useAuth();
  const variaveis = variaveisDoModelo(template.body);
  const [valores, setValores] = useState<Record<string, string>>(valoresIniciais ?? {});
  const [endereco, setEndereco] = useState<"" | "residencial" | "profissional">("");
  const [patientName, setPatientName] = useState(
    valoresIniciais?.nome_paciente ?? valoresIniciais?.paciente ?? valoresIniciais?.nome ?? "",
  );
  const [metodo, setMetodo] = useState(usuario?.assinatura_metodo_preferido ?? "MANUAL");
  const [gerando, setGerando] = useState(false);
  const [erro, setErro] = useState("");
  const [geradoId, setGeradoId] = useState<number | null>(null);
  const [email, setEmail] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [resultadoEnvio, setResultadoEnvio] = useState<{ enviado: boolean; link: string | null } | null>(null);
  const [aguardandoExterno, setAguardandoExterno] = useState(false);
  const [assinadoExternoAgora, setAssinadoExternoAgora] = useState(false);

  const faltando = variaveis.filter((v) => !valores[v]?.trim());

  async function gerar() {
    setGerando(true);
    setErro("");
    try {
      const r = await api.post<{ id: number }>("/document-templates/gerar", {
        template_id: template.id,
        variables: valores,
        endereco: endereco || null,
        patient_name: patientName.trim() || null,
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
      const blob = await api.blob(
        `/document-templates/gerados/${geradoId}/pdf?metodo=${encodeURIComponent(metodo)}`,
      );
      baixarBlob(blob, `${template.doc_type}-${geradoId}.pdf`);
      setAguardandoExterno(METODOS_MANUAL_EXTERNO.has(metodo));
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
        `/document-templates/gerados/${geradoId}/enviar-email`,
        { email },
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
          <input
            value={patientName}
            onChange={(e) => setPatientName(e.target.value)}
            placeholder="Usado para organizar e pesquisar o histórico"
          />
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

          {aguardandoExterno && geradoId && (
            <AssinaturaExternaITI
              metodo={metodo}
              nomeProvedor={provedores?.find((p) => p.codigo === metodo)?.nome ?? metodo}
              enviarUrl={`/document-templates/gerados/${geradoId}/assinatura-externa`}
              onConcluido={() => {
                setAguardandoExterno(false);
                setAssinadoExternoAgora(true);
              }}
            />
          )}
          {assinadoExternoAgora && (
            <p style={{ color: "var(--sucesso)", fontSize: "0.86rem", marginTop: "0.4rem" }}>
              Assinatura conferida com sucesso — o documento já está assinado.
            </p>
          )}

          <div style={{ marginTop: "0.8rem" }}>
            <label>Enviar por e-mail ao paciente (link seguro, válido por 7 dias)</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="paciente@exemplo.com"
            />
            <button
              className="botao"
              style={{ marginTop: "0.4rem" }}
              onClick={enviar}
              disabled={enviando || !email}
            >
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
  const [paginaGerados, setPaginaGerados] = useState(1);
  const [temMaisGerados, setTemMaisGerados] = useState(false);
  const [carregandoMais, setCarregandoMais] = useState(false);
  const [provedores, setProvedores] = useState<Provedor[] | null>(null);
  const [erroGerados, setErroGerados] = useState("");
  const [buscaGerados, setBuscaGerados] = useState("");
  const [tipoGerados, setTipoGerados] = useState("");

  const recarregar = () => api.get<Template[]>("/document-templates").then(setLista);

  function caminhoGerados(pagina: number) {
    const p = new URLSearchParams({ page: String(pagina), page_size: "20" });
    if (buscaGerados.trim()) p.set("nome", buscaGerados.trim());
    if (tipoGerados) p.set("tipo", tipoGerados);
    return `/document-templates/gerados?${p}`;
  }

  async function recarregarGerados() {
    const resposta = await api.get<GeradosResposta>(caminhoGerados(1));
    setGerados(resposta.items);
    setPaginaGerados(resposta.page);
    setTemMaisGerados(resposta.has_more);
  }

  async function carregarMaisGerados() {
    setCarregandoMais(true);
    setErroGerados("");
    try {
      const resposta = await api.get<GeradosResposta>(caminhoGerados(paginaGerados + 1));
      setGerados((atuais) => [...(atuais ?? []), ...resposta.items]);
      setPaginaGerados(resposta.page);
      setTemMaisGerados(resposta.has_more);
    } catch (e) {
      setErroGerados(e instanceof ApiError ? e.message : "Não foi possível carregar mais documentos.");
    } finally {
      setCarregandoMais(false);
    }
  }

  useEffect(() => {
    recarregar();
    api.get<Provedor[]>("/assinatura/provedores").then(setProvedores).catch(() => {});
  }, []);

  useEffect(() => {
    let ativo = true;
    setGerados(null);
    setErroGerados("");
    setPaginaGerados(1);
    api.get<GeradosResposta>(caminhoGerados(1))
      .then((resposta) => {
        if (!ativo) return;
        setGerados(resposta.items);
        setPaginaGerados(resposta.page);
        setTemMaisGerados(resposta.has_more);
      })
      .catch((e) => {
        if (ativo) setErroGerados(e instanceof ApiError ? e.message : "Não foi possível carregar o histórico.");
      });
    return () => { ativo = false; };
  }, [buscaGerados, tipoGerados]);

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
      setValoresIniciais({
        ...(detalhe.variables ?? {}),
        nome_paciente: detalhe.patient_name ?? detalhe.variables?.nome_paciente ?? "",
      });
      setGerandoDe(template);
      document.getElementById(`modelo-${template.id}`)?.scrollIntoView({ behavior: "smooth", block: "center" });
    } catch (e) {
      setErroGerados(e instanceof ApiError ? e.message : "Não foi possível recriar este documento.");
    }
  }

  const gruposGerados = new Map<string, Gerado[]>();
  for (const gerado of gerados ?? []) {
    const paciente = gerado.patient_name?.trim() || "Paciente não informado";
    gruposGerados.set(paciente, [...(gruposGerados.get(paciente) ?? []), gerado]);
  }

  return (
    <>
      <p className="eyebrow">Documentos</p>
      <h1>Modelos de atestado e laudo</h1>
      <p style={{ color: "var(--texto-secundario)", maxWidth: "60ch" }}>
        Crie modelos com variáveis entre chaves duplas — ex.: <code>{"{{dias_afastamento}}"}</code> —
        preenchidas na hora de gerar o documento.
      </p>

      <Link to="/avaliacao-preoperatoria" className="cartao cartao--clinico"
            style={{ display: "block", marginTop: "0.8rem", color: "inherit" }}>
        <p className="eyebrow" style={{ margin: 0 }}>Função relacionada</p>
        <strong>Avaliação Cardiológica Pré-Operatória de Risco Cirúrgico</strong>
        <p style={{ margin: "0.2rem 0 0", fontSize: "0.86rem", color: "var(--texto-secundario)" }}>
          Escores de risco cirúrgico (RCRI, Gupta MICA) direto num documento pronto para
          assinar, imprimir ou enviar ao paciente.
        </p>
      </Link>

      <button
        className="botao"
        style={{ marginTop: "0.8rem" }}
        onClick={() => setEditando({ title: "", doc_type: "atestado", body: "" })}
      >
        + Novo modelo
      </button>

      {editando && (
        <div className="cartao" style={{ marginTop: "0.8rem" }}>
          <label>Título</label>
          <input value={editando.title ?? ""} onChange={(e) => setEditando({ ...editando, title: e.target.value })} />
          <label style={{ marginTop: "0.5rem" }}>Tipo</label>
          <select
            value={editando.doc_type ?? "atestado"}
            onChange={(e) => setEditando({ ...editando, doc_type: e.target.value })}
          >
            <option value="atestado">Atestado</option>
            <option value="laudo">Laudo</option>
            <option value="outro">Outro</option>
          </select>
          <label style={{ marginTop: "0.5rem" }}>Corpo do documento</label>
          <textarea
            rows={8}
            value={editando.body ?? ""}
            placeholder={"Atesto que o(a) paciente {{nome}} necessita de afastamento de suas atividades por {{dias_afastamento}} dias, a partir de {{data_inicio}}, por motivo de {{motivo}}."}
            onChange={(e) => setEditando({ ...editando, body: e.target.value })}
          />
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
                  <button
                    className="botao"
                    style={{ padding: "0.3rem 0.6rem" }}
                    onClick={() => {
                      setGerandoDe(gerandoDe?.id === t.id ? null : t);
                      setValoresIniciais(undefined);
                    }}
                  >
                    Usar
                  </button>
                  <button
                    className="botao botao--secundario"
                    style={{ padding: "0.3rem 0.6rem" }}
                    onClick={() => setEditando(t)}
                  >
                    Editar
                  </button>
                  <button
                    className="botao botao--secundario"
                    style={{ padding: "0.3rem 0.6rem" }}
                    onClick={() => apagar(t.id)}
                  >
                    Apagar
                  </button>
                </div>
              </div>
              {gerandoDe?.id === t.id && (
                <GerarDocumento
                  template={t}
                  provedores={provedores}
                  valoresIniciais={valoresIniciais}
                  onFechar={() => {
                    setGerandoDe(null);
                    setValoresIniciais(undefined);
                  }}
                  onGerado={recarregarGerados}
                />
              )}
            </div>
          ))
        )}
      </div>

      <h2 style={{ marginTop: "2rem" }}>Documentos gerados</h2>
      <div className="grade grade--2" style={{ marginBottom: "0.8rem" }}>
        <div>
          <label>Procurar pelo paciente</label>
          <input
            value={buscaGerados}
            onChange={(e) => setBuscaGerados(e.target.value)}
            placeholder="Nome completo ou parte do nome"
          />
        </div>
        <div>
          <label>Tipo de documento</label>
          <select value={tipoGerados} onChange={(e) => setTipoGerados(e.target.value)}>
            <option value="">Todos</option>
            <option value="atestado">Atestado</option>
            <option value="laudo">Laudo</option>
            <option value="outro">Outro</option>
          </select>
        </div>
      </div>
      {erroGerados && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erroGerados}</p>}
      {gerados === null ? (
        <Carregando />
      ) : gerados.length === 0 ? (
        <Vazio titulo="Nenhum documento gerado ainda" />
      ) : (
        <>
          {[...gruposGerados.entries()]
            .sort(([a], [b]) => a.localeCompare(b, "pt-BR"))
            .map(([paciente, documentos]) => (
              <section key={paciente} style={{ marginBottom: "1rem" }}>
                <h3 style={{ marginBottom: "0.45rem" }}>{paciente}</h3>
                {documentos.map((g) => (
                  <div
                    key={g.id}
                    className="cartao"
                    style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}
                  >
                    <div>
                      <p className="eyebrow" style={{ margin: 0 }}>{RÓTULO[g.doc_type] ?? g.doc_type}</p>
                      <strong>{g.title}</strong>
                      <p style={{ margin: 0, fontSize: "0.8rem", color: "var(--texto-secundario)" }}>
                        {new Date(g.created_at).toLocaleString("pt-BR")}
                      </p>
                    </div>
                    <div style={{ display: "flex", gap: 6 }}>
                      <button
                        className="botao botao--secundario"
                        style={{ padding: "0.3rem 0.6rem" }}
                        onClick={() => recriarBaseadoEm(g.id)}
                      >
                        Recriar baseado neste
                      </button>
                      <button
                        className="botao botao--secundario"
                        style={{ padding: "0.3rem 0.6rem" }}
                        onClick={async () => {
                          const blob = await api.blob(`/document-templates/gerados/${g.id}/pdf`);
                          baixarBlob(blob, `${g.doc_type}-${g.id}.pdf`);
                        }}
                      >
                        Baixar PDF
                      </button>
                    </div>
                  </div>
                ))}
              </section>
            ))}
          {temMaisGerados && (
            <button
              className="botao botao--secundario"
              onClick={carregarMaisGerados}
              disabled={carregandoMais}
            >
              {carregandoMais ? "Carregando…" : "Carregar mais"}
            </button>
          )}
        </>
      )}
    </>
  );
}
