import { useCorviaTheme } from "../lib/corviaTheme";
import ScientificJourneyScene, { type ScientificJourney } from "./ScientificJourneyScene";

export type CardiologySpaceSceneId =
  | "consultorio" | "hospital" | "ensino" | "pesquisa" | "gestao"
  | "descobrir" | "evidencias" | "aprender" | "ensinar" | "produzir";

type ClinicalScene = Exclude<CardiologySpaceSceneId, ScientificJourney>;
const SCENE_BY_SPACE: Record<ClinicalScene, string> = {
  consultorio: "/spaces/corvia-room-consultorio.jpg",
  hospital: "/spaces/corvia-room-hospital.jpg",
  ensino: "/spaces/corvia-room-ensino.jpg",
  pesquisa: "/spaces/corvia-room-pesquisa.jpg",
  gestao: "/spaces/corvia-room-gestao.jpg",
};

const LIGHT_SCENE_BY_SPACE: Record<ClinicalScene, string> = {
  consultorio: "/spaces/corvia-room-consultorio-light-640.webp",
  hospital: "/spaces/corvia-room-hospital-light-640.webp",
  ensino: "/spaces/corvia-room-ensino-light-640.webp",
  pesquisa: "/spaces/corvia-room-pesquisa-light-640.webp",
  gestao: "/spaces/corvia-room-gestao-light-640.webp",
};

/**
 * Cenas arquitetônicas produzidas a partir da prancha aprovada. A imagem é
 * estritamente decorativa: o nome e a descrição acessíveis pertencem ao botão
 * do portal, evitando duplicação para leitores de tela.
 */
export default function CardiologySpaceScene({ space }: { space: CardiologySpaceSceneId }) {
  const { theme } = useCorviaTheme();
  if (!(space in SCENE_BY_SPACE)) return <ScientificJourneyScene journey={space as ScientificJourney} />;
  const scene = theme === "light" ? LIGHT_SCENE_BY_SPACE[space as ClinicalScene] : SCENE_BY_SPACE[space as ClinicalScene];

  return (
    <img
      className="spaces-door__scene"
      src={scene}
      data-scene-theme={theme}
      alt=""
      width="1200"
      height="800"
      decoding="async"
      draggable="false"
    />
  );
}
