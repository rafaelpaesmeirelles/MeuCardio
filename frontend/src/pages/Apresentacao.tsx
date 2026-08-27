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

function baixar(blob: Blob, nome: string) {
  const url = URL.createObjectURL(blob);
  const ancora = document.createElement("a");
  ancora.href = url;
  ancora.download = nome;
  ancora.click();
  URL.revokeObjectURL(url);
}

export default function Apresentacao() {
  const [documentos, setDocumentos] = useState<Documento[] | null>(null);
  const [busca, setBusca] = useState("");
  // 07/08/2026, pedido do Rafael: toda ferramenta de busca do site precisa de
  // pelo menos duas formas de refinar — aqui, além do termo livre, filtrar
  // por tema (já presente em cada documento do catálogo), igual ao padrão
  // já usado em Busca.tsx e nas páginas de listagem da biblioteca.
  const [tema, setTema] = useState("");
  const [selecionado, setSelecionado] = useState<Documento | null>(null);
  const [anotacao, setAnotacao] = useState("");
  const [formato, setFormato] = useState<"pdf" | "pptx">("pdf");
  const [gerando, setGerando] = useState(false);
  const [erro, setErro] = useState("");
  const [tentativa, setTentativa] = useState(0);

  useEffect(() => {
    setDocumentos(null);
    setErro("");
    api.get<Documento[]>("/library/presentation-options")
      .then(setDocumentos)
      .catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível carregar os documentos."));
  }, [tentativa]);

  const temas = useMemo(() => {
    const contagem = new Map<string, number>();
    (documentos ?? []).forEach((d) => contagem.set(d.theme, (contagem.get(d.theme) ?? 0) + 1));
    return [...contagem.entries()].sort((a, b) => a[0].localeCompare(b[0], "pt-BR"));
  }, [documentos]);

  const filtrados = useMemo(() => {
    const termo = busca.trim().toLocaleLowerCase("pt-BR");
    return (documentos ?? [])
      .filter((documento) => !tema || documento.theme === tema)
      .filter((documento) => !termo || [documento.title, documento.theme, documento.kind, documento.summary ?? ""]
        .some((campo) => campo.toLocaleLowerCase("pt-BR").includes(termo)));
  }, [documentos, busca, tema]);

  async function gerar() {
    if (!selecionado) return;
    setGerando(true);
    setErro("");
    try {
      const blob = await api.blobPost(
        `/biblioteca/${selecionado.slug}/apresentacao`,
        { anotacao: anotacao.trim(), formato },
      );
      baixar(blob, `${selecionado.slug}-apresentacao.${formato}`);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível gerar a apresentação.");
    } finally {
      setGerando(false);
    }
  }

  if (erro && !documentos) return <div><Erro mensagem={erro} /><button className="botao" style={{ marginTop: "0.8rem" }} onClick={() => setTentativa((valor) => valor + 1)}>Tentar carregar novamente</button></div>;
  if (!documentos) return <Carregando texto="Abrindo o catálogo de apresentações…" />;

  return (
    <>
      <p className="eyebrow">Aula e round</p>
      <h1>Modo Apresentação</h1>
      <p style={{ color: "var(--texto-secundario)", maxWidth: "68ch" }}>
        Escolha um documento ou fluxograma publicado e gere uma apresentação em
        PDF pronto para projetar ou PowerPoint editável, com a marca Corvia,
        seus dados profissionais e sua logo cadastrada.
      </p>

      <div className="grade grade--2" style={{ alignItems: "start", marginTop: "1rem" }}>
        <section>
          <div className="filtros-conteudo">
            <label><strong>Procurar assunto</strong>
              <input
                id="busca-apresentacao"
                value={busca}
                onChange={(e) => setBusca(e.target.value)}
                placeholder="Ex.: insuficiência cardíaca, fibrilação atrial, fluxograma…"
              />
            </label>
            <label><strong>Área/tema</strong>
              <select value={tema} onChange={(e) => setTema(e.target.value)}>
                <option value="">Todas as áreas ({documentos?.length ?? 0})</option>
                {temas.map(([nome, contagem]) => (
                  <option key={nome} value={nome}>{nome} ({contagem})</option>
                ))}
              </select>
            </label>
          </div>

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

              <fieldset style={{ border: 0, padding: 0, margin: "0.8rem 0" }}>
                <legend style={{ fontWeight: 700, marginBottom: "0.45rem" }}>Formato do arquivo</legend>
                <label style={{ display: "flex", alignItems: "flex-start", gap: 9, fontWeight: 400, marginBottom: "0.45rem" }}>
                  <input type="radio" name="formato-apresentacao-pagina" checked={formato === "pdf"} onChange={() => setFormato("pdf")} />
                  <span><strong>PDF</strong><br /><span className="dado">Pronto para projetar, com diagramação fechada.</span></span>
                </label>
                <label style={{ display: "flex", alignItems: "flex-start", gap: 9, fontWeight: 400 }}>
                  <input type="radio" name="formato-apresentacao-pagina" checked={formato === "pptx"} onChange={() => setFormato("pptx")} />
                  <span><strong>PowerPoint editável (.pptx)</strong><br /><span className="dado">Permite reorganizar, cortar e complementar os slides.</span></span>
                </label>
              </fieldset>

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
                {gerando ? "Gerando arquivo…" : formato === "pptx" ? "Gerar PowerPoint editável" : "Gerar apresentação em PDF"}
              </button>
            </>
          )}
        </section>
      </div>
    </>
  );
}
