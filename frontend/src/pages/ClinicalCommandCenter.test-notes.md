# Focused validation — Clinical Command Center

Before merge/deploy, validate only the new launch surface and its integration points:

- TypeScript + Vite production build.
- Authenticated `/` renders the new Command Center.
- Clinical Command Bar routes search/action intents without runtime error.
- Quick actions preserve existing routes.
- Radar handles empty guideline/study states.
- Intelligence handles unavailable counts safely.
- Assistant rail handles: no agenda, agenda present, mobility disabled, geolocation denied, route available, Mail unavailable/available.
- Mobile: 390x844 and 412x915; no horizontal page overflow; dock does not cover content; action sheet opens/closes; keyboard/focus remains visible.
- Desktop: 1440x900 and 1920x1080; rail remains readable and sticky.
- Existing non-Home routes keep their previous light-mode shell/layout.
- No production deploy is authorized by this branch.
