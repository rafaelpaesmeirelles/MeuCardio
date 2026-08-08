import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Carregando, Erro, Vazio } from "../components/Estado";
import TudoSobreEsteTema from "../components/TudoSobreEsteTema";
import { api } from "../lib/api";

type Tema = { tema: string; total_marcos: number };

type Marco = {
  ano: number;
  tipo: "diretriz" | "estudo";
  slug: string;
  titulo: string;
  descricao: string;
  fonte: string;
  rota: string;
  documento: { slug: string; titulo: string; rota: string } | null;
};

type Timeline = { tema: string; total: number; marcos: Marco[] };

const ROTULO_TIPO: Record<string, string> = { diretriz: "Diretriz/recomendação", estudo: "Estudo" };

// Agrupa marcos do mesmo ano e do mesmo tipo (ex.: várias recomendações da
// mesma diretriz publicadas no mesmo ano) num só cartão, com o primeiro em
// destaque e os demais atrás de "ver mais" — sem isso, um tema com muita
// evidência do mesmo ano vira uma parede de cartões repetidos.
type Grupo = { chave: string; ano: number; tipo: string; principal: Marco; outros: Marco[] };

function agruparPorAnoETipo(marcos: Marco[]): Grupo[] {
  const porChave = new Map<string, Grupo>();
  for (const m of marcos) {
    const chave = `${m.ano}__${m.tipo}`;
    const existente = porChave.get(chave);
    if (existente) existente.outros.push(m);
    else porChave.set(chave, { chave, ano: m.ano, tipo: m.tipo, principal: m, outros: [] });
  }
  return [...porChave.values()];
}

function agruparPorDecada(grupos: Grupo[]): { decada: number; itens: Grupo[] }[] {
  const porDecada = new Map<number, Grupo[]>();
  for (const g of grupos) {
    const decada = Math.floor(g.ano / 10) * 10;
    const lista = porDecada.get(decada);
    if (lista) lista.push(g);
    else porDecada.set(decada, [g]);
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
        </div>
        <Link to={principal.rota} className="timeline-doenca__titulo">{principal.titulo}</Link>
        <p className="timeline-doenca__resumo">{principal.descricao}</p>
        <p className="timeline-doenca__fonte">{principal.fonte}</p>
        {principal.documento && (
          <Link to={principal.documento.rota} className="timeline-doenca__fonte">
            → Ver documento completo na Biblioteca: {principal.documento.titulo}
          </Link>
        )}

        {outros.length > 0 && (
          <div className="timeline-doenca__itens">
            <button type="button" className="timeline-doenca__alternar" onClick={() => setAberto((v) => !v)}>
              {aberto ? "Ocultar" : `Ver mais ${outros.length} marco${outros.length > 1 ? "s" : ""} de ${principal.ano}`}
            </button>
            {aberto && (
              <ul className="timeline-doenca__sublista">
                {outros.map((m) => (
                  <li key={m.slug}>
                    <Link to={m.rota}>{m.titulo}</Link>
                    <span className="timeline-doenca__classe">{m.fonte}</span>
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

  useEffect(() => {
    api.get<Tema[]>("/trilhas/timeline/temas")
      .then((lista) => {
        setTemas(lista);
        // Sem tema escolhido na URL, abre com o primeiro da lista — nunca com
        // a tela vazia à espera de um clique.
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
    api.get<Timeline>(`/trilhas/timeline?tema=${encodeURIComponent(temaAtivo)}`)
      .then(setTimeline)
      .catch((causa) => setErroTimeline(causa instanceof Error ? causa.message : "Não foi possível carregar a timeline deste tema."))
      .finally(() => setCarregandoTimeline(false));
  }, [temaAtivo]);

  const decadas = useMemo(() => {
    if (!timeline) return [];
    return agruparPorDecada(agruparPorAnoETipo(timeline.marcos));
  }, [timeline]);

  return (
    <div>
      <p className="eyebrow">Trilhas de estudo</p>
      <h1>Timeline de evolução do conhecimento</h1>

      <div className="timeline-doenca__entrada">
        <strong>Como o conhecimento e o tratamento de cada doença evoluíram</strong>
        <span>
          Linha do tempo construída a partir das evidências (recomendações de diretriz/sociedade) e dos
          estudos já publicados e revisados na Corvia, por tema — nenhum marco é escrito à parte; cada um
          é o próprio item da biblioteca, na ordem em que a ciência avançou. Clique em qualquer marco
          para abrir a página completa dele, com acesso a tudo mais que a Corvia tem sobre o mesmo tema.
        </span>
      </div>

      {erroTemas ? <Erro mensagem={erroTemas} /> : temas === null ? (
        <Carregando texto="Carregando os temas com timeline disponível…" />
      ) : temas.length === 0 ? (
        <Vazio titulo="Nenhuma timeline disponível ainda" acao="Assim que houver evidência ou estudo publicado com tema e ano, a timeline aparece aqui." />
      ) : (
        <>
          <div className="timeline-doenca__seletor" role="tablist" aria-label="Escolha a doença/tema">
            {temas.map((t) => (
              <button
                key={t.tema}
                type="button"
                role="tab"
                aria-selected={t.tema === temaAtivo}
                className={`timeline-doenca__chip${t.tema === temaAtivo ? " timeline-doenca__chip--ativo" : ""}`}
                onClick={() => setSearchParams({ tema: t.tema })}
              >
                <strong>{t.tema}</strong>
                <span>{t.total_marcos} marco{t.total_marcos === 1 ? "" : "s"}</span>
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
            <div className="timeline-doenca__eixo">
              {decadas.map(({ decada, itens }) => (
                <div className="timeline-doenca__decada" key={decada}>
                  <span className="timeline-doenca__decada-rotulo">{decada}</span>
                  <ul className="timeline-doenca__lista">
                    {itens.map((g) => (
                      <CartaoMarco key={g.chave} grupo={g} />
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}

          <TudoSobreEsteTema tema={temaAtivo} titulo="Tudo mais que a Corvia tem sobre este tema" />
        </>
      )}
    </div>
  );
}
