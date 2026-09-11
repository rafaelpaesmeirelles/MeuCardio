import { useEffect, useRef, useState } from "react";
import { api, ApiError } from "../lib/api";
import { useAuth } from "../lib/auth";
import AssinaturaExternaITI from "./AssinaturaExternaITI";
import OfertaEnvioEmailPaciente from "./OfertaEnvioEmailPaciente";

export type Provedor = {
  codigo: string;
  nome: string;
  nivel: string;
  familia: string;
  disponivel: boolean;
  motivo: string | null;
};

const METODOS_MANUAL_EXTERNO = new Set(["GOVBR", "VIDAAS", "BIRDID", "SAFEID", "NEOID", "REMOTEID", "A3_TOKEN"]);

function baixarBlob(blob: Blob, nomeArquivo: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = nomeArquivo;
  a.click();
  URL.revokeObjectURL(url);
}

export default function FinalizarDocumentoGerado({ geradoId, nomeArquivoBase, provedores, onFechar }: {
  geradoId: number;
  nomeArquivoBase: string;
  provedores: Provedor[] | null;
  onFechar: () => void;
}) {
  const { usuario } = useAuth();
  const [metodo, setMetodo] = useState(usuario?.assinatura_metodo_preferido ?? "MANUAL");
  const [erro, setErro] = useState("");
  const [email, setEmail] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [resultadoEnvio, setResultadoEnvio] = useState<{ enviado: boolean; link: string | null } | null>(null);
  const [aguardandoExterno, setAguardandoExterno] = useState(false);
  const [assinadoExternoAgora, setAssinadoExternoAgora] = useState(false);
  const [emitido, setEmitido] = useState(false);
  const [assinaturaConcluida, setAssinaturaConcluida] = useState(false);
  const [estadoCarregado, setEstadoCarregado] = useState(false);
  const [baixando, setBaixando] = useState(false);
  const [opcoes, setOpcoes] = useState(provedores);
  const contexto = useRef(0);
  const consultaOpcoes = useRef(0);

  async function carregarOpcoes() {
    const atual = contexto.current;
    const consulta = ++consultaOpcoes.current;
    try {
      const disponiveis = await api.get<Provedor[]>("/assinatura/provedores");
      if (atual === contexto.current && consulta === consultaOpcoes.current) setOpcoes(disponiveis);
    } catch {
      if (atual !== contexto.current || consulta !== consultaOpcoes.current) return;
      setOpcoes([]);
      setErro("Não foi possível carregar os métodos de assinatura. Tente novamente.");
    }
  }

  useEffect(() => {
    const atual = ++contexto.current;
    setMetodo(usuario?.assinatura_metodo_preferido ?? "MANUAL");
    setErro("");
    setEmail("");
    setEnviando(false);
    setBaixando(false);
    setEstadoCarregado(false);
    setEmitido(false);
    setAssinaturaConcluida(false);
    setAguardandoExterno(false);
    setAssinadoExternoAgora(false);
    setResultadoEnvio(null);
    api.get<{ assinatura: { metodo: string; assinado_em: string | null } | null }>(`/document-templates/gerados/${geradoId}`)
      .then(({ assinatura }) => {
        if (atual !== contexto.current) return;
        if (assinatura) {
          setMetodo(assinatura.metodo);
          setEmitido(true);
          setAssinaturaConcluida(Boolean(assinatura.assinado_em));
          setAguardandoExterno(METODOS_MANUAL_EXTERNO.has(assinatura.metodo) && !assinatura.assinado_em);
        }
        setEstadoCarregado(true);
      })
      .catch(() => { if (atual === contexto.current) setErro("Não foi possível consultar a emissão. Feche e abra o documento novamente."); });
    carregarOpcoes();
    return () => { contexto.current += 1; };
  }, [geradoId]);

  useEffect(() => {
    if (!emitido && usuario?.assinatura_metodo_preferido) {
      setMetodo(usuario.assinatura_metodo_preferido);
    }
  }, [usuario?.assinatura_metodo_preferido, emitido]);

  async function baixar() {
    if (baixando || !estadoCarregado) return;
    const atual = contexto.current;
    setBaixando(true);
    setErro("");
    try {
      const blob = await api.blob(`/document-templates/gerados/${geradoId}/pdf?metodo=${encodeURIComponent(metodo)}`);
      if (atual !== contexto.current) return;
      baixarBlob(blob, `${nomeArquivoBase}-${geradoId}.pdf`);
      const externo = METODOS_MANUAL_EXTERNO.has(metodo);
      setAguardandoExterno(externo && !assinaturaConcluida);
      if (metodo !== "MANUAL" && !externo) setAssinaturaConcluida(true);
      setEmitido(true);
    } catch (e) {
      if (atual === contexto.current) setErro(e instanceof ApiError ? e.message : "Não foi possível baixar o PDF.");
    } finally {
      if (atual === contexto.current) setBaixando(false);
    }
  }

  async function enviar() {
    if (enviando || baixando || !email || !emitido || (metodo !== "MANUAL" && !assinaturaConcluida)) return;
    const atual = contexto.current;
    setEnviando(true);
    setErro("");
    try {
      const r = await api.post<{ enviado: boolean; link: string | null }>(
        `/document-templates/gerados/${geradoId}/enviar-email`, { email },
      );
      if (atual === contexto.current) setResultadoEnvio(r);
    } catch (e) {
      if (atual === contexto.current) setErro(e instanceof ApiError ? e.message : "Não foi possível enviar o e-mail.");
    } finally {
      if (atual === contexto.current) setEnviando(false);
    }
  }

  function fechar() {
    // Impede efeitos tardios nesta interface, sem cancelar emissão/envio no servidor.
    contexto.current += 1;
    onFechar();
  }

  return (
    <div className="cartao" style={{ marginTop: "0.8rem" }}>
      <p style={{ color: "var(--sucesso)" }}>Documento gerado.</p>
      <div style={{ marginTop: "0.4rem" }}>
        <label htmlFor={`assinatura-documento-${geradoId}`} style={{ color: "var(--atelier-ink, var(--texto))", WebkitTextFillColor: "currentColor" }}>Método de assinatura</label>
        <select id={`assinatura-documento-${geradoId}`} value={metodo} disabled={emitido || baixando || !estadoCarregado} onChange={(e) => setMetodo(e.target.value)}>
          {!opcoes?.length && <option value={metodo}>{opcoes === null ? "Carregando métodos…" : "Métodos indisponíveis"}</option>}
          {(opcoes ?? []).map((p) => (
            <option key={p.codigo} value={p.codigo} disabled={!p.disponivel}>
              {p.nome}{!p.disponivel ? " — indisponível" : ""}
            </option>
          ))}
        </select>
        {(() => {
          const escolhido = opcoes?.find((p) => p.codigo === metodo);
          if (!escolhido || escolhido.disponivel) return null;
          return <p style={{ color: "var(--alerta)", fontSize: "0.82rem", margin: "0.3rem 0 0" }}>{escolhido.motivo}</p>;
        })()}
      </div>
      {opcoes?.length === 0 && <button className="botao botao--secundario" onClick={carregarOpcoes}>Recarregar métodos de assinatura</button>}
      {!emitido && <p className="dado">Escolha como assinar antes de emitir. O certificado A1 assina diretamente no CorVIA quando está conectado em Minha conta.</p>}
      {emitido && !assinaturaConcluida && metodo === "MANUAL" && <p className="dado">Este PDF foi emitido sem assinatura digital. Use “Recriar baseado neste” para emitir uma nova versão com certificado.</p>}
      <button className="botao" style={{ marginTop: "0.6rem" }} onClick={baixar}
        disabled={baixando || !estadoCarregado || (!emitido && !opcoes?.some((p) => p.codigo === metodo && p.disponivel))}>
        {baixando ? "Preparando PDF…" : emitido ? "Baixar PDF" : metodo === "MANUAL" ? "Emitir sem assinatura digital e baixar" : METODOS_MANUAL_EXTERNO.has(metodo) ? "Preparar PDF para assinatura externa" : "Assinar digitalmente e baixar PDF"}
      </button>

      {aguardandoExterno && (
        <AssinaturaExternaITI
          metodo={metodo}
          nomeProvedor={opcoes?.find((p) => p.codigo === metodo)?.nome ?? metodo}
          enviarUrl={`/document-templates/gerados/${geradoId}/assinatura-externa`}
          onConcluido={() => { setAguardandoExterno(false); setAssinadoExternoAgora(true); setAssinaturaConcluida(true); }}
        />
      )}
      {assinadoExternoAgora && (
        <p style={{ color: "var(--sucesso)", fontSize: "0.86rem", marginTop: "0.4rem" }}>
          Assinatura conferida com sucesso — o documento já está assinado.
        </p>
      )}

      <OfertaEnvioEmailPaciente
        endpointBase={`/document-templates/gerados/${geradoId}`}
        habilitado={assinaturaConcluida}
      />

      <div style={{ marginTop: "0.8rem" }}>
        <label htmlFor={`email-documento-${geradoId}`} style={{ color: "var(--atelier-ink, var(--texto))", WebkitTextFillColor: "currentColor" }}>Enviar por e-mail ao paciente (link seguro, válido por 7 dias)</label>
        <input id={`email-documento-${geradoId}`} type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="paciente@exemplo.com" />
        <button className="botao" style={{ marginTop: "0.4rem" }} onClick={enviar} disabled={enviando || !email || !emitido || (metodo !== "MANUAL" && !assinaturaConcluida) || baixando}>
          {enviando ? "Enviando…" : "Enviar por e-mail"}
        </button>
      </div>

      {resultadoEnvio && (
        resultadoEnvio.enviado ? (
          <p style={{ color: "var(--sucesso)", fontSize: "0.86rem" }}>E-mail enviado.</p>
        ) : (
          <p style={{ fontSize: "0.86rem" }}>
            O envio automático não está disponível agora. Copie o link e envie manualmente:{" "}
            <code style={{ wordBreak: "break-all" }}>{resultadoEnvio.link}</code>
          </p>
        )
      )}

      {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erro}</p>}
      <button className="botao botao--secundario" style={{ marginTop: "0.8rem" }} onClick={fechar}>Fechar</button>
    </div>
  );
}
