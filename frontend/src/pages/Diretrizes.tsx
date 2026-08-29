import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import { Carregando, Erro } from "../components/Estado";
import {
  ClinicalContextLink,
  ClinicalEmpty,
  ClinicalMetric,
  ClinicalPageHeader,
  ClinicalSection,
} from "../components/ClinicalCommandPrimitives";

type StatusAtualizacao = "detected" | "aguardando_revisao" | "revisada" | "analisada" | "revisao_necessaria" | "aplicada_auto";
type Mudanca = {
  category: string;
  change_pt: string;
  previous_pt: string | null;
  practical_impact_pt: string;
  explicit_in_source: boolean;
  source_url: string;
};
type Impacto = {
  item_type: string;
  item_id: number;
  target_label: string | null;
  target_section: string | null;
  change_summary_pt: string | null;
  source_url: string | null;
  applied_at: string | null;
  mode: string | null;
};
type Atualizacao = {
  id: number;
  slug: string;
  org: string;
  title: string;
  title_original: string;
  title_pt: string | null;
  summary_pt: string | null;
  theme: string | null;
  published_at: string;
  discovered_at: string;
  url: string | null;
  doi: string | null;
  status: StatusAtualizacao;
  key_changes: Mudanca[];
  limitations: string[];
  impacts: Impacto[];
  summary_document_slug: string | null;
  clinical_content_changed: boolean;
  translation_mode: string | null;
  analyzed_at: string | null;
};

type Notificacao = {
  notification_id: number;
  read_at: string | null;
  message: string;
  guideline: Atualizacao;
};

type RespostaAtualizacoes = { cutoff: string; items: Atualizacao[] };
type RespostaNotificacoes = { cutoff: string; items: Notificacao[] };
type DiretrizBiblioteca = { slug: string; title: string; theme: string };

function dataBr(valor: string) {
  return new Date(valor).toLocaleDateString("pt-BR", { timeZone: "UTC" });
}

function statusLabel(status: StatusAtualizacao) {
  if (status === "aplicada_auto") return "CorVIA atualizado";
  if (status === "analisada") return "Analisada";
  if (status === "revisao_necessaria") return "Revisão necessária";
  if (status === "revisada") return "Revisada";
  if (status === "aguardando_revisao") return "Aguardando revisão";
  return "Detectada";
}

function statusClass(status: StatusAtualizacao) {
  return ["aplicada_auto", "analisada", "revisada"].includes(status) ? "selo--revisado" : "selo--pendente";
}

function titulo(item: Atualizacao) {
  return item.title_pt?.trim() || item.title;
}

function categoria(valor: string) {
  const mapa: Record<string, string> = {
    definicao: "Definição", diagnostico: "Diagnóstico", tratamento: "Tratamento",
    fluxograma: "Fluxograma", monitorizacao: "Monitorização", seguranca: "Segurança",
    prevencao: "Prevenção", procedimento: "Procedimento", outro: "Prática clínica",
  };
  return mapa[valor] || valor;
}

function temLeituraPortugues(item: Atualizacao) {
  return Boolean(item.title_pt || item.summary_pt || item.key_changes.length || item.impacts.length || item.limitations.length);
}

function CardAtualizacao({ item }: { item: Atualizacao }) {
  const mudancas = item.key_changes.filter((mudanca) => mudanca.explicit_in_source);
  const leituraDisponivel = temLeituraPortugues(item);

  return (
    <article className="cc-guideline-row">
      <div>
        <small>{item.org} · {dataBr(item.published_at)}{item.theme ? ` · ${item.theme}` : ""}</small>
        <strong>{titulo(item)}</strong>
        {item.title_pt && item.title_pt !== item.title_original && <span>Título original: {item.title_original}</span>}
        {item.summary_pt ? <p>{item.summary_pt}</p> : <span>Análise clínica em processamento.</span>}

        {leituraDisponivel && (
          <div id={`leitura-portugues-${item.slug}`} className="cc-detail-card" style={{ scrollMarginTop: "1rem" }}>
            <p className="eyebrow">Leitura em português</p>
            {item.title_pt && <p><strong>{item.title_pt}</strong></p>}
            {item.summary_pt && <p>{item.summary_pt}</p>}

            {mudancas.length > 0 && (
              <>
                <p><strong>Principais mudanças</strong></p>
                <ul className="cc-clinical-list">
                  {mudancas.map((mudanca, indice) => (
                    <li key={`${item.id}-mudanca-${indice}`}>
                      <strong>{categoria(mudanca.category)}:</strong> {mudanca.change_pt}
                      {mudanca.previous_pt && <><br /><small>Antes: {mudanca.previous_pt}</small></>}
                      <br /><small>Impacto prático: {mudanca.practical_impact_pt}</small>
                    </li>
                  ))}
                </ul>
              </>
            )}

            {item.impacts.length > 0 && (
              <>
                <p><strong>Impacto no CorVIA</strong></p>
                <ul className="cc-clinical-list">
                  {item.impacts.map((impacto) => (
                    <li key={`${impacto.item_type}-${impacto.item_id}`}>
                      <strong>{impacto.target_label || impacto.item_type}</strong>
                      {impacto.target_section ? ` · ${impacto.target_section}` : ""}
                      {impacto.change_summary_pt ? <><br /><span>{impacto.change_summary_pt}</span></> : null}
                    </li>
                  ))}
                </ul>
              </>
            )}

            {item.limitations.length > 0 && (
              <>
                <p><strong>Limitações</strong></p>
                <ul className="cc-clinical-list">
                  {item.limitations.map((limitacao, indice) => <li key={`${item.id}-limitacao-${indice}`}>{limitacao}</li>)}
                </ul>
              </>
            )}

            <p><small>Leitura clínica original em português produzida pelo CorVIA a partir das fontes científicas disponíveis. Não depende do Google Tradutor e não reproduz tradução integral de conteúdo protegido.</small></p>
          </div>
        )}
      </div>
      <div className="cc-guideline-row__side">
        <span className={`selo ${statusClass(item.status)}`}>{statusLabel(item.status)}</span>
        {item.summary_document_slug ? (
          <Link to={`/biblioteca/${item.summary_document_slug}`}>Resumo CorVIA</Link>
        ) : item.summary_pt ? (
          <a href={`#publicacao-${item.slug}`}>Resumo CorVIA</a>
        ) : null}
        {leituraDisponivel && <a href={`#leitura-portugues-${item.slug}`}>Traduzido</a>}
        {item.url && <a href={item.url} target="_blank" rel="noopener noreferrer">Original ↗</a>}
      </div>
    </article>
  );
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

  const naoLidas = useMemo(() => (notificacoes?.items ?? []).filter((item) => !item.read_at), [notificacoes?.items]);
  const analisadas = useMemo(() => (atualizacoes?.items ?? []).filter((item) => Boolean(item.summary_pt)).length, [atualizacoes?.items]);
  const aplicadas = useMemo(() => (atualizacoes?.items ?? []).filter((item) => item.clinical_content_changed).length, [atualizacoes?.items]);
  const organizacoes = useMemo(() => new Set((atualizacoes?.items ?? []).map((item) => item.org).filter(Boolean)).size, [atualizacoes?.items]);

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
        eyebrow="CorVIA Intelligence"
        title="Diretrizes e alertas clínicos"
        description="Novas publicações são detectadas, analisadas e resumidas em português. Em cada trabalho, você pode abrir o Resumo CorVIA, uma leitura clínica em português dentro do próprio CorVIA ou a publicação original. Mudanças clínicas só são aplicadas automaticamente quando a fonte primária sustenta explicitamente a mudança e uma segunda verificação independente confirma o override; situações ambíguas permanecem sinalizadas para revisão."
        icon="documento"
        actions={[
          { to: "/evidencias", label: "Evidências", icon: "evidencia" },
          { to: "/estudos", label: "Estudos", icon: "evidencia", tone: "primary" },
        ]}
        meta={<><span className="selo">fontes oficiais</span><span className="selo">leitura em português</span><span className="selo">Tudo com Tudo</span></>}
      />

      <div className="cc-metrics">
        <ClinicalMetric label="Publicações" value={atualizacoes.items.length} detail={`desde ${dataBr(atualizacoes.cutoff)}`} icon="documento" />
        <ClinicalMetric label="Novas para você" value={naoLidas.length} detail="alertas ainda não lidos" icon="evidencia" />
        <ClinicalMetric label="Analisadas" value={analisadas} detail="com síntese clínica em português" icon="check" />
        <ClinicalMetric label="Atualizaram o CorVIA" value={aplicadas} detail={`${organizacoes} organizações monitoradas`} icon="sincronizar" />
      </div>

      {naoLidas.length > 0 && (
        <ClinicalSection eyebrow="Seu radar clínico" title="Novos para você" description="Abra o resumo, a leitura em português ou o original diretamente daqui, sem depender de proxy de tradução externo.">
          <div className="cc-guideline-alerts">
            {naoLidas.map((item) => (
              <article key={item.notification_id} className="cc-guideline-alert">
                <div className="cc-guideline-alert__copy">
                  <small>{item.guideline.org} · {dataBr(item.guideline.published_at)}</small>
                  <strong>{titulo(item.guideline)}</strong>
                  <p>{item.guideline.summary_pt || item.message}</p>
                  {item.guideline.clinical_content_changed && <p><strong>CorVIA atualizado:</strong> {item.guideline.impacts.length} ponto(s) clínico(s) receberam orientação prevalente nova.</p>}
                </div>
                <div className="cc-guideline-alert__actions">
                  {item.guideline.summary_document_slug ? (
                    <Link className="botao" to={`/biblioteca/${item.guideline.summary_document_slug}`}>Resumo CorVIA</Link>
                  ) : item.guideline.summary_pt ? (
                    <a className="botao" href={`#publicacao-${item.guideline.slug}`}>Resumo CorVIA</a>
                  ) : null}
                  {temLeituraPortugues(item.guideline) && <a className="botao botao--secundario" href={`#leitura-portugues-${item.guideline.slug}`}>Traduzido</a>}
                  {item.guideline.url && <a className="botao botao--secundario" href={item.guideline.url} target="_blank" rel="noopener noreferrer">Original ↗</a>}
                  <button className="botao botao--secundario" type="button" onClick={() => void marcarLida(item.notification_id)}>Marcar como lido</button>
                </div>
              </article>
            ))}
          </div>
        </ClinicalSection>
      )}

      <ClinicalSection eyebrow="Monitoramento" title="Publicações identificadas" description="Cada trabalho oferece Resumo CorVIA, leitura clínica em português dentro do CorVIA e fonte original quando disponíveis.">
        {atualizacoes.items.length === 0 ? (
          <ClinicalEmpty title="Nenhuma nova publicação oficial identificada" description="O CorVIA Intelligence continua consultando sociedades, periódicos e indexadores estruturados." />
        ) : (
          <div className="cc-guideline-list">
            {atualizacoes.items.map((item) => (
              <div id={`publicacao-${item.slug}`} key={item.id} style={{ scrollMarginTop: "1rem" }}>
                <CardAtualizacao item={item} />
              </div>
            ))}
          </div>
        )}
      </ClinicalSection>

      <ClinicalSection eyebrow="Biblioteca clínica" title="Guidelines conectadas">
        <div className="cc-context-grid">
          {diretrizes.map((item) => (
            <ClinicalContextLink key={item.slug} to={`/biblioteca/${item.slug}`} icon="evidencia" title={item.title} detail={item.theme} />
          ))}
        </div>
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
