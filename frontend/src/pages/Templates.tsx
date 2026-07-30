import { useEffect, useState } from "react";
import { api, ApiError } from "../lib/api";
import { Carregando, Vazio } from "../components/Estado";

type Template = {
  id: number; title: string; doc_type: string; body: string;
  slug_sistema: string | null; sistema: boolean;
};
type Gerado = { id: number; title: string; doc_type: string; created_at: string };

const RÓTULO: Record<string, string> = { atestado: "Atestado", laudo: "Laudo", outro: "Outro" };

// Itens do DASI (Duke Activity Status Index) — mesmos 12 do backend
// (app/services/calculators.py), com o peso só pra referência visual; quem
// pontua é o servidor.
const DASI_ITENS: { chave: string; rotulo: string }[] = [
  { chave: "cuidar_de_si", rotulo: "Cuidar de si mesmo (comer, vestir-se, tomar banho)" },
  { chave: "caminhar_dentro_de_casa", rotulo: "Caminhar dentro de casa" },
  { chave: "caminhar_200m_plano", rotulo: "Caminhar 1–2 quarteirões (~200 m) em terreno plano" },
  { chave: "subir_um_lance_escada", rotulo: "Subir um lance de escada ou caminhar em aclive" },
  { chave: "correr_curta_distancia", rotulo: "Correr uma curta distância" },
  { chave: "trabalho_domestico_leve", rotulo: "Trabalho doméstico leve (tirar pó, lavar louça)" },
  { chave: "trabalho_domestico_moderado", rotulo: "Trabalho doméstico moderado (aspirar, carregar compras)" },
  { chave: "trabalho_domestico_pesado", rotulo: "Trabalho doméstico pesado (esfregar chão, mover móveis)" },
  { chave: "jardinagem", rotulo: "Jardinagem ou caminhar a 6,4 km/h" },
  { chave: "relacoes_sexuais", rotulo: "Relações sexuais" },
  { chave: "recreacao_moderada", rotulo: "Recreação moderada (golfe, dançar, tênis em duplas)" },
  { chave: "esporte_extenuante", rotulo: "Esporte extenuante (natação, tênis simples, futebol)" },
];

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
  const [tituloCustomizado, setTituloCustomizado] = useState("");
  const [gerando, setGerando] = useState(false);
  const [erro, setErro] = useState("");
  const [geradoId, setGeradoId] = useState<number | null>(null);
  const [email, setEmail] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [resultadoEnvio, setResultadoEnvio] = useState<{ enviado: boolean; link: string | null } | null>(null);

  const éDocumentoEmBranco = template.slug_sistema === "documento-em-branco";
  const faltando = [
    ...variaveis.filter((v) => !valores[v]?.trim()),
    ...(éDocumentoEmBranco && !tituloCustomizado.trim() ? ["título"] : []),
  ];

  async function gerar() {
    setGerando(true);
    setErro("");
    try {
      const r = await api.post<{ id: number }>("/document-templates/gerar", {
        template_id: template.id, variables: valores, endereco: endereco || null,
        titulo_customizado: éDocumentoEmBranco ? tituloCustomizado : undefined,
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
          {éDocumentoEmBranco && (
            <div style={{ marginTop: "0.5rem" }}>
              <label>Título do documento</label>
              <input value={tituloCustomizado} onChange={(e) => setTituloCustomizado(e.target.value)}
                     placeholder="Ex.: Relatório de acompanhamento" />
            </div>
          )}
          {variaveis.length === 0 && <p style={{ fontSize: "0.86rem" }}>Este modelo não tem variáveis a preencher.</p>}
          {variaveis.map((v) => (
            <div key={v} style={{ marginTop: "0.5rem" }}>
              <label>{v}</label>
              {["conteudo", "diagnostico", "restricoes"].includes(v) ? (
                <textarea rows={4} value={valores[v] ?? ""}
                          onChange={(e) => setValores({ ...valores, [v]: e.target.value })} />
              ) : (
                <input value={valores[v] ?? ""} onChange={(e) => setValores({ ...valores, [v]: e.target.value })} />
              )}
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

/** Avaliação cardiológica de risco cirúrgico (Tarefa 30) — não é substituição
 * de {{variável}}: o sistema calcula RCRI (e DASI, se preenchido) e monta um
 * rascunho, que o médico revisa/edita antes de confirmar a emissão. Duas
 * chamadas: /rascunho (não grava nada) e a confirmação (grava GeneratedDocument
 * com o texto já revisado). */
function AvaliacaoPreOperatoria({ onFechar, onGerado }: { onFechar: () => void; onGerado: () => void }) {
  const [procedimento, setProcedimento] = useState("");
  const [categoriaRisco, setCategoriaRisco] = useState<"" | "baixo" | "intermediario" | "alto">("");
  const [rcri, setRcri] = useState<Record<string, boolean>>({});
  const [usarDasi, setUsarDasi] = useState(false);
  const [dasi, setDasi] = useState<Record<string, boolean>>({});
  const [capacidadeFuncional, setCapacidadeFuncional] = useState<"boa" | "reduzida" | "indeterminada">("indeterminada");
  const [gupta, setGupta] = useState<Record<string, string>>({});
  const [guptaCreatininaElevada, setGuptaCreatininaElevada] = useState(false);
  const [observacoes, setObservacoes] = useState("");
  const [endereco, setEndereco] = useState<"" | "residencial" | "profissional">("");

  const [gerandoRascunho, setGerandoRascunho] = useState(false);
  const [rascunho, setRascunho] = useState<string | null>(null);
  const [erro, setErro] = useState("");
  const [confirmando, setConfirmando] = useState(false);
  const [geradoId, setGeradoId] = useState<number | null>(null);
  const [email, setEmail] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [resultadoEnvio, setResultadoEnvio] = useState<{ enviado: boolean; link: string | null } | null>(null);

  const RCRI_ITENS: { chave: string; rotulo: string }[] = [
    { chave: "cirurgia_alto_risco", rotulo: "Cirurgia de alto risco (intraperitoneal, intratorácica ou vascular suprainguinal)" },
    { chave: "doenca_arterial_coronariana", rotulo: "História de doença arterial coronariana" },
    { chave: "insuficiencia_cardiaca_congestiva", rotulo: "História de insuficiência cardíaca congestiva" },
    { chave: "doenca_cerebrovascular", rotulo: "História de doença cerebrovascular (AVC ou AIT)" },
    { chave: "diabetes_insulinodependente", rotulo: "Diabetes em tratamento pré-operatório com insulina" },
    { chave: "creatinina_maior_2", rotulo: "Creatinina sérica pré-operatória > 2,0 mg/dL" },
  ];

  function payloadClinico() {
    return {
      procedimento_planejado: procedimento,
      categoria_risco_cirurgico: categoriaRisco || null,
      ...rcri,
      capacidade_funcional: capacidadeFuncional,
      ...(usarDasi ? dasi : {}),
      gupta_idade: gupta.idade || null,
      gupta_status_funcional: gupta.status_funcional || null,
      gupta_asa: gupta.asa || null,
      gupta_creatinina_elevada: guptaCreatininaElevada,
      gupta_tipo_procedimento: gupta.tipo_procedimento || null,
      observacoes_adicionais: observacoes || null,
    };
  }

  async function gerarRascunho() {
    setGerandoRascunho(true);
    setErro("");
    try {
      const r = await api.post<{ rascunho: string }>(
        "/document-templates/avaliacao-preoperatoria/rascunho", payloadClinico(),
      );
      setRascunho(r.rascunho);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível montar o rascunho.");
    } finally {
      setGerandoRascunho(false);
    }
  }

  async function confirmar() {
    if (!rascunho) return;
    setConfirmando(true);
    setErro("");
    try {
      const r = await api.post<{ id: number }>("/document-templates/avaliacao-preoperatoria", {
        corpo: rascunho, endereco: endereco || null,
      });
      setGeradoId(r.id);
      onGerado();
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível emitir a avaliação.");
    } finally {
      setConfirmando(false);
    }
  }

  async function baixar() {
    if (!geradoId) return;
    const blob = await api.blob(`/document-templates/gerados/${geradoId}/pdf`);
    baixarBlob(blob, `avaliacao-risco-cirurgico-${geradoId}.pdf`);
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

  if (geradoId) {
    return (
      <div className="cartao" style={{ marginTop: "0.8rem" }}>
        <p style={{ color: "var(--sucesso)" }}>Avaliação emitida.</p>
        <button className="botao" onClick={baixar}>Baixar PDF</button>
        <div style={{ marginTop: "0.8rem" }}>
          <label>Enviar por e-mail ao paciente (link seguro, válido por 7 dias)</label>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                 placeholder="paciente@exemplo.com" />
          <button className="botao" style={{ marginTop: "0.4rem" }} onClick={enviar} disabled={enviando || !email}>
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
      </div>
    );
  }

  return (
    <div className="cartao" style={{ marginTop: "0.8rem" }}>
      <p className="eyebrow" style={{ margin: 0 }}>Avaliação cardiológica de risco cirúrgico</p>
      <p style={{ fontSize: "0.82rem", color: "var(--texto-secundario)" }}>
        Calcula RCRI (Lee et al. 1999) e, se você preencher o questionário abaixo, DASI (Hlatky et
        al. 1989) — o Gupta MICA entra só com as variáveis registradas, sem cálculo automático
        (coeficientes não confirmados em fonte primária). O texto gerado é um rascunho: revise e
        ajuste antes de confirmar.
      </p>

      {!rascunho ? (
        <>
          <div style={{ marginTop: "0.6rem" }}>
            <label>Procedimento planejado</label>
            <input value={procedimento} onChange={(e) => setProcedimento(e.target.value)}
                   placeholder="Ex.: Correção de aneurisma de aorta abdominal" />
          </div>
          <div style={{ marginTop: "0.5rem" }}>
            <label>Risco cirúrgico do procedimento (Tabela ESC/ESAIC 2022)</label>
            <select value={categoriaRisco} onChange={(e) => setCategoriaRisco(e.target.value as typeof categoriaRisco)}>
              <option value="">Não classificado</option>
              <option value="baixo">Baixo (&lt;1%)</option>
              <option value="intermediario">Intermediário (1–5%)</option>
              <option value="alto">Alto (&gt;5%)</option>
            </select>
          </div>

          <p style={{ marginTop: "0.8rem", fontWeight: 600 }}>RCRI — Índice de Lee</p>
          {RCRI_ITENS.map((it) => (
            <label key={it.chave} style={{ display: "flex", gap: 8, alignItems: "flex-start", marginTop: "0.3rem", fontWeight: 400 }}>
              <input type="checkbox" checked={!!rcri[it.chave]}
                     onChange={(e) => setRcri({ ...rcri, [it.chave]: e.target.checked })} />
              <span>{it.rotulo}</span>
            </label>
          ))}

          <p style={{ marginTop: "0.8rem", fontWeight: 600 }}>Capacidade funcional</p>
          <label style={{ display: "flex", gap: 8, alignItems: "center", fontWeight: 400 }}>
            <input type="checkbox" checked={usarDasi} onChange={(e) => setUsarDasi(e.target.checked)} />
            <span>Usar o questionário DASI estruturado (preferido pela ESC/ESAIC 2022 e ACC/AHA 2024)</span>
          </label>
          {usarDasi ? (
            DASI_ITENS.map((it) => (
              <label key={it.chave} style={{ display: "flex", gap: 8, alignItems: "flex-start", marginTop: "0.3rem", fontWeight: 400 }}>
                <input type="checkbox" checked={!!dasi[it.chave]}
                       onChange={(e) => setDasi({ ...dasi, [it.chave]: e.target.checked })} />
                <span>{it.rotulo}</span>
              </label>
            ))
          ) : (
            <select style={{ marginTop: "0.3rem" }} value={capacidadeFuncional}
                    onChange={(e) => setCapacidadeFuncional(e.target.value as typeof capacidadeFuncional)}>
              <option value="indeterminada">Não avaliada</option>
              <option value="boa">≥4 METs — sobe dois lances de escada sem sintomas</option>
              <option value="reduzida">&lt;4 METs — não sobe dois lances de escada sem sintomas</option>
            </select>
          )}

          <p style={{ marginTop: "0.8rem", fontWeight: 600 }}>
            Gupta MICA (opcional — registrado sem cálculo de probabilidade)
          </p>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
            <div>
              <label>Idade</label>
              <input value={gupta.idade ?? ""} onChange={(e) => setGupta({ ...gupta, idade: e.target.value })} />
            </div>
            <div>
              <label>Status funcional</label>
              <select value={gupta.status_funcional ?? ""}
                      onChange={(e) => setGupta({ ...gupta, status_funcional: e.target.value })}>
                <option value="">Não informado</option>
                <option value="independente">Independente</option>
                <option value="parcialmente dependente">Parcialmente dependente</option>
                <option value="totalmente dependente">Totalmente dependente</option>
              </select>
            </div>
            <div>
              <label>Classe ASA</label>
              <select value={gupta.asa ?? ""} onChange={(e) => setGupta({ ...gupta, asa: e.target.value })}>
                <option value="">Não informada</option>
                <option value="I">I</option><option value="II">II</option>
                <option value="III">III</option><option value="IV">IV</option><option value="V">V</option>
              </select>
            </div>
            <div>
              <label>Procedimento (categoria)</label>
              <input value={gupta.tipo_procedimento ?? ""}
                     onChange={(e) => setGupta({ ...gupta, tipo_procedimento: e.target.value })} />
            </div>
          </div>
          <label style={{ display: "flex", gap: 8, alignItems: "center", marginTop: "0.4rem", fontWeight: 400 }}>
            <input type="checkbox" checked={guptaCreatininaElevada}
                   onChange={(e) => setGuptaCreatininaElevada(e.target.checked)} />
            <span>Creatinina &gt; 1,5 mg/dL</span>
          </label>

          <div style={{ marginTop: "0.6rem" }}>
            <label>Observações adicionais</label>
            <textarea rows={3} value={observacoes} onChange={(e) => setObservacoes(e.target.value)} />
          </div>

          {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erro}</p>}
          <div style={{ display: "flex", gap: 8, marginTop: "0.8rem" }}>
            <button className="botao" onClick={gerarRascunho} disabled={gerandoRascunho}>
              {gerandoRascunho ? "Calculando…" : "Montar rascunho"}
            </button>
            <button className="botao botao--secundario" onClick={onFechar}>Cancelar</button>
          </div>
        </>
      ) : (
        <>
          <label style={{ marginTop: "0.6rem" }}>Rascunho — revise e ajuste antes de emitir</label>
          <textarea rows={16} value={rascunho} onChange={(e) => setRascunho(e.target.value)} />
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
            <button className="botao" onClick={confirmar} disabled={confirmando}>
              {confirmando ? "Emitindo…" : "Confirmar e emitir"}
            </button>
            <button className="botao botao--secundario" onClick={() => setRascunho(null)}>Voltar aos dados</button>
            <button className="botao botao--secundario" onClick={onFechar}>Cancelar</button>
          </div>
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
          lista.map((t) => {
            const éAvaliacaoPreOp = t.slug_sistema === "avaliacao-risco-cirurgico";
            return (
              <div key={t.id} className="cartao" style={{ marginBottom: "0.5rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div>
                    <p className="eyebrow" style={{ margin: 0 }}>
                      {RÓTULO[t.doc_type] ?? t.doc_type}
                      {t.sistema && (
                        <span style={{ marginLeft: 8, color: "var(--acento)" }}>· Modelo do sistema</span>
                      )}
                    </p>
                    <strong>{t.title}</strong>
                  </div>
                  <div style={{ display: "flex", gap: 6 }}>
                    <button className="botao" style={{ padding: "0.3rem 0.6rem" }}
                            onClick={() => setGerandoDe(gerandoDe?.id === t.id ? null : t)}>
                      {éAvaliacaoPreOp ? "Preencher avaliação" : "Usar"}
                    </button>
                    {!t.sistema && (
                      <>
                        <button className="botao botao--secundario" style={{ padding: "0.3rem 0.6rem" }}
                                onClick={() => setEditando(t)}>Editar</button>
                        <button className="botao botao--secundario" style={{ padding: "0.3rem 0.6rem" }}
                                onClick={() => apagar(t.id)}>Apagar</button>
                      </>
                    )}
                  </div>
                </div>
                {gerandoDe?.id === t.id && (
                  éAvaliacaoPreOp ? (
                    <AvaliacaoPreOperatoria onFechar={() => setGerandoDe(null)} onGerado={recarregarGerados} />
                  ) : (
                    <GerarDocumento template={t} onFechar={() => setGerandoDe(null)} onGerado={recarregarGerados} />
                  )
                )}
              </div>
            );
          })
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
