export type ShelfId = "now" | "next" | "references" | "essential";
export type ShelfProfile = Partial<Record<ShelfId, string[]>>;
export type ShelfArchive = { id: string; profileKey: string; profile: ShelfProfile; savedAt: string };
export type ShelfPreferences = {
  schemaVersion: 1;
  updatedAt: string;
  profiles: Record<string, ShelfProfile>;
  archives: ShelfArchive[];
  reserves: Record<string, string[]>;
};
type Definition = { id: ShelfId; capacity: number };
type PreferenceStorage = Pick<Storage, "getItem" | "setItem">;
const IDS: ShelfId[] = ["now", "next", "references", "essential"];
export const SHELF_PREFERENCES_PREFIX = "corvia:cardiology-spaces:shelves:v1";
export const shelfHistoryKey = (userId: number) => `${SHELF_PREFERENCES_PREFIX}:history:${userId}`;
const copy = <T,>(value: T): T => JSON.parse(JSON.stringify(value)) as T;
const strings = (value: unknown): string[] => Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : [];
const unique = (values: string[]) => [...new Set(values)];
const object = (value: unknown): value is Record<string, unknown> => Boolean(value && typeof value === "object" && !Array.isArray(value));
export const shelfProfileItems = (profile: ShelfProfile): string[] => IDS.flatMap((id) => profile[id] || []);

function parseProfile(value: unknown): ShelfProfile {
  const profile: ShelfProfile = {};
  if (object(value)) for (const id of IDS) if (Array.isArray(value[id])) profile[id] = strings(value[id]);
  return profile;
}

export function emptyShelfPreferences(): ShelfPreferences {
  return { schemaVersion: 1, updatedAt: new Date(0).toISOString(), profiles: {}, archives: [], reserves: {} };
}

export function parseShelfPreferences(raw: string | null): ShelfPreferences {
  try {
    const parsed: unknown = JSON.parse(raw || "null");
    if (!object(parsed) || parsed.schemaVersion !== 1 || !object(parsed.profiles)) return emptyShelfPreferences();
    const result = emptyShelfPreferences();
    result.updatedAt = typeof parsed.updatedAt === "string" ? parsed.updatedAt : result.updatedAt;
    for (const [key, value] of Object.entries(parsed.profiles)) {
      if (object(value)) Object.defineProperty(result.profiles, key, { value: parseProfile(value), enumerable: true, writable: true, configurable: true });
    }
    if (object(parsed.reserves)) for (const [key, value] of Object.entries(parsed.reserves)) Object.defineProperty(result.reserves, key, { value: strings(value), enumerable: true, writable: true, configurable: true });
    if (Array.isArray(parsed.archives)) for (const item of parsed.archives) {
      if (!object(item) || typeof item.profileKey !== "string" || !object(item.profile)) continue;
      const profile = parseProfile(item.profile);
      result.archives.push({ id: JSON.stringify([item.profileKey, profile]), profileKey: item.profileKey, profile, savedAt: typeof item.savedAt === "string" ? item.savedAt : result.updatedAt });
    }
    result.archives = mergeArchives(result.archives);
    return result;
  } catch { return emptyShelfPreferences(); }
}

function mergeArchives(...groups: ShelfArchive[][]): ShelfArchive[] {
  const seen = new Set<string>();
  return groups.flat().filter((archive) => !seen.has(archive.id) && Boolean(seen.add(archive.id))).map(copy);
}

function snapshot(preferences: ShelfPreferences, profileKey: string, profile: ShelfProfile, savedAt: string) {
  const id = JSON.stringify([profileKey, profile]);
  if (!preferences.archives.some((archive) => archive.id === id)) preferences.archives.unshift({ id, profileKey, profile: copy(profile), savedAt });
}

/** Preserve every previous profile and every legacy essential, including empty
 * choices and items beyond the new visible capacity. No old key is deleted. */
export function migrateShelfPreferences(preferences: ShelfPreferences, essentials: Record<string, string[]>, actionIdForPath: (path: string) => string): ShelfPreferences {
  const next = copy(preferences);
  for (const [key, profile] of Object.entries(preferences.profiles)) snapshot(next, key, profile, preferences.updatedAt);
  for (const [space, paths] of Object.entries(essentials)) {
    const key = `essential:${space}`;
    const profile = { essential: paths.map(actionIdForPath) };
    snapshot(next, key, profile, preferences.updatedAt);
    if (!Object.prototype.hasOwnProperty.call(next.profiles[key] || {}, "essential")) next.profiles[key] = { ...next.profiles[key], ...profile };
  }
  return next;
}

/** Preview only: the source and current saved profile are never modified. */
export function previewShelfImport(source: ShelfProfile, definitions: Definition[], allowed: ReadonlySet<string>, previousDraft: ShelfProfile = {}, previousReserve: string[] = []) {
  const items = unique(shelfProfileItems(source));
  const available = items.filter((id) => allowed.has(id));
  const profile: ShelfProfile = {};
  let index = 0;
  for (const definition of definitions) {
    profile[definition.id] = available.slice(index, index + definition.capacity);
    index += definition.capacity;
  }
  const selected = new Set(shelfProfileItems(profile));
  return { profile, reserve: unique([...items, ...previousReserve, ...shelfProfileItems(previousDraft)]).filter((id) => !selected.has(id)) };
}

export function shelfReserveFor(preferences: ShelfPreferences, key: string, draft: ShelfProfile): string[] {
  const selected = new Set(shelfProfileItems(draft));
  return unique([...(preferences.reserves[key] || []), ...shelfProfileItems(preferences.profiles[key] || {})]).filter((id) => !selected.has(id));
}

export function saveShelfProfile(preferences: ShelfPreferences, key: string, draft: ShelfProfile, definitions: Definition[], allowed: ReadonlySet<string>, reserve: string[], now = new Date().toISOString()): ShelfPreferences {
  const next = copy(preferences);
  const previous = preferences.profiles[key];
  if (previous) snapshot(next, key, previous, preferences.updatedAt);
  const profile: ShelfProfile = {};
  for (const definition of definitions) profile[definition.id] = unique(draft[definition.id] || []).filter((id) => allowed.has(id)).slice(0, definition.capacity);
  const selected = new Set(shelfProfileItems(profile));
  next.reserves[key] = unique([...(preferences.reserves[key] || []), ...reserve, ...shelfProfileItems(previous || {}), ...shelfProfileItems(draft)]).filter((id) => !selected.has(id));
  next.profiles[key] = profile;
  next.updatedAt = now;
  return next;
}

export function shelfOrganizationLabel(profileKey: string): string {
  const [mode, space] = profileKey.split(":");
  const modes: Record<string, string> = { complete: "Completo", essential: "Essencial", scientific: "Ciência & Ensino" };
  const spaces: Record<string, string> = { consultorio: "Consultório", hospital: "Hospital", ensino: "Ensino", pesquisa: "Pesquisa", gestao: "Gestão", descobrir: "Descobrir", evidencias: "Evidências", aprender: "Aprender", ensinar: "Ensinar", produzir: "Produzir" };
  return `${modes[mode] || "Organização anterior"} · ${spaces[space] || "Perfil anterior"}`;
}

/** User-scoped memory survives route unmounts when storage is denied/full.
 * The independent history is written first: a failed backup never permits a
 * destructive overwrite of the last durable preference. */
export function createShelfPreferenceStore(storage: () => PreferenceStorage | null = () => typeof window === "undefined" ? null : window.localStorage) {
  const memory = new Map<number, ShelfPreferences>();
  const pending = new Set<number>();
  function read(userId: number): ShelfPreferences {
    const cached = memory.get(userId);
    if (cached && pending.has(userId)) return copy(cached);
    let result = cached ? copy(cached) : emptyShelfPreferences();
    try {
      const saved = storage();
      if (saved) {
        result = parseShelfPreferences(saved.getItem(`${SHELF_PREFERENCES_PREFIX}:${userId}`));
        const history = parseShelfPreferences(saved.getItem(shelfHistoryKey(userId)));
        result.archives = mergeArchives(result.archives, history.archives, cached?.archives || []);
        for (const [key, profile] of Object.entries(cached?.profiles || {})) if (JSON.stringify(profile) !== JSON.stringify(result.profiles[key])) snapshot(result, key, profile, cached!.updatedAt);
      }
    } catch { /* Keep anything already read; failure is not permission to reset. */ }
    memory.set(userId, copy(result));
    return copy(result);
  }
  function write(userId: number, preferences: ShelfPreferences): boolean {
    const previous = read(userId);
    const next = copy(preferences);
    next.archives = mergeArchives(next.archives, previous.archives);
    for (const [key, profile] of Object.entries(previous.profiles)) if (JSON.stringify(profile) !== JSON.stringify(next.profiles[key])) snapshot(next, key, profile, previous.updatedAt);
    memory.set(userId, copy(next));
    pending.add(userId);
    try {
      const saved = storage();
      if (!saved) return false;
      if (next.archives.length) saved.setItem(shelfHistoryKey(userId), JSON.stringify({ ...emptyShelfPreferences(), archives: next.archives }));
      saved.setItem(`${SHELF_PREFERENCES_PREFIX}:${userId}`, JSON.stringify(next));
      pending.delete(userId);
      return true;
    } catch { return false; }
  }
  function sync(userId: number, raw: string | null): ShelfPreferences {
    const previous = memory.get(userId) || read(userId);
    const next = parseShelfPreferences(raw);
    if (pending.has(userId)) {
      // Another tab cannot discard changes whose durable write failed here.
      for (const [key, profile] of Object.entries(next.profiles)) snapshot(previous, key, profile, next.updatedAt);
      previous.archives = mergeArchives(previous.archives, next.archives);
      memory.set(userId, copy(previous));
      return copy(previous);
    }
    next.archives = mergeArchives(next.archives, previous.archives);
    for (const [key, profile] of Object.entries(previous.profiles)) if (JSON.stringify(profile) !== JSON.stringify(next.profiles[key])) snapshot(next, key, profile, previous.updatedAt);
    memory.set(userId, copy(next));
    return copy(next);
  }
  return { read, write, sync };
}

export const shelfPreferenceStore = createShelfPreferenceStore();
