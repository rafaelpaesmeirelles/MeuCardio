import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Icone, { type NomeIcone } from "../components/Icone";
import { api, ApiError } from "../lib/api";
import { useAuth } from "../lib/auth";

/** Tour guiado do primeiro acesso (Trabalho 13, 06/08/2026) — pedido do
 * Rafael: "conjunto de sites... elegantes e profissionais que exaltam
 * todas as funções", explicando uso, benefício ao profissional e
 * aplicabilidade na rotina. Mostrado uma única vez, depois do KYC e do
 * passo do CorvIA Mail — `App.tsx` força a rota enquanto `usuario.
 * onboarding_pendente` for true; ao fim (ou ao pular), `POST /auth/me/
 * onboarding-concluido` fecha o gate de vez.
 *
 * Conteúdo agrupado pelas funções REAIS do produto (rotas de App.tsx),
 * nunca inventado — cada slide cita só o que existe e funciona hoje. */

type Slide = {
  icone: NomeIcone;
  titulo: string;
  resumo: string;
  uso: string;
  beneficio: string;
  rotina: string;
};

const SLIDES: Slide[] = [
  {
    icone: "conhecimento",
    titulo: "Biblioteca científica",
    resumo: "Toda a cardiologia organizada, sempre com a fonte.",
    uso: "Pesquise por doença, diretriz, evidência, estudo, exame ou achado de imagem — tudo com uma busca só, em \"Busca\" ou dentro de cada seção.",
    beneficio: "Você chega direto na recomendação com classe e nível de evidência, sem abrir três guias em outra aba para confirmar a fonte.",
    rotina: "Aquela dúvida no meio da consulta — \"qual é o corte de LDL nessa diretriz mesmo?\" — resolve em segundos, sem sair do fluxo de trabalho.",
  },
  {
    icone: "calculadora",
    titulo: "Ferramentas de decisão",
    resumo: "Escore, fluxograma e interação, prontos para usar.",
    uso: "Calculadoras validadas (CHA₂DS₂-VASc, HAS-BLED, GRACE e outras), fluxogramas em árvore de decisão, checagem de medicamentos e interações.",
    beneficio: "Reduz o cálculo mental e a consulta cruzada de bula — o escore já vem com a interpretação e a conduta associada.",
    rotina: "Na beira do leito ou no ambulatório, decidir anticoagular, escalonar ou pedir mais exame vira um cálculo de 30 segundos, não uma pesquisa de 10 minutos.",
  },
  {
    icone: "prescricao",
    titulo: "Receituário e documentos assinados",
    resumo: "Prescreva e emita já com assinatura digital.",
    uso: "Monte a receita pela base de medicamentos (com preço regulado da CMED), ou gere atestado e laudo pelos seus próprios modelos — e assine com certificado digital A1.",
    beneficio: "O documento sai pronto para o paciente, com validade jurídica de assinatura digital — sem imprimir, assinar à mão e escanear.",
    rotina: "Reaproveite uma receita anterior do mesmo paciente para uma consulta de retorno: os itens já vêm preenchidos, você só ajusta o que mudou.",
  },
  {
    icone: "mail",
    titulo: "CorvIA Mail",
    resumo: "Seu e-mail profissional, dentro da Corvia.",
    uso: "Endereço próprio @corvia.med.br, ou leia Yahoo, iCloud, Gmail e Outlook na mesma caixa — sem trocar de aplicativo.",
    beneficio: "Envie documento e receita já assinados direto ao paciente por e-mail, com assinatura profissional (nome, conselho, logo) em toda mensagem.",
    rotina: "Manda o resultado de um exame ou uma orientação por e-mail sem sair da tela onde você já está trabalhando.",
  },
  {
    icone: "assistente",
    titulo: "Assistente de IA clínica",
    resumo: "Pergunte, com fonte da própria Corvia e da internet.",
    uso: "Converse em linguagem natural — o assistente busca primeiro na base científica da Corvia, e complementa com busca na internet quando precisa de algo mais recente.",
    beneficio: "Cada resposta cita a fonte, então você confere antes de decidir — não é uma resposta genérica sem rastro.",
    rotina: "Pergunta rápida entre um paciente e outro, sem precisar montar uma busca formal — é literalmente conversar.",
  },
  {
    icone: "agenda",
    titulo: "Organização do dia a dia",
    resumo: "Agenda, round hospitalar e indicadores, integrados.",
    uso: "Agenda com sincronização de calendário externo, round hospitalar para acompanhar internados, checklist de alta e indicadores da sua própria prática.",
    beneficio: "Menos ferramenta espalhada — o que hoje está em três apps diferentes (agenda, planilha de round, anotação de indicador) fica num só lugar.",
    rotina: "Confere os pacientes internados do dia e a agenda de consultório na mesma tela, antes de sair de casa.",
  },
  {
    icone: "curso",
    titulo: "Aprendizado contínuo",
    resumo: "Trilhas de estudo, casos clínicos e cursos parceiros.",
    uso: "Trilhas de estudo por tema, casos clínicos interativos com pergunta e resposta, modo apresentação/ensino para aula, e cursos de parceiros para o Título de Especialista.",
    beneficio: "Estudo estruturado, não disperso — cada trilha já organiza a sequência de leitura por relevância clínica.",
    rotina: "Um caso clínico de 5 minutos no intervalo entre consultas mantém o estudo em dia sem reservar uma tarde inteira para isso.",
  },
  {
    icone: "pacientes",
    titulo: "Cuidado além do consultório",
    resumo: "Material educativo e telediagnóstico.",
    uso: "Envie material educativo por e-mail direto ao paciente, ou solicite laudo e consultoria de telediagnóstico (ECG, MAPA, Holter, teste ergométrico).",
    beneficio: "Orientação por escrito reduz retrabalho de explicar a mesma coisa em toda consulta, e o telediagnóstico dá uma segunda opinião sem deslocar o paciente.",
    rotina: "Depois da consulta, manda pro paciente o material sobre a condição dele — ele relê em casa, no tempo dele.",
  },
];

function CartaoSlide({ slide }: { slide: Slide }) {
  return (
    <div className="tour__cartao">
      <div className="tour__icone"><Icone nome={slide.icone} width={30} height={30} /></div>
      <h1>{slide.titulo}</h1>
      <p className="tour__resumo">{slide.resumo}</p>

      <dl className="tour__detalhes">
        <div>
          <dt>Como usar</dt>
          <dd>{slide.uso}</dd>
        </div>
        <div>
          <dt>O que ganha</dt>
          <dd>{slide.beneficio}</dd>
        </div>
        <div>
          <dt>No seu dia a dia</dt>
          <dd>{slide.rotina}</dd>
        </div>
      </dl>
    </div>
  );
}

export default function Tour() {
  const { usuario, recarregar } = useAuth();
  const navigate = useNavigate();
  const [passo, setPasso] = useState(0);
  const [concluindo, setConcluindo] = useState(false);

  const total = SLIDES.length + 2; // slide de boas-vindas + slides de função + slide final
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
      // registra o erro; ele pode ver o tour de novo, mas não fica preso.
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
          <span key={i} className={i <= passo ? "tour__ponto tour__ponto--feito" : "tour__ponto"} />
        ))}
      </div>

      <div className="tour__corpo">
        <div className="tour__slide" key={passo}>
          {ehBoasVindas && (
            <div className="tour__cartao tour__cartao--boas-vindas">
              <h1>Bem-vindo(a) à Corvia, {usuario?.full_name?.split(" ")[0]}.</h1>
              <p className="tour__resumo">
                Antes de começar, um giro rápido pelo que a plataforma oferece — leva menos de
                dois minutos, e você pode pular a qualquer momento.
              </p>
            </div>
          )}
          {slideAtual && <CartaoSlide slide={slideAtual} />}
          {ehFinal && (
            <div className="tour__cartao tour__cartao--boas-vindas">
              <h1>Pronto para começar.</h1>
              <p className="tour__resumo">
                Você já conhece o essencial. O resto você descobre usando — e pode voltar a
                qualquer uma dessas telas pelo menu, quando quiser.
              </p>
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
