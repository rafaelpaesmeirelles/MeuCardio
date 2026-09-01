import { Link } from "react-router-dom";
import LegalDocumentFrame from "../components/LegalDocumentFrame";
import "../styles/legal.css";

const PRIVACIDADE_FEATURES = [
  { icon: "check" as const, title: "LGPD no centro", detail: "Papéis, bases legais e direitos dos titulares descritos com transparência.", tone: "green" as const },
  { icon: "conta" as const, title: "Controle do titular", detail: "Acesso, correção, revogação e eliminação conforme o papel aplicável.", tone: "blue" as const },
  { icon: "sincronizar" as const, title: "Integrações sob escolha", detail: "Localização, mapas e serviços externos dependem da função utilizada.", tone: "violet" as const },
];

export default function PoliticaPrivacidade() {
  return (
    <LegalDocumentFrame
      eyebrow="Privacidade, transparência e segurança"
      title="Política de Privacidade — CorVIA Cardiology Spaces"
      description={<p>Como dados profissionais, clínicos e técnicos são tratados para manter cada espaço conectado sem romper o dever de confidencialidade.</p>}
      updated="28 de agosto de 2026"
      features={PRIVACIDADE_FEATURES}
      tone="cyan"
      footer={<><Link to="/termos">Ler os Termos de Uso</Link><Link to="/">Voltar ao CorVIA</Link></>}
    >
      <section>
        <h2>1. Escopo e contato</h2>
        <p>
          Esta Política de Privacidade descreve como o CorVIA Cardiology Spaces (“CorVIA”), em suas versões web e móvel,
          trata dados pessoais no fornecimento de recursos de apoio à prática clínica, organização profissional,
          prontuário, documentos, prescrições, exames, comunicação, integrações e inteligência artificial.
        </p>
        <p>
          Para assuntos relacionados a privacidade, proteção de dados ou exercício de direitos, entre em contato pelo
          e-mail <a href="mailto:contato@corvia.med.br">contato@corvia.med.br</a>.
        </p>
      </section>

      <section>
        <h2>2. Papéis no tratamento de dados</h2>
        <p>
          Em relação aos dados da conta do profissional, autenticação, segurança, suporte, preferências e administração
          da plataforma, o CorVIA atua como controlador dos dados pessoais, nos termos da Lei nº 13.709/2018 (LGPD).
        </p>
        <p>
          Quando um profissional ou uma instituição insere dados de pacientes no CorVIA para fins assistenciais,
          clínicos ou administrativos, o profissional ou a instituição responsável normalmente atua como controlador
          desses dados, e o CorVIA atua como operador, tratando-os de acordo com as instruções e finalidades definidas
          pelo controlador e com as obrigações legais aplicáveis.
        </p>
      </section>

      <section>
        <h2>3. Dados que podem ser tratados</h2>
        <p>Conforme as funcionalidades utilizadas, o CorVIA pode tratar:</p>
        <ul>
          <li>dados cadastrais e profissionais, como nome, e-mail, telefone, registro profissional, especialidade e locais de atendimento;</li>
          <li>dados de autenticação e segurança, incluindo sessões, endereço IP, dispositivo, sistema operacional e registros de auditoria;</li>
          <li>dados de pacientes inseridos pelo profissional ou instituição, inclusive identificação, antecedentes, diagnósticos, medicamentos, alergias, sinais e sintomas, resultados de exames, imagens, documentos, prescrições e evoluções;</li>
          <li>dados pessoais sensíveis referentes à saúde, quando necessários às funcionalidades clínicas solicitadas;</li>
          <li>arquivos, imagens e informações de exames enviados para organização, análise assistida ou apoio à decisão clínica;</li>
          <li>documentos produzidos na plataforma e dados necessários à assinatura digital;</li>
          <li>dados de agenda, e-mail, calendário e outras integrações quando o usuário autoriza a conexão;</li>
          <li>dados de localização quando o usuário ativa uma funcionalidade que dependa deles e concede a permissão correspondente;</li>
          <li>dados de suporte, comunicações, feedback e informações técnicas necessárias à operação e segurança do serviço;</li>
          <li>dados de contratação e cobrança, quando aplicável, observadas as responsabilidades dos respectivos provedores.</li>
        </ul>
      </section>

      <section>
        <h2>4. Finalidades</h2>
        <p>Os dados podem ser tratados para:</p>
        <ul>
          <li>criar e administrar contas, autenticar usuários e manter o acesso seguro;</li>
          <li>fornecer prontuário, agenda, documentos clínicos, prescrições, exames, calculadoras, diretrizes, conteúdo científico e demais funcionalidades;</li>
          <li>executar recursos de inteligência artificial e suporte à decisão clínica solicitados pelo usuário;</li>
          <li>processar arquivos, textos, imagens e contexto clínico necessários à funcionalidade escolhida;</li>
          <li>permitir integrações autorizadas com mapas, calendários, e-mail, assinatura digital, identidade e outros serviços;</li>
          <li>prevenir fraude, abuso, acessos indevidos e incidentes de segurança;</li>
          <li>prestar suporte, diagnosticar falhas, realizar backups e melhorar desempenho e usabilidade;</li>
          <li>cumprir obrigações legais, regulatórias, contratuais e determinações de autoridades competentes;</li>
          <li>exercer direitos em processos administrativos, arbitrais ou judiciais;</li>
          <li>enviar comunicações relacionadas à conta, segurança, serviço e alterações relevantes da plataforma.</li>
        </ul>
      </section>

      <section>
        <h2>5. Bases legais</h2>
        <p>
          O tratamento é realizado com fundamento nas bases legais aplicáveis a cada situação, incluindo execução de
          contrato e procedimentos preliminares, cumprimento de obrigação legal ou regulatória, exercício regular de
          direitos, legítimo interesse quando cabível e consentimento quando esta for a base adequada.
        </p>
        <p>
          Para dados pessoais sensíveis, inclusive dados de saúde, são observadas as hipóteses específicas previstas
          no art. 11 da LGPD e as responsabilidades do profissional ou instituição controladora do dado clínico.
        </p>
      </section>

      <section>
        <h2>6. Inteligência artificial e suporte à decisão clínica</h2>
        <p>
          Algumas funcionalidades podem utilizar modelos de inteligência artificial para resumir, estruturar, comparar
          ou analisar informações fornecidas pelo usuário, inclusive textos, exames e imagens. O conteúdo necessário à
          solicitação pode ser processado por provedores tecnológicos contratados para viabilizar a funcionalidade.
        </p>
        <p>
          O CorVIA procura limitar o tratamento ao necessário à funcionalidade solicitada. O CorVIA não vende dados
          pessoais nem utiliza dados clínicos para publicidade comportamental. Respostas de inteligência artificial e
          recursos de suporte à decisão são auxiliares e devem ser avaliados pelo profissional responsável; não
          substituem julgamento clínico, diagnóstico, prescrição ou acompanhamento por profissional habilitado.
        </p>
      </section>

      <section>
        <h2>7. Compartilhamento com terceiros</h2>
        <p>
          O CorVIA pode compartilhar dados estritamente necessários com fornecedores que apoiem as funcionalidades
          solicitadas, como serviços de hospedagem, banco de dados, armazenamento, backup, segurança, inteligência
          artificial, e-mail, calendário, mapas, pagamentos, assinatura digital, autenticação e verificação de identidade.
        </p>
        <p>
          Dados também poderão ser disponibilizados a autoridades públicas quando houver obrigação legal, ordem válida
          ou necessidade de proteção de direitos. O CorVIA não comercializa dados pessoais.
        </p>
      </section>

      <section>
        <h2>8. Localização e Google Maps</h2>
        <p>
          No recurso opcional de deslocamentos, quando o profissional concede permissão, o CorVIA pode utilizar a
          posição atual e o próximo local de trabalho cadastrado para calcular distância, duração, trânsito, horário
          recomendado de saída e rotas. A coordenada atual é utilizada durante a consulta e não é gravada pelo CorVIA
          no prontuário ou no histórico da agenda.
        </p>
        <p>
          Para calcular e exibir percursos, podem ser enviados ao Google Maps dados técnicos necessários, como origem,
          destino, modo de viagem e horário. O uso dos mapas também está sujeito aos{" "}
          <a href="https://maps.google.com/help/terms_maps/" target="_blank" rel="noreferrer">Termos do Google Maps/Google Earth</a>{" "}
          e à <a href="https://policies.google.com/privacy" target="_blank" rel="noreferrer">Política de Privacidade do Google</a>.
        </p>
      </section>

      <section>
        <h2>9. Permissões do dispositivo</h2>
        <p>
          O aplicativo pode solicitar permissões como câmera, arquivos/fotos, notificações ou localização quando uma
          funcionalidade depender delas. A permissão é solicitada no contexto de uso e pode ser revogada nas
          configurações do dispositivo. A revogação pode limitar apenas a funcionalidade que depende daquela permissão.
        </p>
      </section>

      <section>
        <h2>10. Segurança</h2>
        <p>
          O CorVIA adota medidas técnicas e administrativas destinadas a proteger os dados contra acesso não autorizado,
          perda, alteração, divulgação ou destruição indevida, incluindo controles de acesso, autenticação, registros de
          auditoria e medidas de segurança de infraestrutura compatíveis com o serviço. Nenhum sistema, contudo, pode
          garantir risco zero em ambientes digitais.
        </p>
      </section>

      <section>
        <h2>11. Retenção e eliminação</h2>
        <p>
          Os dados são mantidos pelo período necessário para cumprir as finalidades desta Política, prestar o serviço,
          observar obrigações legais e regulatórias, preservar registros de segurança e exercer direitos. Quando a
          retenção deixar de ser necessária e não houver fundamento legal para conservação, os dados poderão ser
          eliminados, anonimizados ou agregados de forma compatível com a legislação aplicável.
        </p>
      </section>

      <section>
        <h2>12. Transferência internacional</h2>
        <p>
          Alguns fornecedores tecnológicos podem processar ou armazenar dados fora do Brasil. Quando aplicável, o
          CorVIA adota mecanismos compatíveis com a LGPD e busca utilizar fornecedores com compromissos adequados de
          privacidade, segurança e proteção de dados.
        </p>
      </section>

      <section>
        <h2>13. Direitos dos titulares</h2>
        <p>
          Nos termos da LGPD e conforme aplicável ao papel do CorVIA no tratamento, o titular pode solicitar confirmação
          da existência de tratamento, acesso, correção, anonimização, bloqueio ou eliminação, portabilidade quando
          aplicável, informação sobre compartilhamento, revogação do consentimento e revisão de decisões exclusivamente
          automatizadas nas hipóteses previstas em lei.
        </p>
        <p>
          Solicitações podem ser enviadas para <a href="mailto:contato@corvia.med.br">contato@corvia.med.br</a>. Quando
          o CorVIA atuar como operador de dados inseridos por um profissional ou instituição de saúde, a solicitação
          poderá precisar ser direcionada ao respectivo controlador.
        </p>
      </section>

      <section>
        <h2>14. Crianças e adolescentes</h2>
        <p>
          O CorVIA não é direcionado ao uso autônomo por crianças. Informações clínicas de pacientes menores de idade
          podem ser inseridas por profissionais de saúde no contexto assistencial, observadas as bases legais, deveres
          profissionais e regras específicas de proteção previstas na legislação.
        </p>
      </section>

      <section>
        <h2>15. Natureza do serviço de saúde</h2>
        <p>
          O CorVIA é uma plataforma de apoio à atividade profissional e não substitui avaliação clínica individualizada.
          Salvo quando uma funcionalidade específica for expressamente submetida e autorizada como dispositivo médico
          pelas autoridades competentes, o aplicativo não deve ser interpretado como dispositivo médico autônomo nem
          como substituto de diagnóstico, tratamento ou acompanhamento por profissional habilitado.
        </p>
      </section>

      <section>
        <h2>16. Alterações desta Política</h2>
        <p>
          Esta Política pode ser atualizada para refletir alterações legais, regulatórias, tecnológicas ou funcionais.
          A data da versão vigente será indicada no início da página. Mudanças relevantes poderão ser comunicadas pelos
          canais disponíveis na plataforma.
        </p>
      </section>

    </LegalDocumentFrame>
  );
}
