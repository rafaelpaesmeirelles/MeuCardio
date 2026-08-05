import { useCallback, useEffect, useState } from "react";
import { api, ApiError } from "../lib/api";
import { Carregando, Erro, Vazio } from "../components/Estado";

type Preferencia = {
  visible: boolean;
  online_window_minutes: number;
};

type UsuarioOnline = {
  id: number;
  full_name: string;
  profession: string | null;
  specialty: string | null;
  council: string | null;
  last_seen_at: string | null;
};

type RespostaOnline = {
  online_window_minutes: number;
  items: UsuarioOnline[];
};

function atividade(iso: string | null) {
  if (!iso) return "atividade recente";
  const minutos = Math.max(0, Math.floor((Date.now() - new Date(iso).getTime()) / 60000));
  return minutos < 1 ? "online agora" : `atividade há ${minutos} min`;
}

export default function UsuariosOnline() {
  const [preferencia, setPreferencia] = useState<Preferencia | null>(null);
  const [online, setOnline] = useState<RespostaOnline | null>(null);
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState("");

  const carregar = useCallback(async () => {
    try {
      const [minhaPreferencia, lista] = await Promise.all([
        api.get<Preferencia>("/presence/me"),
        api.get<RespostaOnline>("/presence/online"),
      ]);
      setPreferencia(minhaPreferencia);
      setOnline(lista);
      setErro("");
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível carregar a presença online.");
    }
  }, []);

  useEffect(() => {
    carregar();
    const timer = window.setInterval(carregar, 30_000);
    return () => window.clearInterval(timer);
  }, [carregar]);

  async function alterarVisibilidade(visible: boolean) {
    setSalvando(true);
    setErro("");
    try {
      const resposta = await api.put<Preferencia>("/presence/me", { visible });
      setPreferencia((atual) => ({
        visible: resposta.visible,
        online_window_minutes: atual?.online_window_minutes ?? 5,
      }));
      await carregar();
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível alterar sua visibilidade.");
    } finally {
      setSalvando(false);
    }
  }

  if (erro && (!preferencia || !online)) return <Erro mensagem={erro} />;
  if (!preferencia || !online) return <Carregando texto="Verificando presença online…" />;

  return (
    <section style={{ maxWidth: "82ch" }}>
      <p className="eyebrow">Comunidade profissional</p>
      <h1>Usuários online</h1>
      <p style={{ color: "var(--texto-secundario)", maxWidth: "70ch" }}>
        A presença é opcional e nasce desativada. Você só aparece para outros assinantes
        quando autoriza, e pode revogar a autorização a qualquer momento.
      </p>

      <div className="cartao" style={{ margin: "1rem 0" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
          <div>
            <strong>Mostrar meu nome quando eu estiver online</strong>
            <p style={{ color: "var(--texto-secundario)", margin: "0.3rem 0 0", fontSize: "0.86rem" }}>
              Online significa atividade nos últimos {preferencia.online_window_minutes} minutos.
              E-mail, telefone e dados de acesso nunca são exibidos.
            </p>
          </div>
          <label style={{ display: "flex", alignItems: "center", gap: 8, fontWeight: 600 }}>
            <input
              type="checkbox"
              style={{ width: "auto" }}
              checked={preferencia.visible}
              disabled={salvando}
              onChange={(e) => alterarVisibilidade(e.target.checked)}
            />
            {preferencia.visible ? "Visível" : "Oculto"}
          </label>
        </div>
      </div>

      {erro && <p role="alert" style={{ color: "var(--alerta)" }}>{erro}</p>}

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: 12 }}>
        <h2>Online e visíveis agora</h2>
        <span className="dado">{online.items.length}</span>
      </div>

      {online.items.length === 0 ? (
        <Vazio
          titulo="Nenhum assinante visível neste momento"
          acao="A lista mostra somente quem está online e autorizou a exibição do próprio nome."
        />
      ) : (
        <div className="grade grade--2">
          {online.items.map((usuario) => (
            <article key={usuario.id} className="cartao">
              <div style={{ display: "flex", gap: 9, alignItems: "center" }}>
                <span aria-hidden="true" style={{ width: 9, height: 9, borderRadius: "50%", background: "var(--sucesso)", flexShrink: 0 }} />
                <strong>{usuario.full_name}</strong>
              </div>
              <p style={{ margin: "0.45rem 0 0", color: "var(--texto-secundario)" }}>
                {[usuario.profession, usuario.specialty].filter(Boolean).join(" · ") || "Profissional de saúde"}
              </p>
              {usuario.council && <p className="eyebrow" style={{ margin: "0.35rem 0 0" }}>{usuario.council}</p>}
              <small style={{ color: "var(--texto-secundario)" }}>{atividade(usuario.last_seen_at)}</small>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
