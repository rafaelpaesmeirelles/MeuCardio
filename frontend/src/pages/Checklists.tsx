import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api, ApiError, todasAsPaginas } from "../lib/api";
import { Carregando, Vazio } from "../components/Estado";

type Resumo = {
  slug: string;
  condicao: string;
  resumo: string | null;
  theme: string | null;
  scope_type: "doenca" | "procedimento";
  documento_origem: string | null;
  total_itens: number;
  obrigatorios: number;
};

type Aplicacao = {
  id: number;
  condicao: string;
  scope_type: "doenca" | "procedimento" | null;
  identificacao: string | null;
  finalizado_em: string | null;
  criado_em: string;
  marcados: number;
  total: number;
  faltando_obrigatorios: number;
};

const TITULOS: Record<string, string> = {
  doenca: "Doenças e condições clínicas",
  procedimento: "Procedimentos e intervenções",
};

export default function Checklists() {
  const [modelos, setModelos] = useState<Resumo[] | null>(null);
  const [minhas, setMinhas] = useState<Aplicacao[]>([]);
  const [busca, setBusca] = useState("");
  const [tipo, setTipo] = useState<"" | "doenca" | "procedimento">("");
  const [erro, setErro] = useState("");

  useEffect(() => {
    api.get<Aplicacao[]>("/checklists/aplicacoes/minhas")
      .then(setMinhas)
      .catch(() => setMinhas([]));
  }, []);

  useEffect(() => {
    let ativo = true;
    setModelos(null);
    const atraso = setTimeout(() => {
      const params = new URLSearchParams();
      if (tipo) params.set("scope_type", tipo);
      if (busca.trim()) params.set("q", busca.trim());
      params.set("limit", "500");
      todasAsPaginas<Resumo>(`/checklists?${params}`)
        .then((resposta) => ativo && setModelos(resposta))
        .catch((e) => {
          if (!ativo) return;
          setModelos([]);
          setErro(e instanceof ApiError ? e.message : "Não foi possível carregar os checklists.");
        });
    }, 250);
    return () => {
      ativo = false;
      clearTimeout(atraso);
    };
  }, [busca, tipo]);

  async function iniciar(slug: string) {
    const identificacao = window.prompt(
      "Identificação desta alta (opcional — leito, iniciais ou referência do caso):",
    );
    if (identificacao === null) return;
    try {
      const resposta = await api.post<{ id: number }>("/checklists/aplicacoes", {
        checklist_slug: slug,
        identificacao_livre: identificacao || null,
      });
      window.location.assign(`/checklists/alta/${resposta.id}`);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível iniciar o checklist.");
    }
  }

  const emAndamento = minhas.filter((aplicacao) => !aplicacao.finalizado_em);
  const finalizadas = minhas.filter((aplicacao) => aplicacao.finalizado_em);
  const grupos = useMemo(() => {
    const mapa = new Map<string, Resumo[]>();
    for (const modelo of modelos ?? []) {
      const escopo = modelo.scope_type || "doenca";
      mapa.set(escopo, [...(mapa.get(escopo) ?? []), modelo]);
    }
    return ["doenca", "procedimento"]
      .map((escopo) => [escopo, mapa.get(escopo) ?? []] as const)
      .filter(([, itens]) => itens.length > 0);
  }, [modelos]);

  return (
    <div>
      <p className="eyebrow">Beira do leito</p>
      <h1>Checklist de alta</h1>
      <p className="subtitulo" style={{ maxWidth: "70ch" }}>
        Procure a doença, condição ou procedimento e confira os itens derivados
        dos protocolos da Biblioteca. Cada item mantém a seção de origem.
      </p>
      {erro && <p role="alert" className="erro">{erro}</p>}

      {emAndamento.length > 0 && (
        <section>
          <h2>Em andamento</h2>
          <ul className="checklist__abertas">
            {emAndamento.map((aplicacao) => (
              <li key={aplicacao.id}>
                <Link to={`/checklists/alta/${aplicacao.id}`}>
                  <strong>{aplicacao.condicao}</strong>
                  {aplicacao.identificacao && <span className="dado">{aplicacao.identificacao}</span>}
                </Link>
                <span className="checklist__progresso">
                  {aplicacao.marcados}/{aplicacao.total}
                  {aplicacao.faltando_obrigatorios > 0 && (
                    <em> · {aplicacao.faltando_obrigatorios} obrigatório(s) pendente(s)</em>
                  )}
                </span>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section style={{ marginTop: emAndamento.length ? "1.6rem" : undefined }}>
        <h2>Modelos publicados</h2>
        <div className="grade grade--2" style={{ alignItems: "end", marginBottom: "0.8rem" }}>
          <div>
            <label htmlFor="buscar-checklist">Pesquisar nome ou assunto</label>
            <input
              id="buscar-checklist"
              value={busca}
              onChange={(e) => setBusca(e.target.value)}
              placeholder="Ex.: insuficiência cardíaca, TAVI, revascularização…"
            />
          </div>
          <div>
            <label htmlFor="tipo-checklist">Tipo</label>
            <select id="tipo-checklist" value={tipo} onChange={(e) => setTipo(e.target.value as typeof tipo)}>
              <option value="">Doenças e procedimentos</option>
              <option value="doenca">Somente doenças/condições</option>
              <option value="procedimento">Somente procedimentos</option>
            </select>
          </div>
        </div>

        {modelos === null ? (
          <Carregando texto="Procurando checklists…" />
        ) : modelos.length === 0 ? (
          <Vazio
            titulo="Nenhum checklist encontrado"
            acao="Tente outro nome, assunto ou tipo."
          />
        ) : grupos.map(([escopo, itens]) => (
          <section key={escopo} style={{ marginBottom: "1.4rem" }}>
            <p className="eyebrow" style={{ margin: 0 }}>
              {escopo === "procedimento" ? "Procedimentos" : "Doenças"}
            </p>
            <h3 style={{ marginTop: "0.25rem" }}>{TITULOS[escopo]}</h3>
            <div className="painel__funcoes">
              {itens.map((modelo) => (
                <article key={modelo.slug} className="cartao painel__funcao">
                  <p className="eyebrow" style={{ margin: 0 }}>
                    {modelo.theme || TITULOS[escopo]}
                  </p>
                  <strong>{modelo.condicao}</strong>
                  <span>{modelo.resumo || "Checklist clínico revisado para alta."}</span>
                  <span className="dado">
                    {modelo.total_itens} itens · {modelo.obrigatorios} obrigatórios
                  </span>
                  <button className="botao botao--acao" onClick={() => iniciar(modelo.slug)}>
                    Usar nesta alta
                  </button>
                  <Link className="botao" to={`/checklists/${modelo.slug}`}>
                    Abrir e ver conexões
                  </Link>
                  {modelo.documento_origem && (
                    <Link className="checklist__origem" to={`/biblioteca/${modelo.documento_origem}`}>
                      Ver protocolo de origem
                    </Link>
                  )}
                </article>
              ))}
            </div>
          </section>
        ))}
      </section>

      {finalizadas.length > 0 && (
        <section>
          <h2 style={{ marginTop: "1.8rem" }}>Finalizadas</h2>
          <ul className="checklist__abertas">
            {finalizadas.slice(0, 20).map((aplicacao) => (
              <li key={aplicacao.id}>
                <Link to={`/checklists/alta/${aplicacao.id}`}>
                  <strong>{aplicacao.condicao}</strong>
                  {aplicacao.identificacao && <span className="dado">{aplicacao.identificacao}</span>}
                </Link>
                <span className="checklist__progresso">
                  {aplicacao.marcados}/{aplicacao.total}
                  {aplicacao.faltando_obrigatorios > 0 && (
                    <em> · finalizada com pendência justificada</em>
                  )}
                </span>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
