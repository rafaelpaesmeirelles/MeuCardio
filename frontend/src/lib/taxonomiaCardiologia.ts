export type AreaCardiologia = {
  id: string;
  label: string;
  descricao: string;
};

export const AREAS_CARDIOLOGIA: AreaCardiologia[] = [
  { id: "pediatrica", label: "Cardiologia pediátrica", descricao: "Infância, adolescência, cardiopatias congênitas e cardiologia fetal" },
  { id: "cardiooncologia", label: "Cardio-Oncologia", descricao: "Cardiotoxicidade, prevenção, monitorização e sobrevivência" },
  { id: "gestacao", label: "Gestação e puerpério", descricao: "Gravidez, parto, puerpério, amamentação e planejamento reprodutivo" },
  { id: "geriatria", label: "Cardio-Geriatria", descricao: "Fragilidade, multimorbidade e cuidado cardiovascular do idoso" },
  { id: "coronaria", label: "Doença coronariana", descricao: "Síndromes coronarianas, isquemia e revascularização" },
  { id: "insuficiencia", label: "Insuficiência cardíaca e miocárdio", descricao: "Insuficiência cardíaca, cardiomiopatias e transplante" },
  { id: "arritmias", label: "Arritmias e eletrofisiologia", descricao: "Ritmo, síncope, dispositivos e morte súbita" },
  { id: "valvopatias", label: "Valvopatias", descricao: "Doenças valvares, intervenção e seguimento" },
  { id: "hipertensao", label: "Hipertensão e prevenção", descricao: "Risco cardiovascular, hipertensão, lípides e prevenção" },
  { id: "vascular", label: "Aorta, vascular e tromboembolismo", descricao: "Aortopatias, circulação pulmonar e doença vascular" },
  { id: "inflamatoria", label: "Pericárdio, endocardite e inflamação", descricao: "Doenças pericárdicas, infecciosas e inflamatórias" },
  { id: "esporte", label: "Cardiologia do esporte e do exercício", descricao: "Coração de atleta, triagem pré-participação e prescrição segura de exercício" },
  { id: "geral", label: "Cardiologia Geral", descricao: "Avaliação, prevenção, diagnóstico e cuidado cardiovascular integrado do adulto" },
];

export function normalizarBusca(valor: string) {
  return valor
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase("pt-BR")
    .trim();
}

export function areaDaCardiologia(...campos: Array<string | null | undefined>): AreaCardiologia {
  const texto = normalizarBusca(campos.filter(Boolean).join(" "));
  const procurar = (...termos: string[]) => termos.some((termo) => texto.includes(termo));

  if (procurar("pediatr", "neonat", "fetal", "congenit", "kawasaki", "reumatica")) return AREAS_CARDIOLOGIA[0];
  if (procurar("cardio-onco", "cardioonco", "oncolog", "cardiotox", "quimioter", "antracic", "cancer")) return AREAS_CARDIOLOGIA[1];
  if (procurar("gravidez", "gesta", "puerper", "amament", "lacta", "materna")) return AREAS_CARDIOLOGIA[2];
  if (procurar("geriatr", "idoso", "fragilidade", "longevidade")) return AREAS_CARDIOLOGIA[3];
  if (procurar("coron", "isquemi", "infarto", "angina", "revascular", "aterosclero")) return AREAS_CARDIOLOGIA[4];
  if (procurar("insuficiencia cardiaca", "cardiomiop", "miocard", "transplante", "choque cardiogenico")) return AREAS_CARDIOLOGIA[5];
  if (procurar("arrit", "fibril", "taquic", "bradic", "eletrofisio", "marcapasso", "ressincron", "sincope", "morte subita")) return AREAS_CARDIOLOGIA[6];
  if (procurar("valv", "aortica", "mitral", "tricusp", "pulmonar")) return AREAS_CARDIOLOGIA[7];
  if (procurar("hipertens", "prevenc", "dislip", "lipid", "diabetes", "risco cardiovascular", "obesidade")) return AREAS_CARDIOLOGIA[8];
  if (procurar("aorta", "vascular", "trombo", "embolia", "pulmonar", "carot", "perifer")) return AREAS_CARDIOLOGIA[9];
  if (procurar("pericard", "endocard", "miocardite", "inflama", "infecc")) return AREAS_CARDIOLOGIA[10];
  if (procurar("esporte", "exercicio", "atleta", "atletica", "treinamento fisico", "cardiologia esportiva", "morte subita no esporte", "coracao de atleta", "pre-participacao esportiva", "preparticipacao esportiva")) return AREAS_CARDIOLOGIA[11];
  return AREAS_CARDIOLOGIA[12];
}
