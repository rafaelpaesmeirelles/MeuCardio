import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  ClinicalContextLink,
  ClinicalEmpty,
  ClinicalMetric,
  ClinicalPageHeader,
  ClinicalSection,
} from "../components/ClinicalCommandPrimitives";
import { Carregando, Erro, SeloRevisao } from "../components/Estado";
import TudoSobreEsteTema from "../components/TudoSobreEsteTema";
import { api } from "../lib/api";

const TEMA = "Terapia intensiva";
const CALCULADORAS_DIRETAS = new Set([
  "infusao-continua-peso",
  "vasoativos-choque-cardiogenico-acc-2025",
  "ventilacao-protetora-uco",
  "conferencia-bomba-infusao-uco",
  "estadiamento-scai-choque-cardiogenico",
  "acidose-metabolica-winter-anion-gap-uco",
  "oxigenacao-pao2-fio2-sdra-uco",
  "lesao-renal-aguda-kdigo-uco",
]);

type Documento = {
  slug: string;
  title: string;
  kind: string;
  theme: string;
  summary: string | null;
  review_status: string;
};

type PaginaDocumentos = { total: number; items: Documento[] };
type Calculadora = { slug: string; name: string; theme: string; purpose: string; status: string };
type Checklist = { slug: string; condicao: string; resumo: string; theme: string | null; review_status: string };
type Grupo = "Choque e suporte circulatório" | "Ventilação e via aérea" | "Ritmo e pós-parada" | "Sedação e segurança" | "Outros cuidados intensivos";

const ORDEM_GRUPOS: Grupo[] = [
  "Choque e suporte circulatório",
  "Ventilação e via aérea",
  "Ritmo e pós-parada",
  "Sedação e segurança",
  "Outros cuidados intensivos",
];

const REGRAS_GRUPO: Array<[Grupo, RegExp]> = [
  ["Choque e suporte circulatório", /choque|hemodin|vasoativ|inotr[oó]p|ecmo|impella|bal[aã]o|iabp|baixo d[eé]bito|ventr[ií]culo direito|tamponamento|pocus/i],
  ["Ventilação e via aérea", /ventila|peep|sdra|ards|via a[eé]rea|intuba|oxig[eê]n|respirat|pulmonar|pneumot[oó]rax/i],
  ["Ritmo e pós-parada", /parada|p[oó]s-?rcp|ressuscita|arritm|fibrila|taquicard|bradicard|ritmo/i],
  ["Sedação e segurança", /seda[cç][aã]o|analges|delirium|rass|cam-?icu|abcdef|eletr[oó]lit|nutri[cç]|mobiliza|infec[cç]|seguran[cç]a/i],
];

function grupoDoDocumento(documento: Documento): Grupo {
  const texto = `${documento.title} ${documento.summary ?? ""}`;
  return REGRAS_GRUPO.find(([, padrao]) => padrao.test(texto))?.[0] ?? "Outros cuidados intensivos";
}

function DocumentoCard({ documento }: { documento: Documento }) {
  return (
    <Link to={`/biblioteca/${documento.slug}`} className="cc-tool-card">
      <span className="cc-tool-card__icon" aria-hidden="true">{documento.kind.slice(0, 1).toUpperCase()}</span>
      <span className="cc-tool-card__copy">
        <small>{documento.kind.replaceAll("_", " ")}</small>
        <strong>{documento.title}</strong>
        <p>{documento.summary || "Conteúdo clínico estruturado da Unidade Coronariana."}</p>
      </span>
      <span className="cc-tool-card__open"><SeloRevisao status={documento.review_status} /></span>
    </Link>
  );
}

export default function CardiologiaIntensiva() {
  const [documentos, setDocumentos] = useState<Documento[] | null>(null);
  const [calculadoras, setCalculadoras] = useState<Calculadora[]>([]);
  const [checklists, setChecklists] = useState<Checklist[]>([]);
  const [erro, setErro] = useState("");
  const [busca, setBusca] = useState("");

  useEffect(() => {
    let ativo = true;
    setErro("");
    Promise.all([
      api.get<PaginaDocumentos>(`/library/documents?theme=${encodeURIComponent(TEMA)}&limit=200`),
      api.get<Calculadora[]>("/calculators"),
      api.get<Checklist[]>("/checklists"),
    ])
      .then(([pagina, catalogoCalculadoras, catalogoChecklists]) => {
        if (!ativo) return;
        setDocumentos(pagina.items);
        setCalculadoras(catalogoCalculadoras.filter((item) => CALCULADORAS_DIRETAS.has(item.slug)));
        setChecklists(catalogoChecklists.filter((item) => item.theme === TEMA));
      })
      .catch((causa) => {
        if (ativo) setErro(causa instanceof Error ? causa.message : "Não foi possível abrir a central intensiva.");
      });
    return () => { ativo = false; };
  }, []);

  const documentosFiltrados = useMemo(() => {
    const termo = busca.trim().toLocaleLowerCase("pt-BR");
    if (!termo) return documentos ?? [];
    return (documentos ?? []).filter((documento) =>
      `${documento.title} ${documento.summary ?? ""}`.toLocaleLowerCase("pt-BR").includes(termo)
    );
  }, [busca, documentos]);

  const grupos = useMemo(() => {
    const mapa = new Map<Grupo, Documento[]>(ORDEM_GRUPOS.map((grupo) => [grupo, []]));
    for (const documento of documentosFiltrados) mapa.get(grupoDoDocumento(documento))?.push(documento);
    return ORDEM_GRUPOS.map((nome) => ({ nome, itens: mapa.get(nome) ?? [] })).filter((grupo) => grupo.itens.length > 0);
  }, [documentosFiltrados]);

  if (documentos === null && !erro) return <Carregando texto="Montando a central de Cardiologia Intensiva…" />;

  return (
    <>
      <ClinicalPageHeader
        eyebrow="Cockpit assistencial"
        title="Cardiologia Intensiva & Unidade Coronariana"
        icon="emergencia"
        description="Acesso operacional a suporte hemodinâmico, ventilação, pós-parada, segurança e conhecimento publicado — com cálculo rastreável e decisão final preservada pelo médico."
        actions={[
          { to: "/calculadoras/ventilacao-protetora-uco", label: "Ventilação protetora", icon: "calculadora", tone: "primary" },
          { to: "/emergencia", label: "Emergências", icon: "emergencia", tone: "danger" },
        ]}
      />

      {erro && <Erro mensagem={erro} />}

      <div className="cc-metrics" aria-label="Cobertura da central intensiva">
        <ClinicalMetric label="Conteúdos publicados" value={(documentos ?? []).length} detail="Tema canônico Terapia intensiva" icon="conhecimento" />
        <ClinicalMetric label="Calculadoras operacionais" value={calculadoras.length} detail="Ventilação, infusão e choque" icon="calculadora" />
        <ClinicalMetric label="Checklists conectados" value={checklists.length} detail="Modelos publicados no mesmo tema" icon="check" />
      </div>

      <ClinicalSection
        eyebrow="Estações rápidas"
        title="Decisão e conferência à beira leito"
        description="Atalhos diretos; nenhuma estação substitui protocolo local, conferência da bomba ou avaliação clínica."
      >
        <div className="cc-context-grid">
          <ClinicalContextLink to="/calculadoras/estadiamento-scai-choque-cardiogenico" icon="emergencia" title="Estadiamento SCAI" detail="A–E, modificador de parada e reavaliação seriada" />
          <ClinicalContextLink to="/calculadoras/conferencia-bomba-infusao-uco" icon="check" title="Dupla conferência da bomba" detail="Dose prescrita × concentração × velocidade programada" />
          <ClinicalContextLink to="/calculadoras/ventilacao-protetora-uco" icon="calculadora" title="Ventilação protetora" detail="PBW, VT 4–8 mL/kg, platô e pressão de distensão" />
          <ClinicalContextLink to="/calculadoras/oxigenacao-pao2-fio2-sdra-uco" icon="calculadora" title="Oxigenação e SDRA" detail="PaO₂/FiO₂, suporte e gate de edema cardiogênico" />
          <ClinicalContextLink to="/calculadoras/acidose-metabolica-winter-anion-gap-uco" icon="calculadora" title="Acidose metabólica" detail="Winter, ânion gap e correção opcional por albumina" />
          <ClinicalContextLink to="/calculadoras/lesao-renal-aguda-kdigo-uco" icon="calculadora" title="Lesão renal aguda" detail="KDIGO por creatinina, diurese e componente mais grave" />
          <ClinicalContextLink to="/calculadoras/vasoativos-choque-cardiogenico-acc-2025" icon="calculadora" title="Vasoativos no choque" detail="Dose-alvo, concentração e conversão para mL/h" />
          <ClinicalContextLink to="/calculadoras/infusao-continua-peso" icon="medicamento" title="Central de infusões" detail="Vasopressores, inotrópicos, vasodilatadores e sedação" />
          <ClinicalContextLink to="/emergencia" icon="emergencia" title="Emergência cardiovascular" detail="Protocolos de risco imediato e fluxos críticos" />
        </div>
      </ClinicalSection>

      <ClinicalSection
        eyebrow="Conhecimento operacional"
        title="Mapa da Unidade Coronariana"
        description="Os documentos vêm do corpus publicado e são agrupados para navegação; o conteúdo clínico não é duplicado nesta página."
        action={<Link to={`/biblioteca?tema=${encodeURIComponent(TEMA)}`}>Abrir tema completo</Link>}
      >
        <label htmlFor="busca-uco">Filtrar conteúdo intensivo</label>
        <input
          id="busca-uco"
          type="search"
          value={busca}
          onChange={(evento) => setBusca(evento.target.value)}
          placeholder="Ex.: choque, ECMO, ventilação, delirium, pós-parada"
        />

        {grupos.length === 0 ? (
          <ClinicalEmpty title="Nenhum conteúdo corresponde ao filtro" description="Tente outro termo clínico." />
        ) : (
          <div className="cc-tool-sections" style={{ marginTop: "0.8rem" }}>
            {grupos.map((grupo, indice) => (
              <section className="cc-tool-group" key={grupo.nome} aria-labelledby={`grupo-uco-${indice}`}>
                <div className="cc-tool-group__heading">
                  <h3 id={`grupo-uco-${indice}`}>{grupo.nome}</h3>
                  <span>{grupo.itens.length}</span>
                </div>
                <div className="cc-tool-grid">
                  {grupo.itens.map((documento) => <DocumentoCard key={documento.slug} documento={documento} />)}
                </div>
              </section>
            ))}
          </div>
        )}
      </ClinicalSection>

      <div className="aviso">
        <strong>Gate de segurança do módulo inicial:</strong> ainda não há prescrição automática de antibióticos,
        seleção automática de modo ventilatório ou biblioteca de diluições fixas. Concentração, compatibilidade,
        acesso, função orgânica e protocolo institucional permanecem verificações obrigatórias do profissional.
      </div>

      <TudoSobreEsteTema tema={TEMA} titulo="Tudo com Tudo — Terapia intensiva" />
    </>
  );
}
