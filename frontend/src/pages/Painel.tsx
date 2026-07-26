import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth";
import { Carregando } from "../components/Estado";
import ApoioBiolab from "../components/ApoioBiolab";

type Tema = { theme: string; count: number };
type Paciente = { id: number; initials: string; bed: string | null; unit: string | null };

export default function Painel() {
  const { usuario } = useAuth();
  const [temas, setTemas] = useState<Tema[] | null>(null);
  const [pacientes, setPacientes] = useState<Paciente[]>([]);

  useEffect(() => {
    api.get<Tema[]>("/library/themes").then(setTemas).catch(() => setTemas([]));
    api.get<Paciente[]>("/round/patients").then(setPacientes).catch(() => setPacientes([]));
  }, []);

  const totalDocs = temas?.reduce((s, t) => s + t.count, 0) ?? 0;

  return (
    <>
      <p className="eyebrow">Painel</p>
      <h1>Bom trabalho, {usuario?.full_name.split(" ")[0]}.</h1>

      <div className="grade grade--3" style={{ marginTop: "1.2rem" }}>
        <Link to="/round" className="cartao cartao--clinico" style={{ color: "inherit" }}>
          <p className="eyebrow">Round de hoje</p>
          <p className="dado" style={{ fontSize: "2rem", margin: "0.2rem 0" }}>
            {pacientes.length}
          </p>
          <p style={{ margin: 0, color: "var(--cinza-texto)" }}>
            {pacientes.length === 1 ? "paciente internado" : "pacientes internados"}
          </p>
        </Link>

        <Link to="/biblioteca" className="cartao" style={{ color: "inherit" }}>
          <p className="eyebrow">Biblioteca</p>
          <p className="dado" style={{ fontSize: "2rem", margin: "0.2rem 0" }}>{totalDocs}</p>
          <p style={{ margin: 0, color: "var(--cinza-texto)" }}>
            documentos em {temas?.length ?? 0} temas
          </p>
        </Link>

        <Link to="/calculadoras" className="cartao" style={{ color: "inherit" }}>
          <p className="eyebrow">Escores</p>
          <p style={{ margin: "0.4rem 0 0", fontWeight: 600 }}>
            CHA₂DS₂-VASc · HAS-BLED · HEART · CKD-EPI
          </p>
          <p style={{ margin: 0, color: "var(--cinza-texto)" }}>Com fórmula e referência à vista</p>
        </Link>
      </div>

      <h2 style={{ marginTop: "1.8rem" }}>Temas da biblioteca</h2>
      {temas === null ? (
        <Carregando />
      ) : temas.length === 0 ? (
        <div className="cartao">
          <h3>A biblioteca está vazia</h3>
          <p style={{ margin: 0, color: "var(--cinza-texto)" }}>
            Coloque os arquivos Markdown em <code>content/&lt;tema&gt;/</code> e rode{" "}
            <code>docker compose exec backend python -m app.services.importer</code>.
          </p>
        </div>
      ) : (
        <div className="grade grade--3">
          {temas.map((t) => (
            <Link
              key={t.theme}
              to={`/biblioteca?tema=${encodeURIComponent(t.theme)}`}
              className="cartao"
              style={{ color: "inherit" }}
            >
              <strong>{t.theme}</strong>
              <span className="dado" style={{ float: "right", color: "var(--cinza-texto)" }}>
                {t.count}
              </span>
            </Link>
          ))}
        </div>
      )}
      <ApoioBiolab />
    </>
  );
}
