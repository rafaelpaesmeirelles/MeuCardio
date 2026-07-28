import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";

type Curso = {
  slug: string;
  nome: string;
  parceiro: string;
  descricao: string | null;
  frase_destaque: string | null;
  frase_destaque_fonte: string | null;
  preco_total_centavos: number;
  assinado: boolean;
};

export default function Cursos() {
  const [cursos, setCursos] = useState<Curso[] | null>(null);

  useEffect(() => {
    api
      .get<Curso[]>("/api/cursos")
      .then(setCursos)
      .catch(() => setCursos([]));
  }, []);

  if (cursos === null) return <p>Carregando…</p>;

  return (
    <div>
      <h1>Cursos parceiros</h1>
      <p className="subtitulo">
        Cursos de preparação para o Título de Especialista em Cardiologia, oferecidos
        por parceiros e assinados dentro do MeuCardio. A assinatura de um curso é
        separada da assinatura da plataforma.
      </p>

      {cursos.length === 0 ? (
        <p className="curso__vazio">
          Nenhum curso parceiro ativo no momento.
        </p>
      ) : (
        <div className="painel__funcoes">
          {cursos.map((c) => (
            <Link key={c.slug} to={`/cursos/${c.slug}`} className="cartao painel__funcao">
              <strong>{c.nome}</strong>
              <span>{c.descricao || `Curso oferecido por ${c.parceiro}.`}</span>
              <span className="dado">
                {c.assinado
                  ? "Você já assina"
                  : (c.preco_total_centavos / 100).toLocaleString("pt-BR", {
                      style: "currency",
                      currency: "BRL",
                    }) + "/mês"}
              </span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
