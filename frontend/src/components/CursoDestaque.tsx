import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";

type Curso = {
  slug: string;
  nome: string;
  parceiro: string;
  frase_destaque: string | null;
  frase_destaque_fonte: string | null;
  preco_total_centavos: number;
  assinado: boolean;
};

/**
 * Cartão do curso parceiro em destaque, no Painel principal.
 *
 * Some por inteiro quando não há curso ativo em destaque — quem decide é o
 * servidor, que devolve `curso: null`. Nada de moldura vazia nem texto de
 * exemplo no ar: um espaço reservado sem conteúdo passa a impressão de página
 * quebrada, e um texto de exemplo esquecido é pior ainda.
 *
 * A frase de destaque só aparece acompanhada de quem afirmou o dado. Índice de
 * aprovação é afirmação de terceiro, e este cartão fica ao lado de conteúdo
 * clínico que o produto faz questão de manter rastreável.
 */
export default function CursoDestaque() {
  const [curso, setCurso] = useState<Curso | null>(null);
  const [carregou, setCarregou] = useState(false);

  useEffect(() => {
    api
      .get<{ curso: Curso | null }>("/cursos/destaque")
      .then((r) => setCurso(r.curso))
      .catch(() => setCurso(null))
      .finally(() => setCarregou(true));
  }, []);

  // Enquanto carrega não reserva espaço: piscar uma moldura vazia e depois
  // escondê-la desloca o resto do Painel na frente do usuário.
  if (!carregou || !curso) return null;

  const preco = (curso.preco_total_centavos / 100).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });

  return (
    <section className="curso-destaque" aria-labelledby="curso-destaque-titulo">
      <div className="curso-destaque__selo">Curso parceiro</div>

      <div className="curso-destaque__corpo">
        <h2 id="curso-destaque-titulo" className="curso-destaque__nome">
          {curso.nome}
        </h2>
        <p className="curso-destaque__parceiro">por {curso.parceiro}</p>

        {curso.frase_destaque && (
          <p className="curso-destaque__frase">
            {curso.frase_destaque}
            {curso.frase_destaque_fonte && (
              <span className="curso-destaque__fonte">
                Dado informado por {curso.frase_destaque_fonte}
              </span>
            )}
          </p>
        )}
      </div>

      <div className="curso-destaque__acao">
        {curso.assinado ? (
          <>
            <span className="curso-destaque__assinado">Você já assina</span>
            <Link to={`/cursos/${curso.slug}`} className="botao">
              Acessar o curso
            </Link>
          </>
        ) : (
          <>
            <span className="curso-destaque__preco">
              {preco}
              <small>/mês</small>
            </span>
            <Link to={`/cursos/${curso.slug}`} className="botao botao--acao">
              Conhecer o curso
            </Link>
          </>
        )}
      </div>
    </section>
  );
}
