import { useState } from "react";
import { api } from "../lib/api";

/**
 * Tarefa 16 — exporta o documento aberto em formato de aula ou round.
 *
 * A anotação é opcional e **não é salva**: ela vai no corpo da requisição, é
 * usada na geração do PDF e desaparece. É deliberado — a observação de um round
 * específico ("discutir o caso do leito 12") não é conteúdo da plataforma, e
 * guardá-la seria o primeiro passo para ela reaparecer como se fosse.
 *
 * O aviso disso fica visível ao lado do campo, e não numa nota de rodapé: quem
 * escreve uma observação precisa saber, na hora de escrever, que ela é
 * descartável.
 */
export default function ExportarApresentacao({ slug, titulo }: {
  slug: string;
  titulo: string;
}) {
  const [aberto, setAberto] = useState(false);
  const [anotacao, setAnotacao] = useState("");
  const [gerando, setGerando] = useState(false);
  const [erro, setErro] = useState("");

  async function exportar() {
    setGerando(true);
    setErro("");
    try {
      const blob = await api.blobPost(
        `/biblioteca/${slug}/apresentacao`,
        { anotacao }
      );
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${slug}-apresentacao.pdf`;
      a.click();
      URL.revokeObjectURL(url);
      setAberto(false);
      setAnotacao("");
    } catch (e: any) {
      setErro(e?.message || "Não foi possível gerar a apresentação.");
    } finally {
      setGerando(false);
    }
  }

  if (!aberto) {
    return (
      <button className="botao botao--secundario" onClick={() => setAberto(true)}>
        Exportar para aula ou round
      </button>
    );
  }

  return (
    <div className="cartao" style={{ marginTop: "0.8rem" }}>
      <p className="eyebrow">Exportar “{titulo}”</p>
      <p style={{ fontSize: "0.86rem", margin: "0.5rem 0 0.7rem" }}>
        Gera um PDF em paisagem, com um assunto por página e corpo grande, pronto
        para projetar. O conteúdo é o mesmo que está publicado aqui.
      </p>

      <label htmlFor="anotacao" style={{ fontSize: "0.84rem", fontWeight: 600 }}>
        Anotação para esta apresentação (opcional)
      </label>
      <textarea
        id="anotacao"
        value={anotacao}
        onChange={(e) => setAnotacao(e.target.value.slice(0, 2000))}
        rows={3}
        placeholder="Ex.: discutir com a equipe o caso do leito 12."
        style={{ width: "100%", marginTop: "0.35rem" }}
      />
      <p className="dado" style={{ marginTop: "0.3rem" }}>
        Sai numa página própria, identificada como sua. Não é salva na plataforma
        e não altera o documento — some quando o arquivo termina de ser gerado.
      </p>

      {erro && <p className="erro">{erro}</p>}

      <div style={{ display: "flex", gap: 8, marginTop: "0.8rem" }}>
        <button className="botao botao--acao" onClick={exportar} disabled={gerando}>
          {gerando ? "Gerando…" : "Gerar PDF"}
        </button>
        <button
          className="botao botao--secundario"
          onClick={() => { setAberto(false); setErro(""); }}
          disabled={gerando}
        >
          Cancelar
        </button>
      </div>
    </div>
  );
}
