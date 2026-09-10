# Universal Favorites, internal scientific originals and owner-approved clinical updates

Date: 2026-09-10. Repository: rafaelpaesmeirelles/MeuCardio.
Branch: codex/universal-favorites-20260910. PR: 922.
Base: 97270582d93cac6327c9d843395fa704be831373 (PR921 deployed and independently verified).

## User authority and release constraints

The owner requested universal Meus Favoritos after the previous deployment, with original, Portuguese summary and translation when available. Subsequent explicit instructions require Intelligence to store originals, enable consultation inside CorVIA, add them to the collection, and submit proposed clinical/treatment updates to the owner under “Mudanças de Conduta Baseadas em Novas Evidências para Aprovação” before applying them. Autonomous normal deployment is authorized. This approval is implementation authority, not advance approval of individual clinical changes.

“Sem novo ci backend” remains binding. PR922 has its own sealed decision; no full or focused backend CI is requested. Narrow local regression tests address authorization, ownership, migrations, concurrency and integration risks. Corpus, inventory, frontend, visual, canonical RC2 and deployment gates remain in force. No bypass/admin merge, no production source edits and no paid AI test calls.

## Implementation and boundaries

- Existing favorites are retained; integer identities remain compatible while canonical slugs support calculators, scientific readers and trusted registered function shortcuts. Metadata resolution is batched. Unavailable/deleted content remains removable without revealing unpublished titles. Favorites do not grant access.
- Own scientific documents remain private. Favorites link to the selected original, summary or translation. Reading never authorizes analysis, incorporation or payment. Owner-scoped file access remains separate from shared scientific assets; PDF viewing is sandboxed and blob URLs are revoked when leaving.
- The original reader uses the already-stored licensed JATS XML, verifies source identity and integrity and renders extracted original text safely. It retains an XML download and the publisher link. Text rendering does not claim to reproduce PDF layout, figures or supplemental files.
- Original-publication catalog entries require stored original, identity/hash/license and public-source provenance. They are distinct from reviewed clinical guidance. DOI identity avoids duplicate catalog entries when a published document or study already represents the source. Initial search covers bibliographic metadata; encrypted full-article text is not added to lexical search in this change.
- Each clinical target receives an individually reviewable proposal, and new pending proposals trigger an owner-only in-app notice. Clinical proposals are drafts until the configured owner administrator explicitly approves them. The UI shows proposed changes, sources and affected content. Approval must match the reviewed proposal/version and the unchanged target; it is recorded and applied transactionally. Rejection does not change published guidance. Legacy AI confirmation is not human approval. Previously published historical changes must not be relabeled as owner-approved.
- Emergency packages read their referenced documents. Approved changes to those documents propagate to connected online readers; this does not mean automatic reconstruction of every decision-tree node or immediate synchronization of offline copies.
- Study-track access requires both published and reviewed state. Active AI processing is distinguished from failed processing.
- Dormant course/checkout routes remain aliases to learning tracks. Private patient records are not converted into shared scientific favorites or source assets.

## Local verification evidence

Completed before final integration:
- CI decision: 73 policy tests and two exact PR/main contract checks passed. Scope wording subsequently extended without changing identity or relaxing gates.
- Favorites UI: 8 focused React tests passed (2.27s): canonical target operations, duplicate-click control, per-user isolation, status failures, unavailable removal and private links.
- Private favorite links: 4 focused React tests passed (1.94s): correct document/section, no paid mutation, malformed identity rejection and stale-response isolation.
- Internal original reader: 12 focused React tests passed (2.61s), including source-key validation and stale-source response isolation; no paid calls.
- Favorites backend: 8 focused tests passed (41.76s), including migration compatibility, aliases, ownership, availability, canonical conflicts, function gates and batched metadata.

- Administrative UI and owner notice: 10 behavioral tests passed across two focused runs; exact canonical function registry parity (44), explicit approval, conflicts, per-user isolation and inconclusive verification rendering.
- Original catalog UI: 4 focused tests passed for internal entry, validation, section and pagination.
- Original/status backend: 3 focused tests passed, including stored original integrity and public-source eligibility withdrawal; no repetition of the eight Favorites tests.
- Production frontend build passed (TypeScript and Vite, Vite build 33.59s). Entry 305,996 bytes / 95,479 gzip; 80 split page entries; precache 3,126,285 bytes. Existing budgets unchanged.
- Route inventory explicitly increased from 77 to 78 for the new administrative route; matching App/registry and admin gate/group/space remain asserted.
- Visual QA now includes 16 additional synthetic cases (mobile/desktop, both themes, owner and other roles, pending proposals and mixed favorites). Existing cases/tolerances remain; no local duplicate browser matrix was run.

- Final administrative UI patch: one additional focused test passed (2.77s). Backend can_approve=false is enforced by the UI and handler, with rejection still available; empty impact_scope no longer crashes.
- Clinical approval backend: 14 focused tests passed (66.34s); lightweight list serialization then passed its affected test (8.35s). Three new provenance cases and two affected pipeline regressions passed (30.44s): source changes before saving or enqueueing, and legacy/mismatched analysis cache.
- Original catalog: four PostgreSQL tests passed on the optimized SQL (18.90s). EXPLAIN ANALYZE in an isolated synthetic database with 12,000 documents and 100 originals reported 39.2ms planning and 522ms execution; transaction rolled back. These are synthetic measurements, not a production latency guarantee.
- Independent read-only review concluded with no remaining blockers: exact owner approval, source and target concurrency, audit proof, legacy-path guards, source-cache provenance, RAG consistency, access boundaries, original identity and deduplication.

Final CI, exact release commits, gate runs and read-only production verification are recorded in PR922 after the normal rollout. This implementation audit precedes deployment.

## Operational dependencies preserved

PR921 is already live at the base commit. Original acquisition and Portuguese processing are progressive; the implementation does not certify that all approximately 12,000 scientific items have full translations. Existing institutional and subscriber AI budgets remain unchanged. WhatsApp has a visible entry, but real activation still depends on configured Meta integration; no sandbox activation or outbound WhatsApp message is part of this change.


## First PR gate follow-up

Implementation head bd8ce12e72d7153ae3076a47133bf9e1f0977247 passed CI (both backend test jobs skipped), frontend, corpus database/inventory, deep inventory, route coverage and approved-reference QA. RC2 stopped at the static feature inventory because the newly authorized admin route/router had not been added to that second inventory. They are now registered explicitly, with the new supporting files protected; existing expectations remain.

Visual QA completed the existing 32 mobile and 10 Intelligence cases with no page errors, then stopped when the new helper attempted to use the Home galaxy control on an internal page. The helper now operates the actual account-menu theme radio control, closes the overlay and asserts the resulting theme. No application UI, tolerance or existing case was removed. The corrected combined head must pass normal gates before merge.


## Second visual gate follow-up

Head 8c6b3f51f72914456ffe60376ed9ba187a6b27ec passed RC2 and the other required PR gates; both backend test jobs remained skipped. Visual QA again completed the existing mobile and Intelligence cases without page errors. The new pending-notice fixture was bypassed by the service worker retained from those preceding cases: actual QA API responses contained no pending proposals. The synthetic Favorites/approval cases now use their own authenticated browser context with service workers blocked, while the existing real-app matrix keeps its original context and behavior. Assertions and tolerances remain unchanged; no approval mutation is permitted.


## Visual inspection before merge

Head 53c9bcbbc73704f915907c57efada70a95e48a81 passed every required PR gate, with both backend jobs skipped. Visual QA produced 93 images: 15 pages, 10 Intelligence surfaces, 32 mobile matrix cases, and 16 Favorites/approval fixture cases; no page errors, test failures or approval mutations. Direct inspection of the generated screenshots nevertheless found weak light-theme contrast in the new pending notice, Favorites links and controls. Merge was held for a scoped contrast correction rather than treating passing geometry assertions as proof of legibility. Existing dark/light layouts and release budgets remain protected.

Scoped light-theme link/control colors and the shared notice now use the active palette. CSS parsing and syntax checks passed; the declared ink/panel pair measures 10.84:1. Visual QA records computed contrast with alpha composition, requires 4.5:1 for ordinary text and 3:1 for large text, and reports complex unresolved paint stacks as indeterminate for direct screenshot review. Numerical probes passed, including translucent foreground and inherited background cases. No local browser matrix or backend CI was added.
