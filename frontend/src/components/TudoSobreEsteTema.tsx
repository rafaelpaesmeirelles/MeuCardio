import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";

/**
 * "Tudo sobre este tema no Ecossistema Corvia" — pedido do Rafael, 08/08/2026:
 * a partir de QUALQUER item (documento, evidência, estudo, medicamento, exame,
 * caso clínico, trilha, imagem de galeria, calculadora, protocolo de
 * emergência, checklist ou material do paciente), o médico precisa ver tudo
 * que o ecossistema tem sobre aquele tópico e chegar lá num clique — sem
 * precisar voltar para a busca e refazer o filtro por tema manualmente.
 *
 * Puramente aditivo: some sozinho (`return null`) quando o item não tem tema
 * (`tema` vazio), quando a chamada falha, ou quando não há absolutamente
 * nenhum item relacionado publicado — nunca mostra uma seção vazia. Consome
 * `GET /api/relacionados`, cuja lógica de cruzamento (o que conta como "mesmo
 * tema" em cada uma das doze frentes do ecossistema) vive inteiramente no
 * backend (`app/services/related_content.py`) — este componente só exibe o
 * que a API já decidiu, nunca decide relação por conta própria.
 */

type ItemRelacionado = {
  slug: string;
  titulo: string;
  subtitulo: string | null;
  rota: string;
};

type Grupo = {
  tipo: string;
  rotulo: string;
  rota_lista: string;
  itens: ItemRelacionado[];
};

type Resposta = { tema: string; grupos: Grupo[]; total: number };

type Props = {
  /** Tema do item atual — o mesmo valor gravado em `theme`/`tema` no banco. */
  tema: string | null | undefined;
  /** Tipo e slug do próprio item, para nunca aparecer na sua própria lista. */
  excluirTipo?: string;
  excluirSlug?: string;
  /** Título da seção — o padrão já é o texto pensado para a maioria das páginas. */
  titulo?: string;
};

export default function TudoSobreEsteTema({ tema, excluirTipo, excluirSlug, titulo }: Props) {
  const [resposta, setResposta] = useState<Resposta | null>(null);

  useEffect(() => {
    setResposta(null);
    const t = (tema ?? "").trim();
    if (!t) return;
    const params = new URLSearchParams({ tema: t });
    if (excluirTipo) params.set("excluir_tipo", excluirTipo);
    if (excluirSlug) {
      params.set("excluir_slug", excluirSlug);
      params.set("assunto", excluirSlug);
    }
    api
      .get<Resposta>(`/relacionados?${params.toString()}`)
      .then(setResposta)
      .catch(() => {
        // Silencioso de propósito: este painel é um complemento da página, não
        // o conteúdo principal — uma falha aqui não pode quebrar a leitura do
        // item que o médico já abriu.
      });
  }, [tema, excluirTipo, excluirSlug]);

  if (!resposta || resposta.total === 0) return null;
  const grupos = resposta.grupos.filter((g) => g.itens.length > 0);
  if (grupos.length === 0) return null;

  return (
    <section className="cartao" style={{ marginTop: "1.2rem" }}>
      <p className="eyebrow">{titulo ?? "Tudo sobre este tema no Ecossistema Corvia"}</p>
      <p style={{ fontSize: "0.86rem", color: "var(--texto-secundario)", marginTop: "-0.2rem" }}>
        {resposta.total} {resposta.total === 1 ? "item publicado" : "itens publicados"} sobre{" "}
        <strong>{resposta.tema}</strong> em outras frentes do ecossistema — acesse direto.
      </p>

      <div style={{ display: "flex", flexDirection: "column", gap: "0.9rem", marginTop: "0.8rem" }}>
        {grupos.map((g) => (
          <div key={g.tipo}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
              <p style={{ fontWeight: 600, fontSize: "0.88rem", margin: "0 0 0.35rem" }}>{g.rotulo}</p>
              <Link to={g.rota_lista} style={{ fontSize: "0.78rem" }}>
                ver todos »
              </Link>
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem" }}>
              {g.itens.map((item) => (
                <Link
                  key={item.slug}
                  to={item.rota}
                  className="chip"
                  title={item.subtitulo ?? undefined}
                  style={{ textDecoration: "none", maxWidth: "26rem" }}
                >
                  {item.titulo}
                </Link>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
