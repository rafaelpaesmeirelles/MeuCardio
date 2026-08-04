import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../lib/api";
import { Carregando, SeloRevisao, Vazio } from "../components/Estado";

type Doc = {
  slug: string; title: string; kind: string; theme: string;
  summary: string | null; review_status: string;
};

type CatalogFront = {
  key: string;
  label: string;
  route: string;
  count: number;
};

type Catalog = {
  total: number;
  fronts: CatalogFront[];
  expected_minimum?: number;
  physical_files_expected?: number;
  integrity_ok?: boolean;
  missing?: number;
};

type DocumentPage = {
  total: number;
  next_offset: number | null;
  has_more: boolean;
  items: Doc[];
};

const PAGE_SIZE = 100;

export default function Biblioteca() {
  const [params, setParams] = useSearchParams();
  const tema = params.get("tema") ?? "";
  const [catalogo, setCatalogo] = useState<Catalog | null>(null);
  const [temas, setTemas] = useState<{ theme: string; count: number }[]>([]);
  const [docs, setDocs] = useState<Doc[] | null>(null);
  const [totalDocs, setTotalDocs] = useState(0);
  const [proximoOffset, setProximoOffset] = useState<number | null>(null);
  const [carregandoMais, setCarregandoMais] = useState(false);

  useEffect(() => {
    Promise.all([
      api.get<Catalog>("/library/catalog"),
      api.get<{ theme: string; count: number }[]>("/library/themes"),
    ]).then(([catalogoResposta, temasResposta]) => {
      setCatalogo(catalogoResposta);
      setTemas(temasResposta);
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
          {catalogo.total.toLocaleString("pt-BR")} itens publicados em {catalogo.fronts.length} coleções.
        </p>
      )}

      {catalogo?.integrity_ok === false && (
        <section
          className="cartao"
          role="alert"
          style={{ borderColor: "var(--acao)", marginBottom: "1rem" }}
        >
          <strong>Acervo abaixo do inventário certificado</strong>
          <p style={{ marginBottom: 0 }}>
            Esta instalação contém {catalogo.total.toLocaleString("pt-BR")} itens. O mínimo certificado é
            {(catalogo.expected_minimum ?? 4_936).toLocaleString("pt-BR")}; faltam
            {(catalogo.missing ?? 0).toLocaleString("pt-BR")} registros. O inventário preserva também
            {(catalogo.physical_files_expected ?? 1_327).toLocaleString("pt-BR")} arquivos físicos.
          </p>
        </section>
      )}

      {catalogo === null ? (
        <Carregando texto="Contando o acervo…" />
      ) : (
        <div className="grade grade--3" style={{ margin: "1rem 0 1.5rem" }}>
          {catalogo.fronts.map((frente) => (
            <Link key={frente.key} to={frente.route} className="cartao" style={{ color: "inherit" }}>
              <p className="eyebrow">Coleção</p>
              <h3>{frente.label}</h3>
              <p style={{ color: "var(--texto-secundario)", marginBottom: 0 }}>
                {frente.count.toLocaleString("pt-BR")} itens publicados
              </p>
            </Link>
          ))}
        </div>
      )}

      <p className="eyebrow">Documentos científicos</p>
      <h2>{tema || "Todos os temas"}</h2>

      <div style={{ display: "flex", gap: 6, flexWrap: "wrap", margin: "0.8rem 0 1.2rem" }}>
        <button
          className={`botao ${tema ? "botao--secundario" : ""}`}
          style={{ padding: "0.35rem 0.75rem", fontSize: "0.82rem" }}
          onClick={() => setParams({})}
        >
          Tudo
        </button>
        {temas.map((t) => (
          <button
            key={t.theme}
            className={`botao ${tema === t.theme ? "" : "botao--secundario"}`}
            style={{ padding: "0.35rem 0.75rem", fontSize: "0.82rem" }}
            onClick={() => setParams({ tema: t.theme })}
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
            Exibindo {docs.length.toLocaleString("pt-BR")} de {totalDocs.toLocaleString("pt-BR")} documentos.
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
    </>
  );
}
