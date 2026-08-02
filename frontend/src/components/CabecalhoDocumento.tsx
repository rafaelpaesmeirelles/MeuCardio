type Medico = {
  full_name: string;
  council_name?: string | null;
  council_number?: string | null;
  council_state?: string | null;
  rqe?: string | null;
  specialty?: string | null;
  document_logo_url?: string | null;
};

/**
 * Cabeçalho dos documentos que saem impressos — receituário, atestado, laudo.
 *
 * Antes do rebrand estes documentos saíam **sem marca nenhuma**: só o título e o
 * nome do médico. Como eles circulam fora da plataforma — vão para a farmácia,
 * para o RH da empresa, para outro serviço —, são o lugar em que a marca mais
 * aparece e o único em que ela aparece para quem não é assinante.
 *
 * A ordem aqui não é estética. O documento é do **médico**, não da plataforma:
 * quem assina, quem responde pelo conteúdo e quem o paciente procura é ele. Por
 * isso o nome e o registro profissional têm peso visual maior que a logo, e a
 * logo fica como identificação de origem, não como emissor.
 */
export default function CabecalhoDocumento({ medico }: { medico: Medico }) {
  const registro = [medico.council_name, medico.council_number]
    .filter(Boolean)
    .join(" ");
  const uf = medico.council_state ? `/${medico.council_state}` : "";

  return (
    <header className="doc-cabecalho">
      <div className="doc-cabecalho__profissional">
        {medico.document_logo_url && (
          <img
            className="doc-cabecalho__logo-pessoal"
            src={medico.document_logo_url}
            alt=""
          />
        )}
        <strong className="doc-cabecalho__nome">{medico.full_name}</strong>
        {registro && (
          <span className="doc-cabecalho__registro">
            {registro}
            {uf}
            {medico.rqe && ` · RQE ${medico.rqe}`}
          </span>
        )}
        {medico.specialty && (
          <span className="doc-cabecalho__especialidade">{medico.specialty}</span>
        )}
      </div>
      <img
        className="doc-cabecalho__logo"
        src="/corvia-logo.png"
        alt="Corvia — O caminho do coração"
      />
    </header>
  );
}
