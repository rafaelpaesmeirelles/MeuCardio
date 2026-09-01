import { useEffect, useState } from "react";
import { api, ApiError } from "../lib/api";
import LogoProvedor from "../components/LogoProvedor";
import CampoSenha from "../components/CampoSenha";
import { googleAccountConnectVisible } from "../lib/cardiologySpacesFeature";

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
const PROVEDORES_SINCRONIZAVEIS = ["google_calendar", "microsoft_365", "apple_icloud"] as const;
const PROVEDOR_LOGO: Record<string, "google" | "microsoft" | "apple"> = {
  google_calendar: "google", microsoft_365: "microsoft", apple_icloud: "apple",
};
const PROVEDOR_NOME: Record<string, string> = {
  google_calendar: "Google", microsoft_365: "Microsoft", apple_icloud: "Apple iCloud",
};
const PROVEDOR_CHAVE_CONEXAO: Record<string, "google" | "microsoft" | "apple"> = {
  google_calendar: "google", microsoft_365: "microsoft", apple_icloud: "apple",
};
const GOOGLE_ACCOUNT_CONNECT_VISIBLE = googleAccountConnectVisible();

/** Central única para conectar e acompanhar contas externas. O backend mantém
 * OAuth/IMAP vivo em segundo plano e esta tela apenas mostra o estado atual.
 * E-mail externo é proxy ao vivo: "sincronizar" uma conta mail-only verifica
 * credencial/heartbeat; não copia a caixa para o banco CorVIA. */
export default function Sincronizacao() {
  const [integracoes, setIntegracoes] = useState<IntegracaoExterna[] | null>(null);
  const [capacidades, setCapacidades] = useState<CapacidadesSync | null>(null);
  const [consentimento, setConsentimento] = useState(false);
  const [conectando, setConectando] = useState<string | null>(null);
  const [erro, setErro] = useState("");
  const [mensagem, setMensagem] = useState("");
  const [formAberto, setFormAberto] = useState<"apple" | null>(null);
  const [removendo, setRemovendo] = useState<number | null>(null);
  const [apple, setApple] = useState({
    apple_id: "", app_specific_password: "", consent_accepted: false,
    mail: false, mail_consent_accepted: false,
  });

  async function carregar() {
    const [i, c] = await Promise.all([
      api.get<IntegracaoExterna[]>("/agenda/integrations"),
      api.get<CapacidadesSync>("/agenda/capabilities"),
    ]);
    setIntegracoes(i);
    setCapacidades(c);
  }

  useEffect(() => {
    carregar().catch(() => {});
    // Reflete heartbeat/sync do worker sem exigir F5. A sincronização em si
    // ocorre no servidor; este timer apenas atualiza os indicadores da tela.
    const timer = window.setInterval(() => carregar().catch(() => {}), 30_000);
    return () => window.clearInterval(timer);
  }, []);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const conectada = params.get("conta_conectada");
    const falha = params.get("conta_erro");
    const sincronizacao = params.get("sincronizacao");
    if (conectada) {
      setMensagem(
        sincronizacao === "pendente"
          ? `Conta ${PROVEDOR_NOME[conectada] || "externa"} conectada; a sincronização continuará automaticamente em segundo plano.`
          : `Conta ${PROVEDOR_NOME[conectada] || "externa"} conectada e sincronizada.`,
      );
      carregar().catch(() => {});
    }
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
      setMensagem("Conta Apple conectada. A manutenção da conexão passa a ser automática.");
      await carregar();
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível conectar o iCloud.");
    }
  }

  function reconectar(item: IntegracaoExterna) {
    const chave = PROVEDOR_CHAVE_CONEXAO[item.provider];
    if (chave === "google" || chave === "microsoft") { conectarOAuth(chave); return; }
    if (chave === "apple") { setApple((a) => ({ ...a, apple_id: item.display_name })); setFormAberto("apple"); return; }
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

  async function removerConta(id: number, nome: string) {
    if (!window.confirm(`Remover ${nome} do CorVIA? O vínculo e as credenciais salvas no CorVIA serão excluídos, assim como os contatos importados dessa conta. Sua conta no provedor não será apagada.`)) return;
    setErro(""); setMensagem(""); setRemovendo(id);
    try {
      await api.delete(`/agenda/integrations/${id}`);
      setIntegracoes((atuais) => atuais?.filter((item) => item.id !== id) ?? null);
      setMensagem("Conta removida do CorVIA.");
      await carregar();
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível remover a conta.");
    } finally { setRemovendo(null); }
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
        Conecte {GOOGLE_ACCOUNT_CONNECT_VISIBLE ? "Google, Microsoft e Apple" : "Microsoft e Apple"} — quantas contas quiser — e escolha o que cada
        uma integra à Agenda e ao CorvIA Mail. Depois de conectada, a conta permanece vinculada:
        A manutenção é automática: OAuth é renovado em segundo plano e o iCloud recebe heartbeat
        de credencial e o CorVIA Mail consulta caixas externas ao vivo. Reconectar só aparece quando
        a autorização realmente expirar; para encerrar o vínculo, use Remover conta.
      </p>

      <div className="cartao" style={{ maxWidth: 720 }}>
        {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erro}</p>}
        {mensagem && <p style={{ color: "var(--sucesso)", fontSize: "0.86rem" }}>{mensagem}</p>}
        <p style={{ marginTop: 0, fontSize: "0.78rem", color: "var(--texto-secundario)" }}>
          <span className="selo">Sincronização contínua</span>{" "}
          Alterações de calendário são buscadas automaticamente pelo servidor; e-mail externo é lido diretamente no provedor.
        </p>

        <label className="agenda-check" style={{ alignItems: "flex-start", fontSize: "0.84rem", margin: "0 0 0.6rem" }}>
          <input type="checkbox" checked={consentimento} onChange={(e) => setConsentimento(e.target.checked)} />
          Autorizo a leitura dos meus calendários, contatos e e-mails, e o envio de mensagens pela
          minha conta, para uso na Agenda e no CorvIA Mail. Posso revogar a qualquer momento.
        </label>

        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: "1rem" }}>
          {GOOGLE_ACCOUNT_CONNECT_VISIBLE && (
            <button className="botao botao--secundario" disabled={!consentimento || conectando !== null || !configurado("google_calendar")}
                    onClick={() => conectarOAuth("google")}>
              <LogoProvedor provedor="google" /> {conectando === "google" ? "Abrindo Google…" : "Conectar Google"}
            </button>
          )}
          <button className="botao botao--secundario" disabled={!consentimento || conectando !== null || !configurado("microsoft_365")}
                  onClick={() => conectarOAuth("microsoft")}>
            <LogoProvedor provedor="microsoft" /> {conectando === "microsoft" ? "Abrindo Microsoft…" : "Conectar Microsoft"}
          </button>
          <button className="botao botao--secundario" disabled={!consentimento}
                  onClick={() => setFormAberto(formAberto === "apple" ? null : "apple")}>
            <LogoProvedor provedor="apple" /> Conectar Apple
          </button>
        </div>

        {formAberto === "apple" && (
          <div className="cartao" style={{ marginBottom: "1rem" }}>
            <label>ID Apple
              <input type="email" autoComplete="username" value={apple.apple_id}
                     onChange={(e) => setApple({ ...apple, apple_id: e.target.value })} placeholder="nome@icloud.com" />
            </label>
            <label>Senha específica de app
              <CampoSenha autoComplete="new-password" value={apple.app_specific_password}
                     onChange={(e) => setApple({ ...apple, app_specific_password: e.target.value })} placeholder="xxxx-xxxx-xxxx-xxxx" />
            </label>
            <label className="agenda-check" style={{ alignItems: "flex-start", fontSize: "0.82rem", marginTop: "0.4rem" }}>
              <input type="checkbox" checked={apple.consent_accepted}
                     onChange={(e) => setApple({ ...apple, consent_accepted: e.target.checked })} />
              Autorizo a leitura do Calendário e dos Contatos do iCloud.
            </label>
            <label className="agenda-check" style={{ alignItems: "flex-start", fontSize: "0.82rem" }}>
              <input type="checkbox" checked={apple.mail}
                     onChange={(e) => setApple({ ...apple, mail: e.target.checked, mail_consent_accepted: e.target.checked ? apple.mail_consent_accepted : false })} />
              Também conectar o e-mail do iCloud (mesma senha específica de app).
            </label>
            {apple.mail && (
              <label className="agenda-check" style={{ alignItems: "flex-start", fontSize: "0.82rem" }}>
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

        <h2 style={{ fontSize: "0.95rem", margin: "0.8rem 0 0.4rem" }}>Contas conectadas ({conectadas.length})</h2>
        {conectadas.length === 0 && (
          <p style={{ fontSize: "0.84rem", color: "var(--texto-secundario)" }}>Nenhuma conta conectada ainda.</p>
        )}
        {conectadas.map((item) => {
          const cap = item.capabilities || {};
          const temComponenteSincronizavel = Boolean(cap.read_appointments || cap.read_contacts || cap.read_mail);
          return (
            <div key={item.id} className="cartao" style={{ marginBottom: "0.6rem", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 8 }}>
                <span style={{ display: "flex", gap: 8, alignItems: "center" }}>
                  <LogoProvedor provedor={PROVEDOR_LOGO[item.provider]} />
                  <strong>{item.display_name}</strong>
                  <span className="eyebrow" style={{ margin: 0 }}>{PROVEDOR_NOME[item.provider]}</span>
                </span>
                <span style={{ display: "flex", gap: 6 }}>
                  {(!item.enabled || item.status === "reauth_required") && (
                    <button className="botao" style={{ padding: "0.2rem 0.6rem", fontSize: "0.78rem" }} onClick={() => reconectar(item)}>
                      Reconectar
                    </button>
                  )}
                  <button className="botao botao--secundario" style={{ padding: "0.2rem 0.6rem", fontSize: "0.78rem" }}
                          disabled={removendo === item.id}
                          onClick={() => removerConta(item.id, item.display_name)}>
                    {removendo === item.id ? "Removendo…" : "Remover conta"}
                  </button>
                </span>
              </div>
              {!item.enabled || item.status === "reauth_required" ? (
                <p style={{ margin: 0, fontSize: "0.76rem", color: "var(--alerta)" }}>
                  A autorização desta conta precisa ser renovada. Clique em "Reconectar"; os dados locais
                  já sincronizados não são apagados por isso.
                </p>
              ) : item.last_success_at ? (
                <p style={{ margin: 0, fontSize: "0.76rem", color: "var(--texto-secundario)" }}>
                  Conectada e ativa · manutenção automática · última verificação: {new Date(item.last_success_at).toLocaleString("pt-BR")}
                </p>
              ) : temComponenteSincronizavel ? (
                <p style={{ margin: 0, fontSize: "0.76rem", color: "var(--alerta)" }}>
                  Conectada · primeira verificação automática pendente. Não é necessário sincronizar manualmente.
                </p>
              ) : null}
              {item.enabled && item.status !== "reauth_required" && item.last_error_message && (
                <p style={{ margin: 0, fontSize: "0.76rem", color: "var(--alerta)" }}>
                  Última pendência: {item.last_error_message}
                </p>
              )}
              <p className="eyebrow" style={{ margin: 0 }}>O que sincronizar desta conta</p>
              <div style={{ display: "flex", gap: "1.2rem", flexWrap: "wrap", fontSize: "0.84rem" }}>
                {cap.read_appointments ? (
                  <label className="agenda-check">
                    <input type="checkbox" checked={item.sync_calendar}
                           onChange={(e) => alterarPreferencia(item.id, "sync_calendar", e.target.checked)} />
                    Agenda/calendário
                  </label>
                ) : <span style={{ color: "var(--texto-secundario)" }}>Sem calendário</span>}
                {cap.read_contacts && (
                  <label className="agenda-check">
                    <input type="checkbox" checked={item.contacts_enabled}
                           onChange={(e) => alterarPreferencia(item.id, "contacts", e.target.checked)} />
                    Contatos
                  </label>
                )}
                {cap.read_mail && (
                  <label className="agenda-check">
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
