import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { Carregando, Erro } from "../components/Estado";

type Item = { slug: string; nome: string };

type Verificada = {
  slug: string;
  gravidade: "contraindicada" | "grave" | "moderada" | "leve";
  efeito: string;
  conduta: string;
  fonte: string;
  classe_oposta: string | null;
  farmacos: Item[];
};

type Mencao = { de: Item; cita: Item[]; texto: string };

type Resultado = {
  selecionados: Item[];
  verificadas: Verificada[];
  avisos_de_classe: Verificada[];
  mencoes: Mencao[];
  aviso: string;
};

const ROTULO: Record<Verificada["gravidade"], string> = {
  contraindicada: "Contraindicada",
  grave: "Grave",
  moderada: "Moderada",
  leve: "Leve",
};

export default function Interacoes() {
  const [lista, setLista] = useState<Item[] | null>(null);
  const [escolhidos, setEscolhidos] = useState<string[]>([]);
  const [busca, setBusca] = useState("");
  const [resultado, setResultado] = useState<Resultado | null>(null);
  const [erro, setErro] = useState("");
  const [checando, setChecando] = useState(false);

  useEffect(() => {
    api.get<{ slug: string; generic_name: string }[]>("/drugs")
      .then((l) => setLista(l.map((d) => ({ slug: d.slug, nome: d.generic_name }))))
      .catch((e) => setErro(e.message));
  }, []);

  function alternar(slug: string) {
    setResultado(null);
    setEscolhidos((atual) =>
      atual.includes(slug) ? atual.filter((s) => s !== slug) : [...atual, slug],
    );
  }

  async function checar() {
    setChecando(true);
    setErro("");
    try {
      setResultado(await api.post<Resultado>("/drugs/interacoes", { slugs: escolhidos }));
    } catch (e: any) {
      setErro(e.message);
    } finally {
      setChecando(false);
    }
  }

  if (erro && !lista) return <Erro mensagem={erro} />;
  if (!lista) return <Carregando />;

  const filtrada = busca
    ? lista.filter((d) => d.nome.toLowerCase().includes(busca.toLowerCase()))
    : lista;
  const nomeDe = (s: string) => lista.find((d) => d.slug === s)?.nome ?? s;

  return (
    <>
      <p className="eyebrow">Medicamentos</p>
      <h1>Checador de interação</h1>
      <p style={{ maxWidth: "68ch", color: "var(--texto-secundario)" }}>
        Monte a lista do que o paciente já usa e do que você vai prescrever. O
        sistema separa o que está <strong>verificado contra bula</strong> do que é
        apenas <strong>menção no texto</strong>, sem gravidade atribuída.
      </p>

      <div className="cartao" style={{ marginTop: "1rem" }}>
        <label htmlFor="busca-farmaco">
          <strong>Selecione de 2 a 10 medicamentos</strong>
        </label>
        <input
          id="busca-farmaco"
          value={busca}
          onChange={(e) => setBusca(e.target.value)}
          placeholder="Filtrar pelo nome…"
          style={{ marginTop: "0.4rem" }}
        />

        {escolhidos.length > 0 && (
          <div className="painel__temas" style={{ marginTop: "0.6rem" }}>
            {escolhidos.map((s) => (
              <button key={s} className="painel__tema" onClick={() => alternar(s)}>
                {nomeDe(s)} <span className="dado">✕</span>
              </button>
            ))}
          </div>
        )}

        <div
          style={{
            marginTop: "0.6rem",
            maxHeight: "14rem",
            overflowY: "auto",
            display: "flex",
            flexWrap: "wrap",
            gap: "0.35rem",
          }}
        >
          {filtrada.map((d) => (
            <button
              key={d.slug}
              className="painel__tema"
              onClick={() => alternar(d.slug)}
              disabled={!escolhidos.includes(d.slug) && escolhidos.length >= 10}
              style={escolhidos.includes(d.slug) ? { borderColor: "var(--acento)" } : undefined}
            >
              {d.nome}
            </button>
          ))}
        </div>

        <button
          className="botao"
          style={{ marginTop: "0.8rem" }}
          disabled={escolhidos.length < 2 || checando}
          onClick={checar}
        >
          {checando ? "Checando…" : `Checar ${escolhidos.length} medicamentos`}
        </button>
      </div>

      {erro && <Erro mensagem={erro} />}

      {resultado && (
        <>
          <section className="painel__grupo">
            <h2>Interações verificadas</h2>
            <p className="painel__grupo-sub">
              Com gravidade e fonte nominal — é o único bloco em que o sistema afirma algo.
            </p>
            {resultado.verificadas.length === 0 ? (
              <div className="cartao">
                <strong>Nenhuma interação verificada entre os selecionados.</strong>
                <p style={{ margin: "0.4rem 0 0", fontSize: "0.88rem" }}>{resultado.aviso}</p>
              </div>
            ) : (
              <div style={{ display: "grid", gap: "0.7rem" }}>
                {resultado.verificadas.map((v) => (
                  <article
                    key={v.slug}
                    className={`cartao painel__funcao${
                      v.gravidade === "contraindicada" || v.gravidade === "grave"
                        ? " painel__funcao--destaque"
                        : ""
                    }`}
                  >
                    <strong>
                      {v.farmacos.map((f) => f.nome).join(" + ")}
                      {v.classe_oposta && ` + ${v.classe_oposta}`}{" "}
                      <span className="painel__breve">{ROTULO[v.gravidade]}</span>
                    </strong>
                    <span><strong>Efeito:</strong> {v.efeito}</span>
                    <span><strong>Conduta:</strong> {v.conduta}</span>
                    <span style={{ fontSize: "0.78rem" }}><strong>Fonte:</strong> {v.fonte}</span>
                  </article>
                ))}
              </div>
            )}
          </section>

          {resultado.avisos_de_classe.length > 0 && (
            <section className="painel__grupo">
              <h2>Avisos de classe</h2>
              <p className="painel__grupo-sub">
                Dependem do que o paciente usa <strong>fora desta lista</strong>: um dos
                lados é uma classe inteira, não um fármaco que você selecionou.
              </p>
              <div style={{ display: "grid", gap: "0.7rem" }}>
                {resultado.avisos_de_classe.map((v) => (
                  <article key={v.slug} className="cartao painel__funcao">
                    <strong>
                      {v.farmacos.map((f) => f.nome).join(" + ")}
                      {v.classe_oposta && ` + ${v.classe_oposta}`}{" "}
                      <span className="painel__breve">{ROTULO[v.gravidade]}</span>
                    </strong>
                    <span><strong>Efeito:</strong> {v.efeito}</span>
                    <span><strong>Conduta:</strong> {v.conduta}</span>
                    <span style={{ fontSize: "0.78rem" }}><strong>Fonte:</strong> {v.fonte}</span>
                  </article>
                ))}
              </div>
            </section>
          )}

          <section className="painel__grupo">
            <h2>Menções na bula, sem gravidade atribuída</h2>
            <p className="painel__grupo-sub">
              Trechos do texto de interações dos fármacos escolhidos que citam outro da
              mesma lista. É o que a bula diz — a Corvia não classificou.
            </p>
            {resultado.mencoes.length === 0 ? (
              <p style={{ fontSize: "0.88rem", color: "var(--texto-secundario)" }}>
                Nenhuma menção cruzada no texto dos selecionados.
              </p>
            ) : (
              <div style={{ display: "grid", gap: "0.7rem" }}>
                {resultado.mencoes.map((m, i) => (
                  <article key={i} className="cartao painel__funcao painel__funcao--breve">
                    <strong>
                      {m.de.nome} → cita {m.cita.map((c) => c.nome).join(", ")}
                    </strong>
                    <span>{m.texto}</span>
                  </article>
                ))}
              </div>
            )}
          </section>

          <p
            className="cartao"
            style={{ marginTop: "1rem", fontSize: "0.85rem", color: "var(--texto-secundario)" }}
          >
            {resultado.aviso}
          </p>
        </>
      )}
    </>
  );
}
