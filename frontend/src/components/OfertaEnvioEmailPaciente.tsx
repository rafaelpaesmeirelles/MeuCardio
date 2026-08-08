import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, ApiError } from "../lib/api";

/** Oferta de envio ao paciente por e-mail, pedido do Rafael em 08/08/2026:
 * ao concluir a assinatura digital de uma prescrição/documento, ou ao gerar
 * um item de Material ao Paciente, o assinante com CorvIA Mail ativo pode
 * mandar o arquivo ao paciente sem sair da tela — escolhendo entre o envio
 * automático (pela Corvia, `contato@corvia.med.br`) ou o envio pela própria
 * caixa do CorvIA Mail (compositor pré-preenchido com anexo real).
 *
 * `habilitado` decide SE o passo é oferecido (ex.: só depois da assinatura
 * concluída, ou — para material — assim que o material está pronto). Se o
 * assinante não tem CorvIA Mail ativo, o componente não renderiza nada —
 * mesmo comportamento de "a opção simplesmente não aparece" pedido no spec.
 *
 * `endpointBase` é o prefixo da rota já criada para o documento/material
 * específico (ex.: `/document-templates/gerados/42`, `/receituario/
 * documentos/17`, `/material-paciente/fibrilacao-atrial`) — este componente
 * só acrescenta `/envio-paciente`. */

type Canal = "auto_contato_corvia" | "proprio_corvia_mail";

type RespostaEnvio = {
  canal: Canal;
  enviado: boolean | null;
  erro: string | null;
  anexo: { file_id: string; nome: string } | null;
  assunto_sugerido: string | null;
  corpo_sugerido: string | null;
};

type ContaEmail = { ativa: boolean; status?: string };

type Props = {
  endpointBase: string;
  habilitado: boolean;
  /** Material ao Paciente exige nome do paciente e consentimento explícito
   * (mesma regra já usada em `/material-paciente/{slug}/enviar-email`);
   * documento/receita não. */
  variante?: "documento" | "material";
};

export const CHAVE_PENDING_COMPOSE = "corviamail.pendingCompose";

export default function OfertaEnvioEmailPaciente({ endpointBase, habilitado, variante = "documento" }: Props) {
  const navigate = useNavigate();
  const [corviaMailAtivo, setCorviaMailAtivo] = useState<boolean | null>(null);
  const [aberto, setAberto] = useState(false);
  const [canal, setCanal] = useState<Canal>("auto_contato_corvia");
  const [emailPaciente, setEmailPaciente] = useState("");
  const [nomePaciente, setNomePaciente] = useState("");
  const [recado, setRecado] = useState("");
  const [consentimento, setConsentimento] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState("");
  const [resultado, setResultado] = useState<RespostaEnvio | null>(null);

  useEffect(() => {
    if (!habilitado) return;
    api
      .get<ContaEmail>("/email/conta")
      .then((c) => setCorviaMailAtivo(Boolean(c.ativa && c.status === "ativa")))
      .catch(() => setCorviaMailAtivo(false));
  }, [habilitado]);

  if (!habilitado || !corviaMailAtivo) return null;

  const precisaConsentimento = variante === "material";
  const podeConfirmar =
    emailPaciente.trim().length > 3 &&
    (!precisaConsentimento || (nomePaciente.trim().length > 0 && consentimento));

  async function confirmar() {
    setEnviando(true);
    setErro("");
    try {
      const body: Record<string, unknown> = { email_paciente: emailPaciente.trim(), canal };
      if (precisaConsentimento) {
        body.nome_paciente = nomePaciente.trim();
        body.recado = recado.trim() || undefined;
        body.consentimento = consentimento;
      }
      const r = await api.post<RespostaEnvio>(`${endpointBase}/envio-paciente`, body);
      setResultado(r);
      if (r.canal === "proprio_corvia_mail" && r.anexo) {
        sessionStorage.setItem(
          CHAVE_PENDING_COMPOSE,
          JSON.stringify({
            para: emailPaciente.trim(),
            assunto: r.assunto_sugerido ?? "",
            corpo: r.corpo_sugerido ?? "",
            anexos: [r.anexo],
          }),
        );
        navigate("/caixa-de-email");
      }
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível concluir o envio.");
    } finally {
      setEnviando(false);
    }
  }

  if (!aberto) {
    return (
      <div className="cartao" style={{ marginTop: "0.8rem" }}>
        <p style={{ margin: 0 }}>Enviar ao paciente por e-mail agora, pelo CorvIA Mail?</p>
        <div style={{ display: "flex", gap: 8, marginTop: "0.5rem" }}>
          <button className="botao" onClick={() => setAberto(true)}>Sim, enviar</button>
        </div>
      </div>
    );
  }

  return (
    <div className="cartao" style={{ marginTop: "0.8rem" }}>
      <p className="eyebrow" style={{ marginTop: 0 }}>Enviar ao paciente por e-mail</p>

      <label style={{ display: "flex", gap: 8, alignItems: "flex-start", fontWeight: 400, marginBottom: "0.4rem" }}>
        <input
          type="radio" name="canal-envio-paciente" checked={canal === "auto_contato_corvia"}
          onChange={() => setCanal("auto_contato_corvia")} style={{ marginTop: 3 }}
        />
        <span>
          Enviar automaticamente pela Corvia (contato@corvia.med.br), com mensagem padrão
        </span>
      </label>
      <label style={{ display: "flex", gap: 8, alignItems: "flex-start", fontWeight: 400, marginBottom: "0.6rem" }}>
        <input
          type="radio" name="canal-envio-paciente" checked={canal === "proprio_corvia_mail"}
          onChange={() => setCanal("proprio_corvia_mail")} style={{ marginTop: 3 }}
        />
        <span>
          Enviar do meu próprio e-mail (abre o CorvIA Mail com o anexo já pronto, você escreve o e-mail)
        </span>
      </label>

      <label>E-mail do paciente</label>
      <input
        type="email" value={emailPaciente} onChange={(e) => setEmailPaciente(e.target.value)}
        placeholder="paciente@exemplo.com"
      />

      {precisaConsentimento && (
        <>
          <label style={{ marginTop: "0.5rem" }}>Nome do paciente</label>
          <input value={nomePaciente} onChange={(e) => setNomePaciente(e.target.value)} />
          <label style={{ marginTop: "0.5rem" }}>Recado (opcional)</label>
          <input value={recado} onChange={(e) => setRecado(e.target.value)} maxLength={500} />
          <label style={{ display: "flex", gap: 8, alignItems: "flex-start", fontWeight: 400, marginTop: "0.5rem" }}>
            <input
              type="checkbox" checked={consentimento}
              onChange={(e) => setConsentimento(e.target.checked)} style={{ marginTop: 3 }}
            />
            <span>O paciente autorizou receber este material por e-mail.</span>
          </label>
        </>
      )}

      {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erro}</p>}

      <div style={{ display: "flex", gap: 8, marginTop: "0.6rem" }}>
        <button className="botao" onClick={confirmar} disabled={enviando || !podeConfirmar}>
          {enviando ? "Enviando…" : canal === "auto_contato_corvia" ? "Enviar agora" : "Continuar no CorvIA Mail"}
        </button>
        <button className="botao botao--secundario" onClick={() => setAberto(false)} disabled={enviando}>
          Cancelar
        </button>
      </div>

      {resultado && resultado.canal === "auto_contato_corvia" && (
        resultado.enviado ? (
          <p style={{ color: "var(--sucesso)", fontSize: "0.86rem", marginTop: "0.5rem" }}>
            E-mail enviado ao paciente.
          </p>
        ) : (
          <p style={{ color: "var(--alerta)", fontSize: "0.86rem", marginTop: "0.5rem" }}>
            Não foi possível enviar agora{resultado.erro ? `: ${resultado.erro}` : "."}
          </p>
        )
      )}
    </div>
  );
}
