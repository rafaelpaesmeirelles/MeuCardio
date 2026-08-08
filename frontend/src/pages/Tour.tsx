import { useEffect, useState, type CSSProperties, type ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import Icone, { type NomeIcone } from "../components/Icone";
import { api, ApiError } from "../lib/api";
import { useAuth } from "../lib/auth";

/** Tour guiado do primeiro acesso (Trabalho 13, 06/08/2026 — reformulado por
 * completo em 08/08/2026, pedido do Rafael: o tour original era "simples
 * demais, sem graça", explicava pouco e não impressionava. Esta versão
 * substitui os cartões de texto puro por uma pequena renderização
 * interativa (mockup) de cada funcionalidade real, ao lado de um texto
 * curto que ensina O QUE a função faz e POR QUE importa clinicamente —
 * pensado para impressionar tanto quanto ensinar (inclusive um médico
 * convidado, amigo pessoal do Rafael).
 *
 * Mostrado uma única vez, depois do KYC e do passo do CorvIA Mail —
 * `App.tsx` força a rota enquanto `usuario.onboarding_pendente` for true; ao
 * fim (ou ao pular), `POST /auth/me/onboarding-concluido` fecha o gate.
 *
 * Cada slide cobre uma funcionalidade REAL, tirada do menu de
 * `Shell.tsx`/rotas de `App.tsx` — nada inventado. Os "mockups" são
 * recriações estilizadas em JSX/CSS puro (nunca HTML cru — ver
 * `scripts/check-rendering-security.mjs`), não screenshots reais. */

type Bloco = { rotulo: string; texto: string };
type Slide = {
  icone: NomeIcone;
  titulo: string;
  eyebrow: string;
  resumo: string;
  blocos: Bloco[];
  acento?: "navy" | "vermelho";
  Mockup: () => ReactNode;
};

/* ---------------------------------------------------------------------- */
/* Kit de mockup — primitivas pequenas, reaproveitadas por toda tela abaixo */
/* ---------------------------------------------------------------------- */

function Chrome({ titulo }: { titulo: string }) {
  return (
    <div className="tour-mock__chrome">
      <span className="tour-mock__ponto" />
      <span className="tour-mock__ponto" />
      <span className="tour-mock__ponto" />
      <span className="tour-mock__titulo">{titulo}</span>
    </div>
  );
}

function Linha({ largura, tom }: { largura: string; tom?: "clara" | "acento" }) {
  const classe = tom ? `mk-linha mk-linha--${tom}` : "mk-linha";
  return <span className={classe} style={{ width: largura }} />;
}

function Chip({ children, tom }: { children: ReactNode; tom: "verde" | "teal" | "vermelho" | "ambar" | "branco" }) {
  return <span className={`mk-chip mk-chip--${tom}`}>{children}</span>;
}

/* ---------------------------------------------------------------------- */
/* Mockups por funcionalidade                                             */
/* ---------------------------------------------------------------------- */

function MockAssistente() {
  return (
    <div className="tour-mock">
      <Chrome titulo="Assistente · Clínica" />
      <div className="tour-mock__corpo">
        <Chip tom="teal">🌐 Buscar na internet</Chip>
        <div className="mk-chat__bolha mk-chat__bolha--usuario">
          Corte de LDL na prevenção secundária, ESC 2024?
        </div>
        <div className="mk-chat__bolha mk-chat__bolha--ia">
          <Linha largura="96%" />
          <Linha largura="88%" />
          <Linha largura="60%" />
          <span style={{ fontSize: "0.7rem", color: "rgba(255,255,255,0.55)" }}>
            Meta &lt;55&nbsp;mg/dL em risco muito alto<span className="mk-chat__cursor" />
          </span>
          <div className="mk-chat__fontes">
            <Chip tom="teal">[F1] Biblioteca Corvia</Chip>
            <Chip tom="branco">[W2] Web</Chip>
          </div>
        </div>
      </div>
    </div>
  );
}

function MockBiblioteca() {
  return (
    <div className="tour-mock">
      <Chrome titulo="Biblioteca científica" />
      <div className="tour-mock__corpo">
        <div className="mk-busca">
          <Icone nome="busca" width={13} height={13} />
          diretriz insuficiência cardíaca
        </div>
        <div className="mk-cartao">
          <Linha largura="70%" tom="clara" />
          <div style={{ height: 6 }} />
          <div style={{ display: "flex", gap: 6, marginBottom: 6 }}>
            <Chip tom="verde">Classe I</Chip>
            <Chip tom="teal">Nível A</Chip>
          </div>
          <Linha largura="94%" />
          <div style={{ height: 5 }} />
          <Linha largura="82%" />
        </div>
        <div className="mk-cartao" style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <Icone nome="favorito" width={13} height={13} className="mk-favorito" />
          <Linha largura="60%" tom="clara" />
        </div>
      </div>
    </div>
  );
}

function MockCalculadora() {
  return (
    <div className="tour-mock">
      <Chrome titulo="CHA₂DS₂-VASc" />
      <div className="tour-mock__corpo">
        <div className="mk-calc">
          <div style={{ display: "grid", gap: 8 }}>
            <span className="mk-calc__linha"><span className="mk-check mk-check--on"><Icone nome="check" width={9} height={9} /></span>Insuficiência cardíaca</span>
            <span className="mk-calc__linha"><span className="mk-check mk-check--on"><Icone nome="check" width={9} height={9} /></span>Hipertensão</span>
            <span className="mk-calc__linha"><span className="mk-check" />Diabetes</span>
            <span className="mk-calc__linha"><span className="mk-check mk-check--on"><Icone nome="check" width={9} height={9} /></span>AVC prévio</span>
          </div>
          <div className="mk-gauge" style={{ "--valor": "70%" } as CSSProperties}>
            <span className="mk-gauge__valor">4</span>
          </div>
        </div>
        <Chip tom="vermelho">Alto risco — anticoagular</Chip>
      </div>
    </div>
  );
}

function MockFluxograma() {
  return (
    <div className="tour-mock">
      <Chrome titulo="Fluxograma · Síncope" />
      <div className="tour-mock__corpo" style={{ alignItems: "center" }}>
        <div className="mk-fluxo">
          <svg viewBox="0 0 220 150">
            <rect className="mk-fluxo__no" x="78" y="4" width="64" height="24" rx="5" />
            <text className="mk-fluxo__texto" x="110" y="19">Síncope</text>
            <path className="mk-fluxo__traco mk-fluxo__traco--vivo" d="M110 28 V44" />
            <polygon className="mk-fluxo__no mk-fluxo__no--decisao" points="110,44 150,66 110,88 70,66" />
            <text className="mk-fluxo__texto" x="110" y="69">Sinal de alarme?</text>
            <path className="mk-fluxo__traco mk-fluxo__traco--vivo" d="M70 66 H26 V108" />
            <path className="mk-fluxo__traco" d="M150 66 H194 V108" />
            <rect className="mk-fluxo__no mk-fluxo__no--conduta" x="2" y="108" width="48" height="26" rx="13" />
            <text className="mk-fluxo__texto" x="26" y="125">Internar</text>
            <rect className="mk-fluxo__no mk-fluxo__no--conduta" x="170" y="108" width="48" height="26" rx="13" />
            <text className="mk-fluxo__texto" x="194" y="125">Ambulatório</text>
          </svg>
        </div>
      </div>
    </div>
  );
}

function MockEmergencia() {
  const nomes = ["PCR", "IAM", "AVC", "Anafilaxia", "Choque", "Crise HAS"];
  return (
    <div className="tour-mock">
      <Chrome titulo="Modo Emergência" />
      <div className="tour-mock__corpo">
        <span className="mk-offline"><Icone nome="check" width={10} height={10} /> Funciona sem internet</span>
        <div className="mk-emergencia__grade">
          {nomes.map((n, i) => (
            <div key={n} className={`mk-emergencia__tile${i === 1 ? " mk-emergencia__tile--foco" : ""}`}>
              <Icone nome="emergencia" width={16} height={16} />
              {n}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function MockReceita() {
  return (
    <div className="tour-mock">
      <Chrome titulo="Prescrição eletrônica" />
      <div className="tour-mock__corpo">
        <div className="mk-doc">
          <div className="mk-doc__cabecalho">
            <span className="mk-doc__logo" />
            <div style={{ flex: 1, display: "grid", gap: 4 }}>
              <div className="mk-doc__linha" style={{ width: "58%" }} />
              <div className="mk-doc__linha" style={{ width: "38%", background: "var(--slate-100)" }} />
            </div>
          </div>
          <div className="mk-doc__linha" style={{ width: "92%" }} />
          <div className="mk-doc__linha" style={{ width: "70%" }} />
          <div className="mk-doc__linha" style={{ width: "84%" }} />
          <span className="mk-doc__selo"><Icone nome="check" width={10} height={10} /> Assinado ICP-Brasil</span>
        </div>
      </div>
    </div>
  );
}

function MockMail() {
  return (
    <div className="tour-mock">
      <Chrome titulo="CorvIA Mail" />
      <div className="tour-mock__corpo">
        <Chip tom="teal">voce@corvia.med.br</Chip>
        {[0, 1, 2].map((i) => (
          <div className="mk-mail__linha" key={i}>
            {i === 0 && <span className="mk-mail__bolinha" />}
            <Icone nome="mail" width={13} height={13} style={{ opacity: 0.6, flex: "0 0 auto" }} />
            <div className="mk-mail__conteudo">
              <Linha largura={i === 0 ? "70%" : "55%"} tom={i === 0 ? "clara" : undefined} />
              <Linha largura="40%" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function MockAgenda() {
  const eventos = new Set([9, 14, 20]);
  return (
    <div className="tour-mock">
      <Chrome titulo="Agenda · Round" />
      <div className="tour-mock__corpo">
        <div className="mk-agenda__grade">
          {Array.from({ length: 21 }).map((_, i) => (
            <span
              key={i}
              className={`mk-agenda__dia${i === 14 ? " mk-agenda__dia--hoje" : eventos.has(i) ? " mk-agenda__dia--evento" : ""}`}
            />
          ))}
        </div>
        <div className="mk-leito">
          <span className="mk-leito__num">204</span>
          <Linha largura="50%" tom="clara" />
          <Chip tom="ambar">Round hoje</Chip>
        </div>
      </div>
    </div>
  );
}

function MockTrilhas() {
  return (
    <div className="tour-mock">
      <Chrome titulo="Trilhas · Casos clínicos" />
      <div className="tour-mock__corpo">
        <div className="mk-trilha">
          <span className="mk-trilha__passo mk-trilha__passo--feito"><Icone nome="check" width={11} height={11} /></span>
          <span className="mk-trilha__linha mk-trilha__linha--feita" />
          <span className="mk-trilha__passo mk-trilha__passo--feito"><Icone nome="check" width={11} height={11} /></span>
          <span className="mk-trilha__linha mk-trilha__linha--feita" />
          <span className="mk-trilha__passo mk-trilha__passo--atual">3</span>
          <span className="mk-trilha__linha" />
          <span className="mk-trilha__passo">4</span>
        </div>
        <div className="mk-cartao">
          <Linha largura="90%" tom="clara" />
          <div style={{ height: 8 }} />
          <div style={{ display: "grid", gap: 6 }}>
            <Chip tom="branco">A. Betabloqueador</Chip>
            <Chip tom="teal">B. IECA/BRA</Chip>
          </div>
        </div>
      </div>
    </div>
  );
}

function MockGestao() {
  return (
    <div className="tour-mock">
      <Chrome titulo="Gestão da prática" />
      <div className="tour-mock__corpo">
        <div className="mk-gestao__provedores">
          <span className="mk-provedor" style={{ background: "#4285F4" }}>G</span>
          <span className="mk-provedor" style={{ background: "#00A4EF" }}>M</span>
          <span className="mk-provedor" style={{ background: "#555" }}>A</span>
          <span className="mk-provedor" style={{ background: "#7B0099" }}>Y</span>
        </div>
        <Chip tom="verde">4 contas sincronizadas</Chip>
        <div className="mk-barras">
          {[38, 62, 44, 80, 56, 70].map((h, i) => (
            <span key={i} className="mk-barra" style={{ height: `${h}%`, opacity: 0.55 + i * 0.07 }} />
          ))}
        </div>
      </div>
    </div>
  );
}

/* ---------------------------------------------------------------------- */
/* Conteúdo dos slides — funcionalidades reais (Shell.tsx / App.tsx)      */
/* ---------------------------------------------------------------------- */

const SLIDES: Slide[] = [
  {
    icone: "assistente",
    eyebrow: "Decisão clínica",
    titulo: "Assistente de IA clínica",
    resumo: "Pergunte em linguagem natural — com fonte, não achismo.",
    blocos: [
      { rotulo: "O que é", texto: "Converse com o assistente: ele busca primeiro na base científica própria da Corvia e complementa com a internet quando precisa de algo mais recente." },
      { rotulo: "Por que importa", texto: "Cada resposta cita a fonte — você confere antes de decidir, em vez de receber uma resposta genérica sem rastro." },
      { rotulo: "No seu dia a dia", texto: "Aquela dúvida entre um paciente e outro se resolve conversando, sem montar uma busca formal." },
    ],
    Mockup: MockAssistente,
  },
  {
    icone: "conhecimento",
    eyebrow: "Conhecimento",
    titulo: "Biblioteca científica",
    resumo: "Toda a cardiologia organizada, sempre com classe e nível de evidência.",
    blocos: [
      { rotulo: "O que é", texto: "Doença, diretriz, evidência, estudo, exame ou achado de imagem — tudo com uma busca só, e favoritos para achar de novo em um clique." },
      { rotulo: "Por que importa", texto: "Você chega direto na recomendação com classe e nível, sem abrir três guias em outra aba para confirmar a fonte." },
      { rotulo: "No seu dia a dia", texto: "\"Qual o corte de LDL nessa diretriz mesmo?\" — resolve em segundos, sem sair do fluxo da consulta." },
    ],
    Mockup: MockBiblioteca,
  },
  {
    icone: "calculadora",
    eyebrow: "Decisão clínica",
    titulo: "Calculadoras e escores",
    resumo: "Escore validado, com interpretação e conduta prontas.",
    blocos: [
      { rotulo: "O que é", texto: "CHA₂DS₂-VASc, HAS-BLED, GRACE e outras — cada uma já vem com a interpretação e a conduta associada, não só o número." },
      { rotulo: "Por que importa", texto: "Reduz o cálculo mental e a consulta cruzada de bula na hora de decidir anticoagular, escalonar ou ajustar dose." },
      { rotulo: "No seu dia a dia", texto: "Na beira do leito, um escore vira uma decisão de 30 segundos, não uma conta de cabeça sob pressão." },
    ],
    Mockup: MockCalculadora,
  },
  {
    icone: "seta",
    eyebrow: "Decisão clínica",
    titulo: "Fluxogramas de decisão",
    resumo: "Árvore de decisão clínica, passo a passo, sem ambiguidade.",
    blocos: [
      { rotulo: "O que é", texto: "Cada fluxograma é uma árvore estrita — um caminho por resposta, terminando sempre numa conduta clara." },
      { rotulo: "Por que importa", texto: "Nada de grafo confuso com setas se cruzando: cada decisão tem só os ramos que importam para ela." },
      { rotulo: "No seu dia a dia", texto: "Diante de um quadro atípico, você segue o fluxo em vez de reconstruir o raciocínio da diretriz de memória." },
    ],
    Mockup: MockFluxograma,
  },
  {
    icone: "emergencia",
    eyebrow: "Modo Emergência",
    titulo: "Modo Emergência",
    resumo: "31 protocolos com conduta imediata — funciona sem internet.",
    blocos: [
      { rotulo: "O que é", texto: "Ao abrir uma vez, o pacote inteiro (protocolos, documentos, fluxogramas) fica salvo no aparelho." },
      { rotulo: "Por que importa", texto: "Numa parada ou numa emergência hipertensiva, o fluxograma de conduta aparece pronto, sem depender de sinal." },
      { rotulo: "No seu dia a dia", texto: "Corredor sem sinal, plantão de UPA, sala de emergência — é exatamente a situação para a qual esta tela foi feita." },
    ],
    acento: "vermelho",
    Mockup: MockEmergencia,
  },
  {
    icone: "prescricao",
    eyebrow: "Pacientes e prática",
    titulo: "Prescrição digital com assinatura",
    resumo: "Receita e documento já saem assinados digitalmente.",
    blocos: [
      { rotulo: "O que é", texto: "Monte a receita pela base de medicamentos (com preço regulado da CMED) ou gere atestado e laudo — e assine com certificado digital." },
      { rotulo: "Por que importa", texto: "O documento sai pronto para o paciente, com validade jurídica de assinatura digital, sem imprimir e escanear." },
      { rotulo: "No seu dia a dia", texto: "Reaproveite a receita de um retorno: os itens já vêm preenchidos, você só ajusta o que mudou." },
    ],
    Mockup: MockReceita,
  },
  {
    icone: "mail",
    eyebrow: "Comunicação",
    titulo: "CorvIA Mail",
    resumo: "Seu e-mail profissional, dentro da própria Corvia.",
    blocos: [
      { rotulo: "O que é", texto: "Endereço próprio @corvia.med.br, ou leia Yahoo, iCloud, Gmail e Outlook na mesma caixa, sem trocar de aplicativo." },
      { rotulo: "Por que importa", texto: "Envie documento e receita já assinados direto ao paciente, com sua assinatura profissional em toda mensagem." },
      { rotulo: "No seu dia a dia", texto: "Manda o resultado de um exame por e-mail sem sair da tela onde você já está trabalhando." },
    ],
    Mockup: MockMail,
  },
  {
    icone: "agenda",
    eyebrow: "Pacientes e prática",
    titulo: "Agenda e round hospitalar",
    resumo: "Agenda, internados e checklist de alta, no mesmo lugar.",
    blocos: [
      { rotulo: "O que é", texto: "Agenda com sincronização de calendário externo, round hospitalar para acompanhar internados e checklist de alta." },
      { rotulo: "Por que importa", texto: "O que hoje está em três apps diferentes (agenda, planilha de round, checklist em papel) fica num só lugar." },
      { rotulo: "No seu dia a dia", texto: "Confere os internados do dia e a agenda do consultório na mesma tela, antes de sair de casa." },
    ],
    Mockup: MockAgenda,
  },
  {
    icone: "curso",
    eyebrow: "Conhecimento",
    titulo: "Trilhas de estudo e casos clínicos",
    resumo: "Estudo estruturado, não disperso.",
    blocos: [
      { rotulo: "O que é", texto: "Trilhas de estudo por tema, casos clínicos interativos com pergunta e resposta, e cursos de parceiros para o Título de Especialista." },
      { rotulo: "Por que importa", texto: "Cada trilha já organiza a sequência de leitura por relevância clínica — nada de garimpar por conta própria." },
      { rotulo: "No seu dia a dia", texto: "Um caso clínico de 5 minutos no intervalo entre consultas mantém o estudo em dia." },
    ],
    Mockup: MockTrilhas,
  },
  {
    icone: "gestao",
    eyebrow: "Gestão",
    titulo: "Sua prática, organizada",
    resumo: "Contas sincronizadas, indicadores e favoritos, sempre à mão.",
    blocos: [
      { rotulo: "O que é", texto: "Sincronize quantas contas quiser (Google, Microsoft, Apple, Yahoo), acompanhe seus próprios indicadores e guarde favoritos." },
      { rotulo: "Por que importa", texto: "Agenda e e-mail de várias contas numa visão só, sem escolher qual aplicativo abrir a cada momento." },
      { rotulo: "No seu dia a dia", texto: "Tudo o que você usa com frequência fica a um clique — sem procurar de novo toda vez." },
    ],
    Mockup: MockGestao,
  },
];

/* ---------------------------------------------------------------------- */
/* Boas-vindas — avatar do Instagram (se informado) com fallback gracioso */
/* ---------------------------------------------------------------------- */

function iniciais(nome?: string | null): string {
  if (!nome) return "C";
  const partes = nome.trim().split(/\s+/);
  const primeiro = partes[0]?.[0] ?? "";
  const ultimo = partes.length > 1 ? partes[partes.length - 1][0] : "";
  return (primeiro + ultimo).toUpperCase() || "C";
}

function AvatarBoasVindas({ fotoUrl, nome }: { fotoUrl: string | null | undefined; nome?: string | null }) {
  const [falhou, setFalhou] = useState(false);
  const mostrarFoto = !!fotoUrl && !falhou;
  return (
    <div className="tour-boasvindas__avatar-wrap">
      <div className="tour-boasvindas__avatar">
        {mostrarFoto ? (
          // eslint-disable-next-line jsx-a11y/alt-text
          <img
            src={fotoUrl ?? undefined}
            alt={`Foto de perfil de ${nome ?? "usuário"}`}
            className="tour-boasvindas__avatar-img"
            onError={() => setFalhou(true)}
          />
        ) : (
          <div className="tour-boasvindas__avatar-fallback" aria-hidden="true">
            {iniciais(nome)}
          </div>
        )}
        <span className="tour-boasvindas__selo" title="Corvia">
          <Icone nome="favorito" width={14} height={14} />
        </span>
      </div>
    </div>
  );
}

export default function Tour() {
  const { usuario, recarregar } = useAuth();
  const navigate = useNavigate();
  const [passo, setPasso] = useState(0);
  const [concluindo, setConcluindo] = useState(false);

  const total = SLIDES.length + 2; // boas-vindas + funcionalidades + final
  const ehBoasVindas = passo === 0;
  const ehFinal = passo === total - 1;
  const slideAtual = !ehBoasVindas && !ehFinal ? SLIDES[passo - 1] : null;

  useEffect(() => {
    function aoTeclar(e: KeyboardEvent) {
      if (e.key === "ArrowRight") avancar();
      if (e.key === "ArrowLeft") voltar();
    }
    window.addEventListener("keydown", aoTeclar);
    return () => window.removeEventListener("keydown", aoTeclar);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [passo]);

  function avancar() {
    setPasso((p) => Math.min(p + 1, total - 1));
  }
  function voltar() {
    setPasso((p) => Math.max(p - 1, 0));
  }

  async function concluir() {
    setConcluindo(true);
    try {
      await api.post("/auth/me/onboarding-concluido", {});
    } catch (e) {
      // Mesmo se a chamada falhar, não trava o médico fora do site — só
      // engole o erro; ele pode ver o tour de novo, mas não fica preso.
      if (!(e instanceof ApiError)) throw e;
    } finally {
      recarregar();
      navigate("/");
    }
  }

  return (
    <div className="tour">
      <div className="tour__topo">
        <img src="/corvia-logo-compacta.png" alt="Corvia" className="tour__logo" />
        {!ehFinal && (
          <button className="tour__pular" onClick={concluir} disabled={concluindo}>
            Pular tour
          </button>
        )}
      </div>

      <div className="tour__progresso" role="progressbar" aria-valuenow={passo + 1} aria-valuemax={total}>
        {Array.from({ length: total }).map((_, i) => (
          <button
            key={i}
            type="button"
            className={`tour__ponto${i <= passo ? " tour__ponto--feito" : ""}${i === passo ? " tour__ponto--atual" : ""}`}
            aria-label={`Ir para o passo ${i + 1} de ${total}`}
            onClick={() => setPasso(i)}
          />
        ))}
      </div>

      <div className="tour__corpo">
        <div className="tour__slide" key={passo}>
          {ehBoasVindas && (
            <div className="tour__cartao tour__cartao--central">
              <p className="tour-boasvindas__eyebrow">Ecossistema Corvia</p>
              <AvatarBoasVindas fotoUrl={usuario?.instagram_photo_url} nome={usuario?.full_name} />
              <h1>Bem-vindo ao Ecossistema Corvia, {usuario?.full_name?.split(" ")[0]}.</h1>
              <p className="tour__resumo">
                Antes de começar, um giro rápido pelo que a plataforma oferece — leva menos de
                dois minutos, e você pode pular a qualquer momento.
              </p>
              <svg className="tour-boasvindas__pulso" viewBox="0 0 420 44" aria-hidden="true">
                <path d="M0 22 H140 L158 6 L176 38 L194 14 L208 30 L222 22 H420" />
              </svg>
            </div>
          )}

          {slideAtual && (
            <div className={`tour__cartao tour__cartao--feature`}>
              <div className={`tour-mock-lado${slideAtual.acento === "vermelho" ? " tour-mock-lado--vermelho" : ""}`}>
                <slideAtual.Mockup />
              </div>
              <div className="tour-texto-lado">
                <div className="tour-texto-lado__topo">
                  <span className="tour-texto-lado__icone"><Icone nome={slideAtual.icone} width={22} height={22} /></span>
                  <span className="tour-texto-lado__contador">{slideAtual.eyebrow} · {passo} de {SLIDES.length}</span>
                </div>
                <h2>{slideAtual.titulo}</h2>
                <p className="tour-texto-lado__resumo">{slideAtual.resumo}</p>
                <div className="tour-texto-lado__blocos">
                  {slideAtual.blocos.map((b, i) => (
                    <div className={`tour-texto-lado__bloco${i === 1 ? " tour-texto-lado__bloco--destaque" : ""}`} key={b.rotulo}>
                      <p className="tour-texto-lado__rotulo">{b.rotulo}</p>
                      <p className="tour-texto-lado__texto">{b.texto}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {ehFinal && (
            <div className="tour__cartao tour__cartao--central">
              <p className="tour-boasvindas__eyebrow">Tudo pronto</p>
              <h1>Pronto para começar.</h1>
              <p className="tour__resumo">
                Você já conhece o essencial. O resto você descobre usando — e pode voltar a
                qualquer uma dessas telas pelo menu, quando quiser.
              </p>
              <div className="tour-final__grade">
                {SLIDES.map((s) => (
                  <span className="tour-final__item" key={s.titulo}>
                    <Icone nome={s.icone} width={17} height={17} />
                    {s.titulo}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="tour__nav">
        <button className="botao botao--secundario" onClick={voltar} disabled={ehBoasVindas}>
          Voltar
        </button>
        {ehFinal ? (
          <button className="botao" onClick={concluir} disabled={concluindo}>
            {concluindo ? "Entrando…" : "Começar a usar a Corvia"}
          </button>
        ) : (
          <button className="botao" onClick={avancar}>Próximo</button>
        )}
      </div>
    </div>
  );
}
