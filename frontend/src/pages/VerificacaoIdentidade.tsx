import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import { useAuth } from "../lib/auth";
import SelfieAoVivo from "../components/SelfieAoVivo";

/** Verificação de identidade obrigatória pós-pagamento (Trabalho 11/12,
 * 06/08/2026) — bloqueia o resto do site (`App.tsx`, `usuario.kyc_required`)
 * até o assinante enviar documento profissional, documento pessoal e
 * selfie ao vivo. Backend já decide sozinho se libera na hora (conselho
 * sem checagem automática disponível, ou CRM confirmado) ou se fica
 * esperando a revisão manual do Rafael — esta tela só reflete o que
 * `GET /api/kyc/status` diz, nunca decide por conta própria. */

type KycWaiverConfig = {
  professional_front: boolean;
  professional_back: boolean;
  personal_front: boolean;
  personal_back: boolean;
  personal_digital: boolean;
  selfie: boolean;
};

const SEM_DISPENSAS: KycWaiverConfig = {
  professional_front: false,
  professional_back: false,
  personal_front: false,
  personal_back: false,
  personal_digital: false,
  selfie: false,
};

type StatusKyc = {
  status: string | null;
  liberado: boolean;
  conselho_check_status?: string | null;
  criado_em?: string | null;
  nota_revisao?: string | null;
  waivers?: KycWaiverConfig;
  requirements?: KycWaiverConfig;
};

type TipoDocumentoPessoal = "fotos" | "digital";

const MENSAGEM_POR_STATUS: Record<string, { titulo: string; corpo: string; tom: "sucesso" | "info" | "alerta" }> = {
  aguardando_revisao: {
    titulo: "Documentos recebidos — em análise",
    tom: "info",
    corpo: "Não foi possível confirmar automaticamente seu registro profissional. " +
      "Um administrador vai revisar seus dados; assim que aprovado, o acesso libera sozinho.",
  },
  liberado_conselho_ok: {
    titulo: "Liberado — registro confirmado automaticamente",
    tom: "sucesso",
    corpo: "Seu registro no conselho foi confirmado. A revisão final dos documentos ainda vai " +
      "acontecer, mas você já pode usar a Corvia normalmente.",
  },
  liberado_sem_checagem: {
    titulo: "Liberado — aguardando confirmação manual",
    tom: "sucesso",
    corpo: "Não existe checagem automática disponível para o seu conselho, então liberamos seu " +
      "acesso direto. Um administrador vai validar pessoalmente os seus dados e documentos em breve.",
  },
  aprovado: {
    titulo: "Cadastro aprovado",
    tom: "sucesso",
    corpo: "Seus documentos foram revisados e aprovados definitivamente.",
  },
  rejeitado: {
    titulo: "Reenvio necessário",
    tom: "alerta",
    corpo: "Alguma informação ou documento não pôde ser confirmado. Reveja a nota abaixo e envie novamente.",
  },
  reenvio_solicitado: {
    titulo: "Complete os requisitos restantes",
    tom: "alerta",
    corpo: "A configuração de requisitos mudou ou um item precisa ser reenviado. Envie somente o que continua obrigatório.",
  },
};

/** Convidado nunca depende de revisão administrativa: uma submissão que
 * satisfaz todos os requisitos não dispensados termina automaticamente em
 * aprovado. Investidor não entra nesta tela, pois não participa do KYC. */
function mensagemPara(status: StatusKyc, ehAcessoAutomatico: boolean) {
  if (ehAcessoAutomatico) {
    if (status.status === "aprovado" || status.liberado) {
      return {
        titulo: "Identidade confirmada",
        tom: "sucesso" as const,
        corpo: "Identidade confirmada. Seu acesso ao CorVIA foi liberado automaticamente.",
      };
    }
    if (status.status === "rejeitado" || status.status === "reenvio_solicitado") {
      return MENSAGEM_POR_STATUS[status.status];
    }
    return {
      titulo: "Confirmando sua identidade",
      tom: "info" as const,
      corpo: "Estamos confirmando seus dados — isso é concluído automaticamente, sem espera.",
    };
  }
  return status.status ? MENSAGEM_POR_STATUS[status.status] ?? null : null;
}

function Cartao({ status, ehAcessoAutomatico, aoContinuar, aoReenviar }: {
  status: StatusKyc; ehAcessoAutomatico: boolean; aoContinuar: () => void; aoReenviar: () => void;
}) {
  const info = mensagemPara(status, ehAcessoAutomatico);
  if (!info) return null;
  const cor = info.tom === "sucesso" ? "var(--sucesso)" : info.tom === "alerta" ? "var(--alerta)" : "var(--texto)";

  return (
    <div className="cartao">
      <h1 style={{ fontSize: "1.2rem", margin: "0 0 0.4rem", color: cor }}>{info.titulo}</h1>
      <p style={{ margin: "0 0 0.8rem" }}>{info.corpo}</p>
      {(status.status === "rejeitado" || status.status === "reenvio_solicitado") && status.nota_revisao && (
        <p style={{
          background: "var(--fundo-alerta, #FBEAEA)", borderRadius: 6, padding: "0.6rem 0.8rem",
          fontSize: "0.88rem", margin: "0 0 0.8rem",
        }}>
          <strong>Motivo:</strong> {status.nota_revisao}
        </p>
      )}
      {status.liberado && (
        <button className="botao" style={{ width: "100%" }} onClick={aoContinuar}>
          {ehAcessoAutomatico ? "Entrar no CorVIA" : "Continuar"}
        </button>
      )}
      {(status.status === "rejeitado" || status.status === "reenvio_solicitado") && (
        <button className="botao" style={{ width: "100%" }} onClick={aoReenviar}>Enviar requisitos pendentes</button>
      )}
    </div>
  );
}

type TipoConta = "normal" | "convidado";

function Formulario({ tipoConta, waivers, aoEnviar }: {
  tipoConta: TipoConta; waivers: KycWaiverConfig; aoEnviar: () => void;
}) {
  const [tipoPessoal, setTipoPessoal] = useState<TipoDocumentoPessoal>("fotos");
  const [docProfFrente, setDocProfFrente] = useState<File | null>(null);
  const [docProfVerso, setDocProfVerso] = useState<File | null>(null);
  const [docPessoalFrente, setDocPessoalFrente] = useState<File | null>(null);
  const [docPessoalVerso, setDocPessoalVerso] = useState<File | null>(null);
  const [docPessoalDigital, setDocPessoalDigital] = useState<File | null>(null);
  const [selfie, setSelfie] = useState<File | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState("");

  const fotosPessoaisCompletas =
    (waivers.personal_front || !!docPessoalFrente) &&
    (waivers.personal_back || !!docPessoalVerso);
  const documentoDigitalCompleto = waivers.personal_digital || !!docPessoalDigital;
  const documentoPessoalCompleto = fotosPessoaisCompletas || documentoDigitalCompleto;
  const documentoProfissionalCompleto =
    (waivers.professional_front || !!docProfFrente) &&
    (waivers.professional_back || !!docProfVerso);
  const selfieCompleta = waivers.selfie || !!selfie;
  const pronto = documentoProfissionalCompleto && selfieCompleta && documentoPessoalCompleto;

  async function enviar() {
    setErro("");
    setEnviando(true);
    try {
      await api.uploadMultiplo("/kyc/submeter", {
        doc_profissional_frente: docProfFrente,
        doc_profissional_verso: docProfVerso,
        selfie,
        doc_pessoal_frente: tipoPessoal === "fotos" ? docPessoalFrente : null,
        doc_pessoal_verso: tipoPessoal === "fotos" ? docPessoalVerso : null,
        doc_pessoal_digital: tipoPessoal === "digital" ? docPessoalDigital : null,
      });
      aoEnviar();
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível enviar seus documentos agora.");
    } finally {
      setEnviando(false);
    }
  }

  const titulo = tipoConta === "convidado"
    ? "Confirme seus dados e sua identidade"
    : "Confirme sua identidade profissional";

  return (
    <div className="cartao">
      <h1 style={{ fontSize: "1.2rem", margin: "0 0 0.4rem" }}>{titulo}</h1>
      <p style={{ margin: "0 0 1rem", fontSize: "0.9rem" }}>
        Etapa obrigatória, exigida uma única vez, para proteger pacientes e colegas contra uso
        indevido de documentos assinados na plataforma. Seus arquivos ficam cifrados e são vistos
        só por quem administra a Corvia.
      </p>

      {!waivers.professional_front ? (
        <CampoArquivo
          rotulo="Documento profissional — frente"
          descricao="Carteira do conselho de classe, válida em todo o território nacional."
          valor={docProfFrente} onSelecionar={setDocProfFrente}
        />
      ) : <Dispensado rotulo="Documento profissional — frente" />}
      {!waivers.professional_back ? (
        <CampoArquivo rotulo="Documento profissional — verso" valor={docProfVerso} onSelecionar={setDocProfVerso} />
      ) : <Dispensado rotulo="Documento profissional — verso" />}

      <div style={{ marginTop: "1rem" }}>
        <label style={{ display: "block", marginBottom: "0.4rem" }}>Documento pessoal</label>
        <div style={{ display: "flex", gap: 6, marginBottom: "0.6rem" }}>
          <button type="button" className={tipoPessoal === "fotos" ? "botao" : "botao botao--secundario"}
                  style={{ flex: 1 }} onClick={() => setTipoPessoal("fotos")}>
            Foto (frente e verso)
          </button>
          <button type="button" className={tipoPessoal === "digital" ? "botao" : "botao botao--secundario"}
                  style={{ flex: 1 }} onClick={() => setTipoPessoal("digital")}>
            PDF digital (gov.br / CNH Digital)
          </button>
        </div>
        {tipoPessoal === "fotos" ? (
          <>
            {!waivers.personal_front
              ? <CampoArquivo rotulo="Frente" valor={docPessoalFrente} onSelecionar={setDocPessoalFrente} />
              : <Dispensado rotulo="Documento pessoal — frente" />}
            {!waivers.personal_back
              ? <CampoArquivo rotulo="Verso" valor={docPessoalVerso} onSelecionar={setDocPessoalVerso} />
              : <Dispensado rotulo="Documento pessoal — verso" />}
          </>
        ) : !waivers.personal_digital ? (
          <CampoArquivo
            rotulo="PDF do documento digital" aceitar="application/pdf"
            descricao="Baixado do app gov.br ou do app CNH Digital."
            valor={docPessoalDigital} onSelecionar={setDocPessoalDigital}
          />
        ) : <Dispensado rotulo="Documento pessoal digital (PDF)" />}
      </div>

      {!waivers.selfie
        ? <SelfieAoVivo arquivo={selfie} onCapturar={setSelfie} onLimpar={() => setSelfie(null)} />
        : <Dispensado rotulo="Selfie ao vivo" />}

      {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem", marginTop: "0.8rem" }}>{erro}</p>}

      <button className="botao" style={{ width: "100%", marginTop: "1.2rem" }}
              disabled={!pronto || enviando} onClick={enviar}>
        {enviando ? "Enviando…" : "Enviar para verificação"}
      </button>
    </div>
  );
}

function Dispensado({ rotulo }: { rotulo: string }) {
  return (
    <div style={{ marginTop: "0.6rem", padding: "0.55rem 0.7rem", border: "1px solid var(--borda)", borderRadius: 7 }}>
      <span className="selo selo--revisado">Dispensado pelo administrador</span>
      <span style={{ marginLeft: 7, fontSize: "0.86rem" }}>{rotulo}</span>
    </div>
  );
}

function CampoArquivo({ rotulo, descricao, aceitar = "image/jpeg,image/png,image/webp,application/pdf", valor, onSelecionar }: {
  rotulo: string; descricao?: string; aceitar?: string;
  valor: File | null; onSelecionar: (a: File | null) => void;
}) {
  return (
    <div style={{ marginTop: "0.6rem" }}>
      <label style={{ display: "block", marginBottom: "0.2rem", fontSize: "0.9rem" }}>{rotulo}</label>
      {descricao && <p className="eyebrow" style={{ margin: "0 0 0.3rem" }}>{descricao}</p>}
      <label className="botao botao--secundario" style={{ cursor: "pointer", display: "inline-block", marginBottom: 0 }}>
        {valor ? `✓ ${valor.name}` : "Escolher arquivo"}
        <input type="file" accept={aceitar} style={{ display: "none" }}
               onChange={(e) => onSelecionar(e.target.files?.[0] ?? null)} />
      </label>
    </div>
  );
}

export default function VerificacaoIdentidade() {
  const { usuario, recarregar: recarregarUsuario } = useAuth();
  const navigate = useNavigate();
  const [status, setStatus] = useState<StatusKyc | null>(null);
  const [carregando, setCarregando] = useState(true);
  const [mostrarFormulario, setMostrarFormulario] = useState(false);

  async function recarregarStatus() {
    setCarregando(true);
    try {
      const s = await api.get<StatusKyc>("/kyc/status");
      setStatus(s);
      setMostrarFormulario(!s.status || s.status === "rejeitado" || s.status === "reenvio_solicitado");
    } finally {
      setCarregando(false);
    }
  }

  useEffect(() => { recarregarStatus(); }, []);

  async function continuar() {
    // Servidor é quem manda de verdade: busca `/auth/me` de novo e
    // atualiza `usuario.kyc_required` no contexto, pra o gate do App.tsx
    // não bater de volta aqui na próxima navegação.
    recarregarUsuario();
    navigate("/corvia-mail");
  }

  if (carregando) return <p className="eyebrow">Carregando…</p>;

  // Investidor nunca participa do KYC; este ramo é apenas defesa contra
  // navegação manual para a rota enquanto a sessão de demonstração estiver ativa.
  if (usuario?.investidor) {
    return <p className="eyebrow">Modo Investidor não exige verificação de identidade.</p>;
  }
  const tipoConta: TipoConta = usuario?.convidado ? "convidado" : "normal";
  const ehAcessoAutomatico = tipoConta === "convidado";
  const waivers = status?.waivers ?? SEM_DISPENSAS;

  return (
    <div className="pagina" style={{ maxWidth: 560 }}>
      {status && !mostrarFormulario && (
        <div style={{ marginBottom: "1rem" }}>
          <Cartao
            status={status} ehAcessoAutomatico={ehAcessoAutomatico}
            aoContinuar={continuar} aoReenviar={() => setMostrarFormulario(true)}
          />
        </div>
      )}
      {mostrarFormulario && <Formulario tipoConta={tipoConta} waivers={waivers} aoEnviar={recarregarStatus} />}
      <p className="eyebrow" style={{ marginTop: "1rem" }}>
        Olá, {usuario?.full_name?.split(" ")[0]} — esta etapa se aplica a contas reais sujeitas ao KYC;
        requisitos individualmente dispensados pelo administrador não precisam ser enviados.
      </p>
    </div>
  );
}
