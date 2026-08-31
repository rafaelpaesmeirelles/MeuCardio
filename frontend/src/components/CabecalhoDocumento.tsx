type Medico = {
  full_name: string;
  professional_title?: string | null;
  profession?: string | null;
  council_name?: string | null;
  council_number?: string | null;
  council_state?: string | null;
  rqe?: string | null;
  specialty?: string | null;
  document_logo_url?: string | null;
  document_logo_dark_background?: boolean;
  workplace_name?: string | null;
  workplace_department?: string | null;
  workplace_role?: string | null;
  workplace_notes?: string | null;
  include_workplace_on_documents?: boolean;
};

export default function CabecalhoDocumento({ medico }: { medico: Medico }) {
  const registro = [medico.council_name, medico.council_number].filter(Boolean).join(" ");
  const uf = medico.council_state ? `/${medico.council_state}` : "";
  const nomeBase = medico.professional_title
    ? medico.full_name.split(/\s+/).filter((parte) => !/^(sr|sra|dr|dra|prof|profa|me|ma|esp)\.?$/i.test(parte)).join(" ") || medico.full_name
    : medico.full_name;
  const nome = [medico.professional_title, nomeBase].filter(Boolean).join(" ");
  const local = medico.include_workplace_on_documents
    ? [medico.workplace_name, [medico.workplace_department, medico.workplace_role].filter(Boolean).join(" · "), medico.workplace_notes].filter(Boolean)
    : [];

  return (
    <header className="doc-cabecalho">
      <div className="doc-cabecalho__profissional">
        {medico.document_logo_url && (
          <span className={`doc-cabecalho__logo-pessoal-placa ${medico.document_logo_dark_background ? "doc-cabecalho__logo-pessoal-placa--escura" : ""}`}>
            <img className="doc-cabecalho__logo-pessoal" src={medico.document_logo_url} alt="" />
          </span>
        )}
        <strong className="doc-cabecalho__nome">{nome}</strong>
        {medico.profession && <span>{medico.profession}</span>}
        {registro && <span className="doc-cabecalho__registro">{registro}{uf}{medico.rqe && ` · RQE ${medico.rqe}`}</span>}
        {medico.specialty && <span className="doc-cabecalho__especialidade">{medico.specialty}</span>}
        {local.map((linha) => <span key={linha}>{linha}</span>)}
      </div>
      <img className="doc-cabecalho__logo" src="/corvia-logo-spaces.svg" alt="CorVIA Cardiology Spaces" />
    </header>
  );
}
