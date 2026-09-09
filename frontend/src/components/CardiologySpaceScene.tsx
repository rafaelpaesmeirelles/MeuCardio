import { useCorviaTheme } from "../lib/corviaTheme";

export type CardiologySpaceSceneId =
  | "consultorio" | "hospital" | "ensino" | "pesquisa" | "gestao"
  | "descobrir" | "evidencias" | "aprender" | "ensinar" | "produzir";

const SCENE_BY_SPACE: Record<CardiologySpaceSceneId, string> = {
  consultorio: "/spaces/corvia-room-consultorio.jpg",
  hospital: "/spaces/corvia-room-hospital.jpg",
  ensino: "/spaces/corvia-room-ensino.jpg",
  pesquisa: "/spaces/corvia-room-pesquisa.jpg",
  gestao: "/spaces/corvia-room-gestao.jpg",
  descobrir: "/spaces/corvia-science-descobrir-dark-768.webp",
  evidencias: "/spaces/corvia-science-evidencias-dark-768.webp",
  aprender: "/spaces/corvia-science-aprender-dark-768.webp",
  ensinar: "/spaces/corvia-science-ensinar-dark-768.webp",
  produzir: "/spaces/corvia-science-produzir-dark-768.webp",
};

const LIGHT_SCENE_BY_SPACE: Record<CardiologySpaceSceneId, string> = {
  consultorio: "/spaces/corvia-room-consultorio-light-640.webp",
  hospital: "/spaces/corvia-room-hospital-light-640.webp",
  ensino: "/spaces/corvia-room-ensino-light-640.webp",
  pesquisa: "/spaces/corvia-room-pesquisa-light-640.webp",
  gestao: "/spaces/corvia-room-gestao-light-640.webp",
  descobrir: "/spaces/corvia-science-descobrir-light-768.webp",
  evidencias: "/spaces/corvia-science-evidencias-light-768.webp",
  aprender: "/spaces/corvia-science-aprender-light-768.webp",
  ensinar: "/spaces/corvia-science-ensinar-light-768.webp",
  produzir: "/spaces/corvia-science-produzir-light-768.webp",
};

/**
 * Cenas arquitetônicas dos espaços clínicos e científicos. A imagem é
 * estritamente decorativa: o nome e a descrição acessíveis pertencem ao botão
 * do portal, evitando duplicação para leitores de tela.
 */
export default function CardiologySpaceScene({ space }: { space: CardiologySpaceSceneId }) {
  const { theme } = useCorviaTheme();
  const scene = theme === "light" ? LIGHT_SCENE_BY_SPACE[space] : SCENE_BY_SPACE[space];

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
