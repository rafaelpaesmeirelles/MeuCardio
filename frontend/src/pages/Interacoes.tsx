import { useEffect, useMemo, useState } from "react";
import { api } from "../lib/api";
import { Carregando, Erro } from "../components/Estado";
import ClinicalText from "../components/ClinicalText";
import {
  ClinicalContextLink,
  ClinicalEmpty,
  ClinicalMetric,
  ClinicalPageHeader,
  ClinicalSection,
} from "../components/ClinicalCommandPrimitives";

type Item = { slug: string; nome: string };
type Verificada = {
  slug: string;
  gravidade: "contraindicada" | "grave" | "moderada" | "leve";
  efeito: string;
  conduta: string;
  fonte: string;
  classe_oposta: string | null;
  farmacos: Item[];
};
type Mencao = { de: Item; cita: Item[]; texto: string };
type Resultado = {
  selecionados: Item[];
  verificadas: Verificada[];
  avisos_de_classe: Verificada[];
  mencoes: Mencao[];
  aviso: string;
};

const ROTULO: Record<Verificada["gravidade"], string> = {
  contraindicada: "Contraindicada",
  grave: "Grave",
  moderada: "Moderada",
  leve: "Leve",
};

function tone(gravidade: Verificada["gravidade"]) {
  if (gravidade === "contraindicada" || gravidade === "grave") return "is-danger";
  if (gravidade === "moderada") return "is-warning";
  return "is-info";
}

function InteractionCard({ item, classe = false }: { item: Verificada; classe?: boolean }) {
  return (
    <article className={`cc-interaction-card ${tone(item.gravidade)}`}>
      <div className="cc-interaction-card__head">
        <div><small>{classe ? "Aviso de classe" : "Interação verificada"}</small><strong>{item.farmacos.map((f) => f.nome).join(" + ")}{item.classe_oposta && ` + ${item.classe_oposta}`}</strong></div>
        <span>{ROTULO[item.gravidade]}</span>
      </div>
      <div className="cc-interaction-card__body">
        <div><b>Efeito</b><ClinicalText compact>{item.efeito}</ClinicalText></div>
        <div><b>Conduta</b><ClinicalText compact>{item.conduta}</ClinicalText></div>
        <div className="cc-interaction-card__source"><b>Fonte</b><ClinicalText compact>{item.fonte}</ClinicalText></div>
      </div>
    </article>
  );
}

export default function Interacoes() {
  const [lista, setLista] = useState<Item[] | null>(null);
  const [escolhidos, setEscolhidos] = useState<string[]>([]);
  const [busca, setBusca] = useState("");
  const [resultado, setResultado] = useState<Resultado | null>(null);
  const [erro, setErro] = useState("");
  const [checando, setChecando] = useState(false);

  useEffect(() => {
    api.get<{ slug: string; generic_name: string }[]>("/drugs")
      .then((l) => setLista(l.map((d) => ({ slug: d.slug, nome: d.generic_name }))))
      .catch((e) => setErro(e.message));
  }, []);

  const filtrada = useMemo(() => {
    const fonte = lista ?? [];
    const termo = busca.trim().toLocaleLowerCase("pt-BR");
    if (!termo) return fonte.slice(0, 24);
    return fonte.filter((d) => d.nome.toLocaleLowerCase("pt-BR").includes(termo)).slice(0, 40);
  }, [lista, busca]);

  function nomeDe(slug: string) {
    return (lista ?? []).find((d) => d.slug === slug)?.nome ?? slug;
  }

  function alternar(slug: string) {
    setResultado(null);
    setEscolhidos((atual) => atual.includes(slug) ? atual.filter((s) => s !== slug) : [...atual, slug]);
  }

  async function checar() {
    setChecando(true);
    setErro("");
    try {
      setResultado(await api.post<Resultado>("/drugs/interacoes", { slugs: escolhidos }));
    } catch (e: unknown) {
      setErro(e instanceof Error ? e.message : "Não foi possível verificar as interações.");
    } finally {
      setChecando(false);
    }
  }

  if (erro && !lista) return <Erro mensagem={erro} />;
  if (!lista) return <Carregando texto="Abrindo segurança medicamentosa…" />;

  return (
    <div className="cc-page cc-interactions-page">
      <ClinicalPageHeader
        eyebrow="Segurança medicamentosa"
        title="Interações"
        description="Monte a combinação em uso ou planejada. A CorVIA separa interação verificada, aviso de classe e simples menção textual — sem inventar gravidade."
        icon="medicamento"
        actions={[
          { to: "/medicamentos", label: "Medicamentos", icon: "medicamento" },
          { to: "/receituario", label: "Prescrever", icon: "prescricao", tone: "primary" },
        ]}
        meta={<><span className="selo">2–10 fármacos</span><span className="selo">fonte nominal</span></>}
      />

      <ClinicalSection eyebrow="Combinação" title="Quais medicamentos estão no contexto?" description="Pesquise e adicione. No celular, mostramos resultados relevantes em lista compacta em vez de uma nuvem com todo o catálogo.">
        <div className="cc-interaction-builder">
          <div className="cc-interaction-builder__search">
            <label htmlFor="cc-interaction-search">Buscar medicamento</label>
            <input id="cc-interaction-search" value={busca} onChange={(e) => setBusca(e.target.value)} placeholder="Ex.: apixabana, AAS, amiodarona…" autoComplete="off" />
          </div>
          <div className="cc-interaction-builder__count"><strong>{escolhidos.length}/10</strong><small>selecionados</small></div>
          <button className="botao" type="button" disabled={escolhidos.length < 2 || checando} onClick={() => void checar()}>{checando ? "Checando…" : "Verificar combinação"}</button>
        </div>

        {escolhidos.length > 0 && (
          <div className="cc-selected-drugs" aria-label="Medicamentos selecionados">
            {escolhidos.map((slug) => <button key={slug} type="button" onClick={() => alternar(slug)}>{nomeDe(slug)} <span>×</span></button>)}
          </div>
        )}

        <div className="cc-drug-picker">
          {filtrada.map((drug) => {
            const selecionado = escolhidos.includes(drug.slug);
            return (
              <button key={drug.slug} type="button" className={selecionado ? "is-selected" : ""} onClick={() => alternar(drug.slug)} disabled={!selecionado && escolhidos.length >= 10}>
                <span>{drug.nome}</span><i>{selecionado ? "Remover" : "Adicionar"}</i>
              </button>
            );
          })}
        </div>
      </ClinicalSection>

      {erro && <Erro mensagem={erro} />}

      {resultado ? (
        <>
          <div className="cc-metrics">
            <ClinicalMetric label="Verificadas" value={resultado.verificadas.length} detail="gravidade atribuída" icon="check" />
            <ClinicalMetric label="Avisos de classe" value={resultado.avisos_de_classe.length} detail="dependem de outro fármaco/classe" icon="medicamento" />
            <ClinicalMetric label="Menções" value={resultado.mencoes.length} detail="sem gravidade atribuída" icon="documento" />
            <ClinicalMetric label="Fármacos" value={resultado.selecionados.length} detail="combinação analisada" icon="medicamento" />
          </div>

          <ClinicalSection eyebrow="Verificado" title="Interações com gravidade e fonte" description="Este é o bloco em que o sistema afirma uma interação estruturada.">
            {resultado.verificadas.length === 0 ? <ClinicalEmpty title="Nenhuma interação verificada entre os selecionados" description={resultado.aviso} /> : <div className="cc-interaction-results">{resultado.verificadas.map((item) => <InteractionCard key={item.slug} item={item} />)}</div>}
          </ClinicalSection>

          {resultado.avisos_de_classe.length > 0 && (
            <ClinicalSection eyebrow="Contexto adicional" title="Avisos de classe" description="Um dos lados é uma classe inteira, não necessariamente outro fármaco que você selecionou.">
              <div className="cc-interaction-results">{resultado.avisos_de_classe.map((item) => <InteractionCard key={item.slug} item={item} classe />)}</div>
            </ClinicalSection>
          )}

          <ClinicalSection eyebrow="Menções" title="Citadas no texto, sem gravidade atribuída" description="A CorVIA mostra o vínculo textual, mas não converte menção em classificação clínica.">
            {resultado.mencoes.length === 0 ? <ClinicalEmpty title="Nenhuma menção cruzada" /> : <div className="cc-mention-list">{resultado.mencoes.map((m, i) => <article key={`${m.de.slug}-${i}`}><strong>{m.de.nome} → {m.cita.map((c) => c.nome).join(", ")}</strong><ClinicalText compact>{m.texto}</ClinicalText></article>)}</div>}
          </ClinicalSection>

          <div className="cc-inline-note"><ClinicalText compact>{resultado.aviso}</ClinicalText></div>
        </>
      ) : (
        <ClinicalSection eyebrow="Resultado" title="A análise aparece aqui">
          <ClinicalEmpty title="Selecione pelo menos dois medicamentos" description="A verificação só é executada quando você pedir; nada é inferido em segundo plano." />
        </ClinicalSection>
      )}

      <ClinicalSection eyebrow="Próximo passo" title="Continue sem perder o contexto">
        <div className="cc-context-grid">
          <ClinicalContextLink to="/medicamentos" icon="medicamento" title="Verbetes" detail="Revisar dose e contraindicações" />
          <ClinicalContextLink to="/receituario" icon="prescricao" title="Prescrição" detail="Preparar a ação clínica" />
          <ClinicalContextLink to="/assistente" icon="assistente" title="Assistente Clínica" detail="Discutir a combinação" />
        </div>
      </ClinicalSection>
    </div>
  );
}
