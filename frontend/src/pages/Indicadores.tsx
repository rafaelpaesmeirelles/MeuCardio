import { useEffect, useState } from "react";
import { api } from "../lib/api";

type Contagem = Record<string, number>;

type Indicadores = {
  janela_dias: number;
  desde: string;
  ate: string;
  como_solicitante: {
    pedidos_abertos: number;
    pedidos_pagos: number;
    pedidos_atendidos: number;
    aguardando: number;
    gasto_centavos: number;
    prazo_cumprido: number;
    prazo_estourado: number;
    por_servico: Contagem;
    por_urgencia: Contagem;
  };
  como_respondente: {
    atendidos: number;
    por_servico: Contagem;
    por_urgencia: Contagem;
    por_exame: Contagem;
    tempo_medio_resposta_horas: number | null;
    tempo_maior_resposta_horas: number | null;
    dentro_do_prazo: number;
    fora_do_prazo: number;
    folga_mediana_horas: number | null;
    receita_centavos: number;
    fila_aberta_agora: number;
  };
  notas: string[];
};

const JANELAS = [
  { dias: 30, rotulo: "30 dias" },
  { dias: 90, rotulo: "90 dias" },
  { dias: 365, rotulo: "12 meses" },
];

function reais(centavos: number) {
  return (centavos / 100).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function horas(v: number | null) {
  if (v === null) return "—";
  if (v < 1) return `${Math.round(v * 60)} min`;
  return `${v.toString().replace(".", ",")} h`;
}

function Indicador({ rotulo, valor, detalhe }: { rotulo: string; valor: string; detalhe?: string }) {
  return (
    <div className="indicador">
      <span className="indicador__valor">{valor}</span>
      <span className="indicador__rotulo">{rotulo}</span>
      {detalhe && <span className="indicador__detalhe">{detalhe}</span>}
    </div>
  );
}

function Distribuicao({ titulo, dados }: { titulo: string; dados: Contagem }) {
  const total = Object.values(dados).reduce((a, b) => a + b, 0);
  if (!total) return null;
  return (
    <div className="distribuicao">
      <h4>{titulo}</h4>
      {Object.entries(dados).map(([chave, n]) => (
        <div key={chave} className="distribuicao__linha">
          <span className="distribuicao__nome">{chave}</span>
          <span className="distribuicao__barra">
            <span style={{ width: `${(n / total) * 100}%` }} />
          </span>
          <span className="dado">{n}</span>
        </div>
      ))}
    </div>
  );
}

export default function Indicadores() {
  const [dias, setDias] = useState(30);
  const [d, setD] = useState<Indicadores | null>(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    setD(null);
    api
      .get<Indicadores>(`/indicadores/meus?dias=${dias}`)
      .then(setD)
      .catch((e) => setErro(e?.message || "Não foi possível carregar os indicadores."));
  }, [dias]);

  if (erro) return <p className="erro">{erro}</p>;

  const resp = d?.como_respondente;
  const sol = d?.como_solicitante;
  // As duas seções só aparecem quando têm o que mostrar. Um painel cheio de
  // zeros não informa nada e ainda sugere que algo quebrou.
  const temResposta = !!resp && (resp.atendidos > 0 || resp.fila_aberta_agora > 0);
  const temSolicitacao = !!sol && sol.pedidos_abertos > 0;

  return (
    <div>
      <h1>Meus indicadores</h1>
      <p className="subtitulo">
        Sua atividade no telediagnóstico. Estes números são seus e não são visíveis
        para nenhum outro usuário.
      </p>

      <div className="indicadores__janela">
        {JANELAS.map((j) => (
          <button
            key={j.dias}
            className={`chip${dias === j.dias ? " chip--ativo" : ""}`}
            onClick={() => setDias(j.dias)}
          >
            {j.rotulo}
          </button>
        ))}
      </div>

      {!d ? (
        <p>Carregando…</p>
      ) : (
        <>
          {temResposta && resp && (
            <>
              <h2>Como respondente</h2>
              <div className="indicadores__grade">
                <Indicador rotulo="atendidos no período" valor={String(resp.atendidos)} />
                <Indicador
                  rotulo="tempo médio de resposta"
                  valor={horas(resp.tempo_medio_resposta_horas)}
                  detalhe={resp.tempo_maior_resposta_horas !== null
                    ? `pior caso: ${horas(resp.tempo_maior_resposta_horas)}`
                    : undefined}
                />
                <Indicador
                  rotulo="dentro do prazo"
                  valor={`${resp.dentro_do_prazo}/${resp.atendidos}`}
                  detalhe={resp.fora_do_prazo > 0 ? `${resp.fora_do_prazo} fora do prazo` : "nenhum atraso"}
                />
                <Indicador rotulo="receita no período" valor={reais(resp.receita_centavos)} />
                <Indicador rotulo="na fila agora" valor={String(resp.fila_aberta_agora)} />
                <Indicador
                  rotulo="folga mediana até o prazo"
                  valor={horas(resp.folga_mediana_horas)}
                />
              </div>
              <div className="indicadores__distribuicoes">
                <Distribuicao titulo="Por serviço" dados={resp.por_servico} />
                <Distribuicao titulo="Por urgência" dados={resp.por_urgencia} />
                <Distribuicao titulo="Por exame" dados={resp.por_exame} />
              </div>
            </>
          )}

          {temSolicitacao && sol && (
            <>
              <h2 style={{ marginTop: "1.8rem" }}>Como solicitante</h2>
              <div className="indicadores__grade">
                <Indicador rotulo="pedidos abertos" valor={String(sol.pedidos_abertos)} />
                <Indicador rotulo="aguardando resposta" valor={String(sol.aguardando)} />
                <Indicador rotulo="investido no período" valor={reais(sol.gasto_centavos)} />
                <Indicador
                  rotulo="prazo cumprido com você"
                  valor={`${sol.prazo_cumprido}/${sol.pedidos_atendidos}`}
                />
              </div>
              <div className="indicadores__distribuicoes">
                <Distribuicao titulo="Por serviço" dados={sol.por_servico} />
                <Distribuicao titulo="Por urgência" dados={sol.por_urgencia} />
              </div>
            </>
          )}

          {!temResposta && !temSolicitacao && (
            <p className="curso__vazio">
              Nenhuma atividade de telediagnóstico nesta janela. Os indicadores aparecem
              assim que houver pedido solicitado ou atendido.
            </p>
          )}

          <h3 style={{ marginTop: "1.8rem" }}>Como estes números são calculados</h3>
          <ul className="indicadores__notas">
            {d.notas.map((n) => (
              <li key={n}>{n}</li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
