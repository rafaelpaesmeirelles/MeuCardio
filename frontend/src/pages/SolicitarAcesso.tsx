import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import Icone from "../components/Icone";
import GrafoConstelacao from "../components/GrafoConstelacao";
import CampoSenha from "../components/CampoSenha";
import "../styles/login.css";

// Cadastro profissional no mesmo shell visual do Clinical OS. O segundo
// e-mail é obrigatório porque o login pode ser uma caixa @corvia.med.br que
// depende do próprio acesso à plataforma; recuperação não pode depender do
// recurso que está bloqueado.

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

  if (resposta) {
    return <TelaConfirmacao acessoImediato={resposta.acesso_imediato === true} />;
  }

  return (
    <main className="login login--solicitar-acesso">
      <section className="login-vitrine" aria-labelledby="login-vitrine-titulo">
        <div className="login-vitrine__luz login-vitrine__luz--um" aria-hidden="true" />
        <div className="login-vitrine__luz login-vitrine__luz--dois" aria-hidden="true" />

        <Link to="/" className="login-vitrine__marca" aria-label="CorVIA — página inicial">
          <img src="/corvia-logo.png" alt="CorVIA" />
          <small>Clinical OS do médico</small>
        </Link>

        <div className="login-vitrine__conteudo">
          <h1 id="login-vitrine-titulo">
            O primeiro passo
            <br />
            <em>para o seu Clinical OS.</em>
          </h1>
          <p className="login-vitrine__descricao">
            Confirme seus dados reais uma vez — conhecimento, contexto, paciente, decisão
            e ação ficam conectados no mesmo workspace a partir daí.
          </p>

          <GrafoConstelacao variante="escuro" className="login-vitrine__grafo" />

          <ul className="login-vitrine__beneficios">
            <li><Icone nome="check" aria-hidden="true" />Verificação de identidade uma única vez</li>
            <li><Icone nome="check" aria-hidden="true" />Canal externo independente para recuperar o acesso</li>
            <li><Icone nome="check" aria-hidden="true" />Acesso liberado assim que confirmado</li>
          </ul>
        </div>

        <footer className="login-vitrine__rodape">
          <span>CorVIA — Clinical OS do médico</span>
          <span>Uso exclusivo de profissionais autorizados</span>
        </footer>
      </section>

      <section className="login-acesso" aria-labelledby="login-acesso-titulo">
        <div className="login-acesso__topo">
          <Link to="/" aria-label="CorVIA — início">
            <img src="/corvia-logo-compacta.png" alt="CorVIA" />
          </Link>
          <Link to="/entrar" className="login-acesso__conhecer">
            <span className="login-acesso__conhecer-longo">Já tenho conta</span>
            <span className="login-acesso__conhecer-curto">Entrar</span>
            <Icone nome="seta" aria-hidden="true" />
          </Link>
        </div>

        <div className="login-acesso__conteudo">
          <div className="login-marca-mobile">
            <small>Clinical OS do médico</small>
            <h1>
              Solicitar <strong>acesso profissional</strong>
            </h1>
            <svg className="login-marca-mobile__pulso" viewBox="0 0 320 22" aria-hidden="true">
              <path d="M0 11h104l11-8 12 16 11-12 9 9 8-5h165" />
            </svg>
          </div>

          <div className="login-acesso__introducao">
            <p className="eyebrow">Solicitação de acesso</p>
            <h2 id="login-acesso-titulo">Solicitar acesso ao CorVIA.</h2>
            <p>Preencha seus dados reais e mantenha um segundo e-mail independente para segurança da conta.</p>
          </div>

          <form className="login-formulario" onSubmit={enviar}>
            <div className="login-formulario__secao">
              <h3 className="login-formulario__secao-titulo">Dados pessoais</h3>

              <div className="login-campo">
                <label htmlFor="nome">Nome completo</label>
                <input id="nome" value={dados.full_name} onChange={(e) => set("full_name", e.target.value)} required />
              </div>

              <div className="grade grade--2">
                <div className="login-campo">
                  <label htmlFor="nasc">Data de nascimento</label>
                  <input id="nasc" type="date" value={dados.birth_date}
                         onChange={(e) => set("birth_date", e.target.value)} required />
                </div>
                <div className="login-campo">
                  <label htmlFor="cpf">CPF</label>
                  <input id="cpf" value={dados.cpf} inputMode="numeric" placeholder="000.000.000-00"
                         onChange={(e) => set("cpf", formatarCpf(e.target.value))} required />
                </div>
              </div>

              <div className="login-campo">
                <label htmlFor="instagram">Instagram <span className="eyebrow">(opcional)</span></label>
                <input id="instagram" placeholder="@seu.usuario" value={dados.instagram_handle}
                       onChange={(e) => set("instagram_handle", e.target.value)} />
              </div>
              <p className="login-formulario__secao-nota">
                Só se você quiser — usamos apenas para mostrar sua foto de perfil pública na tela
                de boas-vindas. Nunca procuramos ou adivinhamos seu perfil por conta própria.
              </p>
            </div>

            <div className="login-formulario__secao">
              <h3 className="login-formulario__secao-titulo">Dados profissionais</h3>

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

              <div className="grade grade--3">
                <div className="login-campo">
                  <label htmlFor="conselho">Conselho</label>
                  <select id="conselho" value={dados.council_name} onChange={(e) => set("council_name", e.target.value)}>
                    {CONSELHOS.map((c) => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>
                <div className="login-campo">
                  <label htmlFor="numero">Nº de registro</label>
                  <input id="numero" value={dados.council_number} onChange={(e) => set("council_number", e.target.value)} required />
                </div>
                {!ehOutro && (
                  <div className="login-campo">
                    <label htmlFor="uf">Estado</label>
                    <select id="uf" value={dados.council_state} onChange={(e) => set("council_state", e.target.value)}>
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
                    <input id="conselho-outro" placeholder="Ex.: Ordem dos Farmacêuticos"
                           value={dados.council_name_other}
                           onChange={(e) => set("council_name_other", e.target.value)} />
                  </div>
                  <div className="login-campo">
                    <label htmlFor="conselho-estado-outro">Estado/região</label>
                    <input id="conselho-estado-outro" placeholder="Ex.: São Paulo"
                           value={dados.council_state_other}
                           onChange={(e) => set("council_state_other", e.target.value)} />
                  </div>
                </div>
              )}

              <div className="login-campo">
                <label htmlFor="especialidade">Especialidade <span className="eyebrow">(opcional)</span></label>
                <input id="especialidade" value={dados.specialty} onChange={(e) => set("specialty", e.target.value)} />
              </div>

              <div className="login-campo">
                <label htmlFor="local-trabalho">Local de trabalho <span className="eyebrow">(opcional)</span></label>
                <input id="local-trabalho" placeholder="Instituição, clínica ou consultório"
                       value={dados.workplace_name} onChange={(e) => set("workplace_name", e.target.value)} />
              </div>
              <div className="grade grade--2">
                <input placeholder="Setor/unidade" value={dados.workplace_department} onChange={(e) => set("workplace_department", e.target.value)} aria-label="Setor/unidade" />
                <input placeholder="Cargo/função" value={dados.workplace_role} onChange={(e) => set("workplace_role", e.target.value)} aria-label="Cargo/função" />
              </div>
              <input placeholder="Outras informações profissionais" value={dados.workplace_notes}
                     onChange={(e) => set("workplace_notes", e.target.value)} aria-label="Outras informações profissionais" />

              <div className="login-formulario__checavel">
                <input id="incluir-local" type="checkbox" checked={dados.include_workplace_on_documents}
                       onChange={(e) => set("include_workplace_on_documents", e.target.checked)} />
                <div>
                  <label htmlFor="incluir-local">Incluir o local de trabalho em receitas e documentos</label>
                </div>
              </div>
            </div>

            <div className="login-formulario__secao">
              <h3 className="login-formulario__secao-titulo">Acesso e recuperação</h3>

              <div className="login-campo">
                <label htmlFor="email">E-mail de login</label>
                <input id="email" type="email" autoComplete="username" value={dados.email}
                       onChange={(e) => set("email", e.target.value)} required />
              </div>

              <div className="login-campo">
                <label htmlFor="recovery-email">Segundo e-mail para recuperação de acesso</label>
                <input id="recovery-email" type="email" autoComplete="email" value={dados.recovery_email}
                       onChange={(e) => set("recovery_email", e.target.value)}
                       placeholder="Use um e-mail externo ao CorVIA" required />
                <p className="login-formulario__secao-nota">
                  Obrigatório e diferente do login. Se seu login for uma caixa @corvia.med.br,
                  use aqui Gmail, Outlook, iCloud ou outro endereço que continue acessível mesmo
                  quando você estiver fora do CorVIA.
                </p>
                {dados.recovery_email.length > 0 && !emailRecuperacaoValido && (
                  <p className="login-formulario__secao-nota" style={{ color: "#e8a1ab" }}>
                    Informe um e-mail válido e diferente do e-mail de login.
                  </p>
                )}
              </div>

              <div className="login-campo">
                <label htmlFor="senha">Senha</label>
                <CampoSenha id="senha" autoComplete="new-password" value={dados.password}
                       onChange={(e) => set("password", e.target.value)} required />
                {senhaFraca && (
                  <p className="login-formulario__secao-nota" style={{ color: "#e8a1ab" }}>
                    Mínimo 8 caracteres.
                  </p>
                )}
              </div>
            </div>

            <div className="login-formulario__aviso">
              <Icone nome="documento" aria-hidden="true" />
              <p>
                <strong>Próximo passo:</strong> depois de enviar, seu registro no conselho de
                classe passa por conferência. O segundo e-mail recebe uma confirmação de segurança
                e será usado para recuperação da conta. O CorVIA nunca envia sua senha em texto.
              </p>
            </div>

            {erro && <p role="alert" className="login-formulario__erro">{erro}</p>}

            <button className="login-formulario__entrar" type="submit" disabled={!completo || enviando}>
              <span>{enviando ? "Enviando…" : "Enviar solicitação"}</span>
              {!enviando && <Icone nome="seta" aria-hidden="true" />}
              {enviando && <i className="login-formulario__carregando" aria-hidden="true" />}
            </button>
          </form>

          <div className="login-acesso__novo">
            <span>Já é assinante do CorVIA?</span>
            <Link to="/entrar">Entrar <Icone nome="seta" aria-hidden="true" /></Link>
          </div>

          <p className="login-acesso__seguranca">
            <Icone nome="check" aria-hidden="true" /> Seus dados são usados para confirmar sua
            identidade profissional e proteger o acesso à conta.
          </p>
        </div>

        <footer className="login-acesso__rodape">
          <span>© {new Date().getFullYear()} CorVIA</span>
          <nav aria-label="Links institucionais">
            <Link to="/privacidade">Privacidade</Link>
            <Link to="/termos">Termos</Link>
            <a href="mailto:contato@corvia.med.br">Suporte</a>
          </nav>
        </footer>
      </section>
    </main>
  );
}

function TelaConfirmacao({ acessoImediato }: { acessoImediato: boolean }) {
  return (
    <main className="login login--solicitar-acesso">
      <section className="login-vitrine" aria-hidden="true">
        <div className="login-vitrine__luz login-vitrine__luz--um" />
        <div className="login-vitrine__luz login-vitrine__luz--dois" />
        <Link to="/" className="login-vitrine__marca" aria-label="CorVIA — página inicial">
          <img src="/corvia-logo.png" alt="CorVIA" />
          <small>Clinical OS do médico</small>
        </Link>
        <div className="login-vitrine__conteudo">
          <h1>
            {acessoImediato ? "Tudo pronto." : "Quase lá."}
            <br />
            <em>{acessoImediato ? "Seu acesso já está liberado." : "Só falta a confirmação."}</em>
          </h1>
        </div>
        <footer className="login-vitrine__rodape">
          <span>CorVIA — Clinical OS do médico</span>
          <span>Uso exclusivo de profissionais autorizados</span>
        </footer>
      </section>

      <section className="login-acesso" aria-labelledby="confirmacao-titulo">
        <div className="login-acesso__topo">
          <Link to="/" aria-label="CorVIA — início">
            <img src="/corvia-logo-compacta.png" alt="CorVIA" />
          </Link>
        </div>

        <div className="login-acesso__conteudo">
          <div className="login-confirmacao">
            <div className={`login-confirmacao__selo${acessoImediato ? "" : " login-confirmacao__selo--pendente"}`}>
              <Icone nome={acessoImediato ? "check" : "relogio"} aria-hidden="true" width={24} height={24} />
            </div>
            <h2 id="confirmacao-titulo">
              {acessoImediato ? "Cadastro concluído — acesso liberado" : "Solicitação enviada"}
            </h2>
            {acessoImediato ? (
              <p>
                Seus dados foram registrados e o acesso ao CorVIA já está liberado. Seu segundo
                e-mail também foi registrado como canal independente de recuperação.
              </p>
            ) : (
              <p>
                Seus dados foram registrados. Um administrador vai conferir seu registro no
                conselho de classe. Seu segundo e-mail já ficou protegido como canal de recuperação.
              </p>
            )}
            <Link to="/entrar" className="login-formulario__entrar" style={{ width: "fit-content" }}>
              <span>{acessoImediato ? "Entrar no CorVIA" : "Voltar para o login"}</span>
              <Icone nome="seta" aria-hidden="true" />
            </Link>
          </div>
        </div>

        <footer className="login-acesso__rodape">
          <span>© {new Date().getFullYear()} CorVIA</span>
          <nav aria-label="Links institucionais">
            <Link to="/privacidade">Privacidade</Link>
            <Link to="/termos">Termos</Link>
            <a href="mailto:contato@corvia.med.br">Suporte</a>
          </nav>
        </footer>
      </section>
    </main>
  );
}
