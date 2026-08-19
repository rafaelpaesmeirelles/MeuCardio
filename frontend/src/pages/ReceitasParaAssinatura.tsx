import PrescricaoLivreEspecial from "../components/PrescricaoLivreEspecial";

export default function ReceitasParaAssinatura() {
  return (
    <main className="pagina">
      <div className="pagina__cabecalho">
        <div>
          <p className="eyebrow">Administração clínica</p>
          <h1>Receitas para assinatura</h1>
          <p className="pagina__descricao">
            Solicitações enviadas por Natália, Lenira e Wladmir para sua revisão, assinatura digital e devolução.
          </p>
        </div>
      </div>
      <PrescricaoLivreEspecial queueOnly />
    </main>
  );
}
