import { useEffect, useState } from "react";
import { api, ApiError } from "../lib/api";

// ————————————————————————————————————————————————————————————————————
// Seleção de paciente — camada ÚNICA e reutilizável (pedido do Rafael,
// 12/08/2026, extraída de Templates.tsx para reuso em outras telas de
// geração documental em 02/09/2026): busca no cadastro do próprio médico
// (isolamento por tenant garantido no backend, `patient_profile_for_user`),
// seleciona, mostra resumo, permite trocar, ou cadastra um novo sem sair da
// tela. Todo tipo de documento usa este MESMO componente — nunca
// reimplementado tela a tela. Quando o tipo não exige paciente cadastrado
// (ou o médico não quer cadastrar), "Sem paciente" com nome livre continua
// disponível.
// ————————————————————————————————————————————————————————————————————

export type Endereco = {
  logradouro?: string | null;
  numero?: string | null;
  complemento?: string | null;
  bairro?: string | null;
  cidade?: string | null;
  uf?: string | null;
  cep?: string | null;
};

export type Paciente = {
  id: number;
  full_name: string;
  cpf: string | null;
  birth_date: string | null;
  sex: string | null;
  phone: string | null;
  email: string | null;
  endereco: Endereco;
};

// Mesmos nomes de `app.services.patient_profile_service.NOMES_VARIAVEIS_
// PACIENTE` no backend — qualquer `{{...}}` desta lista, presente no corpo
// de um modelo, é preenchido a partir do paciente selecionado (ou fica
// vazio, nunca bloqueia a geração — campo ausente no cadastro não é erro).
export const VARIAVEIS_PACIENTE = [
  "paciente_nome", "paciente_cpf", "paciente_data_nascimento", "paciente_sexo",
  "paciente_telefone", "paciente_email",
  "paciente_endereco_logradouro", "paciente_endereco_numero", "paciente_endereco_complemento",
  "paciente_endereco_bairro", "paciente_endereco_cidade", "paciente_endereco_uf", "paciente_endereco_cep",
  "paciente_endereco_completo",
] as const;

export function formatarDataBR(iso: string | null | undefined): string {
  if (!iso) return "";
  const [ano, mes, dia] = iso.split("-");
  if (!ano || !mes || !dia) return iso;
  return `${dia}/${mes}/${ano}`;
}

// Mesma lógica (e mesmo separador " — ") de
// `app.services.patient_profile_service.montar_endereco_completo` — pula
// campo vazio sem deixar separador sobrando.
export function montarEnderecoCompleto(end: Endereco | null | undefined): string {
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

export function variaveisDoPaciente(p: Paciente | null): Record<string, string> {
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

export function FormularioNovoPaciente({ onCriado, onCancelar }: {
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

export function SeletorPaciente({ paciente, onSelecionar, nomeAvulso, onNomeAvulsoChange }: {
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
