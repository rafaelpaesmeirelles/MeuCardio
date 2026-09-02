import { useEffect, useMemo, useState } from "react";
import { Link, useLocation, useSearchParams } from "react-router-dom";
import { api } from "../lib/api";
import { Carregando, SeloRevisao, Vazio } from "../components/Estado";
import { normalizarBusca } from "../lib/taxonomiaCardiologia";

type Doc = {
  slug: string; title: string; kind: string; theme: string;
  summary: string | null; review_status: string;
};

type CatalogFront = {
  key: string;
  label: string;
  route: string;
  count: number;
  inventory_count?: number;
};

type Catalog = {
  total: number;
  inventory_total?: number;
  published_total?: number;
  unpublished?: number;
  fronts: CatalogFront[];
  expected_minimum?: number;
  physical_files_expected?: number;
  integrity_ok?: boolean;
  missing?: number;
};

type AreaCount = {
  id: string;
  label: string;
  count: number;
  collections: number;
};

type AreaCountsResponse = { areas: AreaCount[] };

const AREA_ROUTES: Record<string, string> = {
  geral: "/doencas?tab=catalogo&area=geral",
  pediatrica: "/doencas?tab=catalogo&area=cardiopediatria",
  neonatal: "/doencas?tab=catalogo&area=cardiopediatria&q=neonatal",
  congenita: "/doencas?tab=congenitas",
  geriatria: "/doencas?tab=catalogo&area=cardiogeriatria",
  gestacao: "/doencas?tab=catalogo&area=gravidez",
  cardiooncologia: "/doencas?tab=catalogo&area=cardiooncologia",
  fetal: "/doencas?tab=fetal",
};

type DocumentPage = {
  total: number;
  next_offset: number | null;
  has_more: boolean;
  items: Doc[];
};

const PAGE_SIZE = 100;

export default function Biblioteca() {
  const location = useLocation();
  const [params, setParams] = useSearchParams();
  const tema = params.get("tema") ?? "";
  const [catalogo, setCatalogo] = useState<Catalog | null>(null);
  const [contagensAreas, setContagensAreas] = useState<AreaCount[]>([]);
  const [buscaArea, setBuscaArea] = useState("");
  const [temas, setTemas] = useState<{ theme: string; count: number }[]>([]);
  const [docs, setDocs] = useState<Doc[] | null>(null);
  const [totalDocs, setTotalDocs] = useState(0);
  const [proximoOffset, setProximoOffset] = useState<number | null>(null);
  const [carregandoMais, setCarregandoMais] = useState(false);
  const areasFiltradas = useMemo(() => {
    const termo = normalizarBusca(buscaArea);
    if (!termo) return contagensAreas;
    return contagensAreas.filter((area) => normalizarBusca(`${area.label} ${area.id}`).includes(termo));
  }, [buscaArea, contagensAreas]);

  useEffect(() => {
    Promise.all([
      api.get<Catalog>("/library/catalog"),
      api.get<{ theme: string; count: number }[]>("/library/themes"),
      api.get<AreaCountsResponse>("/library/area-counts"),
    ]).then(([catalogoResposta, temasResposta, areasResposta]) => {
      setCatalogo(catalogoResposta);
      setTemas(temasResposta);
      setContagensAreas(areasResposta.areas);
    });
  }, []);

  useEffect(() => {
    setDocs(null);
    const query = new URLSearchParams({ limit: String(PAGE_SIZE), offset: "0" });
    if (tema) query.set("theme", tema);
    api.get<DocumentPage>(`/library/documents?${query}`).then((r) => {
      setDocs(r.items);
      setTotalDocs(r.total);
      setProximoOffset(r.next_offset);
    });
  }, [tema]);

  useEffect(() => {
    if (location.hash !== "#documentos" || docs === null) return;
    requestAnimationFrame(() => {
      const alvo = document.getElementById("documentos");
      alvo?.scrollIntoView({ behavior: "smooth", block: "start" });
      alvo?.focus({ preventScroll: true });
    });
  }, [location.hash, docs]);

  async function carregarMais() {
    if (proximoOffset === null || carregandoMais) return;
    setCarregandoMais(true);
    try {
      const query = new URLSearchParams({
        limit: String(PAGE_SIZE),
        offset: String(proximoOffset),
      });
      if (tema) query.set("theme", tema);
      const r = await api.get<DocumentPage>(`/library/documents?${query}`);
      setDocs((atuais) => [...(atuais ?? []), ...r.items]);
      setTotalDocs(r.total);
      setProximoOffset(r.next_offset);
    } finally {
      setCarregandoMais(false);
    }
  }

  return (
    <>
      <p className="eyebrow">Biblioteca científica</p>
      <h1>Acervo científico</h1>
      {catalogo && (
        <p style={{ color: "var(--texto-secundario)", marginTop: "-0.35rem" }}>
          {catalogo.total.toLocaleString("pt-BR")} registros preservados nas {catalogo.fronts.length} coleções;
          {" "}{(catalogo.published_total ?? catalogo.total).toLocaleString("pt-BR")} publicados.
        </p>
      )}

      <section className="cartao" style={{ margin: "1rem 0 1.25rem" }} aria-labelledby="analise-cientifica-ia-titulo">
        <p className="eyebrow">IA científica · biblioteca privada</p>
        <h2 id="analise-cientifica-ia-titulo">Analisar um documento científico</h2>
        <p style={{ color: "var(--texto-secundario)", maxWidth: "78ch" }}>
          Envie diretriz, consenso, artigo, estudo ou outra evidência. A IA identifica o documento,
          resume em português e traduz para sua biblioteca privada quando necessário. Se houver ganho
          real para o repertório do CorVIA, a incorporação ao acervo compartilhado só ocorre após sua
          autorização explícita e preserva a fonte original.
        </p>
        <Link className="botao" to="/documentos-cientificos-ia">Analisar documento com IA</Link>
      </section>

      {contagensAreas.length > 0 && (
        <section className="cartao" style={{ margin: "1rem 0 1.25rem" }} aria-labelledby="acervo-especializado-titulo">
          <p className="eyebrow">Acervo especializado consolidado</p>
          <h2 id="acervo-especializado-titulo">Conteúdos por área clínica</h2>
          <p style={{ color: "var(--texto-secundario)", maxWidth: "78ch" }}>
            Os totais incluem documentos, evidências, estudos, casos, trilhas, imagens, exames,
            materiais e guias especializados publicados. Um conteúdo pode aparecer em mais de uma
            área relacionada, mas nunca é duplicado dentro da mesma coleção e área.
          </p>
          <label style={{ display: "block", margin: "0.9rem 0 1rem", maxWidth: "40rem" }}>
            <strong>Buscar área da Cardiologia</strong>
            <input
              type="search"
              value={buscaArea}
              onChange={(event) => setBuscaArea(event.target.value)}
              placeholder="Ex.: Cardiologia Geral, Pediátrica ou Cardio-Oncologia"
              style={{ marginTop: "0.35rem" }}
            />
          </label>
          <div className="hoje__temas" aria-label="Totais consolidados por área clínica">
            {areasFiltradas.map((area) => (
              <Link key={area.id} to={AREA_ROUTES[area.id] || "/doencas"}>
                <span>{area.label}</span>
                <small>{area.count.toLocaleString("pt-BR")} · {area.collections} coleções</small>
              </Link>
            ))}
          </div>
          {areasFiltradas.length === 0 && <Vazio titulo="Nenhuma área encontrada" acao="Revise o termo da busca." />}
        </section>
      )}

      {catalogo?.integrity_ok === false && (
        <section
          className="cartao"
          role="alert"
          style={{ borderColor: "var(--acao)", marginBottom: "1rem" }}
        >
          <strong>Acervo abaixo do inventário certificado</strong>
          <p style={{ marginBottom: 0 }}>
            Esta instalação contém {catalogo.total.toLocaleString("pt-BR")} registros. O mínimo certificado é
            {" "}{(catalogo.expected_minimum ?? 4_936).toLocaleString("pt-BR")}; faltam
            {" "}{(catalogo.missing ?? 0).toLocaleString("pt-BR")} registros. O inventário preserva também
            {" "}{(catalogo.physical_files_expected ?? 1_327).toLocaleString("pt-BR")} arquivos físicos.
          </p>
        </section>
      )}

      {catalogo === null ? (
        <Carregando texto="Contando o acervo…" />
      ) : (
        <div className="grade grade--3" style={{ margin: "1rem 0 1.5rem" }}>
          {catalogo.fronts.map((frente) => {
            const destino = frente.key === "documentos"
              ? "/biblioteca?colecao=documentos#documentos"
              : frente.route;
            return (
              <Link key={frente.key} to={destino} className="cartao" style={{ color: "inherit" }}>
                <p className="eyebrow">Coleção</p>
                <h3>{frente.label}</h3>
                <p style={{ color: "var(--texto-secundario)", marginBottom: 0 }}>
                  {frente.count.toLocaleString("pt-BR")} publicados
                  {frente.inventory_count !== undefined && frente.inventory_count !== frente.count
                    ? ` de ${frente.inventory_count.toLocaleString("pt-BR")} preservados`
                    : ""}
                </p>
              </Link>
            );
          })}
        </div>
      )}

      <section id="documentos" tabIndex={-1} style={{ scrollMarginTop: "1rem", outline: "none" }}>
        <p className="eyebrow">Documentos científicos</p>
        <h2>{tema || "Todos os temas"}</h2>

        <div style={{ display: "flex", gap: 6, flexWrap: "wrap", margin: "0.8rem 0 1.2rem" }}>
          <button
            className={`botao ${tema ? "botao--secundario" : ""}`}
            style={{ padding: "0.35rem 0.75rem", fontSize: "0.82rem" }}
            onClick={() => setParams({ colecao: "documentos" })}
          >
            Tudo
          </button>
          {temas.map((t) => (
            <button
              key={t.theme}
              className={`botao ${tema === t.theme ? "" : "botao--secundario"}`}
              style={{ padding: "0.35rem 0.75rem", fontSize: "0.82rem" }}
              onClick={() => setParams({ colecao: "documentos", tema: t.theme })}
            >
              {t.theme} ({t.count.toLocaleString("pt-BR")})
            </button>
          ))}
        </div>

        {docs === null ? (
          <Carregando />
        ) : docs.length === 0 ? (
          <Vazio titulo="Nenhum documento neste tema" acao="Importe conteúdo pelo painel de administração." />
        ) : (
          <>
            <p style={{ color: "var(--texto-secundario)", fontSize: "0.9rem" }}>
              Exibindo {docs.length.toLocaleString("pt-BR")} de {totalDocs.toLocaleString("pt-BR")} documentos publicados.
            </p>
            <div className="grade grade--2">
              {docs.map((d) => (
                <Link key={d.slug} to={`/biblioteca/${d.slug}`} className="cartao" style={{ color: "inherit" }}>
                  <p className="eyebrow">{d.kind}</p>
                  <h3>{d.title}</h3>
                  {d.summary && (
                    <p style={{ color: "var(--texto-secundario)", fontSize: "0.88rem" }}>{d.summary}</p>
                  )}
                  <SeloRevisao status={d.review_status} />
                </Link>
              ))}
            </div>
            {proximoOffset !== null && (
              <div style={{ display: "flex", justifyContent: "center", marginTop: "1.25rem" }}>
                <button className="botao botao--secundario" onClick={carregarMais} disabled={carregandoMais}>
                  {carregandoMais ? "Carregando…" : "Carregar mais documentos"}
                </button>
              </div>
            )}
          </>
        )}
      </section>
    </>
  );
}
