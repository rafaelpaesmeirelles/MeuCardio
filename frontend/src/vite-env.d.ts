/// <reference types="vite/client" />
/// <reference types="vite-plugin-pwa/client" />

interface ImportMetaEnv {
  readonly VITE_HEART_TEAM_ENABLED?: string;
  readonly VITE_WHATSAPP_ASSISTANT_ENABLED?: string;
  readonly VITE_API_URL?: string;
  readonly VITE_CARDIOLOGY_SPACES_ENABLED?: string;
}
interface ImportMeta {
  readonly env: ImportMetaEnv;
}
