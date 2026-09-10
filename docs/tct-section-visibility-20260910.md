# Tudo com Tudo: complete section visibility and published disease overview

Date: 2026-09-10. PR: #919. Baseline production: `02ad2d6a38301667a82eb60444b531d1e1fcd4e1`.

## Reproduced problem

Read-only production catalogue/search inspection confirmed that both `fibrilacao-atrial` and `fibrilacao-atrial-no-idoso` were already published and returned by search. The UI removed the primary disease from its Guide section because it also rendered a summary card above the results. This made the Guide appear to contain only the geriatric entry.

The same atrial-fibrillation query returned 674 eligible results, including 147 documents, but the first global page of 100 contained just one item classified as a guideline. Across the document pages there were six entries under the existing guideline classification, including the Brazilian 2025 and ESC 2024 entries. Six classified entries must not be interpreted as six independently verified guidelines: the existing source metadata includes a trial labelled as a guideline and topic overviews. This release does not silently rewrite scientific classifications or source evidence.

The UI derived sections and their apparent totals from loaded rows. It therefore omitted sections absent from the first page and showed partial counts as if they were final. Normalization also replaced underscores in canonical content types before checking their identity.

## General correction

The search API now classifies eligible candidates into the existing 17 presentation sections before pagination, returns `por_secao` and each result's `secao`, and accepts a validated section filter combined with `frente` by intersection. Publication, useful-relationship eligibility, ranking and alias resolution remain in place. Selecting an empty section cannot activate a broader fallback when the unfiltered full-text candidate set already has matches. Calculators share the section/count contract. Existing non-paginated RAG SQL is unchanged.

The UI renders every section with a positive API total, including sections absent from the first global page. It distinguishes loaded results from the section total and allows loading one section independently. Section and global cursors are separate, responses are deduplicated by typed canonical identity, and stale responses from another query are ignored. The primary disease remains in the Guide section with its own badge. Canonical content types retain their identity.

The disease overview fetches the existing published disease detail and presents definition, epidemiology/context, clinical presentation and diagnostic foundations. Longer sections expand by whole content blocks, and original references and the full guide remain accessible. Loading failures retain the available summary and offer retry. Topic changes clear prior content. This is presentation of published material, not generated medical text or a new paid AI call.

## Local verification and independent review

- Seven new backend regression scenarios passed locally: atrial fibrillation, hypertension alias, medication alias, free text, literal fallback, calculators and SQL compatibility.
- The existing 13-front search regression passed locally.
- Non-paginated RAG SQL and count SQL were compared against the baseline and are textually identical.
- Eight React search interaction scenarios passed, covering missing-first-page sections, primary disease, per-section loading, concurrent global/section responses, deduplication, stale responses, retries and duplicate clicks.
- Five overview rendering scenarios passed, covering structured published content, sources, whole-block expansion, failure/retry and topic isolation.
- A separate agent reviewed the backend, integrated search UI and overview and reported no blocking issue. Integrated TypeScript checking passed (`tsc --noEmit`, exit 0); `git diff --check` passed.

These are focused local checks; no new backend CI suite or full backend suite was run. The persistent release-owner instruction, “Sem novo ci backend”, is recorded for this specific PR and its verified main integration without issuing a passing backend test certificate or reusing PR918's decision.

## Release constraints

Scientific sources, hashes, publication approvals and quarantine are unchanged. Normal corpus, authenticated smoke, frontend/visual and deployment gates remain independent. This report does not claim clinical completeness for every query or a measured gain from paid semantic AI. The prior paid comparison was not completed because that experiment received a provider credit error.

## Deployment status

Implementation and local checks are in progress; production is still the baseline until the normal deployment is verified.
