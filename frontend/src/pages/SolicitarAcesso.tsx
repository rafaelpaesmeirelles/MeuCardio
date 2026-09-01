import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import Icone from "../components/Icone";
import CampoSenha from "../components/CampoSenha";
import PublicCardiologyFrame from "../components/PublicCardiologyFrame";
import "../styles/login.css";

const CONSELHOS = ["CRM", "CRO", "CRBM", "COREN", "CRF", "CREFITO", "CRN", "CRP", "CREF", "CRESS", "Outro"];
const TITULOS = ["", "Sr.", "Sra.", "Dr.", "Dra.", "Prof.", "Profa.", "Prof. Dr.", "Profa. Dra.", "Me.", "Ma.", "Esp."];
const UFS = [
  "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG",
  "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
];

const BENEFICIOS = [
  { icon: "check" as const, title: "Segurança e privacidade", detail: "Dados profissionais protegidos e segundo canal independente de recuperação.", tone: "cyan" as const },
  { icon: "conhecimento" as const, title: "Integração clínica inteligente", detail: "Evidências, protocolos e ferramentas conectados ao mesmo fluxo de decisão.", tone: "violet" as const },
  { icon: "assistente" as const, title: "Fluxo de aprovação ágil", detail: "Cadastro conferido sem perder o contexto do seu perfil profissional.", tone: "green" as const },
];

function formatarCpf(v: string) {
  const d = v.replace(/\D/g, "").slice(0, 11);
  return d
    .replace(/(\d{3})(\d)/, "$1.$2")
    .replace(/(\d{3})(\d)/, "$1.$2")
    .replace(/(\d{3})(\d{1,2})$/, "$1-$2");
}

type RespostaEnvio = { nota: string; acesso_imediato?: boolean };

export default function SolicitarAcesso() {
  const [dados, setDados] = useState({
    full_name: "", birth_date: "", cpf: "", profession: "Médico(a)",
    council_name: "CRM", council_number: "", council_state: "",
    council_name_other: "", council_state_other: "",
    specialty: "", professional_title: "", workplace_name: "", workplace_department: "",
    workplace_role: "", workplace_notes: "", include_workplace_on_documents: false,
    instagram_handle: "",
    email: "", recovery_email: "", password: "",
  });
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [resposta, setResposta] = useState<RespostaEnvio | null>(null);

  function set<K extends keyof typeof dados>(campo: K, valor: (typeof dados)[K]) {
    setDados((d) => ({ ...d, [campo]: valor }));
  }

  const ehOutro = dados.council_name === "Outro";
  const senhaFraca = dados.password.length > 0 && dados.password.length < 8;
  const emailLogin = dados.email.trim().toLowerCase();
  const emailRecuperacao = dados.recovery_email.trim().toLowerCase();
  const emailRecuperacaoValido = emailRecuperacao.includes("@") && emailRecuperacao !== emailLogin;
  const conselhoCompleto = ehOutro
    ? dados.council_name_other.trim() && dados.council_state_other.trim()
    : dados.council_state;
  const completo =
    dados.full_name.trim().split(" ").length >= 2 &&
    dados.birth_date && dados.cpf.replace(/\D/g, "").length === 11 &&
    dados.profession.trim() && dados.council_number.trim() && conselhoCompleto &&
    emailLogin.includes("@") && emailRecuperacaoValido && dados.password.length >= 8;

  async function enviar(event?: FormEvent<HTMLFormElement>) {
    event?.preventDefault();
    if (enviando || !completo) return;
    setErro("");
    setEnviando(true);
    try {
      const r = await api.post<RespostaEnvio>("/auth/solicitar-acesso-com-recuperacao", {
        ...dados,
        email: emailLogin,
        recovery_email: emailRecuperacao,
        specialty: dados.specialty.trim() || null,
        council_state: ehOutro ? null : dados.council_state,
        council_name_other: ehOutro ? dados.council_name_other.trim() : null,
        council_state_other: ehOutro ? dados.council_state_other.trim() : null,
        instagram_handle: dados.instagram_handle.trim().replace(/^@/, "") || null,
      });
      setResposta(r);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível enviar a solicitação.");
    } finally {
      setEnviando(false);
    }
  }

  if (resposta) return <TelaConfirmacao acessoImediato={resposta.acesso_imediato === true} />;

  return (
    <PublicCardiologyFrame
      eyebrow="Identidade profissional"
      title={<>Seu acesso aos cinco espaços começa <strong>aqui.</strong></>}
      description={<p>Um cadastro único conecta Consultório, Hospital, Ensino, Pesquisa e Gestão sem romper a proteção dos seus dados profissionais.</p>}
      features={BENEFICIOS}
      variant="form"
    >
      <div className="prehome-card prehome-card--register">
          <div className="prehome-steps" aria-label="Etapas do primeiro acesso">
            <span className="prehome-step prehome-step--active"><i>1</i>Identificação</span>
            <span className="prehome-step"><i>2</i>Segurança</span>
            <span className="prehome-step"><i>3</i>Acesso</span>
          </div>

          <header className="prehome-card__header prehome-card__header--register">
            <p className="prehome-card__eyebrow"><Icone nome="conta" /> Primeiro acesso</p>
            <h2 id="cadastro-titulo">Criar acesso ao <strong>CorVIA</strong></h2>
            <p>Preencha seus dados reais. O segundo e-mail independente protege a recuperação da sua conta.</p>
          </header>

          <form className="login-formulario" onSubmit={enviar}>
            <fieldset className="login-formulario__secao">
              <legend className="login-formulario__secao-titulo">Dados pessoais</legend>
              <div className="login-campo">
                <label htmlFor="nome">Nome completo</label>
                <input id="nome" value={dados.full_name} onChange={(e) => set("full_name", e.target.value)} placeholder="Ex.: João da Silva" required />
              </div>
              <div className="grade grade--2">
                <div className="login-campo">
                  <label htmlFor="nasc">Data de nascimento</label>
                  <input id="nasc" type="date" value={dados.birth_date} onChange={(e) => set("birth_date", e.target.value)} required />
                </div>
                <div className="login-campo">
                  <label htmlFor="cpf">CPF</label>
                  <input id="cpf" value={dados.cpf} inputMode="numeric" placeholder="000.000.000-00" onChange={(e) => set("cpf", formatarCpf(e.target.value))} required />
                </div>
              </div>
              <div className="login-campo">
                <label htmlFor="instagram">Instagram <span className="eyebrow">(opcional)</span></label>
                <input id="instagram" placeholder="@seu.usuario" value={dados.instagram_handle} onChange={(e) => set("instagram_handle", e.target.value)} />
                <p className="login-formulario__secao-nota">Usado apenas, se você quiser, para sua foto pública de boas-vindas.</p>
              </div>
            </fieldset>

            <fieldset className="login-formulario__secao">
              <legend className="login-formulario__secao-titulo">Dados profissionais</legend>
              <div className="grade grade--2">
                <div className="login-campo">
                  <label htmlFor="tratamento">Como deseja ser chamado(a)</label>
                  <select id="tratamento" value={dados.professional_title} onChange={(e) => set("professional_title", e.target.value)}>
                    {TITULOS.map((t) => <option key={t || "sem"} value={t}>{t || "Sem título"}</option>)}
                  </select>
                </div>
                <div className="login-campo">
                  <label htmlFor="profissao">Profissão</label>
                  <input id="profissao" value={dados.profession} onChange={(e) => set("profession", e.target.value)} required />
                </div>
              </div>

              <div className="grade grade--3">
                <div className="login-campo">
                  <label htmlFor="conselho">Conselho</label>
                  <select id="conselho" value={dados.council_name} onChange={(e) => set("council_name", e.target.value)}>
                    {CONSELHOS.map((c) => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>
                <div className="login-campo">
                  <label htmlFor="numero">Nº de registro</label>
                  <input id="numero" value={dados.council_number} onChange={(e) => set("council_number", e.target.value)} placeholder="Ex.: 123456" required />
                </div>
                {!ehOutro && (
                  <div className="login-campo">
                    <label htmlFor="uf">UF</label>
                    <select id="uf" value={dados.council_state} onChange={(e) => set("council_state", e.target.value)} required>
                      <option value="">—</option>
                      {UFS.map((uf) => <option key={uf} value={uf}>{uf}</option>)}
                    </select>
                  </div>
                )}
              </div>

              {ehOutro && (
                <div className="grade grade--2">
                  <div className="login-campo">
                    <label htmlFor="conselho-outro">Qual conselho</label>
                    <input id="conselho-outro" placeholder="Ex.: Ordem dos Farmacêuticos" value={dados.council_name_other} onChange={(e) => set("council_name_other", e.target.value)} required />
                  </div>
                  <div className="login-campo">
                    <label htmlFor="conselho-estado-outro">Estado/região</label>
                    <input id="conselho-estado-outro" placeholder="Ex.: São Paulo" value={dados.council_state_other} onChange={(e) => set("council_state_other", e.target.value)} required />
                  </div>
                </div>
              )}

              <div className="login-campo">
                <label htmlFor="especialidade">Especialidade <span className="eyebrow">(opcional)</span></label>
                <input id="especialidade" value={dados.specialty} onChange={(e) => set("specialty", e.target.value)} placeholder="Ex.: Cardiologia" />
              </div>

              <div className="login-campo">
                <label htmlFor="local-trabalho">Local de trabalho <span className="eyebrow">(opcional)</span></label>
                <input id="local-trabalho" placeholder="Instituição, clínica ou consultório" value={dados.workplace_name} onChange={(e) => set("workplace_name", e.target.value)} />
              </div>
              <div className="grade grade--2">
                <input placeholder="Setor/unidade" value={dados.workplace_department} onChange={(e) => set("workplace_department", e.target.value)} aria-label="Setor/unidade" />
                <input placeholder="Cargo/função" value={dados.workplace_role} onChange={(e) => set("workplace_role", e.target.value)} aria-label="Cargo/função" />
              </div>
              <input placeholder="Outras informações profissionais" value={dados.workplace_notes} onChange={(e) => set("workplace_notes", e.target.value)} aria-label="Outras informações profissionais" />
              <label className="login-formulario__checavel" htmlFor="incluir-local">
                <input id="incluir-local" type="checkbox" checked={dados.include_workplace_on_documents} onChange={(e) => set("include_workplace_on_documents", e.target.checked)} />
                <span>Incluir o local de trabalho em receitas e documentos</span>
              </label>
            </fieldset>

            <fieldset className="login-formulario__secao">
              <legend className="login-formulario__secao-titulo">Acesso e recuperação</legend>
              <div className="login-campo">
                <label htmlFor="email">E-mail de login</label>
                <input id="email" type="email" autoComplete="username" value={dados.email} onChange={(e) => set("email", e.target.value)} placeholder="seu@email.com" required />
              </div>
              <div className="login-campo">
                <label htmlFor="recovery-email">E-mail externo de recuperação</label>
                <input id="recovery-email" type="email" autoComplete="email" value={dados.recovery_email} onChange={(e) => set("recovery_email", e.target.value)} placeholder="Ex.: seu.email.pessoal@gmail.com" required />
                <p className="login-formulario__secao-nota">Obrigatório, único e diferente do login. Deve continuar acessível mesmo fora do CorVIA.</p>
                {dados.recovery_email.length > 0 && !emailRecuperacaoValido && <p className="login-formulario__erro login-formulario__erro--inline">Informe um e-mail válido e diferente do login.</p>}
              </div>
              <div className="login-campo">
                <label htmlFor="senha">Criar senha</label>
                <CampoSenha id="senha" autoComplete="new-password" value={dados.password} onChange={(e) => set("password", e.target.value)} required />
                {senhaFraca && <p className="login-formulario__erro login-formulario__erro--inline">Mínimo de 8 caracteres.</p>}
              </div>
            </fieldset>

            <div className="login-formulario__aviso">
              <Icone nome="documento" aria-hidden="true" />
              <p><strong>Próximo passo:</strong> sua solicitação será conferida e o canal externo receberá as comunicações de segurança. O CorVIA nunca envia sua senha em texto.</p>
            </div>

            {erro && <p role="alert" className="login-formulario__erro">{erro}</p>}
            <button className="login-formulario__entrar" type="submit" disabled={!completo || enviando}>
              <span>{enviando ? "Enviando…" : "Solicitar acesso"}</span>
              {!enviando && <Icone nome="seta" aria-hidden="true" />}
              {enviando && <i className="login-formulario__carregando" aria-hidden="true" />}
            </button>
          </form>

          <div className="prehome-card__actions">
            <div className="prehome-divider">ou</div>
            <Link to="/entrar" className="prehome-secondary"><Icone nome="conta" /> Já tenho conta</Link>
          </div>
          <footer className="prehome-card__footer"><Icone nome="check" /> Ambiente seguro para uso profissional</footer>
      </div>
    </PublicCardiologyFrame>
  );
}

function TelaConfirmacao({ acessoImediato }: { acessoImediato: boolean }) {
  return (
    <PublicCardiologyFrame
      eyebrow={acessoImediato ? "Conta aprovada" : "Fluxo de acesso"}
      title={acessoImediato ? <>Acesso <strong>liberado.</strong></> : <>Solicitação <strong>recebida.</strong></>}
      description={<p>{acessoImediato ? "Sua identidade profissional está pronta para entrar no Cardiology Spaces." : "Seu cadastro seguirá a conferência profissional com o canal de recuperação já protegido."}</p>}
      features={BENEFICIOS}
      variant="form"
      tone={acessoImediato ? "cyan" : "violet"}
    >
      <div className="prehome-card">
          <div className="prehome-confirmation">
            <div className={`prehome-confirmation__icon${acessoImediato ? "" : " prehome-confirmation__icon--pending"}`}>
              <Icone nome={acessoImediato ? "check" : "relogio"} aria-hidden="true" />
            </div>
            <p className="prehome-card__eyebrow">{acessoImediato ? "Conta aprovada" : "Cadastro em análise"}</p>
            <h2 id="confirmacao-titulo">{acessoImediato ? "Pronto para começar" : "Solicitação enviada"}</h2>
            <p>{acessoImediato ? "Seu acesso ao CorVIA já está liberado e o segundo e-mail ficou registrado como canal independente de recuperação." : "Seus dados foram registrados. Um administrador conferirá o registro profissional; seu canal de recuperação já ficou protegido."}</p>
            <div className="prehome-confirmation__checks">
              <span>Canal de recuperação configurado <Icone nome="check" /></span>
              <span>Dados profissionais preservados <Icone nome="check" /></span>
              {acessoImediato && <span>Perfil profissional ativo <Icone nome="check" /></span>}
            </div>
            <Link to="/entrar" className="prehome-primary"><span>{acessoImediato ? "Entrar no CorVIA" : "Voltar ao login"}</span><Icone nome="seta" /></Link>
          </div>
          <footer className="prehome-card__footer"><Icone nome="check" /> Ambiente seguro para uso profissional</footer>
      </div>
    </PublicCardiologyFrame>
  );
}
