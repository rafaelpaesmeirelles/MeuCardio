import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../lib/api";

type Item = {
  id: string;
  texto: string;
  categoria?: string;
  obrigatorio?: boolean;
  origem_secao?: string;
};

type Aplicacao = {
  id: number;
  condicao: string;
  documento_origem: string | null;
  identificacao: string | null;
  itens: Item[];
  marcados: string[];
  observacoes: string | null;
  finalizado_em: string | null;
  faltando_obrigatorios: number;
};

const ROTULO_CATEGORIA: Record<string, string> = {
  medicacao: "Medicação",
  orientacao: "Orientação",
  seguimento: "Seguimento",
  encaminhamento: "Encaminhamento",
};

export default function ChecklistAlta() {
  const { id = "" } = useParams();
  const [a, setA] = useState<Aplicacao | null>(null);
  const [marcados, setMarcados] = useState<string[]>([]);
  const [obs, setObs] = useState("");
  const [erro, setErro] = useState("");
  const [salvando, setSalvando] = useState(false);

  useEffect(() => {
    api
      .get<Aplicacao>(`/api/checklists/aplicacoes/${id}`)
      .then((r) => {
        setA(r);
        setMarcados(r.marcados || []);
        setObs(r.observacoes || "");
      })
      .catch((e) => setErro(e?.message || "Não foi possível carregar."));
  }, [id]);

  async function salvar(finalizar = false) {
    setSalvando(true);
    setErro("");
    try {
      await api.patch(`/api/checklists/aplicacoes/${id}`, {
        marcados,
        observacoes: obs,
        finalizar,
      });
      const r = await api.get<Aplicacao>(`/api/checklists/aplicacoes/${id}`);
      setA(r);
    } catch (e: any) {
      setErro(e?.message || "Não foi possível salvar.");
    } finally {
      setSalvando(false);
    }
  }

  if (erro && !a) return <p className="erro">{erro}</p>;
  if (!a) return <p>Carregando…</p>;

  const finalizado = !!a.finalizado_em;
  const marcadoSet = new Set(marcados);
  const faltandoObrig = a.itens.filter((i) => i.obrigatorio && !marcadoSet.has(i.id));
  const porCategoria = a.itens.reduce<Record<string, Item[]>>((acc, i) => {
    const c = i.categoria || "outros";
    (acc[c] ||= []).push(i);
    return acc;
  }, {});

  return (
    <div>
      <p className="curso__voltar">
        <Link to="/checklists">← Checklists de alta</Link>
      </p>
      <h1>{a.condicao}</h1>
      {a.identificacao && <p className="subtitulo">{a.identificacao}</p>}

      {finalizado && (
        <p className="aviso aviso--ok">
          Alta finalizada. Este registro não pode mais ser alterado — ele descreve os
          itens como estavam no momento em que foi preenchido.
        </p>
      )}
      {erro && <p className="erro">{erro}</p>}

      <div className="checklist__contador">
        <strong>
          {marcados.length}/{a.itens.length}
        </strong>{" "}
        conferidos
        {faltandoObrig.length > 0 && (
          <span className="checklist__pendente">
            {faltandoObrig.length} obrigatório(s) pendente(s)
          </span>
        )}
      </div>

      {Object.entries(porCategoria).map(([cat, itens]) => (
        <section key={cat} className="checklist__grupo">
          <h3>{ROTULO_CATEGORIA[cat] || cat}</h3>
          {itens.map((i) => (
            <label
              key={i.id}
              className={`checklist__item${marcadoSet.has(i.id) ? " checklist__item--ok" : ""}`}
            >
              <input
                type="checkbox"
                checked={marcadoSet.has(i.id)}
                disabled={finalizado}
                onChange={(e) =>
                  setMarcados((m) =>
                    e.target.checked ? [...m, i.id] : m.filter((x) => x !== i.id)
                  )
                }
              />
              <span className="checklist__texto">
                {i.texto}
                {i.obrigatorio && <em className="checklist__obrig">obrigatório</em>}
                {/* A origem fica à vista, e não escondida num tooltip: é ela que
                    responde por que o item está na lista, e é o que permite
                    discordar dele com fundamento. */}
                {i.origem_secao && (
                  <span className="checklist__origem-item">de: {i.origem_secao}</span>
                )}
              </span>
            </label>
          ))}
        </section>
      ))}

      <h3>Observações</h3>
      <textarea
        className="checklist__obs"
        rows={3}
        value={obs}
        disabled={finalizado}
        placeholder="Se algum item obrigatório não se aplica a este paciente, registre aqui o motivo."
        onChange={(e) => setObs(e.target.value)}
      />

      {!finalizado && (
        <div className="checklist__acoes">
          <button className="botao" onClick={() => salvar(false)} disabled={salvando}>
            {salvando ? "Salvando…" : "Salvar"}
          </button>
          <button className="botao botao--acao" onClick={() => salvar(true)} disabled={salvando}>
            Finalizar alta
          </button>
          {faltandoObrig.length > 0 && (
            <span className="checklist__nota">
              Dá para finalizar com pendência, mas o motivo precisa estar escrito nas
              observações.
            </span>
          )}
        </div>
      )}

      {a.documento_origem && (
        <p className="checklist__origem">
          <Link to={`/biblioteca/${a.documento_origem}`}>Ver o protocolo de origem</Link>
        </p>
      )}
    </div>
  );
}
