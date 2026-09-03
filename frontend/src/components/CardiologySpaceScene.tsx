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
  descobrir: "/spaces/corvia-room-consultorio.jpg",
  evidencias: "/spaces/corvia-room-hospital.jpg",
  aprender: "/spaces/corvia-room-ensino.jpg",
  ensinar: "/spaces/corvia-room-pesquisa.jpg",
  produzir: "/spaces/corvia-room-gestao.jpg",
};

const LIGHT_SCENE_BY_SPACE: Record<CardiologySpaceSceneId, string> = {
  consultorio: "/spaces/corvia-room-consultorio-light-640.webp",
  hospital: "/spaces/corvia-room-hospital-light-640.webp",
  ensino: "/spaces/corvia-room-ensino-light-640.webp",
  pesquisa: "/spaces/corvia-room-pesquisa-light-640.webp",
  gestao: "/spaces/corvia-room-gestao-light-640.webp",
  descobrir: "/spaces/corvia-room-consultorio-light-640.webp",
  evidencias: "/spaces/corvia-room-hospital-light-640.webp",
  aprender: "/spaces/corvia-room-ensino-light-640.webp",
  ensinar: "/spaces/corvia-room-pesquisa-light-640.webp",
  produzir: "/spaces/corvia-room-gestao-light-640.webp",
};

/**
 * Cenas arquitetônicas produzidas a partir da prancha aprovada. A imagem é
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
