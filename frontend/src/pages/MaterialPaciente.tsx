import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { Carregando, Erro } from "../components/Estado";

/**
 * Tarefa 12 — material educativo para entregar ao paciente.
 *
 * A separação com o resto da biblioteca é proposital e não é só de navegação: o
 * conteúdo aqui é escrito em outro registro, para quem não é da área, e não
 * contém dose, receita nem conduta. Misturar os dois na mesma listagem faria o
 * médico abrir um esperando o outro.
 */

type Material = {
  slug: string;
  titulo: string;
  subtitulo: string | null;
  tema: string;
  resumo: string | null;
};

export default function MaterialPaciente() {
  const [itens, setItens] = useState<Material[] | null>(null);
  const [erro, setErro] = useState("");
  const [baixando, setBaixando] = useState("");

  useEffect(() => {
    api
      .get<Material[]>("/api/material-paciente")
      .then(setItens)
      .catch((e) => setErro(e?.message || "Não foi possível carregar."));
  }, []);

  async function baixar(m: Material) {
    setBaixando(m.slug);
    setErro("");
    try {
      const blob = await api.blob(`/api/material-paciente/${m.slug}/pdf`);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${m.slug}-material-do-paciente.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e: any) {
      setErro(e?.message || "Não foi possível gerar o PDF.");
    } finally {
      setBaixando("");
    }
  }

  if (erro && !itens) return <Erro mensagem={erro} />;
  if (!itens) return <Carregando />;

  return (
    <div>
      <h1>Material para o paciente</h1>
      <p className="subtitulo">
        Explicações em linguagem acessível, para imprimir e entregar na consulta.
        O PDF sai com o seu nome e registro profissional — é a você que o paciente
        volta com dúvida.
      </p>

      <div className="cartao" style={{ marginBottom: "1.2rem" }}>
        <p className="eyebrow">O que este material é e o que não é</p>
        <p style={{ fontSize: "0.88rem", margin: "0.4rem 0 0" }}>
          É explicação da condição, escrita para leigo. <strong>Não contém dose,
          receita nem conduta individualizada</strong>, por decisão de escopo: o que
          fazer com o diagnóstico é da consulta, não de um folheto. Cada material
          declara as diretrizes em que se apoia.
        </p>
      </div>

      {erro && <p className="erro">{erro}</p>}

      {itens.length === 0 ? (
        <p>Nenhum material publicado ainda.</p>
      ) : (
        <div className="painel__funcoes">
          {itens.map((m) => (
            <div key={m.slug} className="cartao painel__funcao">
              <p className="eyebrow">{m.tema}</p>
              <strong>{m.titulo}</strong>
              {m.subtitulo && <span>{m.subtitulo}</span>}
              <button
                className="botao botao--acao"
                style={{ marginTop: "0.7rem" }}
                onClick={() => baixar(m)}
                disabled={baixando === m.slug}
              >
                {baixando === m.slug ? "Gerando…" : "Baixar PDF para entregar"}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
