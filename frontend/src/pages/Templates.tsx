import { useEffect, useRef, useState } from "react";
import { api, ApiError } from "../lib/api";
import { useAuth } from "../lib/auth";
import { Carregando, Vazio } from "../components/Estado";
import AssinaturaExternaITI from "../components/AssinaturaExternaITI";
import OfertaEnvioEmailPaciente from "../components/OfertaEnvioEmailPaciente";

// Trabalho 14 (06/08/2026) — mesmo conjunto de `provedor._MANUAL_EXTERNO`
// no backend: métodos que não têm API própria e passam pelo Assinador ITI.
const METODOS_MANUAL_EXTERNO = new Set(["GOVBR", "VIDAAS", "BIRDID", "SAFEID", "NEOID", "REMOTEID", "A3_TOKEN"]);

type Template = { id: number; title: string; doc_type: string; body: string };
type Gerado = { id: number; title: string; doc_type: string; created_at: string; patient_name: string | null };
type GeradosResposta = {
  items: Gerado[];
  page: number;
  page_size: number;
  has_more: boolean;
  total: number;
};
type PatientSnapshot = {
  profile_id: number | null;
  full_name: string | null;
  cpf: string | null;
  birth_date: string | null;
  sex: string | null;
  phone: string | null;
  email: string | null;
  endereco: Endereco;
};
type GeradoDetalhe = {
  doc_type: string;
  title: string;
  template_id: number | null;
  variables: Record<string, any> | null;
  patient_name: string | null;
  rendered_body: string;
  patient_profile_id: number | null;
  patient_snapshot: PatientSnapshot | null;
};
type Provedor = {
  codigo: string;
  nome: string;
  nivel: string;
  familia: string;
  disponivel: boolean;
  motivo: string | null;
};

// 12/08/2026 — cadastro de paciente reutilizável entre documentos
// (`GET/POST/PUT/DELETE /api/pacientes`), separado do prontuário anônimo
// do Round por decisão de produto (ver CLAUDE.md) — este é o cadastro
// IDENTIFICÁVEL, escopado por médico, pensado para reaproveitar dado de
// contato do paciente em qualquer documento.
type Endereco = {
  logradouro?: string | null;
  numero?: string | null;
  complemento?: string | null;
  bairro?: string | null;
  cidade?: string | null;
  uf?: string | null;
  cep?: string | null;
};
type Paciente = {
  id: number;
  full_name: string;
  cpf: string | null;
  birth_date: string | null;
  sex: string | null;
  phone: string | null;
  email: string | null;
  endereco: Endereco;
};

const RÓTULO: Record<string, string> = {
  atestado: "Atestado",
  laudo: "Laudo",
  outro: "Outro",
  solicitacao_exames: "Solicitação de exames",
  documento_livre: "Documento em branco",
};

// Mesmos nomes de `app.services.patient_profile_service.NOMES_VARIAVEIS_
// PACIENTE` no backend — qualquer `{{...}}` desta lista, presente no corpo
// de um modelo, é preenchido a partir do paciente selecionado (ou fica
// vazio, nunca bloqueia a geração — campo ausente no cadastro não é erro).
const VARIAVEIS_PACIENTE = [
  "paciente_nome", "paciente_cpf", "paciente_data_nascimento", "paciente_sexo",
  "paciente_telefone", "paciente_email",
  "paciente_endereco_logradouro", "paciente_endereco_numero", "paciente_endereco_complemento",
  "paciente_endereco_bairro", "paciente_endereco_cidade", "paciente_endereco_uf", "paciente_endereco_cep",
  "paciente_endereco_completo",
] as const;

function formatarDataBR(iso: string | null | undefined): string {
  if (!iso) return "";
  const [ano, mes, dia] = iso.split("-");
  if (!ano || !mes || !dia) return iso;
  return `${dia}/${mes}/${ano}`;
}

// Mesma lógica (e mesmo separador " — ") de
// `app.services.patient_profile_service.montar_endereco_completo` — pula
// campo vazio sem deixar separador sobrando.
function montarEnderecoCompleto(end: Endereco | null | undefined): string {
  if (!end) return "";
  const logradouro = (end.logradouro || "").trim();
  const numero = (end.numero || "").trim();
  const complemento = (end.complemento || "").trim();
  const bairro = (end.bairro || "").trim();
  const cidade = (end.cidade || "").trim();
  const uf = (end.uf || "").trim();
  const cep = (end.cep || "").trim();

  let linha1 = logradouro;
  if (numero) linha1 = linha1 ? `${linha1}, ${numero}` : numero;
  if (complemento) linha1 = linha1 ? `${linha1} — ${complemento}` : complemento;

  const cidadeUf = cidade && uf ? `${cidade}/${uf}` : cidade || uf;
  const partes = [linha1, bairro, cidadeUf].filter(Boolean);
  if (cep) partes.push(`CEP ${cep}`);
  return partes.join(" — ");
}

function variaveisDoPaciente(p: Paciente | null): Record<string, string> {
  if (!p) return Object.fromEntries(VARIAVEIS_PACIENTE.map((k) => [k, ""]));
  return {
    paciente_nome: p.full_name || "",
    paciente_cpf: p.cpf || "",
    paciente_data_nascimento: formatarDataBR(p.birth_date),
    paciente_sexo: p.sex || "",
    paciente_telefone: p.phone || "",
    paciente_email: p.email || "",
    paciente_endereco_logradouro: p.endereco?.logradouro || "",
    paciente_endereco_numero: p.endereco?.numero || "",
    paciente_endereco_complemento: p.endereco?.complemento || "",
    paciente_endereco_bairro: p.endereco?.bairro || "",
    paciente_endereco_cidade: p.endereco?.cidade || "",
    paciente_endereco_uf: p.endereco?.uf || "",
    paciente_endereco_cep: p.endereco?.cep || "",
    paciente_endereco_completo: montarEnderecoCompleto(p.endereco),
  };
}

function variaveisDoModelo(body: string): string[] {
  const encontradas = new Set<string>();
  for (const m of body.matchAll(/\{\{(\w+)\}\}/g)) encontradas.add(m[1]);
  return [...encontradas];
}

function substituirVariaveis(body: string, valores: Record<string, string>): string {
  return body.replace(/\{\{(\w+)\}\}/g, (_match, nome) => valores[nome] ?? "");
}

function baixarBlob(blob: Blob, nomeArquivo: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = nomeArquivo;
  a.click();
  URL.revokeObjectURL(url);
}

// ————————————————————————————————————————————————————————————————————
// Seleção de paciente — camada ÚNICA e reutilizável (pedido do Rafael,
// 12/08/2026): busca no cadastro do próprio médico (isolamento por
// tenant garantido no backend, `patient_profile_for_user`), seleciona,
// mostra resumo, permite trocar, ou cadastra um novo sem sair da tela.
// Todo tipo de documento usa este MESMO componente — nunca reimplementado
// tela a tela. Quando o tipo não exige paciente cadastrado (ou o médico
// não quer cadastrar), "Sem paciente" com nome livre continua disponível.
// ————————————————————————————————————————————————————————————————————
function FormularioNovoPaciente({ onCriado, onCancelar }: {
  onCriado: (p: Paciente) => void;
  onCancelar: () => void;
}) {
  const [nome, setNome] = useState("");
  const [cpf, setCpf] = useState("");
  const [nascimento, setNascimento] = useState("");
  const [sexo, setSexo] = useState("");
  const [telefone, setTelefone] = useState("");
  const [email, setEmail] = useState("");
  const [endereco, setEndereco] = useState<Endereco>({});
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState("");

  async function salvar() {
    if (!nome.trim()) { setErro("Informe o nome do paciente."); return; }
    setSalvando(true);
    setErro("");
    try {
      const p = await api.post<Paciente>("/pacientes", {
        full_name: nome.trim(),
        cpf: cpf.trim() || null,
        birth_date: nascimento || null,
        sex: sexo || null,
        phone: telefone.trim() || null,
        email: email.trim() || null,
        endereco: Object.values(endereco).some(Boolean) ? endereco : null,
      });
      onCriado(p);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível cadastrar o paciente.");
    } finally {
      setSalvando(false);
    }
  }

  return (
    <div className="cartao" style={{ marginTop: "0.5rem" }}>
      <p className="eyebrow" style={{ margin: 0 }}>Novo paciente</p>
      <div className="grade grade--2">
        <div>
          <label>Nome completo</label>
          <input value={nome} onChange={(e) => setNome(e.target.value)} />
        </div>
        <div>
          <label>CPF (opcional)</label>
          <input value={cpf} onChange={(e) => setCpf(e.target.value)} placeholder="000.000.000-00" />
        </div>
        <div>
          <label>Data de nascimento (opcional)</label>
          <input type="date" value={nascimento} onChange={(e) => setNascimento(e.target.value)} />
        </div>
        <div>
          <label>Sexo (opcional)</label>
          <select value={sexo} onChange={(e) => setSexo(e.target.value)}>
            <option value="">Não informado</option>
            <option value="F">Feminino</option>
            <option value="M">Masculino</option>
          </select>
        </div>
        <div>
          <label>Telefone (opcional)</label>
          <input value={telefone} onChange={(e) => setTelefone(e.target.value)} />
        </div>
        <div>
          <label>E-mail (opcional)</label>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
        </div>
      </div>
      <p className="eyebrow" style={{ marginTop: "0.6rem" }}>Endereço (opcional)</p>
      <div className="grade grade--2">
        <input placeholder="Logradouro" value={endereco.logradouro ?? ""} onChange={(e) => setEndereco({ ...endereco, logradouro: e.target.value })} />
        <input placeholder="Número" value={endereco.numero ?? ""} onChange={(e) => setEndereco({ ...endereco, numero: e.target.value })} />
        <input placeholder="Complemento" value={endereco.complemento ?? ""} onChange={(e) => setEndereco({ ...endereco, complemento: e.target.value })} />
        <input placeholder="Bairro" value={endereco.bairro ?? ""} onChange={(e) => setEndereco({ ...endereco, bairro: e.target.value })} />
        <input placeholder="Cidade" value={endereco.cidade ?? ""} onChange={(e) => setEndereco({ ...endereco, cidade: e.target.value })} />
        <input placeholder="UF" maxLength={2} value={endereco.uf ?? ""} onChange={(e) => setEndereco({ ...endereco, uf: e.target.value.toUpperCase() })} />
        <input placeholder="CEP" value={endereco.cep ?? ""} onChange={(e) => setEndereco({ ...endereco, cep: e.target.value })} />
      </div>
      {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erro}</p>}
      <div style={{ display: "flex", gap: 8, marginTop: "0.6rem" }}>
        <button className="botao" onClick={salvar} disabled={salvando}>{salvando ? "Salvando…" : "Cadastrar paciente"}</button>
        <button className="botao botao--secundario" onClick={onCancelar}>Cancelar</button>
      </div>
    </div>
  );
}

function SeletorPaciente({ paciente, onSelecionar, nomeAvulso, onNomeAvulsoChange }: {
  paciente: Paciente | null;
  onSelecionar: (p: Paciente | null) => void;
  nomeAvulso: string;
  onNomeAvulsoChange: (v: string) => void;
}) {
  const [busca, setBusca] = useState("");
  const [resultados, setResultados] = useState<Paciente[] | null>(null);
  const [criando, setCriando] = useState(false);
  const [buscando, setBuscando] = useState(false);

  useEffect(() => {
    if (paciente) return;
    let ativo = true;
    setBuscando(true);
    const p = new URLSearchParams();
    if (busca.trim()) p.set("busca", busca.trim());
    api.get<Paciente[]>(`/pacientes${p.toString() ? `?${p}` : ""}`)
      .then((r) => { if (ativo) setResultados(r); })
      .catch(() => { if (ativo) setResultados([]); })
      .finally(() => { if (ativo) setBuscando(false); });
    return () => { ativo = false; };
  }, [busca, paciente]);

  if (paciente) {
    return (
      <div>
        <label>Paciente</label>
        <div className="cartao" style={{ padding: "0.6rem 0.8rem" }}>
          <strong>{paciente.full_name}</strong>
          <p style={{ margin: "0.2rem 0 0", fontSize: "0.82rem", color: "var(--texto-secundario)" }}>
            {[
              paciente.cpf && `CPF ${paciente.cpf}`,
              paciente.birth_date && `nasc. ${formatarDataBR(paciente.birth_date)}`,
              paciente.phone,
            ].filter(Boolean).join(" · ") || "Sem dados adicionais cadastrados"}
          </p>
          <button
            className="botao botao--secundario"
            style={{ marginTop: "0.4rem", padding: "0.25rem 0.55rem", fontSize: "0.82rem" }}
            onClick={() => onSelecionar(null)}
          >
            Trocar paciente
          </button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <label>Paciente</label>
      <input
        value={busca}
        onChange={(e) => setBusca(e.target.value)}
        placeholder="Buscar paciente já cadastrado, por nome"
      />
      {buscando && <p style={{ fontSize: "0.8rem", color: "var(--texto-secundario)" }}>Buscando…</p>}
      {resultados && resultados.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column", gap: 4, marginTop: "0.35rem" }}>
          {resultados.slice(0, 8).map((p) => (
            <button
              key={p.id}
              className="botao botao--secundario"
              style={{ justifyContent: "flex-start", textAlign: "left" }}
              onClick={() => onSelecionar(p)}
            >
              {p.full_name}
              {p.cpf && <span style={{ color: "var(--texto-secundario)", marginLeft: 6 }}>· CPF {p.cpf}</span>}
            </button>
          ))}
        </div>
      )}
      {resultados && resultados.length === 0 && busca.trim() && !buscando && (
        <p style={{ fontSize: "0.8rem", color: "var(--texto-secundario)" }}>Nenhum paciente cadastrado com esse nome.</p>
      )}

      {criando ? (
        <FormularioNovoPaciente
          onCriado={(p) => { setCriando(false); onSelecionar(p); }}
          onCancelar={() => setCriando(false)}
        />
      ) : (
        <button className="botao botao--secundario" style={{ marginTop: "0.4rem" }} onClick={() => setCriando(true)}>
          + Cadastrar novo paciente
        </button>
      )}

      <div style={{ marginTop: "0.7rem", paddingTop: "0.6rem", borderTop: "1px solid var(--borda)" }}>
        <label>Ou sem paciente cadastrado — nome livre (opcional)</label>
        <input
          value={nomeAvulso}
          onChange={(e) => onNomeAvulsoChange(e.target.value)}
          placeholder="Nome do paciente/destinatário, sem ficha cadastrada"
        />
      </div>
    </div>
  );
}

function SeletorEnderecoPrescritor({ endereco, onChange }: {
  endereco: "" | "residencial" | "profissional";
  onChange: (v: "" | "residencial" | "profissional") => void;
}) {
  return (
    <div>
      <label>Endereço do prescritor no cabeçalho/rodapé (opcional)</label>
      <select value={endereco} onChange={(e) => onChange(e.target.value as typeof endereco)}>
        <option value="">Nenhum</option>
        <option value="profissional">Profissional do prescritor (consultório)</option>
        <option value="residencial">Residencial do prescritor</option>
      </select>
    </div>
  );
}

// ————————————————————————————————————————————————————————————————————
// Bloco estruturado de exames — usado tanto no atalho direto "Solicitar
// Exames" quanto como ferramenta de inserção dentro de "Usar Modelo"
// (pedido do Rafael, 12/08/2026: a estrutura de exames vale nos dois
// fluxos). Sempre aceita item digitado livremente, além da sugestão.
// ————————————————————————————————————————————————————————————————————
function BlocoExames({ exames, onExamesChange, indicacao, onIndicacaoChange, cid, onCidChange,
  prioridade, onPrioridadeChange, observacoes, onObservacoesChange, sugestoes }: {
  exames: string[];
  onExamesChange: (v: string[]) => void;
  indicacao: string;
  onIndicacaoChange: (v: string) => void;
  cid: string;
  onCidChange: (v: string) => void;
  prioridade: "rotina" | "urgente";
  onPrioridadeChange: (v: "rotina" | "urgente") => void;
  observacoes: string;
  onObservacoesChange: (v: string) => void;
  sugestoes: Record<string, string[]> | null;
}) {
  const [novoExame, setNovoExame] = useState("");

  function adicionar(nome: string) {
    const limpo = nome.trim();
    if (!limpo || exames.includes(limpo)) return;
    onExamesChange([...exames, limpo]);
    setNovoExame("");
  }
  function remover(idx: number) {
    onExamesChange(exames.filter((_, i) => i !== idx));
  }
  function mover(idx: number, direcao: -1 | 1) {
    const alvo = idx + direcao;
    if (alvo < 0 || alvo >= exames.length) return;
    const copia = [...exames];
    [copia[idx], copia[alvo]] = [copia[alvo], copia[idx]];
    onExamesChange(copia);
  }

  return (
    <div>
      <label>Exames solicitados</label>
      {exames.length === 0 && (
        <p style={{ fontSize: "0.82rem", color: "var(--texto-secundario)", margin: "0 0 0.3rem" }}>
          Nenhum exame adicionado ainda.
        </p>
      )}
      {exames.map((e, i) => (
        <div key={`${e}-${i}`} style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
          <span style={{ flex: 1, padding: "0.3rem 0.5rem", background: "var(--superficie-suave)", borderRadius: 8 }}>{e}</span>
          <button type="button" className="botao botao--secundario" style={{ padding: "0.2rem 0.45rem" }} onClick={() => mover(i, -1)} disabled={i === 0}>↑</button>
          <button type="button" className="botao botao--secundario" style={{ padding: "0.2rem 0.45rem" }} onClick={() => mover(i, 1)} disabled={i === exames.length - 1}>↓</button>
          <button type="button" className="botao botao--secundario" style={{ padding: "0.2rem 0.45rem" }} onClick={() => remover(i)}>Remover</button>
        </div>
      ))}
      <div style={{ display: "flex", gap: 6 }}>
        <input
          list="exames-sugeridos-datalist"
          value={novoExame}
          onChange={(e) => setNovoExame(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); adicionar(novoExame); } }}
          placeholder="Digite ou escolha um exame (lista de sugestão, sempre aceita texto livre)"
        />
        <button type="button" className="botao botao--secundario" onClick={() => adicionar(novoExame)}>Adicionar</button>
      </div>
      <datalist id="exames-sugeridos-datalist">
        {Object.values(sugestoes ?? {}).flat().map((e) => <option key={e} value={e} />)}
      </datalist>

      <div className="grade grade--2" style={{ marginTop: "0.6rem" }}>
        <div>
          <label>Indicação clínica / justificativa</label>
          <input value={indicacao} onChange={(e) => onIndicacaoChange(e.target.value)} />
        </div>
        <div>
          <label>CID (opcional)</label>
          <input value={cid} onChange={(e) => onCidChange(e.target.value)} placeholder="Ex.: I48.9" />
        </div>
        <div>
          <label>Prioridade</label>
          <select value={prioridade} onChange={(e) => onPrioridadeChange(e.target.value as "rotina" | "urgente")}>
            <option value="rotina">Rotina</option>
            <option value="urgente">Urgente</option>
          </select>
        </div>
        <div>
          <label>Observações (opcional)</label>
          <input value={observacoes} onChange={(e) => onObservacoesChange(e.target.value)} />
        </div>
      </div>
    </div>
  );
}

function montarCorpoExames(exames: string[], indicacao: string, cid: string,
  prioridade: "rotina" | "urgente", observacoes: string, nomePaciente: string | null): string {
  const linhas: string[] = [];
  if (nomePaciente) { linhas.push(`Paciente: ${nomePaciente}`, ""); }
  linhas.push("Solicito a realização dos seguintes exames:", "");
  linhas.push(...exames.map((e) => `- ${e}`));
  if (indicacao.trim()) { linhas.push("", `Indicação clínica: ${indicacao.trim()}`); }
  if (cid.trim()) linhas.push(`CID: ${cid.trim()}`);
  if (prioridade === "urgente") { linhas.push("", "Prioridade: URGENTE"); }
  if (observacoes.trim()) { linhas.push("", `Observações: ${observacoes.trim()}`); }
  return linhas.join("\n");
}

// ————————————————————————————————————————————————————————————————————
// Finalização — assinar, baixar PDF, enviar por e-mail. Compartilhada por
// TODOS os tipos de documento gerado (modelo, exames, atestado, livre):
// as rotas de `app/api/documents.py` já são genéricas por `GeneratedDocument.
// id`, então esta parte da tela não precisa saber de qual fluxo o
// documento veio.
// ————————————————————————————————————————————————————————————————————
function FinalizarDocumentoGerado({ geradoId, nomeArquivoBase, provedores, onFechar }: {
  geradoId: number;
  nomeArquivoBase: string;
  provedores: Provedor[] | null;
  onFechar: () => void;
}) {
  const { usuario } = useAuth();
  const [metodo, setMetodo] = useState(usuario?.assinatura_metodo_preferido ?? "MANUAL");
  const [erro, setErro] = useState("");
  const [email, setEmail] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [resultadoEnvio, setResultadoEnvio] = useState<{ enviado: boolean; link: string | null } | null>(null);
  const [aguardandoExterno, setAguardandoExterno] = useState(false);
  const [assinadoExternoAgora, setAssinadoExternoAgora] = useState(false);
  const [emitido, setEmitido] = useState(false);

  useEffect(() => {
    if (usuario?.assinatura_metodo_preferido) {
      setMetodo(usuario.assinatura_metodo_preferido);
    }
  }, [usuario?.assinatura_metodo_preferido]);

  async function baixar() {
    try {
      const blob = await api.blob(`/document-templates/gerados/${geradoId}/pdf?metodo=${encodeURIComponent(metodo)}`);
      baixarBlob(blob, `${nomeArquivoBase}-${geradoId}.pdf`);
      setAguardandoExterno(METODOS_MANUAL_EXTERNO.has(metodo));
      setEmitido(true);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível baixar o PDF.");
    }
  }

  async function enviar() {
    if (!email) return;
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

      {aguardandoExterno && (
        <AssinaturaExternaITI
          metodo={metodo}
          nomeProvedor={provedores?.find((p) => p.codigo === metodo)?.nome ?? metodo}
          enviarUrl={`/document-templates/gerados/${geradoId}/assinatura-externa`}
          onConcluido={() => { setAguardandoExterno(false); setAssinadoExternoAgora(true); }}
        />
      )}
      {assinadoExternoAgora && (
        <p style={{ color: "var(--sucesso)", fontSize: "0.86rem", marginTop: "0.4rem" }}>
          Assinatura conferida com sucesso — o documento já está assinado.
        </p>
      )}

      <OfertaEnvioEmailPaciente
        endpointBase={`/document-templates/gerados/${geradoId}`}
        habilitado={emitido && !aguardandoExterno}
      />

      <div style={{ marginTop: "0.8rem" }}>
        <label>Enviar por e-mail ao paciente (link seguro, válido por 7 dias)</label>
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="paciente@exemplo.com" />
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

type Origem = "modelo" | "exames" | "atestado" | "livre";

type ValoresIniciaisRecriar = {
  paciente: Paciente | null;
  nomeAvulso: string;
  variaveisModelo: Record<string, string>;
  exames: string[];
  indicacao: string;
  cid: string;
  prioridade: "rotina" | "urgente";
  observacoes: string;
  diasAfastamento: string;
  dataInicio: string;
  dataFim: string;
  tituloLivre: string;
  corpoLivre: string;
};

// ————————————————————————————————————————————————————————————————————
// Fluxo único de geração — o mesmo componente atende os quatro pontos de
// entrada (Solicitar Exames / Emitir Atestado / Documento em Branco /
// Usar Modelo). Sequência sempre igual, pedido do Rafael (12/08/2026):
// paciente → dados específicos da origem → conteúdo editável → prévia →
// gerar → assinar/baixar/enviar. O CONTEÚDO NUNCA fica escondido — mesmo
// um modelo sem variável nenhuma mostra o texto num editor livre, porque
// modelo é ponto de partida, nunca documento final imutável.
// ————————————————————————————————————————————————————————————————————
function FluxoDocumento({ origem, template, provedores, exameSugestoes, valoresIniciais, onFechar, onGerado }: {
  origem: Origem;
  template?: Template;
  provedores: Provedor[] | null;
  exameSugestoes: Record<string, string[]> | null;
  valoresIniciais?: Partial<ValoresIniciaisRecriar>;
  onFechar: () => void;
  onGerado: () => void;
}) {
  const { usuario } = useAuth();
  const [paciente, setPaciente] = useState<Paciente | null>(valoresIniciais?.paciente ?? null);
  const [nomeAvulso, setNomeAvulso] = useState(valoresIniciais?.nomeAvulso ?? "");
  const [enderecoPrescritor, setEnderecoPrescritor] = useState<"" | "residencial" | "profissional">("");

  // — Variáveis do modelo (origem "modelo") —
  const variaveisModeloDoTexto = template ? variaveisDoModelo(template.body) : [];
  const [valoresVariaveis, setValoresVariaveis] = useState<Record<string, string>>(valoresIniciais?.variaveisModelo ?? {});

  // — Campos estruturados de exames (origem "exames", e também
  //   disponíveis como ferramenta de inserção dentro de "modelo") —
  const [exames, setExames] = useState<string[]>(valoresIniciais?.exames ?? []);
  const [indicacao, setIndicacao] = useState(valoresIniciais?.indicacao ?? "");
  const [cid, setCid] = useState(valoresIniciais?.cid ?? "");
  const [prioridade, setPrioridade] = useState<"rotina" | "urgente">(valoresIniciais?.prioridade ?? "rotina");
  const [observacoesExames, setObservacoesExames] = useState(valoresIniciais?.observacoes ?? "");
  const [mostrarBlocoExamesNoModelo, setMostrarBlocoExamesNoModelo] = useState(false);

  // — Campos do atestado rápido —
  const [diasAfastamento, setDiasAfastamento] = useState(valoresIniciais?.diasAfastamento ?? "");
  const [dataInicio, setDataInicio] = useState(valoresIniciais?.dataInicio ?? "");
  const [dataFim, setDataFim] = useState(valoresIniciais?.dataFim ?? "");
  const [cidAtestado, setCidAtestado] = useState(valoresIniciais?.cid ?? "");
  const [observacoesAtestado, setObservacoesAtestado] = useState(valoresIniciais?.observacoes ?? "");

  // — Documento em branco —
  const [tituloLivre, setTituloLivre] = useState(valoresIniciais?.tituloLivre ?? "");

  // — Conteúdo editável, sempre visível, sempre a fonte de verdade do que
  //   vai no PDF (regra central: modelo é ponto de partida, não texto
  //   final imutável). `editadoManualmente` trava o auto-preenchimento
  //   assim que o médico digita algo com as próprias mãos, pra não
  //   apagar a edição dele quando outro campo mudar depois.
  const [corpo, setCorpo] = useState("");
  const editadoManualmente = useRef(false);
  const [mostrarPreview, setMostrarPreview] = useState(false);
  const [salvandoNoModelo, setSalvandoNoModelo] = useState(false);
  const [avisoModeloSalvo, setAvisoModeloSalvo] = useState(false);

  const variaveisPacienteAtuais = variaveisDoPaciente(paciente);

  useEffect(() => {
    if (editadoManualmente.current) return;
    if (origem === "modelo" && template) {
      setCorpo(substituirVariaveis(template.body, { ...variaveisPacienteAtuais, ...valoresVariaveis }));
    } else if (origem === "exames") {
      setCorpo(montarCorpoExames(exames, indicacao, cid, prioridade, observacoesExames, paciente?.full_name ?? (nomeAvulso.trim() || null)));
    } else if (origem === "atestado") {
      const nome = paciente?.full_name ?? (nomeAvulso.trim() || "acima identificado(a)");
      let periodo = "por período a ser definido";
      if (dataInicio && dataFim) {
        const dias = Math.round((new Date(dataFim).getTime() - new Date(dataInicio).getTime()) / 86400000) + 1;
        periodo = `no período de ${formatarDataBR(dataInicio)} a ${formatarDataBR(dataFim)} (${dias} dia(s))`;
      } else if (diasAfastamento) {
        periodo = `por ${diasAfastamento} dia(s)`;
        if (dataInicio) periodo += `, a partir de ${formatarDataBR(dataInicio)}`;
      }
      const linhas = [`Atesto, para os devidos fins, que o(a) paciente ${nome} necessita de afastamento de suas atividades habituais ${periodo}.`];
      if (cidAtestado.trim()) linhas.push("", `CID: ${cidAtestado.trim()}`);
      if (observacoesAtestado.trim()) linhas.push("", `Observações: ${observacoesAtestado.trim()}`);
      setCorpo(linhas.join("\n"));
    }
    // "livre" não auto-preenche: o textarea É o conteúdo, ponto.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [origem, template, valoresVariaveis, paciente, nomeAvulso, exames, indicacao, cid, prioridade,
    observacoesExames, diasAfastamento, dataInicio, dataFim, cidAtestado, observacoesAtestado]);

  useEffect(() => {
    if (origem === "livre" && valoresIniciais?.corpoLivre !== undefined) setCorpo(valoresIniciais.corpoLivre);
  }, [origem, valoresIniciais?.corpoLivre]);

  function inserirBlocoExamesNoTexto() {
    const bloco = montarCorpoExames(exames, indicacao, cid, prioridade, observacoesExames, null);
    setCorpo((atual) => (atual.trim() ? `${atual}\n\n${bloco}` : bloco));
    editadoManualmente.current = true;
  }

  async function salvarAlteracoesNoModelo() {
    if (!template) return;
    setSalvandoNoModelo(true);
    try {
      await api.put(`/document-templates/${template.id}`, { title: template.title, doc_type: template.doc_type, body: corpo });
      setAvisoModeloSalvo(true);
    } finally {
      setSalvandoNoModelo(false);
    }
  }

  const faltandoVariaveisModelo = origem === "modelo"
    ? variaveisModeloDoTexto.filter((v) => !(VARIAVEIS_PACIENTE as readonly string[]).includes(v) && !valoresVariaveis[v]?.trim())
    : [];

  const [gerando, setGerando] = useState(false);
  const [erro, setErro] = useState("");
  const [geradoId, setGeradoId] = useState<number | null>(null);

  async function gerar() {
    setGerando(true);
    setErro("");
    try {
      let resposta: { id: number };
      const enderecoParam = enderecoPrescritor || null;
      if (origem === "modelo" && template) {
        resposta = await api.post<{ id: number }>("/document-templates/gerar", {
          template_id: template.id,
          variables: valoresVariaveis,
          patient_profile_id: paciente?.id ?? null,
          patient_name: paciente ? null : (nomeAvulso.trim() || null),
          endereco: enderecoParam,
          corpo_final: corpo,
        });
      } else if (origem === "exames") {
        resposta = await api.post<{ id: number }>("/document-templates/gerar-exames", {
          patient_profile_id: paciente?.id ?? null,
          patient_name: paciente ? null : (nomeAvulso.trim() || null),
          exames, indicacao: indicacao.trim() || null, cid: cid.trim() || null,
          prioridade, observacoes: observacoesExames.trim() || null,
          endereco: enderecoParam, corpo_final: corpo,
        });
      } else if (origem === "atestado") {
        resposta = await api.post<{ id: number }>("/document-templates/gerar-atestado", {
          patient_profile_id: paciente?.id ?? null,
          patient_name: paciente ? null : (nomeAvulso.trim() || null),
          dias_afastamento: diasAfastamento ? Number(diasAfastamento) : null,
          data_inicio: dataInicio || null, data_fim: dataFim || null,
          cid: cidAtestado.trim() || null, observacoes: observacoesAtestado.trim() || null,
          endereco: enderecoParam, corpo_final: corpo,
        });
      } else {
        resposta = await api.post<{ id: number }>("/document-templates/gerar-livre", {
          titulo: tituloLivre.trim() || "Documento",
          corpo,
          patient_profile_id: paciente?.id ?? null,
          patient_name: paciente ? null : (nomeAvulso.trim() || null),
          endereco: enderecoParam,
        });
      }
      setGeradoId(resposta.id);
      onGerado();
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível gerar o documento.");
    } finally {
      setGerando(false);
    }
  }

  if (geradoId) {
    return (
      <FinalizarDocumentoGerado
        geradoId={geradoId}
        nomeArquivoBase={origem}
        provedores={provedores}
        onFechar={onFechar}
      />
    );
  }

  const medicoResumo = usuario ? [
    usuario.full_name,
    usuario.council_name && `${usuario.council_name}-${usuario.council_state ?? ""} ${usuario.council_number ?? ""}`.trim(),
    usuario.rqe && `RQE ${usuario.rqe}`,
  ].filter(Boolean).join(" · ") : "";

  return (
    <div className="cartao" style={{ marginTop: "0.8rem" }}>
      <SeletorPaciente paciente={paciente} onSelecionar={setPaciente} nomeAvulso={nomeAvulso} onNomeAvulsoChange={setNomeAvulso} />

      {origem === "modelo" && (
        <div style={{ marginTop: "0.8rem" }}>
          {variaveisModeloDoTexto.filter((v) => !(VARIAVEIS_PACIENTE as readonly string[]).includes(v)).length === 0 ? (
            <p style={{ fontSize: "0.86rem", color: "var(--texto-secundario)" }}>
              Este modelo não tem variáveis próprias além das de paciente — o texto abaixo já está pronto para revisar e editar.
            </p>
          ) : (
            variaveisModeloDoTexto
              .filter((v) => !(VARIAVEIS_PACIENTE as readonly string[]).includes(v))
              .map((v) => (
                <div key={v} style={{ marginTop: "0.5rem" }}>
                  <label>{v}</label>
                  <input value={valoresVariaveis[v] ?? ""} onChange={(e) => setValoresVariaveis({ ...valoresVariaveis, [v]: e.target.value })} />
                </div>
              ))
          )}

          <div style={{ marginTop: "0.7rem" }}>
            <button className="botao botao--secundario" onClick={() => setMostrarBlocoExamesNoModelo((v) => !v)}>
              {mostrarBlocoExamesNoModelo ? "Ocultar lista estruturada de exames" : "+ Adicionar lista de exames a este documento"}
            </button>
            {mostrarBlocoExamesNoModelo && (
              <div style={{ marginTop: "0.5rem" }}>
                <BlocoExames
                  exames={exames} onExamesChange={setExames}
                  indicacao={indicacao} onIndicacaoChange={setIndicacao}
                  cid={cid} onCidChange={setCid}
                  prioridade={prioridade} onPrioridadeChange={setPrioridade}
                  observacoes={observacoesExames} onObservacoesChange={setObservacoesExames}
                  sugestoes={exameSugestoes}
                />
                <button className="botao" style={{ marginTop: "0.4rem" }} onClick={inserirBlocoExamesNoTexto} disabled={exames.length === 0}>
                  Inserir no texto do documento
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {origem === "exames" && (
        <div style={{ marginTop: "0.8rem" }}>
          <BlocoExames
            exames={exames} onExamesChange={setExames}
            indicacao={indicacao} onIndicacaoChange={setIndicacao}
            cid={cid} onCidChange={setCid}
            prioridade={prioridade} onPrioridadeChange={setPrioridade}
            observacoes={observacoesExames} onObservacoesChange={setObservacoesExames}
            sugestoes={exameSugestoes}
          />
        </div>
      )}

      {origem === "atestado" && (
        <div className="grade grade--2" style={{ marginTop: "0.8rem" }}>
          <div>
            <label>Dias de afastamento</label>
            <input type="number" min={1} max={365} value={diasAfastamento} onChange={(e) => setDiasAfastamento(e.target.value)} />
          </div>
          <div>
            <label>Data de início (opcional com dias, obrigatória com data final)</label>
            <input type="date" value={dataInicio} onChange={(e) => setDataInicio(e.target.value)} />
          </div>
          <div>
            <label>Data final (alternativa a "dias de afastamento")</label>
            <input type="date" value={dataFim} onChange={(e) => setDataFim(e.target.value)} />
          </div>
          <div>
            <label>CID (opcional)</label>
            <input value={cidAtestado} onChange={(e) => setCidAtestado(e.target.value)} />
          </div>
          <div style={{ gridColumn: "1 / -1" }}>
            <label>Observações (opcional)</label>
            <input value={observacoesAtestado} onChange={(e) => setObservacoesAtestado(e.target.value)} />
          </div>
        </div>
      )}

      {origem === "livre" && (
        <div style={{ marginTop: "0.8rem" }}>
          <label>Título do documento</label>
          <input value={tituloLivre} onChange={(e) => setTituloLivre(e.target.value)} placeholder="Ex.: Declaração de comparecimento" />
        </div>
      )}

      <div style={{ marginTop: "0.9rem" }}>
        <label>Conteúdo do documento — revise e edite livremente antes de gerar</label>
        <textarea
          rows={12}
          style={{ width: "100%", fontFamily: "inherit" }}
          value={corpo}
          onChange={(e) => { editadoManualmente.current = true; setCorpo(e.target.value); }}
        />
        {origem === "modelo" && template && (
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: "0.35rem" }}>
            <button className="botao botao--secundario" style={{ fontSize: "0.82rem" }} onClick={salvarAlteracoesNoModelo} disabled={salvandoNoModelo}>
              {salvandoNoModelo ? "Salvando…" : "Salvar estas alterações no modelo original"}
            </button>
            {avisoModeloSalvo && <span style={{ fontSize: "0.82rem", color: "var(--sucesso)" }}>Modelo atualizado.</span>}
          </div>
        )}
        <p style={{ fontSize: "0.78rem", color: "var(--texto-secundario)", margin: "0.3rem 0 0" }}>
          Esta edição vale só para este documento — o modelo salvo só muda se você usar o botão acima.
        </p>
      </div>

      <div style={{ marginTop: "0.7rem" }}>
        <SeletorEnderecoPrescritor endereco={enderecoPrescritor} onChange={setEnderecoPrescritor} />
      </div>

      <div style={{ marginTop: "0.7rem" }}>
        <button className="botao botao--secundario" onClick={() => setMostrarPreview((v) => !v)}>
          {mostrarPreview ? "Ocultar prévia" : "Visualizar documento"}
        </button>
        {mostrarPreview && (
          <div className="cartao" style={{ marginTop: "0.5rem", background: "var(--superficie-suave)" }}>
            <p className="eyebrow" style={{ margin: 0 }}>Prévia do documento</p>
            <p style={{ margin: "0.2rem 0" }}>
              <strong>Paciente:</strong> {paciente?.full_name ?? nomeAvulso.trim() ?? "Não informado"}
              {paciente?.cpf && ` · CPF ${paciente.cpf}`}
              {paciente?.birth_date && ` · nasc. ${formatarDataBR(paciente.birth_date)}`}
            </p>
            {paciente?.endereco && montarEnderecoCompleto(paciente.endereco) && (
              <p style={{ margin: "0.2rem 0" }}><strong>Endereço do paciente:</strong> {montarEnderecoCompleto(paciente.endereco)}</p>
            )}
            <p style={{ margin: "0.2rem 0" }}><strong>Prescritor:</strong> {medicoResumo || "—"}</p>
            <p style={{ margin: "0.2rem 0" }}>
              <strong>Endereço no documento:</strong>{" "}
              {enderecoPrescritor === "profissional" ? "Profissional do prescritor" : enderecoPrescritor === "residencial" ? "Residencial do prescritor" : "Nenhum"}
            </p>
            <pre style={{ whiteSpace: "pre-wrap", fontFamily: "inherit", marginTop: "0.5rem", padding: "0.6rem", background: "white", borderRadius: 8, border: "1px solid var(--borda)" }}>
              {corpo || "(documento vazio)"}
            </pre>
          </div>
        )}
      </div>

      {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erro}</p>}
      <div style={{ display: "flex", gap: 8, marginTop: "0.8rem" }}>
        <button
          className="botao"
          onClick={gerar}
          disabled={
            gerando || !corpo.trim() ||
            (origem === "modelo" && faltandoVariaveisModelo.length > 0) ||
            (origem === "exames" && exames.length === 0) ||
            (origem === "atestado" && !diasAfastamento && !(dataInicio && dataFim)) ||
            (origem === "livre" && !tituloLivre.trim())
          }
        >
          {gerando ? "Gerando…" : "Gerar documento"}
        </button>
        <button className="botao botao--secundario" onClick={onFechar}>Cancelar</button>
      </div>
    </div>
  );
}

export default function Templates() {
  const [lista, setLista] = useState<Template[] | null>(null);
  const [editando, setEditando] = useState<Partial<Template> | null>(null);
  const [salvando, setSalvando] = useState(false);
  const [fluxoAberto, setFluxoAberto] = useState<{ origem: Origem; template?: Template } | null>(null);
  const [valoresIniciais, setValoresIniciais] = useState<Partial<ValoresIniciaisRecriar> | undefined>(undefined);
  const [gerados, setGerados] = useState<Gerado[] | null>(null);
  const [paginaGerados, setPaginaGerados] = useState(1);
  const [temMaisGerados, setTemMaisGerados] = useState(false);
  const [carregandoMais, setCarregandoMais] = useState(false);
  const [provedores, setProvedores] = useState<Provedor[] | null>(null);
  const [exameSugestoes, setExameSugestoes] = useState<Record<string, string[]> | null>(null);
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
    api.get<Record<string, string[]>>("/document-templates/exames-sugeridos").then(setExameSugestoes).catch(() => {});
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

  function abrirFluxo(origem: Origem, template?: Template) {
    setValoresIniciais(undefined);
    setFluxoAberto({ origem, template });
    setTimeout(() => document.getElementById("fluxo-documento")?.scrollIntoView({ behavior: "smooth", block: "start" }), 50);
  }

  async function recriarBaseadoEm(gid: number) {
    setErroGerados("");
    try {
      const detalhe = await api.get<GeradoDetalhe>(`/document-templates/gerados/${gid}`);
      const paciente: Paciente | null = detalhe.patient_snapshot && detalhe.patient_profile_id
        ? {
          id: detalhe.patient_profile_id,
          full_name: detalhe.patient_snapshot.full_name ?? "",
          cpf: detalhe.patient_snapshot.cpf,
          birth_date: detalhe.patient_snapshot.birth_date,
          sex: detalhe.patient_snapshot.sex,
          phone: detalhe.patient_snapshot.phone,
          email: detalhe.patient_snapshot.email,
          endereco: detalhe.patient_snapshot.endereco ?? {},
        }
        : null;
      const nomeAvulso = !paciente ? (detalhe.patient_name ?? "") : "";

      if (detalhe.template_id) {
        const template = lista?.find((t) => t.id === detalhe.template_id);
        if (!template) {
          setErroGerados("O modelo original não existe mais.");
          return;
        }
        setValoresIniciais({ paciente, nomeAvulso, variaveisModelo: detalhe.variables ?? {} });
        abrirFluxo("modelo", template);
        return;
      }

      if (detalhe.doc_type === "solicitacao_exames") {
        setValoresIniciais({
          paciente, nomeAvulso,
          exames: detalhe.variables?.exames ?? [],
          indicacao: detalhe.variables?.indicacao ?? "",
          cid: detalhe.variables?.cid ?? "",
          prioridade: (detalhe.variables?.prioridade as "rotina" | "urgente") ?? "rotina",
          observacoes: detalhe.variables?.observacoes ?? "",
        });
        abrirFluxo("exames");
        return;
      }
      if (detalhe.doc_type === "documento_livre") {
        setValoresIniciais({
          paciente, nomeAvulso,
          tituloLivre: detalhe.variables?.titulo ?? detalhe.title ?? "",
          corpoLivre: detalhe.variables?.corpo ?? detalhe.rendered_body,
        });
        abrirFluxo("livre");
        return;
      }
      if (detalhe.doc_type === "atestado" && !detalhe.template_id) {
        setValoresIniciais({
          paciente, nomeAvulso,
          diasAfastamento: detalhe.variables?.dias_afastamento ? String(detalhe.variables.dias_afastamento) : "",
          dataInicio: detalhe.variables?.data_inicio ?? "",
          dataFim: detalhe.variables?.data_fim ?? "",
          cid: detalhe.variables?.cid ?? "",
          observacoes: detalhe.variables?.observacoes ?? "",
        });
        abrirFluxo("atestado");
        return;
      }
      setErroGerados("Este documento foi gerado antes desta função existir — não dá pra recriar automaticamente.");
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
      <h1>Documentos e Solicitações</h1>
      <p style={{ color: "var(--texto-secundario)", maxWidth: "62ch" }}>
        Solicite exames, emita atestados, crie documentos livres ou utilize seus modelos personalizados.
      </p>

      <p className="eyebrow" style={{ marginTop: "1.2rem" }}>Ações clínicas</p>
      <div className="grade grade--3">
        <button className="cartao cartao--clinico" style={{ textAlign: "left" }} onClick={() => abrirFluxo("exames")}>
          <strong>Solicitar Exames</strong>
          <p style={{ margin: "0.2rem 0 0", fontSize: "0.84rem", color: "var(--texto-secundario)" }}>
            Lista de exames com sugestão por categoria, sempre com texto livre.
          </p>
        </button>
        <button className="cartao cartao--clinico" style={{ textAlign: "left" }} onClick={() => abrirFluxo("atestado")}>
          <strong>Emitir Atestado Médico</strong>
          <p style={{ margin: "0.2rem 0 0", fontSize: "0.84rem", color: "var(--texto-secundario)" }}>
            Por quantidade de dias ou por período, com CID opcional.
          </p>
        </button>
        <button className="cartao cartao--clinico" style={{ textAlign: "left" }} onClick={() => abrirFluxo("livre")}>
          <strong>Documento em Branco</strong>
          <p style={{ margin: "0.2rem 0 0", fontSize: "0.84rem", color: "var(--texto-secundario)" }}>
            Título e texto livre — emissão avulsa, sem depender de modelo nenhum.
          </p>
        </button>
      </div>

      <p className="eyebrow" style={{ marginTop: "1.4rem" }}>Modelos</p>
      <div className="grade grade--2">
        <button
          className="cartao"
          style={{ textAlign: "left" }}
          onClick={() => document.getElementById("modelos-salvos")?.scrollIntoView({ behavior: "smooth", block: "start" })}
        >
          <strong>Usar Modelo</strong>
          <p style={{ margin: "0.2rem 0 0", fontSize: "0.84rem", color: "var(--texto-secundario)" }}>
            Reabra um modelo já salvo, preencha e edite antes de gerar.
          </p>
        </button>
        <button
          className="cartao"
          style={{ textAlign: "left" }}
          onClick={() => setEditando({ title: "", doc_type: "atestado", body: "" })}
        >
          <strong>+ Criar Modelo</strong>
          <p style={{ margin: "0.2rem 0 0", fontSize: "0.84rem", color: "var(--texto-secundario)" }}>
            Um modelo novo, reutilizável, com variáveis entre chaves duplas.
          </p>
        </button>
      </div>

      {fluxoAberto && (
        <div id="fluxo-documento">
          <FluxoDocumento
            origem={fluxoAberto.origem}
            template={fluxoAberto.template}
            provedores={provedores}
            exameSugestoes={exameSugestoes}
            valoresIniciais={valoresIniciais}
            onFechar={() => { setFluxoAberto(null); setValoresIniciais(undefined); }}
            onGerado={recarregarGerados}
          />
        </div>
      )}

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
          <div className="cartao" style={{ marginTop: "0.6rem", background: "var(--superficie-suave)" }}>
            <p className="eyebrow" style={{ margin: 0 }}>Variáveis do paciente disponíveis</p>
            <p style={{ fontSize: "0.82rem", color: "var(--texto-secundario)", margin: "0.2rem 0 0.4rem" }}>
              Ao usar este modelo com um paciente cadastrado selecionado, estas variáveis são
              preenchidas sozinhas — se algum dado não existir no cadastro, a variável fica em branco
              sem impedir a geração.
            </p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
              {VARIAVEIS_PACIENTE.map((v) => (
                <code key={v} style={{ padding: "0.15rem 0.4rem", background: "white", borderRadius: 6, fontSize: "0.78rem" }}>
                  {`{{${v}}}`}
                </code>
              ))}
            </div>
          </div>
          <div style={{ display: "flex", gap: 8, marginTop: "0.6rem" }}>
            <button className="botao" onClick={salvar} disabled={salvando}>
              {salvando ? "Salvando…" : "Salvar modelo"}
            </button>
            <button className="botao botao--secundario" onClick={() => setEditando(null)}>Cancelar</button>
          </div>
        </div>
      )}

      <div id="modelos-salvos" style={{ marginTop: "1.4rem" }}>
          <h2>Modelos salvos</h2>
          {lista === null ? (
            <Carregando />
          ) : lista.length === 0 ? (
            <Vazio titulo="Nenhum modelo ainda" acao='Use "+ Criar Modelo" acima.' />
          ) : (
            lista.map((t) => (
              <div key={t.id} id={`modelo-${t.id}`} className="cartao" style={{ marginBottom: "0.5rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 8 }}>
                  <div>
                    <p className="eyebrow" style={{ margin: 0 }}>{RÓTULO[t.doc_type] ?? t.doc_type}</p>
                    <strong>{t.title}</strong>
                  </div>
                  <div style={{ display: "flex", gap: 6 }}>
                    <button className="botao" style={{ padding: "0.3rem 0.6rem" }} onClick={() => abrirFluxo("modelo", t)}>
                      Usar
                    </button>
                    <button className="botao botao--secundario" style={{ padding: "0.3rem 0.6rem" }} onClick={() => setEditando(t)}>
                      Editar
                    </button>
                    <button className="botao botao--secundario" style={{ padding: "0.3rem 0.6rem" }} onClick={() => apagar(t.id)}>
                      Apagar
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
      </div>

      <div style={{ marginTop: "0.8rem" }}>
        <a
          href="/avaliacao-preoperatoria"
          className="cartao cartao--clinico"
          style={{ display: "block", color: "inherit" }}
        >
          <p className="eyebrow" style={{ margin: 0 }}>Função relacionada</p>
          <strong>Avaliação Cardiológica Pré-Operatória de Risco Cirúrgico</strong>
          <p style={{ margin: "0.2rem 0 0", fontSize: "0.86rem", color: "var(--texto-secundario)" }}>
            Escores de risco cirúrgico (RCRI, Gupta MICA) direto num documento pronto para
            assinar, imprimir ou enviar ao paciente.
          </p>
        </a>
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
            <option value="solicitacao_exames">Solicitação de exames</option>
            <option value="documento_livre">Documento em branco</option>
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
                    style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 8, marginBottom: "0.5rem" }}
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
