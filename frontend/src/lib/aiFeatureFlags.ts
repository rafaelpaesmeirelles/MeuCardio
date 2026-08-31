function enabled(value: string | undefined): boolean {
  return value?.trim().toLowerCase() === "true";
}

export function heartTeamEnabled(): boolean {
  return enabled(import.meta.env.VITE_HEART_TEAM_ENABLED);
}

export function whatsappAssistantEnabled(): boolean {
  return enabled(import.meta.env.VITE_WHATSAPP_ASSISTANT_ENABLED);
}
