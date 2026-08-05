import { Link } from "react-router-dom";
import "../styles/legal.css";

export default function PoliticaPrivacidade() {
  return (
    <main className="legal-page" id="conteudo-principal">
      <header>
        <Link to="/" aria-label="Voltar ao Corvia"><img src="/corvia-logo-compacta.png" alt="Corvia" /></Link>
        <p className="eyebrow">Transparência e controle</p>
        <h1>Política de Privacidade — localização e mapas</h1>
        <p>Última atualização: 5 de agosto de 2026.</p>
      </header>

      <section>
        <h2>Escopo e controlador</h2>
        <p>Este aviso descreve especificamente o tratamento de dados no recurso opcional “Próximos deslocamentos” do Corvia. Para dúvidas ou exercício de direitos relacionados a esse tratamento, o canal do controlador é <a href="mailto:contato@corvia.med.br">contato@corvia.med.br</a>.</p>
      </section>

      <section>
        <h2>Dados utilizados e finalidade</h2>
        <p>Quando o profissional ativa voluntariamente o recurso e autoriza a localização no aparelho, o Corvia utiliza a posição atual, o próximo local de trabalho cadastrado, o horário previsto e a margem de chegada para calcular distância, duração, trânsito, horário recomendado de saída e rotas alternativas.</p>
        <ul>
          <li>A coordenada atual é obtida pelo navegador ou aplicativo somente durante o uso do painel em primeiro plano.</li>
          <li>A coordenada atual não é gravada no banco de dados, no histórico de auditoria nem nos registros de agenda.</li>
          <li>O consentimento, sua versão, data de concessão ou revogação e preferências de atualização são registrados para respeitar a escolha do profissional.</li>
          <li>Endereços e coordenadas dos locais de trabalho permanecem cadastrados até serem alterados ou removidos pelo profissional.</li>
        </ul>
      </section>

      <section>
        <h2>Compartilhamento com Google Maps</h2>
        <p>Para calcular e exibir os percursos, o Corvia envia ao Google Maps as coordenadas de origem e destino, o modo de viagem, o horário de partida e parâmetros técnicos necessários. O Google pode tratar também informações técnicas da conexão conforme seus próprios documentos.</p>
        <p>O uso dos mapas está sujeito aos <a href="https://maps.google.com/help/terms_maps/" target="_blank" rel="noreferrer">Termos Adicionais do Google Maps/Google Earth</a> e à <a href="https://policies.google.com/privacy" target="_blank" rel="noreferrer">Política de Privacidade do Google</a>.</p>
      </section>

      <section>
        <h2>Base, escolha e revogação</h2>
        <p>O recurso é opcional e permanece desativado até uma manifestação positiva do profissional. A autorização pode ser revogada a qualquer momento nas configurações da Agenda ou nas permissões do aparelho, sem impedir o uso das demais funções do Corvia. Depois da revogação, novos cálculos de localização deixam de ser realizados.</p>
      </section>

      <section>
        <h2>Segurança e retenção</h2>
        <p>As chaves de cálculo de rotas permanecem no servidor. A chave pública usada para apresentar o mapa é limitada ao domínio e à API correspondente. As rotas são calculadas para a consulta corrente e não são persistidas pelo Corvia. Informações de consentimento são mantidas enquanto necessárias para demonstrar e respeitar a preferência registrada, observadas as obrigações legais aplicáveis.</p>
      </section>

      <section>
        <h2>Direitos do titular</h2>
        <p>O profissional pode solicitar confirmação do tratamento, acesso, correção, informação sobre compartilhamento, revogação do consentimento e eliminação dos dados tratados com base no consentimento, ressalvadas as hipóteses legais de conservação. A solicitação pode ser enviada para <a href="mailto:contato@corvia.med.br">contato@corvia.med.br</a>.</p>
      </section>

      <footer><Link to="/termos">Ler os Termos de Uso de mapas e deslocamento</Link><Link to="/">Voltar ao Corvia</Link></footer>
    </main>
  );
}
