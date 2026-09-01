import { Link } from "react-router-dom";
import LegalDocumentFrame from "../components/LegalDocumentFrame";
import "../styles/legal.css";

const TERMOS_FEATURES = [
  { icon: "rota" as const, title: "Orientação, não garantia", detail: "Tempos, distâncias e trânsito são estimativas do provedor de mapas.", tone: "blue" as const },
  { icon: "emergencia" as const, title: "Condução responsável", detail: "A via, a sinalização e as autoridades sempre prevalecem sobre a tela.", tone: "pink" as const },
  { icon: "pin" as const, title: "Localização opcional", detail: "O recurso depende de escolha expressa e pode ser desativado.", tone: "violet" as const },
];

export default function TermosUso() {
  return (
    <LegalDocumentFrame
      eyebrow="Uso responsável"
      title="Termos de Uso — mapas e deslocamento"
      description={<p>Condições claras para usar o planejamento entre espaços como apoio de rota, sem substituir a realidade da via e a direção segura.</p>}
      updated="5 de agosto de 2026"
      features={TERMOS_FEATURES}
      tone="blue"
      footer={<><Link to="/privacidade">Ler a Política de Privacidade</Link><Link to="/">Voltar ao CorVIA</Link></>}
    >
      <section>
        <h2>Finalidade do recurso</h2>
        <p>“Próximos deslocamentos” auxilia o planejamento entre a posição atual do profissional e o próximo local de trabalho cadastrado. O recurso apresenta estimativas de duração, distância, trânsito, horário de saída e rotas alternativas.</p>
      </section>

      <section>
        <h2>Estimativas e disponibilidade</h2>
        <p>Condições viárias podem mudar rapidamente. Tempos, distâncias, congestionamentos, incidentes e alternativas são estimativas fornecidas pelo provedor de mapas e não constituem garantia de chegada. O profissional deve considerar margem de segurança, sinalização, interdições, condições climáticas e orientações das autoridades.</p>
      </section>

      <section>
        <h2>Segurança durante a condução</h2>
        <p>Não interaja com o painel enquanto estiver dirigindo. Antes de iniciar o deslocamento, escolha a rota e, quando necessário, abra a navegação no aplicativo apropriado. Respeite o Código de Trânsito Brasileiro, a sinalização e as condições reais da via, que prevalecem sobre qualquer orientação digital.</p>
      </section>

      <section>
        <h2>Google Maps</h2>
        <p>Os cálculos e o mapa podem utilizar serviços do Google Maps. Ao usar o recurso, aplicam-se também os <a href="https://maps.google.com/help/terms_maps/" target="_blank" rel="noreferrer">Termos Adicionais do Google Maps/Google Earth</a>, os <a href="https://cloud.google.com/maps-platform/terms" target="_blank" rel="noreferrer">Termos da Google Maps Platform</a> e a <a href="https://policies.google.com/privacy" target="_blank" rel="noreferrer">Política de Privacidade do Google</a>.</p>
      </section>

      <section>
        <h2>Localização e escolha do profissional</h2>
        <p>A função depende de autorização expressa no CorVIA e de permissão concedida pelo sistema operacional. O profissional pode desativá-la a qualquer momento. O funcionamento, as categorias de dados e o compartilhamento necessário estão descritos na <Link to="/privacidade">Política de Privacidade de localização e mapas</Link>.</p>
      </section>

      <section>
        <h2>Contato</h2>
        <p>Dúvidas, solicitações ou relato de funcionamento incorreto podem ser enviados para <a href="mailto:contato@corvia.med.br">contato@corvia.med.br</a>.</p>
      </section>

    </LegalDocumentFrame>
  );
}
