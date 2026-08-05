import { useEffect, useMemo, useState } from "react";
import { api, ApiError } from "../lib/api";
import { Carregando, Erro, Vazio } from "../components/Estado";

type Documento = {
  slug: string;
  title: string;
  theme: string;
  kind: string;
  summary: string | null;
  review_status: string;
};

type PaginaDocumentos = {
  total: number;
  limit: number;
  offset: number;
  next_offset: number | null;
  has_more: boolean;
  items: Documento[];
};

function baixar(blob: Blob, nome: string) {
  const url = URL.createObjectURL(blob);
  const ancora = document.createElement("a");
  ancora.href = url;
  ancora.download = nome;
  ancora.click();
  URL.revokeObjectURL(url);
}

async function carregarTodoCatalogo(): Promise<Documento[]> {
  const todos: Documento[] = [];
  let offset = 0;
  do {
    const pagina = await api.get<PaginaDocumentos>(
      `/library/documents?limit=200&offset=${offset}`,
    );
    todos.push(...pagina.items);
    if (pagina.next_offset === null) break;
    offset = pagina.next_offset;
  } while (true);
  return todos;
}

export default function Apresentacao() {
  const [documentos, setDocumentos] = useState<Documento[] | null>(null);
  const [busca, setBusca] = useState("");
  const [selecionado, setSelecionado] = useState<Documento | null>(null);
  const [anotacao, setAnotacao] = useState("");
  const [gerando, setGerando] = useState(false);
  const [erro, setErro] = useState("");

  useEffect(() => {
    carregarTodoCatalogo()
      .then(setDocumentos)
      .catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível carregar os documentos."));
  }, []);

  const filtrados = useMemo(() => {
    const termo = busca.trim().toLocaleLowerCase("pt-BR");
    if (!documentos || !termo) return documentos ?? [];
    return documentos.filter((documento) =>
      [documento.title, documento.theme, documento.kind, documento.summary ?? ""]
        .some((campo) => campo.toLocaleLowerCase("pt-BR").includes(termo)),
    );
  }, [documentos, busca]);

  async function gerar() {
    if (!selecionado) return;
    setGerando(true);
    setErro("");
    try {
      const blob = await api.blobPost(
        `/biblioteca/${selecionado.slug}/apresentacao`,
        { anotacao: anotacao.trim() },
      );
      baixar(blob, `${selecionado.slug}-apresentacao.pdf`);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível gerar a apresentação.");
    } finally {
      setGerando(false);
    }
  }

  if (erro && !documentos) return <Erro mensagem={erro} />;
  if (!documentos) return <Carregando texto="Abrindo o catálogo de apresentações…" />;

  return (
    <>
      <p className="eyebrow">Aula e round</p>
      <h1>Modo Apresentação</h1>
      <p style={{ color: "var(--texto-secundario)", maxWidth: "68ch" }}>
        Escolha um documento ou fluxograma publicado e gere um PDF em paisagem,
        com a marca Corvia, seus dados profissionais e sua logo cadastrada.
      </p>

      <div className="grade grade--2" style={{ alignItems: "start", marginTop: "1rem" }}>
        <section>
          <label htmlFor="busca-apresentacao">Procurar assunto</label>
          <input
            id="busca-apresentacao"
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
            placeholder="Ex.: insuficiência cardíaca, fibrilação atrial, fluxograma…"
          />

          <div style={{ display: "grid", gap: "0.55rem", marginTop: "0.8rem", maxHeight: "68vh", overflowY: "auto", paddingRight: 4 }}>
            {filtrados.length === 0 ? (
              <Vazio titulo="Nenhum documento encontrado" acao="Tente outro termo." />
            ) : filtrados.map((documento) => (
              <button
                type="button"
                key={documento.slug}
                className="cartao"
                onClick={() => { setSelecionado(documento); setErro(""); }}
                aria-pressed={selecionado?.slug === documento.slug}
                style={{
                  textAlign: "left",
                  cursor: "pointer",
                  width: "100%",
                  borderLeft: selecionado?.slug === documento.slug
                    ? "4px solid var(--acento)"
                    : undefined,
                }}
              >
                <p className="eyebrow" style={{ margin: 0 }}>
                  {documento.theme} · {documento.kind}
                </p>
                <strong>{documento.title}</strong>
                {documento.summary && (
                  <span style={{ display: "block", marginTop: 4, fontSize: "0.84rem", color: "var(--texto-secundario)" }}>
                    {documento.summary}
                  </span>
                )}
              </button>
            ))}
          </div>
        </section>

        <section className="cartao" style={{ position: "sticky", top: "1rem" }}>
          {!selecionado ? (
            <Vazio
              titulo="Selecione um documento"
              acao="O título, o resumo e o tipo aparecerão aqui antes da geração."
            />
          ) : (
            <>
              <p className="eyebrow" style={{ margin: 0 }}>Documento selecionado</p>
              <h2 style={{ marginTop: "0.35rem" }}>{selecionado.title}</h2>
              <p style={{ color: "var(--texto-secundario)" }}>
                {selecionado.theme} · {selecionado.kind}
              </p>
              {selecionado.summary && <p>{selecionado.summary}</p>}

              <label htmlFor="anotacao-apresentacao" style={{ marginTop: "0.8rem" }}>
                Anotação do apresentador (opcional)
              </label>
              <textarea
                id="anotacao-apresentacao"
                rows={5}
                value={anotacao}
                maxLength={2000}
                onChange={(e) => setAnotacao(e.target.value)}
                placeholder="Ex.: discutir com a equipe o caso do leito 12."
              />
              <p className="eyebrow" style={{ margin: "0.3rem 0 0" }}>
                A anotação entra em página própria, não é salva e não altera o conteúdo científico.
              </p>

              {erro && <p role="alert" style={{ color: "var(--alerta)" }}>{erro}</p>}
              <button className="botao" style={{ width: "100%", marginTop: "0.9rem" }} onClick={gerar} disabled={gerando}>
                {gerando ? "Gerando PDF…" : "Gerar apresentação em PDF"}
              </button>
            </>
          )}
        </section>
      </div>
    </>
  );
}
