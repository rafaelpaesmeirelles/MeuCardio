import { useState } from "react";
import { api, ApiError } from "../lib/api";

/** Trabalho 14 (06/08/2026), ampliado no mesmo dia a pedido do Rafael:
 * "gere um site que abrira antes da pagina do ITI explicando como é o
 * fluxo pra assinar e devolver ao Corvia".
 *
 * Os 6 códigos do catálogo que passam por aqui (GOVBR e as 5 clouds
 * QUALIFICADA sem credencial comercial própria — VIDAAS, BIRDID, SAFEID,
 * NEOID, REMOTEID) não têm API: o Assinador ITI (assinador.iti.br,
 * Lei 14.063/2020) é gratuito e público, mas o fluxo é necessariamente
 * manual — o médico sai da Corvia, assina, e volta com o arquivo. Este
 * painel existe para que ninguém chegue ao ITI sem saber o que vai
 * encontrar lá, nem volte para a Corvia sem saber o que fazer com o PDF
 * assinado.
 *
 * Mantido como componente único (não uma rota/página separada) para que
 * o médico não perca o contexto do documento que está emitindo — mas
 * cumpre o mesmo papel de "site que abre antes do ITI": aparece assim
 * que o PDF não assinado é baixado, e só depois de lido é que o link
 * externo abre. */

const ORIENTACAO_CERTIFICADO: Record<string, string> = {
  GOVBR: "sua conta gov.br, com selo de confiabilidade Prata ou Ouro",
  VIDAAS: "seu certificado em nuvem VIDaaS (muitos CRMs já oferecem)",
  BIRDID: "seu certificado em nuvem Bird ID",
  SAFEID: "seu certificado em nuvem SafeID",
  NEOID: "seu certificado em nuvem NeoID",
  REMOTEID: "seu certificado em nuvem Remote ID",
};

export default function AssinaturaExternaITI({
  metodo, nomeProvedor, enviarUrl, onConcluido,
}: {
  metodo: string;
  nomeProvedor: string;
  enviarUrl: string;
  onConcluido: (resultado: { assinado: true; assinado_em: string }) => void;
}) {
  const [arquivo, setArquivo] = useState<File | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState("");
  const [abriuIti, setAbriuIti] = useState(false);

  const orientacao = ORIENTACAO_CERTIFICADO[metodo]
    ?? `seu certificado digital (${nomeProvedor})`;

  function abrirIti() {
    window.open("https://assinador.iti.br", "_blank", "noopener,noreferrer");
    setAbriuIti(true);
  }

  async function enviarAssinado() {
    if (!arquivo) return;
    setEnviando(true);
    setErro("");
    try {
      const resultado = await api.upload<{ assinado: true; assinado_em: string }>(
        enviarUrl, "arquivo", arquivo,
      );
      onConcluido(resultado);
    } catch (e) {
      setErro(
        e instanceof ApiError
          ? e.message
          : "Não foi possível conferir o arquivo enviado.",
      );
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div
      className="cartao"
      style={{ marginTop: "0.6rem", background: "var(--fundo-destaque, #f6f8f7)", border: "1px solid var(--linha)" }}
    >
      <strong>Falta assinar — {nomeProvedor} funciona pelo Assinador ITI</strong>
      <p style={{ fontSize: "0.86rem", marginTop: "0.3rem" }}>
        A Corvia não assina nada por você: o PDF que acabou de baixar ainda{" "}
        <strong>não está assinado</strong>. O Assinador ITI (assinador.iti.br) é o
        serviço gratuito e público do governo federal para assinar qualquer PDF —
        a Corvia não tem acesso a ele por API, então os passos abaixo acontecem
        fora daqui.
      </p>

      <ol style={{ fontSize: "0.86rem", paddingLeft: "1.2rem", marginTop: "0.5rem" }}>
        <li>O PDF sem assinatura já foi baixado no seu dispositivo agora há pouco.</li>
        <li>
          Clique em <em>"Abrir Assinador ITI"</em> abaixo — abre em nova aba, sem
          fechar esta tela.
        </li>
        <li>No Assinador ITI, envie esse mesmo PDF que você acabou de baixar.</li>
        <li>
          Escolha assinar com {orientacao}. Certificado A1/A3 instalado no
          computador também funciona, qualquer que seja o método escolhido aqui.
        </li>
        <li>Ao final, baixe o PDF assinado que o Assinador ITI devolver.</li>
        <li>Volte a esta aba e envie esse arquivo assinado no campo abaixo.</li>
      </ol>

      <p style={{ fontSize: "0.8rem", color: "var(--texto-secundario)", marginTop: "0.4rem" }}>
        A Corvia confere de verdade que o arquivo devolvido tem uma assinatura
        digital real e íntegra embutida antes de aceitar — nunca marca como
        assinado só porque um arquivo qualquer voltou.
      </p>

      <button className="botao" style={{ marginTop: "0.6rem" }} onClick={abrirIti}>
        Abrir Assinador ITI (nova aba)
      </button>

      <div style={{ marginTop: "0.8rem", opacity: abriuIti ? 1 : 0.6 }}>
        <label>Enviar o PDF já assinado</label>
        <input
          type="file" accept="application/pdf"
          onChange={(e) => setArquivo(e.target.files?.[0] ?? null)}
        />
        <button
          className="botao" style={{ marginTop: "0.4rem" }}
          onClick={enviarAssinado} disabled={!arquivo || enviando}
        >
          {enviando ? "Conferindo assinatura…" : "Enviar PDF assinado"}
        </button>
      </div>

      {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem", marginTop: "0.4rem" }}>{erro}</p>}
    </div>
  );
}
