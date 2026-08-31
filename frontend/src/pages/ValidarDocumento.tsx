import { FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "../styles/validar-documento.css";

type Prescritor = {
  nome: string;
  conselho: string | null;
  numero: string | null;
  uf: string | null;
  rqe: string | null;
};

type Resultado = {
  codigo: string;
  valido: boolean;
  tipo: string;
  tipo_receita: string | null;
  emissao_confirmada_corvia: boolean;
  emitido_em: string | null;
  registrado_corvia_em: string;
  prescritor: Prescritor | null;
  metodo: string;
  metodo_nome: string;
  metodo_familia: string;
  nivel: string;
  fluxo_assinatura: string;
  fluxo_assinatura_descricao: string;
  integridade_hash: boolean;
  assinatura_encontrada: boolean;
  assinatura_intacta: boolean;
  estrutura_valida: boolean;
  cobre_documento_inteiro: boolean;
  titular: string | null;
  emissor_certificado: string | null;
  numero_serie_certificado: string | null;
  certificado_valido_de: string | null;
  certificado_valido_ate: string | null;
  certificado_valido_no_momento_assinatura: boolean | null;
  politicas_certificado: string[];
  assinado_em: string | null;
  qualificada_icp_brasil: boolean;
  cadeia_confianca_validada: boolean;
  sha256: string;
  pdf_original_disponivel: boolean;
  pdf_original_url: string | null;
  validacao_independente_url: string;
  aviso: string;
};

function normalizar(valor: string) {
  return valor.trim().toUpperCase().replace(/\s+/g, "");
}

function dataHora(valor: string | null | undefined) {
  if (!valor) return "Não informado";
  const data = new Date(valor);
  if (Number.isNaN(data.getTime())) return "Não informado";
  return data.toLocaleString("pt-BR");
}

function registroPrescritor(prescritor: Prescritor | null) {
  if (!prescritor) return "Não identificado";
  const conselho = [prescritor.conselho, prescritor.numero, prescritor.uf].filter(Boolean).join("/");
  return conselho ? `${prescritor.nome} — ${conselho}` : prescritor.nome;
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

  const receitaValida = Boolean(
    resultado?.valido && resultado.tipo === "prescription_document" && resultado.emissao_confirmada_corvia,
  );

  return (
    <main className="corvia-validator" id="conteudo-principal">
      <section className="corvia-validator__panel">
        <header className="corvia-validator__header">
          <img src="/corvia-logo-spaces-dark.svg" alt="CorVIA Cardiology Spaces" />
          <p>Validação pública de documento clínico</p>
          <h1>Confira a autenticidade da emissão e da assinatura</h1>
          <span>O QR confirma o documento emitido pelo CorVIA sem revelar medicamentos, diagnóstico ou dados do paciente nesta página.</span>
        </header>

        <form className="corvia-validator__form" onSubmit={enviar}>
          <label htmlFor="codigo-validacao">Código de validação</label>
          <div>
            <input
              id="codigo-validacao"
              value={codigo}
              onChange={(event) => setCodigo(event.target.value)}
              placeholder="R123-1A2B3C4D5E6F7A8B…"
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
              <strong>{receitaValida ? "Emissão CorVIA confirmada — receita autêntica" : resultado.valido ? "Documento emitido pelo CorVIA com integridade criptográfica confirmada" : "A validação encontrou uma inconsistência"}</strong>
              <span>Código {resultado.codigo}</span>
            </div>

            <div className="corvia-validator__trust-row" aria-label="Resumo da validação">
              <span className={resultado.emissao_confirmada_corvia ? "is-ok" : "is-warn"}>Emissão {resultado.emissao_confirmada_corvia ? "confirmada" : "não confirmada"}</span>
              <span className={resultado.integridade_hash ? "is-ok" : "is-warn"}>Hash {resultado.integridade_hash ? "confere" : "divergente"}</span>
              <span className={resultado.assinatura_intacta ? "is-ok" : "is-warn"}>Assinatura {resultado.assinatura_intacta ? "íntegra" : "não confirmada"}</span>
            </div>

            <dl>
              <div><dt>Tipo</dt><dd>{resultado.tipo === "prescription_document" ? `Receituário${resultado.tipo_receita ? ` — ${resultado.tipo_receita}` : ""}` : "Documento clínico"}</dd></div>
              <div><dt>Emitido pelo CorVIA em</dt><dd>{dataHora(resultado.registrado_corvia_em || resultado.emitido_em)}</dd></div>
              <div><dt>Prescritor</dt><dd>{registroPrescritor(resultado.prescritor)}</dd></div>
              <div><dt>Assinado em</dt><dd>{dataHora(resultado.assinado_em)}</dd></div>
              <div><dt>Método informado na emissão</dt><dd>{resultado.metodo_nome}</dd></div>
              <div><dt>Onde ocorreu a assinatura</dt><dd>{resultado.fluxo_assinatura === "corvia_local" ? "Dentro do CorVIA" : resultado.fluxo_assinatura === "externo_reimportado" ? "Fora do CorVIA, com reimportação validada" : "Sem assinatura concluída"}</dd></div>
              <div><dt>Titular do certificado</dt><dd>{resultado.titular || "Não identificado"}</dd></div>
              <div><dt>Emissor do certificado</dt><dd>{resultado.emissor_certificado || "Não identificado"}</dd></div>
              <div><dt>Número de série</dt><dd>{resultado.numero_serie_certificado || "Não identificado"}</dd></div>
              <div><dt>Validade do certificado</dt><dd>{resultado.certificado_valido_de && resultado.certificado_valido_ate ? `${dataHora(resultado.certificado_valido_de)} até ${dataHora(resultado.certificado_valido_ate)}` : "Não identificada"}</dd></div>
              <div><dt>Válido na hora da assinatura</dt><dd>{resultado.certificado_valido_no_momento_assinatura === true ? "Sim, pelo período gravado no certificado" : resultado.certificado_valido_no_momento_assinatura === false ? "Não" : "Não determinado"}</dd></div>
              <div><dt>Política ICP-Brasil</dt><dd>{resultado.qualificada_icp_brasil ? "A1/A2/A3/A4 detectada no certificado" : "Não confirmada nesta verificação"}</dd></div>
              <div><dt>Integridade do PDF</dt><dd>{resultado.integridade_hash && resultado.assinatura_intacta ? "Íntegra" : "Inconsistente"}</dd></div>
              <div><dt>Cobertura da assinatura</dt><dd>{resultado.cobre_documento_inteiro ? "Documento inteiro" : "Não confirmada"}</dd></div>
            </dl>

            <p className="corvia-validator__flow"><b>Rastreabilidade da assinatura</b><span>{resultado.fluxo_assinatura_descricao}</span></p>
            <p className="corvia-validator__hash"><b>SHA-256 do PDF original emitido</b><code>{resultado.sha256}</code></p>

            <div className="corvia-validator__actions">
              {resultado.pdf_original_disponivel && resultado.pdf_original_url && (
                <a className="is-primary" href={resultado.pdf_original_url}>Baixar PDF original assinado</a>
              )}
              <a href={resultado.validacao_independente_url} target="_blank" rel="noreferrer">Validar independentemente no ITI</a>
            </div>
            {!resultado.pdf_original_disponivel && resultado.tipo === "prescription_document" && (
              <p className="corvia-validator__download-note">Este QR confirma a autenticidade, mas não possui a capability forte exigida para liberar o PDF. Receitas emitidas com o novo QR CorVIA passam a oferecer o download do arquivo original.</p>
            )}

            <p className="corvia-validator__notice">{resultado.aviso}</p>
          </section>
        )}

        <footer>
          A CorVIA confirma a emissão registrada, o SHA-256 e a integridade criptográfica do PDF persistido. A cadeia de confiança, revogação e validade jurídica final do certificado devem ser confirmadas também em um validador independente, como o VALIDAR/ITI.
        </footer>
      </section>
    </main>
  );
}
