export type TimelineTopic = { tema: string; total_marcos: number };
export type TimelineSummary = {
  tema: string;
  total: number;
  primeiro_ano: number | null;
  ultimo_ano: number | null;
  marcos: Array<{ ano: number; titulo: string; rota: string; slug: string }>;
};

const key = (userId: number) => `corvia:scientific-timeline:topic:${userId}`;

export function lastTimelineTopic(userId?: number) {
  try { return userId ? sessionStorage.getItem(key(userId)) || "" : ""; }
  catch { return ""; }
}

export function rememberTimelineTopic(userId: number | undefined, topic: string) {
  try { if (userId && topic) sessionStorage.setItem(key(userId), topic); }
  catch { /* Browsing remains available without session storage. */ }
}
