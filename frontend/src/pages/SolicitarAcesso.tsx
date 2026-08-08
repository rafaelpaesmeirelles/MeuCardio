import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import Credito from "../components/Credito";
import CampoSenha from "../components/CampoSenha";

const CONSELHOS = ["CRM", "CRO", "CRBM", "COREN", "CRF", "CREFITO", "CRN", "CRP", "CREF", "CRESS", "Outro"];
const TITULOS = ["", "Sr.", "Sra.", "Dr.", "Dra.", "Prof.", "Profa.", "Prof. Dr.", "Profa. Dra.", "Me.", "Ma.", "Esp."];
const UFS = [
  "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG",
  "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
];

function formatarCpf(v: string) {
  const d = v.replace(/\D/g, "").slice(0, 11);
  return d
    .replace(/(\d{3})(\d)/, "$1.$2")
    .replace(/(\d{3})(\d)/, "$1.$2")
    .replace(/(\d{3})(\d{1,2})$/, "$1-$2");
}

export default function SolicitarAcesso() {
  const navigate = useNavigate();
  const [dados, setDados] = useState({
    full_name: "", birth_date: "", cpf: "", profession: "Médico(a)",
    council_name: "CRM", council_number: "", council_state: "",
    specialty: "", professional_title: "", workplace_name: "", workplace_department: "",
    workplace_role: "", workplace_notes: "", include_workplace_on_documents: false,
    email: "", password: "",
  });
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [enviado, setEnviado] = useState(false);

  function set<K extends keyof typeof dados>(campo: K, valor: (typeof dados)[K]) {
    setDados((d) => ({ ...d, [campo]: valor }));
  }

  const senhaFraca = dados.password.length > 0 && dados.password.length < 8;
  const completo =
    dados.full_name.trim().split(" ").length >= 2 &&
    dados.birth_date && dados.cpf.replace(/\D/g, "").length === 11 &&
    dados.profession.trim() && dados.council_number.trim() && dados.council_state &&
    dados.email.includes("@") && dados.password.length >= 8;

  async function enviar() {
    setErro("");
    setEnviando(true);
    try {
      await api.post("/auth/solicitar-acesso", {
        ...dados,
        specialty: dados.specialty.trim() || null,
      });
      setEnviado(true);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível enviar a solicitação.");
    } finally {
      setEnviando(false);
    }
  }

  if (enviado) {
    return (
      <div className="login">
        <div className="login__cartao">
          <div className="login__brasao">
            <h1 style={{ fontSize: "1.25rem", marginTop: 14 }}>Solicitação enviada</h1>
          </div>
          <p>
            Seus dados foram registrados. Um administrador vai conferir seu registro no
            conselho de classe antes de liberar o acesso — você recebe a confirmação por
            e-mail quando isso acontecer.
          </p>
          <Link to="/entrar" className="botao" style={{ display: "block", textAlign: "center", marginTop: "1rem" }}>
            Voltar para o login
          </Link>
          <Credito compacto />
        </div>
      </div>
    );
  }

  return (
    <div className="login">
      <div className="login__cartao" style={{ maxWidth: 460 }}>
        <div className="login__brasao">
          <h1 style={{ fontSize: "1.25rem", marginTop: 14 }}>Solicitar acesso</h1>
        </div>

        <p className="aviso" style={{ borderTop: "none", marginTop: 0, paddingTop: 0 }}>
          Seu acesso só é liberado depois que um administrador confirmar seu registro
          profissional. Preencha com os dados reais do seu conselho de classe.
        </p>

        <label htmlFor="nome">Nome completo</label>
        <input id="nome" value={dados.full_name} onChange={(e) => set("full_name", e.target.value)} />

        <div className="grade grade--2" style={{ marginTop: "0.8rem" }}>
          <div>
            <label htmlFor="nasc">Data de nascimento</label>
            <input id="nasc" type="date" value={dados.birth_date}
                   onChange={(e) => set("birth_date", e.target.value)} />
          </div>
          <div>
            <label htmlFor="cpf">CPF</label>
            <input id="cpf" value={dados.cpf} inputMode="numeric" placeholder="000.000.000-00"
                   onChange={(e) => set("cpf", formatarCpf(e.target.value))} />
          </div>
        </div>

        <label htmlFor="tratamento" style={{ marginTop: "0.8rem" }}>Como deseja ser chamado(a)</label>
        <select id="tratamento" value={dados.professional_title} onChange={(e) => set("professional_title", e.target.value)}>
          {TITULOS.map((t) => <option key={t || "sem"} value={t}>{t || "Sem título"}</option>)}
        </select>

        <label htmlFor="profissao" style={{ marginTop: "0.8rem" }}>Profissão</label>
        <input id="profissao" value={dados.profession} onChange={(e) => set("profession", e.target.value)} />

        <div className="grade grade--3" style={{ marginTop: "0.8rem" }}>
          <div>
            <label htmlFor="conselho">Conselho</label>
            <select id="conselho" value={dados.council_name} onChange={(e) => set("council_name", e.target.value)}>
              {CONSELHOS.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div>
            <label htmlFor="numero">Nº de registro</label>
            <input id="numero" value={dados.council_number} onChange={(e) => set("council_number", e.target.value)} />
          </div>
          <div>
            <label htmlFor="uf">Estado</label>
            <select id="uf" value={dados.council_state} onChange={(e) => set("council_state", e.target.value)}>
              <option value="">—</option>
              {UFS.map((uf) => <option key={uf} value={uf}>{uf}</option>)}
            </select>
          </div>
        </div>

        <label htmlFor="especialidade" style={{ marginTop: "0.8rem" }}>
          Especialidade <span className="eyebrow">(opcional)</span>
        </label>
        <input id="especialidade" value={dados.specialty} onChange={(e) => set("specialty", e.target.value)} />

        <h2 style={{ fontSize: "1rem", marginTop: "1.1rem" }}>Local de trabalho <span className="eyebrow">(opcional)</span></h2>
        <input placeholder="Instituição, clínica ou consultório" value={dados.workplace_name} onChange={(e) => set("workplace_name", e.target.value)} />
        <div className="grade grade--2" style={{ marginTop: "0.6rem" }}>
          <input placeholder="Setor/unidade" value={dados.workplace_department} onChange={(e) => set("workplace_department", e.target.value)} />
          <input placeholder="Cargo/função" value={dados.workplace_role} onChange={(e) => set("workplace_role", e.target.value)} />
        </div>
        <input style={{ marginTop: "0.6rem" }} placeholder="Outras informações profissionais" value={dados.workplace_notes} onChange={(e) => set("workplace_notes", e.target.value)} />
        <label style={{ display: "flex", gap: 8, alignItems: "center", fontWeight: 400, marginTop: "0.6rem" }}>
          <input type="checkbox" style={{ width: "auto" }} checked={dados.include_workplace_on_documents}
                 onChange={(e) => set("include_workplace_on_documents", e.target.checked)} />
          Incluir o local de trabalho em receitas e documentos
        </label>

        <label htmlFor="email" style={{ marginTop: "0.8rem" }}>E-mail (será seu login)</label>
        <input id="email" type="email" value={dados.email} onChange={(e) => set("email", e.target.value)} />

        <label htmlFor="senha" style={{ marginTop: "0.8rem" }}>Senha</label>
        <CampoSenha id="senha" autoComplete="new-password" value={dados.password}
               onChange={(e) => set("password", e.target.value)} />
        {senhaFraca && (
          <p style={{ color: "var(--alerta)", fontSize: "0.82rem", margin: "0.3rem 0 0" }}>
            Mínimo 8 caracteres.
          </p>
        )}

        {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erro}</p>}

        <button className="botao" style={{ width: "100%", marginTop: "1.1rem" }}
                onClick={enviar} disabled={!completo || enviando}>
          {enviando ? "Enviando…" : "Enviar solicitação"}
        </button>
        <button className="botao botao--secundario" style={{ width: "100%", marginTop: "0.5rem" }}
                onClick={() => navigate("/entrar")}>
          Já tenho conta
        </button>

        <Credito compacto />
      </div>
    </div>
  );
}
