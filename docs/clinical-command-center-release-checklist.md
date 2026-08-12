# CorVIA Clinical Command Center — release checklist

## Product acceptance

- Home communicates “resolver agora”, not “acompanhar pacientes”.
- Search, ask and act are visually obvious in the first viewport.
- Assistant Personal remains visible as a continuous professional companion.
- CorVIA Intelligence is distinct from Assistant Personal.
- Knowledge Graph is visible as a connected-content capability without dominating navigation.
- Empty states are useful and never fabricate data.

## Technical acceptance

- Production build passes.
- No new migration.
- No auth/billing/KYC behavior change.
- No production cron/provider/Hostinger change.
- Existing routes remain valid.
- No cross-user data is persisted in shared storage; command history stays browser-local.
- Agenda/mobility/mail failures degrade safely.
- Keyboard focus and reduced-motion behavior verified.
- Mobile and desktop screenshots reviewed by Rafael before merge.

## Deployment gate

This branch is review-only until explicit human authorization. No production deployment is authorized by this checklist.
