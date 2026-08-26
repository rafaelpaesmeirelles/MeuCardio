import { useEffect, useMemo, useState } from "react";
import { api, ApiError } from "../lib/api";
import { Carregando, Erro } from "../components/Estado";
import {
  ClinicalContextLink,
  ClinicalEmpty,
  ClinicalMetric,
  ClinicalPageHeader,
  ClinicalSection,
} from "../components/ClinicalCommandPrimitives";

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
type DiretrizBiblioteca = {
  slug: string;
  title: string;
  theme: string;
};

function dataBr(valor: string) {
  return new Date(valor).toLocaleDateString("pt-BR", { timeZone: "UTC" });
}

function statusLabel(status: Atualizacao["status"]) {
  if (status === "revisada") return "Revisada";
  if (status === "aguardando_revisao") return "Aguardando revisão";
  return "Detectada";
}

export default function Diretrizes() {
  const [atualizacoes, setAtualizacoes] = useState<RespostaAtualizacoes | null>(null);
  const [notificacoes, setNotificacoes] = useState<RespostaNotificacoes | null>(null);
  const [diretrizes, setDiretrizes] = useState<DiretrizBiblioteca[] | null>(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    Promise.all([
      api.get<RespostaAtualizacoes>("/guideline-updates"),
      api.get<RespostaNotificacoes>("/guideline-updates/me?include_read=true"),
      api.get<{ items: DiretrizBiblioteca[] }>("/library/documents?kind=diretriz&limit=200"),
    ])
      .then(([lista, alertas, biblioteca]) => {
        setAtualizacoes(lista);
        setNotificacoes(alertas);
        setDiretrizes(biblioteca.items);
      })
      .catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível carregar as atualizações."));
  }, []);

  const naoLidas = useMemo(
    () => (notificacoes?.items ?? []).filter((item) => !item.read_at),
    [notificacoes?.items],
  );
  const revisadas = useMemo(
    () => (atualizacoes?.items ?? []).filter((item) => item.status === "revisada").length,
    [atualizacoes?.items],
  );
  const organizacoes = useMemo(
    () => new Set((atualizacoes?.items ?? []).map((item) => item.org).filter(Boolean)).size,
    [atualizacoes?.items],
  );

  async function marcarLida(id: number) {
    try {
      const resposta = await api.post<{ notification_id: number; read_at: string }>(`/guideline-updates/${id}/read`, {});
      setNotificacoes((atual) => atual ? {
        ...atual,
        items: atual.items.map((item) => item.notification_id === id ? { ...item, read_at: resposta.read_at } : item),
      } : atual);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível marcar o alerta como lido.");
    }
  }

  if (erro) return <Erro mensagem={erro} />;
  if (!atualizacoes || !notificacoes || !diretrizes) return <Carregando texto="Verificando publicações oficiais…" />;

  return (
    <div className="cc-page cc-guidelines-page">
      <ClinicalPageHeader
        eyebrow="Guidelines"
        title="Diretrizes e alertas clínicos"
        description="Publicações oficiais detectadas com rastreabilidade. Nenhuma recomendação, dose ou protocolo muda na CorVIA sem revisão clínica humana."
        icon="documento"
        actions={[
          { to: "/evidencias", label: "Evidências", icon: "evidencia" },
          { to: "/estudos", label: "Estudos", icon: "evidencia", tone: "primary" },
        ]}
        meta={<><span className="selo">monitoramento oficial</span><span className="selo">revisão humana</span></>}
      />

      <div className="cc-metrics">
        <ClinicalMetric label="Publicações" value={atualizacoes.items.length} detail={`desde ${dataBr(atualizacoes.cutoff)}`} icon="documento" />
        <ClinicalMetric label="Novas para você" value={naoLidas.length} detail="alertas ainda não lidos" icon="evidencia" />
        <ClinicalMetric label="Revisadas" value={revisadas} detail="análise clínica concluída" icon="check" />
        <ClinicalMetric label="Organizações" value={organizacoes} detail="fontes oficiais detectadas" icon="documento" />
      </div>

      {naoLidas.length > 0 && (
        <ClinicalSection eyebrow="Seu radar clínico" title="Novos para você" description="Priorize o que foi publicado desde sua última revisão.">
          <div className="cc-guideline-alerts">
            {naoLidas.map((item) => (
              <article key={item.notification_id} className="cc-guideline-alert">
                <div className="cc-guideline-alert__copy">
                  <small>{item.guideline.org} · {dataBr(item.guideline.published_at)}</small>
                  <strong>{item.guideline.title}</strong>
                  <p>{item.message}</p>
                </div>
                <div className="cc-guideline-alert__actions">
                  {item.guideline.url && <a className="botao" href={item.guideline.url} target="_blank" rel="noopener noreferrer">Abrir oficial ↗</a>}
                  <button className="botao botao--secundario" type="button" onClick={() => void marcarLida(item.notification_id)}>Marcar como lido</button>
                </div>
              </article>
            ))}
          </div>
        </ClinicalSection>
      )}

      <ClinicalSection eyebrow="Monitoramento" title="Publicações identificadas" description="Itens não revisados permanecem explicitamente rotulados; detecção não equivale a mudança clínica.">
        {atualizacoes.items.length === 0 ? (
          <ClinicalEmpty title="Nenhuma nova diretriz oficial identificada" description="A rotina de monitoramento continua consultando as fontes oficiais." />
        ) : (
          <div className="cc-guideline-list">
            {atualizacoes.items.map((item) => (
              <article key={item.id} className="cc-guideline-row">
                <div>
                  <small>{item.org} · {dataBr(item.published_at)}</small>
                  <strong>{item.title}</strong>
                  <span>{item.status === "revisada" ? "Revisão clínica concluída." : "Publicação detectada; análise clínica aguardando revisão humana."}</span>
                </div>
                <div className="cc-guideline-row__side">
                  <span className={`selo ${item.status === "revisada" ? "selo--revisado" : "selo--pendente"}`}>{statusLabel(item.status)}</span>
                  {item.url && <a href={item.url} target="_blank" rel="noopener noreferrer">Documento oficial ↗</a>}
                </div>
              </article>
            ))}
          </div>
        )}
      </ClinicalSection>

      <ClinicalSection
        eyebrow="Biblioteca clínica"
        title="Guidelines revisadas e conectadas"
        description="Sínteses publicadas na CorVIA, organizadas por área e ligadas aos documentos e fluxogramas do mesmo assunto."
      >
        {diretrizes.length === 0 ? (
          <ClinicalEmpty title="Nenhuma guideline revisada publicada" description="As sínteses aparecem aqui depois da revisão clínica e da publicação." />
        ) : (
          <div className="cc-context-grid">
            {diretrizes.map((item) => (
              <ClinicalContextLink
                key={item.slug}
                to={`/biblioteca/${item.slug}`}
                icon="diretriz"
                title={item.title}
                detail={item.theme}
              />
            ))}
          </div>
        )}
      </ClinicalSection>

      <ClinicalSection eyebrow="Conhecimento conectado" title="Da diretriz à decisão">
        <div className="cc-context-grid">
          <ClinicalContextLink to="/evidencias" icon="evidencia" title="Evidências" detail="Recomendações estruturadas" />
          <ClinicalContextLink to="/estudos" icon="evidencia" title="Estudos" detail="Literatura que sustenta a recomendação" />
          <ClinicalContextLink to="/assistente" icon="assistente" title="Assistente Clínica" detail="Discutir impacto na prática" />
        </div>
      </ClinicalSection>
    </div>
  );
}
