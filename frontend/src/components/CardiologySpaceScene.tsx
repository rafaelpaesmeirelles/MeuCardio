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

/**
 * Cenas arquitetônicas produzidas a partir da prancha aprovada. A imagem é
 * estritamente decorativa: o nome e a descrição acessíveis pertencem ao botão
 * do portal, evitando duplicação para leitores de tela.
 */
export default function CardiologySpaceScene({ space }: { space: CardiologySpaceSceneId }) {
  return (
    <img
      className="spaces-door__scene"
      src={SCENE_BY_SPACE[space]}
      alt=""
      width="1200"
      height="800"
      decoding="async"
      draggable="false"
    />
  );
}
