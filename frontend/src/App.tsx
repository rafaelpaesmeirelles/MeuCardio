import { lazy, Suspense, useEffect, type ReactNode } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import Shell from "./components/Shell";
import { Carregando } from "./components/Estado";
import HomeQuickActionsPersonalizer from "./components/HomeQuickActionsPersonalizer";
import OptionalFeatureBoundary from "./components/OptionalFeatureBoundary";
import { cardiologySpacesEnabled } from "./lib/cardiologySpacesFeature";
import { heartTeamEnabled, whatsappAssistantEnabled } from "./lib/aiFeatureFlags";
import { useAuth } from "./lib/auth";

const Entrar = lazy(() => import("./pages/Entrar"));
const Produto = lazy(() => import("./pages/Produto"));
const Painel = lazy(() => import("./pages/Painel"));
const CardiologySpacesHome = lazy(() => import("./pages/CardiologySpacesHome"));
const Apresentacao = lazy(() => import("./pages/Apresentacao"));
const Trilhas = lazy(() => import("./pages/Trilhas"));
const TimelineDoencas = lazy(() => import("./pages/TimelineDoencas"));
const MaterialPaciente = lazy(() => import("./pages/MaterialPaciente"));
const MaterialPacienteDetalhe = lazy(() => import("./pages/MaterialPacienteDetalhe"));
const Emergencia = lazy(() => import("./pages/Emergencia"));
const Trilha = lazy(() => import("./pages/Trilha"));
const CasosClinicos = lazy(() => import("./pages/CasosClinicos"));
const CasoClinico = lazy(() => import("./pages/CasoClinico"));
const Checklists = lazy(() => import("./pages/Checklists"));
const ChecklistModelo = lazy(() => import("./pages/ChecklistModelo"));
const ChecklistAlta = lazy(() => import("./pages/ChecklistAlta"));
const Indicadores = lazy(() => import("./pages/Indicadores"));
// Compatibilidade de inventário/deep-link: o módulo legado continua conhecido pelo
// bundle, mas não possui mais ponto de entrada no produto. As URLs /cursos*
// redirecionam para Trilhas abaixo e os shells não exibem a opção.
const CursosLegado = lazy(() => import("./pages/Cursos"));
const Biblioteca = lazy(() => import("./pages/Biblioteca"));
const ScientificDocumentAI = lazy(() => import("./pages/ScientificDocumentAI"));
const Fluxogramas = lazy(() => import("./pages/Fluxogramas"));
const Diretrizes = lazy(() => import("./pages/Diretrizes"));
const Galeria = lazy(() => import("./pages/Galeria"));
const ImagemGaleria = lazy(() => import("./pages/ImagemGaleria"));
const Documento = lazy(() => import("./pages/Documento"));
const Busca = lazy(() => import("./pages/Busca"));
const Calculadoras = lazy(() => import("./pages/Calculadoras"));
const Calculadora = lazy(() => import("./pages/Calculadora"));
const CardiologiaIntensiva = lazy(() => import("./pages/CardiologiaIntensiva"));
const Medicamentos = lazy(() => import("./pages/MedicamentosClinicalCommand"));
const Interacoes = lazy(() => import("./pages/Interacoes"));
const Condicoes = lazy(() => import("./pages/Condicoes"));
const Prontuario = lazy(() => import("./pages/Prontuario"));
const CardiovascularExamAI = lazy(() => import("./pages/CardiovascularExamAI"));
const Round = lazy(() => import("./pages/RoundGerenciavel"));
const Assistente = lazy(() => import("./pages/Assistente"));
const Admin = lazy(() => import("./pages/Admin"));
const AdminAssinantes = lazy(() => import("./pages/AdminAssinantes"));
const AdminFichaAssinante = lazy(() => import("./pages/AdminFichaAssinante"));
const AdminGerenciarUsuario = lazy(() => import("./pages/AdminGerenciarUsuario"));
const SolicitarAcesso = lazy(() => import("./pages/SolicitarAcesso"));
const EsqueciSenha = lazy(() => import("./pages/EsqueciSenha"));
const RedefinirSenha = lazy(() => import("./pages/RedefinirSenha"));
const Favoritos = lazy(() => import("./pages/Favoritos"));
const Exames = lazy(() => import("./pages/Exames"));
const Exame = lazy(() => import("./pages/Exame"));
const Evidencias = lazy(() => import("./pages/Evidencias"));
const Evidencia = lazy(() => import("./pages/Evidencia"));
const Estudos = lazy(() => import("./pages/Estudos"));
const Estudo = lazy(() => import("./pages/Estudo"));
const Agenda = lazy(() => import("./pages/Agenda"));
const Templates = lazy(() => import("./pages/Templates"));
const AvaliacaoPreOperatoria = lazy(() => import("./pages/AvaliacaoPreOperatoria"));
const EmBreve = lazy(() => import("./pages/EmBreve"));
const MinhaConta = lazy(() => import("./pages/MinhaConta"));
const Sincronizacao = lazy(() => import("./pages/Sincronizacao"));
const Telediagnostico = lazy(() => import("./pages/Telediagnostico"));
const FilaTelediagnostico = lazy(() => import("./pages/FilaTelediagnostico"));
const ReceitasParaAssinatura = lazy(() => import("./components/PrescricaoLivreEspecial"));
const CaixaDeEmail = lazy(() => import("./pages/CaixaDeEmail"));
const CorviaMail = lazy(() => import("./pages/CorviaMail"));
const Receituario = lazy(() => import("./pages/Receituario"));
const UsuariosOnline = lazy(() => import("./pages/UsuariosOnline"));
const GuiaDoencas = lazy(() => import("./pages/GuiaDoencas"));
const GuiaDoenca = lazy(() => import("./pages/GuiaDoenca"));
const TriagemSintomas = lazy(() => import("./pages/TriagemSintomas"));
const ExportarConteudo = lazy(() => import("./pages/ExportarConteudo"));
const PoliticaPrivacidade = lazy(() => import("./pages/PoliticaPrivacidade"));
const ExcluirConta = lazy(() => import("./pages/ExcluirConta"));
const TermosUso = lazy(() => import("./pages/TermosUso"));
const VerificacaoIdentidade = lazy(() => import("./pages/VerificacaoIdentidade"));
const Tour = lazy(() => import("./pages/Tour"));
const CardiologySpacesTour = lazy(() => import("./pages/CardiologySpacesTour"));
const ValidarDocumento = lazy(() => import("./pages/ValidarDocumento"));
const HeartTeamVirtual = lazy(() => import("./pages/HeartTeamVirtual"));
const WhatsAppAssistant = lazy(() => import("./pages/WhatsAppAssistant"));
const AdminAIOperations = lazy(() => import("./pages/AdminAIOperations"));

void CursosLegado;

const INVESTOR_TOUR_SESSION_KEY = "corvia:cardiology-spaces:investor-tour-session:v1";

function RotasSuspensas({ children }: { children: ReactNode }) {
  return (
    <Suspense fallback={<Carregando texto="Carregando a tela…" />}>
      {children}
    </Suspense>
  );
}

export default function App() {
  const { usuario, carregando } = useAuth();
  const location = useLocation();

  useEffect(() => {
    (window as unknown as { __corviaVerificarAtualizacao?: () => void })
      .__corviaVerificarAtualizacao?.();
  }, [location.pathname]);

  const validacaoPublica = location.pathname === "/validar" || location.pathname.startsWith("/validar/");
  if (validacaoPublica) {
    return (
      <RotasSuspensas>
        <Routes>
          <Route path="/validar" element={<ValidarDocumento />} />
          <Route path="/validar/:codigo" element={<ValidarDocumento />} />
        </Routes>
      </RotasSuspensas>
    );
  }

  if (carregando) return <Carregando texto="Abrindo a Corvia…" />;
  if (!usuario) {
    return (
      <RotasSuspensas>
        <Routes>
          <Route path="/" element={<Navigate to="/entrar" replace />} />
          <Route path="/produto" element={<Produto />} />
          <Route path="/entrar" element={<Entrar />} />
          <Route path="/solicitar-acesso" element={<SolicitarAcesso />} />
          <Route path="/esqueci-senha" element={<EsqueciSenha />} />
          <Route path="/redefinir-senha" element={<RedefinirSenha />} />
          <Route path="/corvia-mail" element={<CorviaMail />} />
          <Route path="/privacidade" element={<PoliticaPrivacidade />} />
          <Route path="/excluir-conta" element={<ExcluirConta />} />
          <Route path="/termos" element={<TermosUso />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </RotasSuspensas>
    );
  }

  if (usuario.profile_completion_required && location.pathname !== "/minha-conta") {
    return <Navigate to="/minha-conta" replace />;
  }

  if (usuario.kyc_required && !usuario.profile_completion_required && location.pathname !== "/verificacao-identidade") {
    return <Navigate to="/verificacao-identidade" replace />;
  }

  const noCardiologySpacesTour = location.pathname === "/tour/cardiology-spaces";
  if (
    usuario.onboarding_pendente &&
    !usuario.profile_completion_required &&
    !usuario.kyc_required &&
    !noCardiologySpacesTour
  ) {
    return <Navigate to="/tour/cardiology-spaces?retorno=/" replace />;
  }

  const investorTourSeen = window.sessionStorage.getItem(INVESTOR_TOUR_SESSION_KEY) === "seen";
  if (
    usuario.investidor &&
    !usuario.profile_completion_required &&
    !usuario.kyc_required &&
    !investorTourSeen &&
    !noCardiologySpacesTour
  ) {
    return <Navigate to="/tour/cardiology-spaces?retorno=/" replace />;
  }

  return (
    <>
      {!cardiologySpacesEnabled() && (
        <OptionalFeatureBoundary nome="personalização da página inicial">
          <HomeQuickActionsPersonalizer />
        </OptionalFeatureBoundary>
      )}
      <RotasSuspensas>
        <Routes>
        <Route element={<Shell />}>
          <Route index element={cardiologySpacesEnabled() ? <CardiologySpacesHome /> : <Painel />} />
          <Route path="apresentacao" element={<Apresentacao />} />
          <Route path="biblioteca" element={<Biblioteca />} />
          <Route path="biblioteca/:slug" element={<Documento />} />
          <Route path="documentos-cientificos-ia" element={<ScientificDocumentAI />} />
          <Route path="doencas" element={<GuiaDoencas />} />
          <Route path="doencas/:slug" element={<GuiaDoenca />} />
          <Route path="triagem-sintomas" element={<TriagemSintomas />} />
          <Route path="fluxogramas" element={<Fluxogramas />} />
          <Route path="diretrizes" element={<Diretrizes />} />
          <Route path="busca" element={<Busca />} />
          <Route path="calculadoras" element={<Calculadoras />} />
          <Route path="calculadoras/:slug" element={<Calculadora />} />
          <Route path="cardiologia-intensiva" element={<CardiologiaIntensiva />} />
          <Route path="medicamentos" element={<Medicamentos />} />
          <Route path="interacoes" element={<Interacoes />} />
          <Route path="condicoes" element={<Condicoes />} />
          <Route path="galeria" element={<Galeria />} />
          <Route path="galeria/:slug" element={<ImagemGaleria />} />
          <Route path="exames" element={<Exames />} />
          <Route path="exames/:slug" element={<Exame />} />
          <Route path="evidencias" element={<Evidencias />} />
          <Route path="evidencias/:slug" element={<Evidencia />} />
          <Route path="estudos" element={<Estudos />} />
          <Route path="estudos/:slug" element={<Estudo />} />
          <Route path="trilhas" element={<Trilhas />} />
          <Route path="trilhas/timeline" element={<TimelineDoencas />} />
          <Route path="material-paciente" element={<MaterialPaciente />} />
          <Route path="material-paciente/:slug" element={<MaterialPacienteDetalhe />} />
          <Route path="emergencia" element={<Emergencia />} />
          <Route path="trilhas/:slug" element={<Trilha />} />
          <Route path="casos-clinicos" element={<CasosClinicos />} />
          <Route path="casos-clinicos/:slug" element={<CasoClinico />} />
          <Route path="checklists" element={<Checklists />} />
          <Route path="checklists/:slug" element={<ChecklistModelo />} />
          <Route path="checklists/alta/:id" element={<ChecklistAlta />} />
          <Route path="indicadores" element={<Indicadores />} />
          <Route path="cursos" element={<Navigate to="/trilhas" replace />} />
          <Route path="cursos/:slug" element={<Navigate to="/trilhas" replace />} />
          <Route path="favoritos" element={<Favoritos />} />
          <Route path="assistente" element={<Assistente />} />
          <Route path="heart-team" element={heartTeamEnabled() ? <HeartTeamVirtual /> : <Navigate to="/" replace />} />
          <Route path="heart-team/:caseId" element={heartTeamEnabled() ? <HeartTeamVirtual /> : <Navigate to="/" replace />} />
          <Route path="whatsapp-assistant" element={whatsappAssistantEnabled() ? <WhatsAppAssistant /> : <Navigate to="/minha-conta" replace />} />
          <Route path="prontuario" element={<Prontuario />} />
          <Route path="exames-ia" element={<CardiovascularExamAI />} />
          <Route path="ecg-ia" element={<CardiovascularExamAI />} />
          <Route path="round" element={<Round />} />
          <Route path="agenda" element={<Agenda />} />
          <Route path="documentos" element={<Templates />} />
          <Route path="exportar" element={<ExportarConteudo />} />
          <Route path="avaliacao-preoperatoria" element={<AvaliacaoPreOperatoria />} />
          <Route path="receituario" element={<Receituario />} />
          <Route path="assinatura" element={<Navigate to="/tour?origem=assinatura&modo=quick" replace />} />
          <Route path="minha-conta" element={<MinhaConta />} />
          <Route path="sincronizacao" element={<Sincronizacao />} />
          <Route path="verificacao-identidade" element={<VerificacaoIdentidade />} />
          <Route path="telediagnostico" element={<Telediagnostico />} />
          <Route path="caixa-de-email" element={<CaixaDeEmail />} />
          <Route path="corvia-mail" element={<CorviaMail />} />
          <Route path="usuarios-online" element={<UsuariosOnline />} />
          <Route path="privacidade" element={<PoliticaPrivacidade />} />
          <Route path="excluir-conta" element={<ExcluirConta />} />
          <Route path="termos" element={<TermosUso />} />
          {usuario.role === "admin" && <Route path="admin" element={<Admin />} />}
          {usuario.role === "admin" && <Route path="admin/usuarios" element={<AdminAssinantes />} />}
          {usuario.role === "admin" && <Route path="admin/usuarios/:id" element={<AdminFichaAssinante />} />}
          {usuario.role === "admin" && <Route path="admin/usuarios/:id/gerenciar" element={<AdminGerenciarUsuario />} />}
          {usuario.role === "admin" && <Route path="fila-telediagnostico" element={<FilaTelediagnostico />} />}
          {usuario.role === "admin" && <Route path="receitas-para-assinatura" element={<ReceitasParaAssinatura />} />}
          {usuario.role === "admin" && <Route path="admin/usuarios-online" element={<Navigate to="/usuarios-online" replace />} />}
          {usuario.role === "admin" && <Route path="admin/operacoes-ia" element={(heartTeamEnabled() || whatsappAssistantEnabled()) ? <AdminAIOperations /> : <Navigate to="/admin" replace />} />}
        </Route>
        <Route path="/tour" element={<Tour />} />
        <Route path="/tour/cardiology-spaces" element={<CardiologySpacesTour />} />
        <Route path="/em-breve" element={<EmBreve />} />
        <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </RotasSuspensas>
    </>
  );
}
