export type CardiologySpaceSceneId =
  | "consultorio" | "hospital" | "ensino" | "pesquisa" | "gestao"
  | "descobrir" | "evidencias" | "aprender" | "ensinar" | "produzir";

const SCENE_BY_SPACE: Record<CardiologySpaceSceneId, string> = {
  consultorio: "consultorio",
  hospital: "hospital",
  ensino: "ensino",
  pesquisa: "pesquisa",
  gestao: "gestao",
  descobrir: "consultorio",
  evidencias: "hospital",
  aprender: "ensino",
  ensinar: "pesquisa",
  produzir: "gestao",
};

/**
 * Cenas arquitetônicas produzidas a partir da prancha aprovada. A imagem é
 * estritamente decorativa: o nome e a descrição acessíveis pertencem ao botão
 * do portal, evitando duplicação para leitores de tela.
 */
export default function CardiologySpaceScene({ space, priority = false }: { space: CardiologySpaceSceneId; priority?: boolean }) {
  const scene = `/spaces/corvia-room-${SCENE_BY_SPACE[space]}`;
  return (
    <picture className="spaces-door__picture">
      <source
        type="image/webp"
        srcSet={`${scene}-640.webp 640w, ${scene}-1280.webp 1280w`}
        sizes="(max-width: 950px) 116px, (max-width: 1440px) 18vw, 290px"
      />
      <img
        className="spaces-door__scene"
        src={`${scene}.jpg`}
        alt=""
        width="1536"
        height="1024"
        loading={priority ? "eager" : "lazy"}
        fetchPriority={priority ? "high" : "auto"}
        decoding="async"
        draggable="false"
      />
    </picture>
  );
}
