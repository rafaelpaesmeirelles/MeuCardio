import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Carregando, Erro, Vazio } from "../components/Estado";
import TudoSobreEsteTema from "../components/TudoSobreEsteTema";
import { api } from "../lib/api";

type Tema = { tema: string; total_marcos: number };
type EixoResumo = { eixo: string; total: number };

type Marco = {
  ano: number;
  tipo: "diretriz" | "estudo";
  eixo: string;
  subtipo: string;
  slug: string;
  titulo: string;
  descricao: string;
  fonte: string;
  referencia: string | null;
  rota: string;
  documento: { slug: string; titulo: string; rota: string } | null;
  tags: string[];
  doi: string | null;
  pmid: string | null;
  source_url: string | null;
};

type Timeline = {
  tema: string;
  total: number;
  primeiro_ano: number | null;
  ultimo_ano: number | null;
  eixos: EixoResumo[];
  marcos: Marco[];
};

const ROTULO_TIPO: Record<string, string> = {
  diretriz: "Diretriz/recomendação",
  estudo: "Estudo/trabalho",
};

function rotuloSubtipo(valor: string) {
  return valor
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letra) => letra.toLocaleUpperCase("pt-BR"));
}

type Grupo = {
  chave: string;
  ano: number;
  tipo: string;
  eixo: string;
  principal: Marco;
  outros: Marco[];
};

function agruparPorAnoEixoETipo(marcos: Marco[]): Grupo[] {
  const porChave = new Map<string, Grupo>();
  for (const marco of marcos) {
    const chave = `${marco.ano}__${marco.eixo}__${marco.tipo}`;
    const existente = porChave.get(chave);
    if (existente) existente.outros.push(marco);
    else porChave.set(chave, {
      chave,
      ano: marco.ano,
      tipo: marco.tipo,
      eixo: marco.eixo,
      principal: marco,
      outros: [],
    });
  }
  return [...porChave.values()];
}

function agruparPorDecada(grupos: Grupo[]): { decada: number; itens: Grupo[] }[] {
  const porDecada = new Map<number, Grupo[]>();
  for (const grupo of grupos) {
    const decada = Math.floor(grupo.ano / 10) * 10;
    const lista = porDecada.get(decada);
    if (lista) lista.push(grupo);
    else porDecada.set(decada, [grupo]);
  }
  return [...porDecada.entries()]
    .sort((a, b) => a[0] - b[0])
    .map(([decada, itens]) => ({ decada, itens }));
}

function CartaoMarco({ grupo }: { grupo: Grupo }) {
  const [aberto, setAberto] = useState(false);
  const { principal, outros } = grupo;

  return (
    <li className={`timeline-doenca__marco${principal.tipo === "diretriz" ? " timeline-doenca__marco--diretriz" : ""}`}>
      <span className="timeline-doenca__marcador" aria-hidden="true" />
      <article className="timeline-doenca__cartao">
        <div className="timeline-doenca__cabecalho">
          <span className="timeline-doenca__ano">{principal.ano}</span>
          <span className={`timeline-doenca__selo${principal.tipo === "diretriz" ? " timeline-doenca__selo--diretriz" : ""}`}>
            {ROTULO_TIPO[principal.tipo] ?? principal.tipo}
          </span>
          <span className="timeline-doenca__selo">{principal.eixo}</span>
        </div>
        <Link to={principal.rota} className="timeline-doenca__titulo">{principal.titulo}</Link>
        <p className="timeline-doenca__resumo">{principal.descricao}</p>
        <p className="timeline-doenca__fonte">
          {principal.fonte} · {rotuloSubtipo(principal.subtipo)}
        </p>
        {principal.referencia && <p className="timeline-doenca__fonte">{principal.referencia}</p>}
        {(principal.doi || principal.pmid) && (
          <p className="timeline-doenca__fonte">
            {principal.doi ? `DOI ${principal.doi}` : ""}
            {principal.doi && principal.pmid ? " · " : ""}
            {principal.pmid ? `PMID ${principal.pmid}` : ""}
          </p>
        )}
        {principal.source_url && (
          <a href={principal.source_url} target="_blank" rel="noopener noreferrer" className="timeline-doenca__fonte">
            → Abrir fonte científica original
          </a>
        )}
        {principal.documento && (
          <Link to={principal.documento.rota} className="timeline-doenca__fonte">
            → Ver documento completo na Biblioteca: {principal.documento.titulo}
          </Link>
        )}

        {outros.length > 0 && (
          <div className="timeline-doenca__itens">
            <button type="button" className="timeline-doenca__alternar" onClick={() => setAberto((valor) => !valor)}>
              {aberto ? "Ocultar" : `Ver mais ${outros.length} marco${outros.length > 1 ? "s" : ""} de ${principal.ano} neste eixo`}
            </button>
            {aberto && (
              <ul className="timeline-doenca__sublista">
                {outros.map((marco) => (
                  <li key={marco.slug}>
                    <Link to={marco.rota}>{marco.titulo}</Link>
                    <span className="timeline-doenca__classe">{marco.fonte} · {rotuloSubtipo(marco.subtipo)}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </article>
    </li>
  );
}

export default function TimelineDoencas() {
  const [temas, setTemas] = useState<Tema[] | null>(null);
  const [erroTemas, setErroTemas] = useState("");
  const [searchParams, setSearchParams] = useSearchParams();
  const temaAtivo = searchParams.get("tema") ?? "";

  const [timeline, setTimeline] = useState<Timeline | null>(null);
  const [carregandoTimeline, setCarregandoTimeline] = useState(false);
  const [erroTimeline, setErroTimeline] = useState("");
  const [eixoAtivo, setEixoAtivo] = useState("");

  useEffect(() => {
    api.get<Tema[]>("/trilhas/timeline/temas")
      .then((lista) => {
        setTemas(lista);
        if (!temaAtivo && lista.length > 0) {
          setSearchParams({ tema: lista[0].tema }, { replace: true });
        }
      })
      .catch((causa) => setErroTemas(causa instanceof Error ? causa.message : "Não foi possível carregar os temas."));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!temaAtivo) return;
    setCarregandoTimeline(true);
    setErroTimeline("");
    setEixoAtivo("");
    api.get<Timeline>(`/trilhas/timeline?tema=${encodeURIComponent(temaAtivo)}`)
      .then(setTimeline)
      .catch((causa) => setErroTimeline(causa instanceof Error ? causa.message : "Não foi possível carregar a timeline deste tema."))
      .finally(() => setCarregandoTimeline(false));
  }, [temaAtivo]);

  const marcosFiltrados = useMemo(() => {
    if (!timeline) return [];
    return eixoAtivo ? timeline.marcos.filter((marco) => marco.eixo === eixoAtivo) : timeline.marcos;
  }, [timeline, eixoAtivo]);

  const decadas = useMemo(
    () => agruparPorDecada(agruparPorAnoEixoETipo(marcosFiltrados)),
    [marcosFiltrados],
  );

  return (
    <div>
      <p className="eyebrow">Trilhas de estudo</p>
      <h1>Timeline de evolução do conhecimento</h1>

      <div className="timeline-doenca__entrada">
        <strong>Como cada tema avançou — da investigação à decisão terapêutica</strong>
        <span>
          A linha do tempo é construída exclusivamente a partir de estudos, trabalhos científicos e
          recomendações já publicados e revisados na CorVIA. Ela organiza a evolução de fundamentos,
          investigação/diagnóstico, estratificação, tratamento, procedimentos, prevenção, segurança e
          diretrizes sem criar marcos narrativos artificiais. Cada ponto abre a evidência real que o sustenta.
        </span>
      </div>

      {erroTemas ? <Erro mensagem={erroTemas} /> : temas === null ? (
        <Carregando texto="Carregando os temas com timeline disponível…" />
      ) : temas.length === 0 ? (
        <Vazio titulo="Nenhuma timeline disponível ainda" acao="Assim que houver evidência ou estudo publicado com tema e ano, a timeline aparece aqui." />
      ) : (
        <>
          <div className="timeline-doenca__seletor" role="tablist" aria-label="Escolha a doença/tema">
            {temas.map((tema) => (
              <button
                key={tema.tema}
                type="button"
                role="tab"
                aria-selected={tema.tema === temaAtivo}
                className={`timeline-doenca__chip${tema.tema === temaAtivo ? " timeline-doenca__chip--ativo" : ""}`}
                onClick={() => setSearchParams({ tema: tema.tema })}
              >
                <strong>{tema.tema}</strong>
                <span>{tema.total_marcos} marco{tema.total_marcos === 1 ? "" : "s"}</span>
              </button>
            ))}
          </div>

          {erroTimeline ? <Erro mensagem={erroTimeline} /> : carregandoTimeline || !timeline ? (
            <Carregando texto="Carregando a timeline…" />
          ) : timeline.marcos.length === 0 ? (
            <Vazio
              titulo={`Nenhum marco publicado ainda em ${timeline.tema}`}
              acao="Assim que uma evidência ou estudo desse tema for publicado com ano, ele aparece aqui automaticamente."
            />
          ) : (
            <>
              <div className="timeline-doenca__entrada">
                <strong>{timeline.tema}</strong>
                <span>
                  {timeline.total} marco{timeline.total === 1 ? "" : "s"}
                  {timeline.primeiro_ano && timeline.ultimo_ano ? ` · ${timeline.primeiro_ano}–${timeline.ultimo_ano}` : ""}.
                  Use os eixos abaixo para acompanhar separadamente investigação, tratamento e as demais frentes do conhecimento.
                </span>
              </div>

              <div className="timeline-doenca__seletor" role="tablist" aria-label="Filtrar eixo da evolução científica">
                <button
                  type="button"
                  role="tab"
                  aria-selected={!eixoAtivo}
                  className={`timeline-doenca__chip${!eixoAtivo ? " timeline-doenca__chip--ativo" : ""}`}
                  onClick={() => setEixoAtivo("")}
                >
                  <strong>Todos os eixos</strong>
                  <span>{timeline.total} marcos</span>
                </button>
                {timeline.eixos.map((eixo) => (
                  <button
                    key={eixo.eixo}
                    type="button"
                    role="tab"
                    aria-selected={eixoAtivo === eixo.eixo}
                    className={`timeline-doenca__chip${eixoAtivo === eixo.eixo ? " timeline-doenca__chip--ativo" : ""}`}
                    onClick={() => setEixoAtivo(eixo.eixo)}
                  >
                    <strong>{eixo.eixo}</strong>
                    <span>{eixo.total} marco{eixo.total === 1 ? "" : "s"}</span>
                  </button>
                ))}
              </div>

              {marcosFiltrados.length === 0 ? (
                <Vazio titulo="Nenhum marco neste eixo" acao="Selecione outro eixo ou volte a Todos os eixos." />
              ) : (
                <div className="timeline-doenca__eixo">
                  {decadas.map(({ decada, itens }) => (
                    <div className="timeline-doenca__decada" key={decada}>
                      <span className="timeline-doenca__decada-rotulo">{decada}</span>
                      <ul className="timeline-doenca__lista">
                        {itens.map((grupo) => <CartaoMarco key={grupo.chave} grupo={grupo} />)}
                      </ul>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}

          <TudoSobreEsteTema tema={timeline?.tema || temaAtivo} titulo="Tudo mais que a CorVIA tem sobre este tema" />
        </>
      )}
    </div>
  );
}
