type ScheduledTarget = {
  starts_at?: string;
  ends_at?: string | null;
  source?: string;
  target_type?: string;
  arrival_buffer_minutes?: number;
};

export function mobilitySchedule(target: ScheduledTarget | null, durationSeconds?: number) {
  const start = target?.starts_at ? new Date(target.starts_at) : null;
  if (!start || !Number.isFinite(start.getTime())) return null;
  const returning = target?.source === "return" || target?.target_type === "day_return";
  const hasDuration = Number.isFinite(durationSeconds) && Number(durationSeconds) > 0;
  const buffer = Math.max(0, target?.arrival_buffer_minutes || 0) * 60;
  const departure = returning ? start : hasDuration
    ? new Date(start.getTime() - (Math.ceil(Number(durationSeconds)) + buffer) * 1000)
    : null;
  return { start, departure, returning };
}

export function scheduleDateTime(date: Date) {
  return `${date.toLocaleDateString("pt-BR", { weekday: "short", day: "2-digit", month: "2-digit" })} · ${date.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}`;
}
