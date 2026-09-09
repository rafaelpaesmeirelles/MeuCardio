import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth";
import { lastTimelineTopic, rememberTimelineTopic, type TimelineTopic, type TimelineSummary } from "../lib/scientificTimeline";
import Icone from "./Icone";

export default function ScientificTimelineCard() {
  const { usuario } = useAuth();
  const [topics, setTopics] = useState<TimelineTopic[] | null>(null);
  const [topic, setTopic] = useState("");
  const [summary, setSummary] = useState<TimelineSummary | null>(null);
  const [error, setError] = useState(false);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let active = true;
    setError(false);
    setTopics(null);
    setSummary(null);
    setTopic("");
    api.get<TimelineTopic[]>("/trilhas/timeline/temas").then((items) => {
      if (!active) return;
      const available = items.filter((item) => item.total_marcos > 0);
      const remembered = lastTimelineTopic(usuario?.id);
      setTopics(available);
      setTopic(available.find((item) => item.tema === remembered)?.tema || available[0]?.tema || "");
    }).catch(() => { if (active) setError(true); });
    return () => { active = false; };
  }, [usuario?.id, attempt]);

  useEffect(() => {
    if (!topic) return;
    let active = true;
    setError(false);
    setSummary(null);
    api.get<TimelineSummary>(`/trilhas/timeline?tema=${encodeURIComponent(topic)}`).then((data) => {
      if (!active) return;
      setSummary(data);
      rememberTimelineTopic(usuario?.id, data.tema);
    }).catch(() => { if (active) setError(true); });
    return () => { active = false; };
  }, [topic, usuario?.id]);

  const latest = summary && [...summary.marcos].sort((a, b) => b.ano - a.ano).slice(0, 1);
  const destination = `/trilhas/timeline${summary?.tema || topic ? `?tema=${encodeURIComponent(summary?.tema || topic)}` : ""}`;
  return <section className="spaces-scientific-timeline" aria-label="Minha timeline">
    <h3><Icone nome="relogio" /> Minha timeline</h3>
    <Link className="spaces-scientific-timeline__open" to={destination}>Abrir timeline{topic ? " do tema" : ""} <Icone nome="seta" /></Link>
    {topics && topics.length > 0 && <label>Tema científico
      <select value={topic} onChange={(event) => setTopic(event.target.value)} aria-label="Tema da minha timeline">
        {topics.map((item) => <option key={item.tema} value={item.tema}>{item.tema}</option>)}
      </select>
    </label>}
    {error ? <div role="status"><p>Não foi possível carregar os marcos.</p><button type="button" onClick={() => setAttempt((value) => value + 1)}>Tentar novamente</button></div>
      : topics?.length === 0 ? <p>Os temas aparecerão aqui quando houver marcos científicos publicados.</p>
        : !summary ? <p role="status">Carregando marcos científicos…</p>
          : <>
            <p className="spaces-scientific-timeline__summary">{summary.total} marco{summary.total === 1 ? "" : "s"}{summary.primeiro_ano && summary.ultimo_ano ? ` · ${summary.primeiro_ano}–${summary.ultimo_ano}` : ""}</p>
            <ul>{latest?.map((item) => <li key={item.slug}><span>{item.ano}</span><Link to={item.rota}>{item.titulo}</Link></li>)}</ul>
          </>}
  </section>;
}
