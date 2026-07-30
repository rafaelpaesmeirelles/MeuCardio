import { useEffect, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { api } from "../lib/api";

type Material = { id: number; titulo: string; nome_arquivo: string; tamanho_bytes: number };
type Curso = {
  slug: string;
  nome: string;
  parceiro: string;
  descricao: string | null;
  frase_destaque: string | null;
  frase_destaque_fonte: string | null;
  preco_total_centavos: number;
  assinado: boolean;
  link_aula_ao_vivo?: string | null;
  link_aulas_gravadas?: string | null;
  materiais?: Material[];
  trilhas_vinculadas: string[];
  casos_vinculados: string[];
};

/**
 * Página do curso parceiro dentro da Corvia.
 *
 * O vídeo não vive aqui: aula ao vivo e gravadas ficam no ambiente do parceiro,
 * e estes são links de redirecionamento. O que é servido daqui é o material de
 * apoio, por rota autenticada — o arquivo não tem endereço público.
 */
export default function Curso() {
  const { slug = "" } = useParams();
  const [params] = useSearchParams();
  const [curso, setCurso] = useState<Curso | null>(null);
  const [erro, setErro] = useState("");
  const [assinando, setAssinando] = useState(false);

  useEffect(() => {
    api
      .get<Curso>(`/cursos/${slug}`)
      .then(setCurso)
      .catch((e) => setErro(e?.message || "Não foi possível carregar o curso."));
  }, [slug]);

  async function assinar() {
    setAssinando(true);
    setErro("");
    try {
      const r = await api.post<{ checkout_url: string }>(`/cursos/${slug}/assinar`, {});
      window.location.href = r.checkout_url;
    } catch (e: any) {
      setErro(e?.message || "Não foi possível iniciar a assinatura.");
      setAssinando(false);
    }
  }

  async function baixar(m: Material) {
    try {
      const blob = await api.blob(`/cursos/${slug}/material/${m.id}`);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = m.nome_arquivo;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      setErro("Não foi possível baixar o material.");
    }
  }

  if (erro && !curso) return <p className="erro">{erro}</p>;
  if (!curso) return <p>Carregando…</p>;

  const preco = (curso.preco_total_centavos / 100).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });

  return (
    <div className="curso">
      <p className="curso__voltar">
        <Link to="/cursos">← Todos os cursos</Link>
      </p>

      <h1>{curso.nome}</h1>
      <p className="curso__parceiro">Curso oferecido por {curso.parceiro}</p>

      {params.get("status") === "sucesso" && (
        <p className="aviso aviso--ok">
          Pagamento confirmado. O acesso libera assim que o Stripe confirmar a
          assinatura — se ainda aparecer bloqueado, recarregue em alguns instantes.
        </p>
      )}
      {params.get("status") === "cancelado" && (
        <p className="aviso">Assinatura não concluída. Nada foi cobrado.</p>
      )}
      {erro && <p className="erro">{erro}</p>}

      {curso.frase_destaque && (
        <p className="curso__frase">
          {curso.frase_destaque}
          {curso.frase_destaque_fonte && (
            <span className="curso__fonte">Dado informado por {curso.frase_destaque_fonte}</span>
          )}
        </p>
      )}

      {curso.descricao && <p className="curso__descricao">{curso.descricao}</p>}

      {curso.assinado ? (
        <>
          <h2>Aulas</h2>
          <div className="curso__links">
            {curso.link_aula_ao_vivo && (
              <a className="botao" href={curso.link_aula_ao_vivo} target="_blank" rel="noreferrer">
                Entrar na aula ao vivo
              </a>
            )}
            {curso.link_aulas_gravadas && (
              <a className="botao" href={curso.link_aulas_gravadas} target="_blank" rel="noreferrer">
                Ver aulas gravadas
              </a>
            )}
            {!curso.link_aula_ao_vivo && !curso.link_aulas_gravadas && (
              <p className="curso__vazio">O parceiro ainda não informou os links de acesso.</p>
            )}
          </div>
          <p className="curso__nota">
            As aulas ficam no ambiente do parceiro — estes links levam para lá.
          </p>

          <h2>Material de apoio</h2>
          {curso.materiais && curso.materiais.length > 0 ? (
            <ul className="curso__materiais">
              {curso.materiais.map((m) => (
                <li key={m.id}>
                  <button className="link" onClick={() => baixar(m)}>
                    {m.titulo}
                  </button>
                  <span className="dado">{Math.round(m.tamanho_bytes / 1024)} KB</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="curso__vazio">Nenhum material publicado até agora.</p>
          )}
        </>
      ) : (
        <div className="cartao curso__oferta">
          <span className="curso__preco">
            {preco}
            <small>/mês</small>
          </span>
          <p>
            Assinatura do curso, cobrada à parte da assinatura da Corvia. Uma não
            substitui a outra.
          </p>
          <button className="botao botao--acao" onClick={assinar} disabled={assinando}>
            {assinando ? "Abrindo o pagamento…" : "Assinar este curso"}
          </button>
        </div>
      )}

      {(curso.trilhas_vinculadas.length > 0 || curso.casos_vinculados.length > 0) && (
        <>
          <h2>Para praticar na Corvia</h2>
          <p className="curso__nota">
            Conteúdo da plataforma ligado a este curso, para aplicar o que acabou de
            estudar sem sair daqui.
          </p>
          <ul className="curso__vinculos">
            {curso.trilhas_vinculadas.map((t) => (
              <li key={`t-${t}`}>Trilha: {t}</li>
            ))}
            {curso.casos_vinculados.map((c) => (
              <li key={`c-${c}`}>Caso clínico: {c}</li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
