import { useEffect, useState } from "react";
import { api, ApiError } from "../lib/api";
import { Carregando, Erro, Vazio } from "../components/Estado";

type Atualizacao = {
  id: number;
  slug: string;
  org: string;
  title: string;
  published_at: string;
  discovered_at: string;
  url: string | null;
  status: "detected" | "aguardando_revisao" | "revisada";
  clinical_content_changed: false;
};

type Notificacao = {
  notification_id: number;
  read_at: string | null;
  message: string;
  guideline: Atualizacao;
};

type RespostaAtualizacoes = { cutoff: string; items: Atualizacao[] };
type RespostaNotificacoes = { cutoff: string; items: Notificacao[] };

function dataBr(valor: string) {
  return new Date(valor).toLocaleDateString("pt-BR", { timeZone: "UTC" });
}

export default function Diretrizes() {
  const [atualizacoes, setAtualizacoes] = useState<RespostaAtualizacoes | null>(null);
  const [notificacoes, setNotificacoes] = useState<RespostaNotificacoes | null>(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    Promise.all([
      api.get<RespostaAtualizacoes>("/guideline-updates"),
      api.get<RespostaNotificacoes>("/guideline-updates/me?include_read=true"),
    ])
      .then(([lista, alertas]) => {
        setAtualizacoes(lista);
        setNotificacoes(alertas);
      })
      .catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível carregar as atualizações."));
  }, []);

  async function marcarLida(id: number) {
    try {
      const resposta = await api.post<{ notification_id: number; read_at: string }>(
        `/guideline-updates/${id}/read`,
        {},
      );
      setNotificacoes((atual) => atual ? {
        ...atual,
        items: atual.items.map((item) => item.notification_id === id
          ? { ...item, read_at: resposta.read_at }
          : item),
      } : atual);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível marcar o alerta como lido.");
    }
  }

  if (erro) return <Erro mensagem={erro} />;
  if (!atualizacoes || !notificacoes) return <Carregando texto="Verificando publicações oficiais…" />;

  const naoLidas = notificacoes.items.filter((item) => !item.read_at);

  return (
    <>
      <p className="eyebrow">Diretrizes</p>
      <h1>Alertas de novas diretrizes</h1>
      <p style={{ maxWidth: "72ch", color: "var(--texto-secundario)" }}>
        Este painel mostra somente publicações oficiais com data igual ou posterior a{" "}
        <strong>10/08/2026</strong>. A detecção automática confirma que a publicação existe;
        ela não modifica recomendações, doses ou protocolos da Corvia sem revisão clínica humana.
      </p>

      {naoLidas.length > 0 && (
        <section style={{ marginTop: "1.2rem" }}>
          <p className="eyebrow">Novos para você</p>
          <div style={{ display: "grid", gap: "0.8rem" }}>
            {naoLidas.map((item) => (
              <article key={item.notification_id} className="cartao painel__funcao painel__funcao--destaque">
                <p className="eyebrow" style={{ margin: 0 }}>
                  {item.guideline.org} · publicado em {dataBr(item.guideline.published_at)}
                </p>
                <strong>{item.guideline.title}</strong>
                <span>{item.message}</span>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                  {item.guideline.url && (
                    <a className="botao" href={item.guideline.url} target="_blank" rel="noopener noreferrer">
                      Abrir publicação oficial ↗
                    </a>
                  )}
                  <button className="botao botao--secundario" onClick={() => marcarLida(item.notification_id)}>
                    Marcar como lido
                  </button>
                </div>
              </article>
            ))}
          </div>
        </section>
      )}

      <section className="painel__grupo">
        <h2>Publicações identificadas desde 10/08/2026</h2>
        <p className="painel__grupo-sub">
          Itens aguardando revisão clínica permanecem claramente rotulados; nenhum conteúdo da plataforma é atualizado em silêncio.
        </p>
        {atualizacoes.items.length === 0 ? (
          <Vazio
            titulo="Nenhuma nova diretriz oficial identificada"
            acao="A rotina continuará consultando automaticamente as fontes oficiais."
          />
        ) : (
          <div className="painel__funcoes">
            {atualizacoes.items.map((item) => (
              <article key={item.id} className="cartao painel__funcao">
                <p className="eyebrow" style={{ margin: 0 }}>
                  {item.org} · {dataBr(item.published_at)}
                </p>
                <strong>{item.title}</strong>
                <span>
                  {item.status === "revisada"
                    ? "Revisão clínica concluída."
                    : "Publicação detectada; análise clínica aguardando revisão humana."}
                </span>
                {item.url && (
                  <a href={item.url} target="_blank" rel="noopener noreferrer">
                    Documento oficial ↗
                  </a>
                )}
              </article>
            ))}
          </div>
        )}
      </section>
    </>
  );
}
