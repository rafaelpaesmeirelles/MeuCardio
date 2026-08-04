export default function Telediagnostico() {
  return (
    <section style={{ maxWidth: "68ch" }}>
      <p className="eyebrow">Serviços profissionais</p>
      <h1>Telediagnóstico</h1>
      <div className="cartao" style={{ marginTop: "1rem", textAlign: "center", padding: "2rem" }}>
        <p className="eyebrow">Em breve</p>
        <h2>O serviço está temporariamente indisponível para novas solicitações</h2>
        <p style={{ color: "var(--texto-secundario)", marginBottom: 0 }}>
          A Corvia está finalizando o fluxo operacional, os prazos, a assinatura dos
          laudos e a estrutura de atendimento. Pedidos e arquivos históricos permanecem
          preservados; nenhum novo envio ou pagamento é aceito enquanto o recurso estiver desligado.
        </p>
      </div>
    </section>
  );
}
