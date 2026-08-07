import { useEffect, useState } from "react";
import { api, ApiError } from "../lib/api";
import LogoProvedor from "../components/LogoProvedor";

type IntegracaoExterna = {
  id: number;
  provider: string;
  display_name: string;
  status: string;
  enabled: boolean;
  contacts_enabled: boolean;
  sync_calendar: boolean;
  sync_mail: boolean;
  capabilities?: Record<string, boolean>;
  contact_count: number;
  last_success_at: string | null;
  last_error_message: string | null;
};
type CapacidadesSync = { connectors: Array<{ provider: string; oauth_configured?: boolean }> };

const PROVEDORES_SINCRONIZAVEIS = ["google_calendar", "microsoft_365", "apple_icloud", "yahoo_mail"] as const;
const PROVEDOR_LOGO: Record<string, "google" | "microsoft" | "apple" | "yahoo"> = {
  google_calendar: "google", microsoft_365: "microsoft", apple_icloud: "apple", yahoo_mail: "yahoo",
};
const PROVEDOR_NOME: Record<string, string> = {
  google_calendar: "Google", microsoft_365: "Microsoft", apple_icloud: "Apple iCloud", yahoo_mail: "Yahoo Mail",
};

/** Trabalho 16 (07/08/2026), item próprio do menu ("Sincronize suas
 * contas", seção Gestão, posição inferior do menu lateral — pedido do
 * Rafael em 07/08/2026): conectar/gerenciar contas Google, Microsoft,
 * Apple e Yahoo num só lugar — múltiplas contas por empresa, escolher o
 * que cada uma sincroniza (agenda, contatos, e-mail) e desconectar quando
 * quiser. A conexão em si (OAuth do Google/Microsoft, formulário de senha
 * específica de app da Apple/Yahoo) reaproveita exatamente as mesmas rotas
 * já usadas pelo painel de configuração da Agenda — o retorno do OAuth do
 * Google/Microsoft sempre pousa em `/agenda` (é o `redirect_uri` fixo
 * cadastrado no provedor), então logo após conectar por aqui o navegador
 * passa brevemente pela Agenda antes — comportamento esperado, não um
 * bug desta tela.
 *
 * O que aparece aqui é só a CONEXÃO e a preferência de sincronização; a
 * ESCOLHA de qual conta VER em cada momento é feita na própria Agenda e no
 * CorvIA Mail (cada um com seu seletor de contas, combinável à vontade). */
export default function Sincronizacao() {
  const [integracoes, setIntegracoes] = useState<IntegracaoExterna[] | null>(null);
  const [capacidades, setCapacidades] = useState<CapacidadesSync | null>(null);
  const [consentimento, setConsentimento] = useState(false);
  const [conectando, setConectando] = useState<string | null>(null);
  const [sincronizando, setSincronizando] = useState<number | null>(null);
  const [erro, setErro] = useState("");
  const [mensagem, setMensagem] = useState("");
  const [formAberto, setFormAberto] = useState<"apple" | "yahoo" | null>(null);
  const [apple, setApple] = useState({
    apple_id: "", app_specific_password: "", consent_accepted: false,
    mail: false, mail_consent_accepted: false,
  });
  const [yahoo, setYahoo] = useState({ endereco: "", senha_de_app: "", consent_accepted: false });

  async function carregar() {
    const [i, c] = await Promise.all([
      api.get<IntegracaoExterna[]>("/agenda/integrations"),
      api.get<CapacidadesSync>("/agenda/capabilities"),
    ]);
    setIntegracoes(i);
    setCapacidades(c);
  }
  useEffect(() => { carregar().catch(() => {}); }, []);

  // Volta do redirecionamento OAuth do Google/Microsoft (que sempre pousa
  // em /agenda) — se o usuário for trazido de volta para cá por algum
  // link, ainda tratamos os parâmetros por segurança, mas o caminho normal
  // é o aviso aparecer na própria Agenda.
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const conectada = params.get("conta_conectada");
    const falha = params.get("conta_erro");
    if (conectada) setMensagem(`Conta ${PROVEDOR_NOME[conectada] || "externa"} conectada.`);
    if (falha) setErro("Não foi possível concluir a conexão com a conta externa.");
    if (conectada || falha) window.history.replaceState({}, "", window.location.pathname);
  }, []);

  async function conectarOAuth(provider: "google" | "microsoft") {
    setConectando(provider); setErro(""); setMensagem("");
    try {
      const r = await api.get<{ authorization_url: string }>(
        `/agenda/oauth/${provider}/start?contacts=true&mail=true&calendar_write=false&consent_accepted=true`
      );
      window.location.assign(r.authorization_url);
    } catch (e) {
      setConectando(null);
      setErro(e instanceof ApiError ? e.message : `Não foi possível conectar ${provider === "google" ? "Google" : "Microsoft"}.`);
    }
  }

  async function conectarApple() {
    setErro(""); setMensagem("");
    try {
      await api.post("/agenda/integrations/apple", { ...apple, contacts: true });
      setApple({ apple_id: "", app_specific_password: "", consent_accepted: false, mail: false, mail_consent_accepted: false });
      setFormAberto(null);
      setMensagem("Conta Apple conectada.");
      await carregar();
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível conectar o iCloud.");
    }
  }

  async function conectarYahoo() {
    setErro(""); setMensagem("");
    try {
      await api.post("/email/conectar-yahoo", yahoo);
      setYahoo({ endereco: "", senha_de_app: "", consent_accepted: false });
      setFormAberto(null);
      setMensagem("Conta Yahoo conectada.");
      await carregar();
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível conectar a Yahoo.");
    }
  }

  /** Trabalho 16, ajuste de 07/08/2026 — Rafael reportou que "clicar em
   * sincronizar não resulta em nada": esta página nasceu só com Conectar +
   * preferências, sem nenhuma ação de "buscar agora" — quem já estava
   * conectado (ex.: Microsoft de véspera) não tinha como pedir uma nova
   * busca por aqui, só na tela antiga da Agenda. Mesma rota que a Agenda já
   * usa (`sincronizarConta`), para não duplicar comportamento. Contas só de
   * e-mail (Yahoo) não têm este botão — a leitura delas é sempre ao vivo,
   * feita no momento de abrir o CorvIA Mail, não por sincronização prévia. */
  async function sincronizarConta(id: number) {
    setSincronizando(id); setErro(""); setMensagem("");
    try {
      await api.post(`/agenda/integrations/${id}/sync-all?full=false`, {});
      await carregar();
      setMensagem("Agenda e contatos atualizados agora.");
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível sincronizar agora.");
    } finally {
      setSincronizando(null);
    }
  }

  async function alterarPreferencia(id: number, campo: "sync_calendar" | "sync_mail" | "contacts", valor: boolean) {
    setErro("");
    try {
      await api.patch(`/agenda/integrations/${id}/preferencias`, { [campo]: valor });
      await carregar();
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível alterar a preferência.");
    }
  }

  async function desconectar(id: number, nome: string) {
    if (!window.confirm(`Desconectar ${nome}? Os contatos sincronizados dela serão removidos do Corvia.`)) return;
    setErro("");
    try {
      await api.delete(`/agenda/integrations/${id}`);
      await carregar();
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível desconectar.");
    }
  }

  if (!integracoes || !capacidades) return null;

  const conectadas = integracoes.filter((i) => (PROVEDORES_SINCRONIZAVEIS as readonly string[]).includes(i.provider));
  const configurado = (provider: string) =>
    capacidades.connectors.find((c) => c.provider === provider)?.oauth_configured !== false;

  return (
    <>
      <p className="eyebrow">Sincronize suas contas</p>
      <h1>Sincronização de contas</h1>
      <p style={{ maxWidth: "62ch", color: "var(--texto-secundario)" }}>
        Conecte Google, Microsoft, Apple e Yahoo — quantas contas quiser, de uma ou de várias
        empresas ao mesmo tempo — e escolha exatamente o que cada uma sincroniza com a Agenda e o
        CorvIA Mail. Altere ou desconecte quando quiser. Para escolher o que VER em cada momento
        (uma conta, várias, ou todas juntas), use o seletor de contas dentro da própria Agenda ou
        do CorvIA Mail.
      </p>

      <div className="cartao" style={{ maxWidth: 720 }}>
        {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erro}</p>}
        {mensagem && <p style={{ color: "var(--sucesso)", fontSize: "0.86rem" }}>{mensagem}</p>}

        <label style={{ display: "flex", gap: 6, alignItems: "flex-start", fontSize: "0.84rem", margin: "0 0 0.6rem" }}>
          <input type="checkbox" checked={consentimento} onChange={(e) => setConsentimento(e.target.checked)} />
          Autorizo a leitura dos meus calendários, contatos e e-mails, e o envio de mensagens pela
          minha conta, para uso na Agenda e no CorvIA Mail. Posso revogar a qualquer momento.
        </label>

        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: "1rem" }}>
          <button className="botao botao--secundario" disabled={!consentimento || conectando !== null || !configurado("google_calendar")}
                  onClick={() => conectarOAuth("google")}>
            <LogoProvedor provedor="google" /> {conectando === "google" ? "Abrindo Google…" : "Conectar Google"}
          </button>
          <button className="botao botao--secundario" disabled={!consentimento || conectando !== null || !configurado("microsoft_365")}
                  onClick={() => conectarOAuth("microsoft")}>
            <LogoProvedor provedor="microsoft" /> {conectando === "microsoft" ? "Abrindo Microsoft…" : "Conectar Microsoft"}
          </button>
          <button className="botao botao--secundario" disabled={!consentimento}
                  onClick={() => setFormAberto(formAberto === "apple" ? null : "apple")}>
            <LogoProvedor provedor="apple" /> Conectar Apple
          </button>
          <button className="botao botao--secundario" disabled={!consentimento}
                  onClick={() => setFormAberto(formAberto === "yahoo" ? null : "yahoo")}>
            <LogoProvedor provedor="yahoo" /> Conectar Yahoo
          </button>
        </div>

        {formAberto === "apple" && (
          <div className="cartao" style={{ marginBottom: "1rem" }}>
            <label>ID Apple
              <input type="email" autoComplete="username" value={apple.apple_id}
                     onChange={(e) => setApple({ ...apple, apple_id: e.target.value })} placeholder="nome@icloud.com" />
            </label>
            <label>Senha específica de app
              <input type="password" autoComplete="new-password" value={apple.app_specific_password}
                     onChange={(e) => setApple({ ...apple, app_specific_password: e.target.value })} placeholder="xxxx-xxxx-xxxx-xxxx" />
            </label>
            <label style={{ display: "flex", gap: 6, alignItems: "flex-start", fontSize: "0.82rem", marginTop: "0.4rem" }}>
              <input type="checkbox" checked={apple.consent_accepted}
                     onChange={(e) => setApple({ ...apple, consent_accepted: e.target.checked })} />
              Autorizo a leitura do Calendário e dos Contatos do iCloud.
            </label>
            <label style={{ display: "flex", gap: 6, alignItems: "flex-start", fontSize: "0.82rem" }}>
              <input type="checkbox" checked={apple.mail}
                     onChange={(e) => setApple({ ...apple, mail: e.target.checked, mail_consent_accepted: e.target.checked ? apple.mail_consent_accepted : false })} />
              Também conectar o e-mail do iCloud (mesma senha específica de app).
            </label>
            {apple.mail && (
              <label style={{ display: "flex", gap: 6, alignItems: "flex-start", fontSize: "0.82rem" }}>
                <input type="checkbox" checked={apple.mail_consent_accepted}
                       onChange={(e) => setApple({ ...apple, mail_consent_accepted: e.target.checked })} />
                Autorizo a leitura e o envio de e-mail pela minha caixa iCloud.
              </label>
            )}
            <p style={{ fontSize: "0.78rem", color: "var(--texto-secundario)", margin: "0.5rem 0" }}>
              Pode conectar mais de uma conta Apple — cada ID diferente vira uma conta nova, sem
              substituir a anterior. Gere a senha em appleid.apple.com → Entrar e Segurança → Senhas
              específicas de app. O Corvia nunca solicita nem guarda sua senha principal da Apple.
            </p>
            <button className="botao"
                    disabled={!apple.apple_id || !apple.app_specific_password || !apple.consent_accepted || (apple.mail && !apple.mail_consent_accepted)}
                    onClick={conectarApple}>
              Conectar
            </button>
          </div>
        )}

        {formAberto === "yahoo" && (
          <div className="cartao" style={{ marginBottom: "1rem" }}>
            <label>Endereço Yahoo
              <input type="email" autoComplete="username" value={yahoo.endereco}
                     onChange={(e) => setYahoo({ ...yahoo, endereco: e.target.value })} placeholder="nome@yahoo.com" />
            </label>
            <label>Senha específica de app
              <input type="password" autoComplete="new-password" value={yahoo.senha_de_app}
                     onChange={(e) => setYahoo({ ...yahoo, senha_de_app: e.target.value })} placeholder="gerada em login.yahoo.com" />
            </label>
            <label style={{ display: "flex", gap: 6, alignItems: "flex-start", fontSize: "0.82rem", marginTop: "0.4rem" }}>
              <input type="checkbox" checked={yahoo.consent_accepted}
                     onChange={(e) => setYahoo({ ...yahoo, consent_accepted: e.target.checked })} />
              Autorizo a leitura e o envio de e-mail pela minha caixa Yahoo.
            </label>
            <p style={{ fontSize: "0.78rem", color: "var(--texto-secundario)", margin: "0.5rem 0" }}>
              Pode conectar mais de uma conta Yahoo. Gere a senha em login.yahoo.com → Segurança da
              conta → Senhas de aplicativos de terceiros. A Yahoo só sincroniza e-mail, sem calendário
              nem contatos.
            </p>
            <button className="botao" disabled={!yahoo.endereco || !yahoo.senha_de_app || !yahoo.consent_accepted}
                    onClick={conectarYahoo}>
              Conectar
            </button>
          </div>
        )}

        <h2 style={{ fontSize: "0.95rem", margin: "0.8rem 0 0.4rem" }}>Contas conectadas ({conectadas.length})</h2>
        {conectadas.length === 0 && (
          <p style={{ fontSize: "0.84rem", color: "var(--texto-secundario)" }}>Nenhuma conta conectada ainda.</p>
        )}
        {conectadas.map((item) => {
          const cap = item.capabilities || {};
          return (
            <div key={item.id} className="cartao" style={{ marginBottom: "0.6rem", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 8 }}>
                <span style={{ display: "flex", gap: 8, alignItems: "center" }}>
                  <LogoProvedor provedor={PROVEDOR_LOGO[item.provider]} />
                  <strong>{item.display_name}</strong>
                  <span className="eyebrow" style={{ margin: 0 }}>{PROVEDOR_NOME[item.provider]}</span>
                </span>
                <span style={{ display: "flex", gap: 6 }}>
                  {cap.read_appointments && (
                    <button className="botao botao--secundario" style={{ padding: "0.2rem 0.6rem", fontSize: "0.78rem" }}
                            disabled={sincronizando === item.id} onClick={() => sincronizarConta(item.id)}>
                      {sincronizando === item.id ? "Sincronizando…" : "Sincronizar agora"}
                    </button>
                  )}
                  <button className="botao botao--secundario" style={{ padding: "0.2rem 0.6rem", fontSize: "0.78rem" }}
                          onClick={() => desconectar(item.id, item.display_name)}>
                    Desconectar
                  </button>
                </span>
              </div>
              {item.last_success_at ? (
                <p style={{ margin: 0, fontSize: "0.76rem", color: "var(--texto-secundario)" }}>
                  Última sincronização: {new Date(item.last_success_at).toLocaleString("pt-BR")}
                </p>
              ) : cap.read_appointments ? (
                <p style={{ margin: 0, fontSize: "0.76rem", color: "var(--alerta)" }}>
                  Ainda sem sincronização bem-sucedida — clique em "Sincronizar agora".
                </p>
              ) : null}
              {item.last_error_message && (
                <p style={{ margin: 0, fontSize: "0.76rem", color: "var(--alerta)" }}>
                  Última falha: {item.last_error_message}
                </p>
              )}
              <p className="eyebrow" style={{ margin: 0 }}>O que sincronizar desta conta</p>
              <div style={{ display: "flex", gap: "1.2rem", flexWrap: "wrap", fontSize: "0.84rem" }}>
                {cap.read_appointments ? (
                  <label style={{ display: "flex", gap: 4, alignItems: "center" }}>
                    <input type="checkbox" checked={item.sync_calendar}
                           onChange={(e) => alterarPreferencia(item.id, "sync_calendar", e.target.checked)} />
                    Agenda/calendário
                  </label>
                ) : <span style={{ color: "var(--texto-secundario)" }}>Sem calendário</span>}
                {cap.read_contacts && (
                  <label style={{ display: "flex", gap: 4, alignItems: "center" }}>
                    <input type="checkbox" checked={item.contacts_enabled}
                           onChange={(e) => alterarPreferencia(item.id, "contacts", e.target.checked)} />
                    Contatos
                  </label>
                )}
                {cap.read_mail && (
                  <label style={{ display: "flex", gap: 4, alignItems: "center" }}>
                    <input type="checkbox" checked={item.sync_mail}
                           onChange={(e) => alterarPreferencia(item.id, "sync_mail", e.target.checked)} />
                    E-mail
                  </label>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </>
  );
}
