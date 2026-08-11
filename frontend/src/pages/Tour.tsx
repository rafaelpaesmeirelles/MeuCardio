import { useCallback, useEffect, useState, type CSSProperties, type ReactNode } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import GrafoConstelacao from "../components/GrafoConstelacao";
import Icone, { type NomeIcone } from "../components/Icone";
import { api, ApiError } from "../lib/api";
import { useAuth } from "../lib/auth";

/** Tour guiado (Trabalho 13, 06/08/2026 — reformulado em 08/08/2026 e
 * reorganizado em dois níveis na issue #52).
 *
 * O mérito da versão anterior foi preservado: cada funcionalidade aparece
 * como uma pequena renderização (mockup) em JSX/CSS puro, não como cartão de
 * texto. O que mudou foi o VOLUME — onboarding de primeiro acesso não pode
 * ser uma apresentação comercial de dez telas.
 *
 * Dois modos, um componente só:
 *
 * - **Quick Start** (`modo="quick"`): o que o médico vê no primeiro acesso.
 *   Cinco funcionalidades, menos de dois minutos. `App.tsx` força a rota
 *   enquanto `usuario.onboarding_pendente` for true; ao concluir ou pular,
 *   `POST /auth/me/onboarding-concluido` fecha o gate.
 * - **Tour completo** (`modo="completo"`): o passeio longo, agora OPCIONAL.
 *   Aberto depois pelo menu (Gestão › Conheça a plataforma → `/tour`) ou
 *   pelo botão do fim do Quick Start. Quando o onboarding já foi concluído,
 *   a visita é voluntária e não chama a rota de conclusão — só volta.
 *
 * O terceiro nível do onboarding (dicas contextuais na primeira visita a
 * cada área) vive em `components/DicaContextual.tsx`, fora daqui.
 *
 * Cada slide cobre uma funcionalidade REAL, conferida contra as rotas de
 * `App.tsx` e o menu de `Shell.tsx` — nada inventado, nenhum número
 * decorado que o produto não sustente. */

type Modo = "quick" | "completo";
type Bloco = { rotulo: string; texto: string };
type Slide = {
  id: string;
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

/** Grafo de conhecimento — o momento em que o tour ensina a mudança de
 * paradigma. Reaproveita o mesmo componente da vitrine do login, para que a
 * primeira imagem que o médico viu do produto seja também a que explica
 * como ele funciona. */
function MockGrafo() {
  return (
    <div className="tour-mock tour-mock--grafo">
      <Chrome titulo="Grafo de Conhecimento Clínico" />
      <div className="tour-mock__corpo">
        <GrafoConstelacao variante="escuro" />
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
          <span className="mk-doc__selo"><Icone nome="check" width={10} height={10} /> Pronto para assinar</span>
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
    id: "assistente",
    icone: "assistente",
    eyebrow: "Decisão clínica",
    titulo: "Assistente e busca clínica",
    resumo: "Pergunte em linguagem natural — com fonte, não achismo.",
    blocos: [
      { rotulo: "O que é", texto: "Converse com o assistente: ele busca primeiro na base científica da própria Corvia e complementa com a internet quando a pergunta pede algo mais recente." },
      { rotulo: "Por que importa", texto: "Cada resposta cita a fonte que usou — você confere antes de decidir, em vez de receber um texto genérico sem rastro." },
      { rotulo: "No seu dia a dia", texto: "A dúvida entre um paciente e outro se resolve conversando, sem montar uma busca formal." },
    ],
    Mockup: MockAssistente,
  },
  {
    id: "grafo",
    icone: "rota",
    eyebrow: "O jeito Corvia",
    titulo: "Tudo na Corvia está conectado",
    resumo: "De um medicamento até a conduta, sem perder o contexto.",
    blocos: [
      { rotulo: "O que é", texto: "Abra um medicamento e encontre ali a doença, a evidência, o estudo, o exame, o caso clínico e a trilha ligados a ele — e siga em qualquer direção a partir de qualquer um deles." },
      { rotulo: "Por que importa", texto: "A Corvia não é um punhado de módulos separados: é um grafo de conhecimento clínico. Você navega pelas relações reais entre os itens, não por menus." },
      { rotulo: "No seu dia a dia", texto: "Chegou pela dose, saiu com a evidência que a sustenta e o caso clínico que a treina — na mesma página." },
    ],
    Mockup: MockGrafo,
  },
  {
    id: "agenda",
    icone: "agenda",
    eyebrow: "Pacientes e prática",
    titulo: "Agenda e round hospitalar",
    resumo: "Agenda, internados e checklist de alta, no mesmo lugar.",
    blocos: [
      { rotulo: "O que é", texto: "Agenda com sincronização de calendário externo (Google, Microsoft, Apple, Yahoo), round hospitalar para acompanhar internados e checklist de alta." },
      { rotulo: "Por que importa", texto: "O que hoje está em três lugares diferentes — agenda, planilha de round, checklist em papel — passa a ficar num só." },
      { rotulo: "No seu dia a dia", texto: "Confere os internados do dia e a agenda do consultório na mesma tela, antes de sair de casa." },
    ],
    Mockup: MockAgenda,
  },
  {
    id: "prescricao",
    icone: "prescricao",
    eyebrow: "Pacientes e prática",
    titulo: "Prescrição e documentos",
    resumo: "Receita, atestado e laudo prontos para assinar.",
    blocos: [
      { rotulo: "O que é", texto: "Monte a receita pela base de medicamentos, com preço regulado da CMED, ou gere atestado, laudo e avaliação pré-operatória a partir de modelos." },
      { rotulo: "Por que importa", texto: "O documento sai com a sua identificação profissional e segue para assinatura digital com o seu certificado, sem imprimir e escanear." },
      { rotulo: "No seu dia a dia", texto: "No retorno, reaproveite a receita anterior: os itens já vêm preenchidos e você ajusta só o que mudou." },
    ],
    Mockup: MockReceita,
  },
  {
    id: "mail",
    icone: "mail",
    eyebrow: "Comunicação",
    titulo: "CorvIA Mail",
    resumo: "Seu e-mail profissional, dentro da própria Corvia.",
    blocos: [
      { rotulo: "O que é", texto: "Endereço próprio @corvia.med.br — ou leia as contas que você já usa (Gmail, Outlook, Yahoo, iCloud) na mesma caixa, sem trocar de aplicativo." },
      { rotulo: "Por que importa", texto: "Envie documento e material ao paciente a partir da tela onde você já está, com a sua assinatura profissional em toda mensagem." },
      { rotulo: "No seu dia a dia", texto: "Responde o paciente sem abrir outro aplicativo nem perder o contexto da consulta." },
    ],
    Mockup: MockMail,
  },
  {
    id: "biblioteca",
    icone: "conhecimento",
    eyebrow: "Conhecimento",
    titulo: "Biblioteca científica",
    resumo: "A cardiologia organizada, com classe e nível de evidência.",
    blocos: [
      { rotulo: "O que é", texto: "Doença, diretriz, evidência, estudo, exame ou achado de imagem — tudo por uma busca só, com favoritos para reencontrar em um clique." },
      { rotulo: "Por que importa", texto: "Você chega direto na recomendação, com classe e nível à vista, sem abrir três abas para confirmar a fonte." },
      { rotulo: "No seu dia a dia", texto: "\"Qual era o corte de LDL nessa diretriz?\" — resolve em segundos, sem sair do fluxo da consulta." },
    ],
    Mockup: MockBiblioteca,
  },
  {
    id: "calculadoras",
    icone: "calculadora",
    eyebrow: "Decisão clínica",
    titulo: "Calculadoras e escores",
    resumo: "Escore validado, com interpretação e conduta junto.",
    blocos: [
      { rotulo: "O que é", texto: "CHA₂DS₂-VASc, HAS-BLED, GRACE, escores de risco cirúrgico e calculadoras de dose — cada uma com a interpretação ao lado do número." },
      { rotulo: "Por que importa", texto: "Menos conta de cabeça e menos consulta cruzada de bula na hora de anticoagular, escalonar ou ajustar dose." },
      { rotulo: "No seu dia a dia", texto: "Na beira do leito, um escore vira decisão de trinta segundos — e vira laudo, se você quiser registrar." },
    ],
    Mockup: MockCalculadora,
  },
  {
    id: "fluxogramas",
    icone: "seta",
    eyebrow: "Decisão clínica",
    titulo: "Fluxogramas de decisão",
    resumo: "Árvore de decisão clínica, passo a passo, sem ambiguidade.",
    blocos: [
      { rotulo: "O que é", texto: "Cada fluxograma é uma árvore estrita — um caminho por resposta, terminando sempre numa conduta clara." },
      { rotulo: "Por que importa", texto: "Nada de grafo confuso com setas se cruzando: cada decisão mostra só os ramos que importam para ela." },
      { rotulo: "No seu dia a dia", texto: "Diante de um quadro atípico, você segue o fluxo em vez de reconstruir a diretriz de memória." },
    ],
    Mockup: MockFluxograma,
  },
  {
    id: "emergencia",
    icone: "emergencia",
    eyebrow: "Modo Emergência",
    titulo: "Modo Emergência",
    resumo: "Protocolos com conduta imediata — funciona sem internet.",
    blocos: [
      { rotulo: "O que é", texto: "Ao abrir uma vez, o pacote inteiro — protocolos, documentos e fluxogramas de conduta — fica salvo no aparelho." },
      { rotulo: "Por que importa", texto: "Numa parada ou numa emergência hipertensiva, a conduta aparece pronta, sem depender de sinal." },
      { rotulo: "No seu dia a dia", texto: "Corredor sem sinal, plantão de UPA, sala de emergência — é exatamente a situação para a qual esta tela foi feita." },
    ],
    acento: "vermelho",
    Mockup: MockEmergencia,
  },
  {
    id: "trilhas",
    icone: "curso",
    eyebrow: "Conhecimento",
    titulo: "Trilhas de estudo e casos clínicos",
    resumo: "Estudo estruturado, não disperso.",
    blocos: [
      { rotulo: "O que é", texto: "Trilhas por tema, com a sequência de leitura já organizada, e casos clínicos interativos com pergunta e resposta comentada." },
      { rotulo: "Por que importa", texto: "A trilha ordena o que ler por relevância clínica — você não precisa garimpar por conta própria." },
      { rotulo: "No seu dia a dia", texto: "Um caso clínico de cinco minutos no intervalo entre consultas mantém o estudo em dia." },
    ],
    Mockup: MockTrilhas,
  },
  {
    id: "gestao",
    icone: "gestao",
    eyebrow: "Gestão",
    titulo: "Sua prática, organizada",
    resumo: "Contas sincronizadas, indicadores e favoritos à mão.",
    blocos: [
      { rotulo: "O que é", texto: "Sincronize quantas contas quiser (Google, Microsoft, Apple, Yahoo), acompanhe seus indicadores de uso e guarde favoritos." },
      { rotulo: "Por que importa", texto: "Agenda e e-mail de várias contas numa visão só, sem decidir qual aplicativo abrir a cada momento." },
      { rotulo: "No seu dia a dia", texto: "O que você usa com frequência fica a um clique, sem procurar de novo toda vez." },
    ],
    Mockup: MockGestao,
  },
];

/** Quick Start — as cinco funcionalidades do primeiro acesso, na ordem em
 * que fazem sentido para quem nunca abriu o produto: entender como se
 * pergunta, entender que tudo é conectado, e então as três frentes de
 * rotina (agenda, prescrição, e-mail). */
const QUICK_START = ["assistente", "grafo", "agenda", "prescricao", "mail"];

function slidesDoModo(modo: Modo): Slide[] {
  if (modo === "completo") return SLIDES;
  const ordem = new Map(QUICK_START.map((id, i) => [id, i]));
  return SLIDES.filter((s) => ordem.has(s.id)).sort(
    (a, b) => (ordem.get(a.id) ?? 0) - (ordem.get(b.id) ?? 0),
  );
}

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
  const { usuario } = useAuth();
  const navigate = useNavigate();
  const [params] = useSearchParams();

  // Primeiro acesso (gate de `App.tsx`) → Quick Start. Visita voluntária,
  // com o onboarding já concluído → tour completo. `?modo=` permite linkar
  // qualquer um dos dois diretamente.
  const pendente = Boolean(usuario?.onboarding_pendente);
  const modoDaUrl = params.get("modo");
  const [modo, setModo] = useState<Modo>(
    modoDaUrl === "completo" || modoDaUrl === "quick"
      ? modoDaUrl
      : pendente
        ? "quick"
        : "completo",
  );
  const [passo, setPasso] = useState(0);
  const [concluindo, setConcluindo] = useState(false);

  const slides = slidesDoModo(modo);
  const total = slides.length + 2; // boas-vindas + funcionalidades + final
  const ehBoasVindas = passo === 0;
  const ehFinal = passo === total - 1;
  const slideAtual = !ehBoasVindas && !ehFinal ? slides[passo - 1] : null;

  const avancar = useCallback(() => {
    setPasso((p) => Math.min(p + 1, total - 1));
  }, [total]);
  const voltar = useCallback(() => {
    setPasso((p) => Math.max(p - 1, 0));
  }, []);

  useEffect(() => {
    function aoTeclar(e: KeyboardEvent) {
      // Não sequestra as setas quando o foco está num controle que já as
      // usa (navegação por teclado nos pontos de progresso, por exemplo).
      const alvo = e.target as HTMLElement | null;
      if (alvo && /^(INPUT|TEXTAREA|SELECT)$/.test(alvo.tagName)) return;
      if (e.key === "ArrowRight") avancar();
      if (e.key === "ArrowLeft") voltar();
    }
    window.addEventListener("keydown", aoTeclar);
    return () => window.removeEventListener("keydown", aoTeclar);
  }, [avancar, voltar]);

  /** Troca para o passeio longo sem sair da página nem fechar o gate. */
  function verTourCompleto() {
    setModo("completo");
    setPasso(1);
  }

  async function concluir() {
    // Visita voluntária (onboarding já concluído): só volta, sem tocar no
    // estado do usuário.
    if (!pendente) {
      navigate("/");
      return;
    }
    setConcluindo(true);
    try {
      await api.post("/auth/me/onboarding-concluido", {});
    } catch (e) {
      // Mesmo se a chamada falhar, não trava o médico fora do site — só
      // engole o erro; ele pode ver o tour de novo, mas não fica preso.
      if (!(e instanceof ApiError)) throw e;
    } finally {
      // Navegação completa do navegador, não troca de rota do React Router.
      //
      // 🐛 Bug real, reproduzido de ponta a ponta nesta subfase (issue #52) e
      // presente desde a versão anterior do tour: `recarregar()` dispara um
      // GET /auth/me e NÃO é aguardado, então o `navigate("/")` seguinte
      // chegava ao gate de `App.tsx` com o usuário ainda em memória —
      // `onboarding_pendente` continuava `true` e o gate devolvia o médico
      // para `/tour`. Resultado: ao clicar em "Começar a usar a Corvia" (ou
      // em "Pular") a tela do tour simplesmente não saía do lugar, e só a
      // navegação manual destravava.
      //
      // Recarregar de verdade garante um `/auth/me` novo antes de o gate
      // rodar. É o mesmo padrão que o login já usa em `lib/auth.tsx`, e o
      // custo de um recarregamento é aceitável num momento que já é de
      // transição de tela — acontece uma única vez por assinante.
      window.location.replace("/");
    }
  }

  const rotuloSair = pendente ? "Pular" : "Fechar";

  return (
    <div className="tour">
      <div className="tour__topo">
        <img src="/corvia-logo-compacta.png" alt="Corvia" className="tour__logo" />
        <button className="tour__pular" onClick={concluir} disabled={concluindo}>
          {ehFinal ? "Fechar" : rotuloSair}
        </button>
      </div>

      <div className="tour__progresso">
        <p className="tour__contador" aria-live="polite">
          {modo === "quick" ? "Início rápido" : "Tour completo"} · Passo {passo + 1} de {total}
        </p>
        <div
          className="tour__pontos"
          role="progressbar"
          aria-label="Progresso do tour"
          aria-valuenow={passo + 1}
          aria-valuemin={1}
          aria-valuemax={total}
          aria-valuetext={`Passo ${passo + 1} de ${total}`}
        >
          {Array.from({ length: total }).map((_, i) => (
            <button
              key={i}
              type="button"
              className={`tour__ponto${i <= passo ? " tour__ponto--feito" : ""}${i === passo ? " tour__ponto--atual" : ""}`}
              aria-label={`Ir para o passo ${i + 1} de ${total}`}
              aria-current={i === passo ? "step" : undefined}
              onClick={() => setPasso(i)}
            />
          ))}
        </div>
      </div>

      <div className="tour__corpo">
        <div className="tour__slide" key={passo}>
          {ehBoasVindas && (
            <div className="tour__cartao tour__cartao--central">
              <p className="tour-boasvindas__eyebrow">Ecossistema Corvia</p>
              <AvatarBoasVindas fotoUrl={usuario?.instagram_photo_url} nome={usuario?.full_name} />
              <h1>Bem-vindo ao Ecossistema Corvia, {usuario?.full_name?.split(" ")[0]}.</h1>
              <p className="tour__resumo">
                {modo === "quick"
                  ? "Cinco telas, menos de dois minutos — o suficiente para começar a usar. Você pode pular a qualquer momento e ver o tour completo depois."
                  : "O passeio completo pelo que a plataforma oferece. Avance no seu ritmo e feche quando quiser."}
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
                  <span className="tour-texto-lado__contador">{slideAtual.eyebrow} · {passo} de {slides.length}</span>
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
                Você já tem o essencial. O resto aparece no caminho — e o tour completo fica
                sempre disponível em <strong>Gestão › Conheça a plataforma</strong>.
              </p>
              <div className="tour-final__grade">
                {slides.map((s) => (
                  <span className="tour-final__item" key={s.titulo}>
                    <Icone nome={s.icone} width={17} height={17} />
                    {s.titulo}
                  </span>
                ))}
              </div>
              {modo === "quick" && (
                <button type="button" className="tour-final__completo" onClick={verTourCompleto}>
                  Ver o tour completo agora
                  <Icone nome="seta" width={15} height={15} aria-hidden="true" />
                </button>
              )}
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
            {concluindo ? "Entrando…" : pendente ? "Começar a usar a Corvia" : "Voltar para a Corvia"}
          </button>
        ) : (
          <button className="botao" onClick={avancar}>Próximo</button>
        )}
      </div>
    </div>
  );
}
