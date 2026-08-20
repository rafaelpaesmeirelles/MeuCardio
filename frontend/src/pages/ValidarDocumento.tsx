import { FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "../styles/validar-documento.css";

type Resultado = {
  codigo: string;
  valido: boolean;
  tipo: string;
  metodo: string;
  nivel: string;
  integridade_hash: boolean;
  assinatura_encontrada: boolean;
  assinatura_intacta: boolean;
  estrutura_valida: boolean;
  cobre_documento_inteiro: boolean;
  titular: string | null;
  emissor_certificado: string | null;
  assinado_em: string | null;
  qualificada_icp_brasil: boolean;
  sha256: string;
  aviso: string;
};

function normalizar(valor: string) {
  return valor.trim().toUpperCase().replace(/\s+/g, "");
}

export default function ValidarDocumento() {
  const params = useParams();
  const navigate = useNavigate();
  const [codigo, setCodigo] = useState(params.codigo ?? "");
  const [resultado, setResultado] = useState<Resultado | null>(null);
  const [erro, setErro] = useState("");
  const [carregando, setCarregando] = useState(false);

  async function validar(valor: string) {
    const codigoFinal = normalizar(valor);
    if (!codigoFinal) return;
    setCarregando(true);
    setErro("");
    setResultado(null);
    try {
      const resposta = await fetch(`/api/documentos-publicos/validar/${encodeURIComponent(codigoFinal)}`, {
        headers: { Accept: "application/json" },
      });
      if (!resposta.ok) {
        const corpo = await resposta.json().catch(() => null);
        throw new Error(corpo?.detail || "Código de validação não encontrado.");
      }
      setResultado(await resposta.json());
      if (params.codigo !== codigoFinal) navigate(`/validar/${codigoFinal}`, { replace: true });
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não foi possível validar o documento.");
    } finally {
      setCarregando(false);
    }
  }

  useEffect(() => {
    if (params.codigo) void validar(params.codigo);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.codigo]);

  function enviar(event: FormEvent) {
    event.preventDefault();
    void validar(codigo);
  }

  return (
    <main className="corvia-validator" id="conteudo-principal">
      <section className="corvia-validator__panel">
        <header className="corvia-validator__header">
          <img src="/corvia-logo-canonical-dark.svg" alt="CorVIA" />
          <p>Validação pública de documento clínico</p>
          <h1>Confira a autenticidade da assinatura digital</h1>
          <span>Digite o código impresso no PDF. Esta consulta não revela dados clínicos nem libera o arquivo.</span>
        </header>

        <form className="corvia-validator__form" onSubmit={enviar}>
          <label htmlFor="codigo-validacao">Código de validação</label>
          <div>
            <input
              id="codigo-validacao"
              value={codigo}
              onChange={(event) => setCodigo(event.target.value)}
              placeholder="R123-1A2B3C4D5E6F7A8B"
              autoCapitalize="characters"
              autoComplete="off"
            />
            <button type="submit" disabled={carregando || !codigo.trim()}>
              {carregando ? "Validando…" : "Validar"}
            </button>
          </div>
        </form>

        {erro && <div className="corvia-validator__status is-error" role="alert"><strong>Não validado</strong><span>{erro}</span></div>}

        {resultado && (
          <section className={`corvia-validator__result ${resultado.valido ? "is-valid" : "is-invalid"}`}>
            <div className="corvia-validator__status">
              <strong>{resultado.valido ? "Documento íntegro e assinatura criptográfica válida" : "A validação encontrou uma inconsistência"}</strong>
              <span>Código {resultado.codigo}</span>
            </div>
            <dl>
              <div><dt>Tipo</dt><dd>{resultado.tipo === "prescription_document" ? "Receituário" : "Documento clínico"}</dd></div>
              <div><dt>Assinante</dt><dd>{resultado.titular || "Não identificado"}</dd></div>
              <div><dt>Assinado em</dt><dd>{resultado.assinado_em ? new Date(resultado.assinado_em).toLocaleString("pt-BR") : "Sem data de assinatura"}</dd></div>
              <div><dt>Integridade do PDF</dt><dd>{resultado.integridade_hash && resultado.assinatura_intacta ? "Íntegra" : "Inconsistente"}</dd></div>
              <div><dt>Cobertura da assinatura</dt><dd>{resultado.cobre_documento_inteiro ? "Documento inteiro" : "Não confirmada"}</dd></div>
              <div><dt>Política ICP-Brasil</dt><dd>{resultado.qualificada_icp_brasil ? "Detectada no certificado" : "Não confirmada nesta verificação"}</dd></div>
            </dl>
            <p className="corvia-validator__hash"><b>SHA-256 do documento emitido</b><code>{resultado.sha256}</code></p>
            <p className="corvia-validator__notice">{resultado.aviso}</p>
          </section>
        )}

        <footer>
          A validação CorVIA confirma integridade criptográfica e os dados presentes na assinatura do PDF. Para validação de cadeia de confiança, revogação e requisitos oficiais adicionais, utilize também o validador oficial do ITI/ICP-Brasil quando aplicável.
        </footer>
      </section>
    </main>
  );
}
