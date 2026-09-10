#!/usr/bin/env python3
"""Reproduce the scoped release from existing authorizations; never edit sources.

Offline only: Git objects and repository files, no database or provider calls.
Requires PyYAML. Historical snapshots are extracted into a temporary directory.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter
from contextlib import contextmanager
from hashlib import sha1, sha256
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import tempfile
from typing import Any, Mapping

import yaml

YAML_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
GIT_OBJECT_ROOT = None

BASELINE = "fedf818cbb248869a20f2db2949e8fe9884f90c7"
PR_BASE = "fb9e1ae2f23885caedc6fd2fc9886bb61e4d861b"
PR_FINAL = "c1eafa1e674b11ab9946e87a70f098a921e425ce"
THEME_ANCHOR = "800a159e09c87176c9c5bc0f53978495dd5a8de9"
THEME_PROOF = "docs/scoped-corpus-theme-normalization-20260910.json"
THEME_MODULE = "backend/app/services/canonical_themes.py"
PACK_SHA = "9c5a671b37558f3bb71ac338d9069845ccc95c373f25bf22a4d474f71a9c92c9"
MANIFEST_V1 = "editorial-approvals/full-corpus-release-20260907.json"
PACK = "releases/scientific-20260909/reviewed-content.json"
HANDOFF = "docs/HANDOFF-producao-prevalentes-20260909.md"
ROUND2 = "docs/prevalentes-round2-release-application-20260909.md"
EVIDENCE = "docs/scoped-corpus-release-evidence-20260910.json"
MANIFEST = "editorial-approvals/scoped-corpus-release-20260910.json"
REPORT = "docs/scoped-corpus-release-provenance-20260910.json"
MEMO = "docs/scoped-corpus-release-provenance-20260910.md"
REVIEWED_391 = "releases/scientific-20260910-unpublished/reviewed-package.json"
REVIEWED_391_SHA = "0f2b139fba0ecd111f935603aad2390a1c1f4afe452d8d2e58cd2a19a915c993"
INTEGRATED_391 = "releases/scientific-20260910/canonical-integration.json"
INTEGRATED_391_SHA = "625bf15746f765468df8402530cbbd7f978918647f014b6a2941533195696de6"
SUPPLEMENT_7 = "releases/scientific-20260910/supplement-publication-items.json"
SUPPLEMENT_7_SHA = "a58a56846520d607745e40a9e2e23274cfcb6a4268ca704be45c81dff6e6aa40"
INTEGRATED_7 = "releases/scientific-20260910/supplement-canonical-manifest.json"
INTEGRATED_7_SHA = "dcc4920247abe9af76c14fbfda0e717ab8fcf5e1ebbc823ac7784835cde14018"
SUPERSESSIONS = "docs/scoped-corpus-review-supersessions-20260910.json"
REVIEW_SUPERSESSIONS = {
    "tirzepatida-e-semaglutida-efeito-sobre-a-pressao-arterial-metanalise-de-32-ensaios": {
        "source_sha256": "c2bacc1117bb19c0c167288d0ce62157f6ff56d926d5574c3b71bb623bab14bd",
        "previous_merge_into": "agonistas-de-glp-1-gip-e-pressao-arterial-magnitude-e-risco-diferencial-de-hipotensao",
        "reason": "A ficha kind=estudo detalha Chen, 32 ensaios, busca, eventos adversos, subgrupos e limitações; o destino anterior kind=documento é síntese multifuentes de Chen e retatrutida. Os formatos revisados são complementares, não cópias literais.",
    },
    "pirtobrutinibe-btk-nao-covalente-versus-ibrutinibe-o-ensaio-bruin-cll-314": {
        "source_sha256": "dd62787e50a8a11bd2c7e67fd43a8f93233a88d1fac5f56201dc441f0425354c",
        "previous_merge_into": "pirtobrutinibe-inibidor-de-btk-nao-covalente-e-menor-toxicidade-cardiovascular",
        "reason": "A ficha kind=estudo detalha desenho, estratificação, ORR por população e situação regulatória do BRUIN CLL-314; o destino anterior kind=documento reúne BRUIN fase1/2, CLL-314 e metanálise em rede. Os formatos revisados são complementares, não cópias literais.",
    },
}
FRONTS = {
    "documentos": "content", "galeria": "galeria/metadados.json",
    "exames": "exames/metadados.json", "evidencias": "evidencias/metadados.json",
    "estudos": "estudos/metadados.json", "medicamentos": "medicamentos/metadados.json",
    "checklists": "checklists/metadados.json", "casos_clinicos": "casos-clinicos/metadados.json",
    "trilhas": "trilhas/metadados.json", "material_paciente": "material-paciente/metadados.json",
    "emergencia": "emergencia/metadados.json", "doencas_especializadas": "doencas/metadados.json",
    "triagem_sintomas": "triagem-sintomas/metadados.json",
}
KINDS = {"documento": "documentos", "caso_clinico": "casos_clinicos", "estudo": "estudos",
         "evidencia": "evidencias", "exame": "exames", "material_paciente": "material_paciente",
         "trilha": "trilhas", "medicamento": "medicamentos", "checklist": "checklists"}
MODULES = ["backend/app/services/" + name + ".py" for name in
           ("disease_manifest", "triage_manifest", "importer", "corpus_release_authorization")]
APPROVAL_BASIS = (
    "Reconciliação de autorizações existentes, solicitada expressamente pelo proprietário: "
    "baseline imutável vinculado ao manifesto válido fedf818c; pacote científico de 09/09 "
    "com hash autorizado e exclusões preservadas; PR915 e rodada2 reproduzidos em c1eafa1e, "
    "cuja inclusão/deploy foi expressamente solicitada ao coordenador. Demais itens ficam "
    "em quarentena. A normalização estrita do único campo theme em 304 fichas no anchor 800a159e "
    "também integra a correção técnica Tudo com Tudo expressamente autorizada nesta sessão. "
    "Inclui ainda a publicação emergencial expressamente autorizada dos 391 rascunhos "
    "revisados em 10/09 e dos sete registros do suplemento Claude sobre benzatina, "
    "vinculados aos pacotes e às fontes canônicas finais por hashes exatos. "
    "Não constitui nova revisão clínica nem assinatura humana de revisão."
)


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def json_hash(value):
    return sha256(encoded(value)).hexdigest()


def file_hash(path):
    return sha256(path.read_bytes()).hexdigest()


@contextmanager
def temporary_source_tree(prefix):
    temporary = tempfile.TemporaryDirectory(prefix=prefix)
    created = Path(temporary.name).resolve()
    target = Path("\\\\?\\" + str(created)) if os.name == "nt" else created
    # Cleanup uses the same exact, newly created temporary target, with long
    # Windows paths supported; no caller-controlled directory is removed.
    temporary.name = str(target)
    try:
        yield target
    finally:
        temporary.cleanup()


def extract_snapshot(archive, target):
    """Copy regular Git archive members without mixed Windows separators."""
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        for member in tar:
            relative = Path(member.name)
            if relative.is_absolute() or ".." in relative.parts or not (member.isdir() or member.isfile()):
                raise RuntimeError("Unsafe archive member")
            destination = target / relative
            if member.isdir():
                destination.mkdir(parents=True, exist_ok=True)
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                with tar.extractfile(member) as source, destination.open("wb") as output:
                    shutil.copyfileobj(source, output)


def reviewed_september_10_sources(root, current):
    """Admit only the 391+7 independently reviewed, owner-authorized identities.

    Complete Markdown bytes include the intentional published=true change.
    Aggregated JSON is approved per record; unrelated fragments gain no approval.
    """
    references, accepted = [], {front: {} for front in FRONTS}

    def checked(relative, expected):
        relative = relative.replace("\\", "/")
        path = root / relative
        if Path(relative).is_absolute() or ".." in Path(relative).parts:
            raise RuntimeError("Invalid additional review evidence path")
        if file_hash(path) != expected:
            raise RuntimeError(f"Additional authorized evidence changed: {relative}")
        references.append({"path": relative, "sha256": expected, "basis": "approved_package"})
        return path

    def document_matches(item, data):
        pieces = re.split(r"^---\s*$", (root / item["path"]).read_text(encoding="utf-8-sig"),
                          maxsplit=2, flags=re.M)
        if len(pieces) != 3 or pieces[2].strip() != data["body_md"].strip():
            return False
        return all(item["metadata"].get(k) == (True if k == "published" else v)
                   for k, v in data.items() if k != "body_md")

    pack = json.loads(checked(REVIEWED_391, REVIEWED_391_SHA).read_text(encoding="utf-8"))
    integrated = json.loads(checked(INTEGRATED_391, INTEGRATED_391_SHA).read_text(encoding="utf-8"))
    rows = {x["data"]["slug"]: x for x in pack["items"]}
    sources = {x["slug"]: x for x in integrated}
    if (pack.get("release_id") != "scientific-20260910-unpublished"
            or not pack.get("ready_for_reviewed_import") or pack.get("expected_count") != 391
            or len(rows) != len(pack["items"]) or len(sources) != len(integrated)
            or len(rows) != 391 or set(rows) != set(sources)):
        raise RuntimeError("Additional reviewed draft scope is not exactly 391")
    for slug, row in rows.items():
        data, proof = row["data"], sources[slug]
        item = current["documentos"].get(slug)
        if (row.get("entity_type") != "documento" or data.get("review_status") != "revisado"
                or data.get("published") is not False or data.get("gaps") or item is None
                or item["path"] != proof["target"]
                or item["source_sha256"] != proof["published_file_sha256"]
                or not document_matches(item, data)):
            raise RuntimeError(f"Canonical source differs from reviewed draft: {slug}")
        accepted["documentos"][slug] = item["source_sha256"]

    supplement = json.loads(checked(SUPPLEMENT_7, SUPPLEMENT_7_SHA).read_text(encoding="utf-8"))
    integrated = json.loads(checked(INTEGRATED_7, INTEGRATED_7_SHA).read_text(encoding="utf-8"))
    rows = {(x["kind"], x["data"]["slug"]): x["data"] for x in supplement["items"]}
    proofs = {(x["kind"], x["slug"]): x for x in integrated}
    if (not supplement.get("ready") or supplement.get("errors") or supplement.get("pending_source_indices")
            or len(rows) != len(supplement["items"]) or len(proofs) != len(integrated)
            or len(rows) != 7 or set(rows) != set(proofs)
            or Counter(kind for kind, _ in rows) != {"documento": 4, "caso_clinico": 2, "material_paciente": 1}):
        raise RuntimeError("Additional supplement scope is not exactly the seven reviewed identities")
    for (kind, slug), data in rows.items():
        proof, front = proofs[(kind, slug)], KINDS[kind]
        item = current[front].get(slug)
        checked(proof["reviewed_proof_path"], proof["reviewed_proof_sha256"])
        checked(proof["source_proof_path"], proof["source_proof_sha256"])
        if (item is None or slug in accepted[front] or item["path"] != proof["canonical_path"]
                or data.get("review_status") != "revisado" or data.get("published") is not True
                or json_hash(data) != proof["publication_data_sha256"]):
            raise RuntimeError(f"Invalid supplemental identity or reviewed data: {kind}/{slug}")
        if kind == "documento":
            valid = item["source_sha256"] == proof["published_file_sha256"] and document_matches(item, data)
        else:
            valid = item["metadata"] == data and item["source_sha256"] == proof["published_fragment_sha256"]
        if not valid:
            raise RuntimeError(f"Canonical source differs from reviewed supplement: {kind}/{slug}")
        accepted[front][slug] = item["source_sha256"]
    if sum(map(len, accepted.values())) != 398:
        raise RuntimeError("Additional review scope changed")
    return accepted, references


def git(root, *args):
    # git archive otherwise applies Windows checkout conversion as well.
    return subprocess.check_output(["git", "-c", "core.autocrlf=false", "-c", "core.eol=lf", *args], cwd=GIT_OBJECT_ROOT or root)


def module(root, name):
    path = root / "backend/app/services" / (name + ".py")
    spec = importlib.util.spec_from_file_location("scoped_" + name + "_" + str(id(root)), path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def slug_resolver(root):
    # Execute only the two pure functions used by the actual importer; never
    # import its database/application dependencies into the audit process.
    path = root / "backend/app/services/importer.py"
    parsed = ast.parse(path.read_text())
    selected = [n for n in parsed.body if isinstance(n, ast.FunctionDef)
                and n.name in {"_slugify", "_resolve_markdown_slug"}]
    if len(selected) != 2:
        raise RuntimeError("Canonical Markdown slug resolver unavailable")
    namespace = {"Any": Any, "Mapping": Mapping}
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(path), "exec"), namespace)
    return namespace["_resolve_markdown_slug"]


def snapshot(root, commit, target):
    paths = set(FRONTS.values()) | set(MODULES) | {MANIFEST_V1}
    paths -= {"doencas/metadados.json", "triagem-sintomas/metadados.json", "material-paciente/metadados.json"}
    paths |= {"doencas", "triagem-sintomas", "material-paciente"}
    archive = git(root, "archive", commit, "--", *sorted(paths))
    extract_snapshot(archive, target)


def inventory(root):
    records, fingerprints = {}, {}
    auth = module(root, "corpus_release_authorization")
    resolve_slug = slug_resolver(root)
    for front, relative in FRONTS.items():
        source = root / relative
        items = {}
        if front == "documentos":
            for path in sorted(source.rglob("*.md")):
                # Same YAML mapping as python-frontmatter, with strict rejection
                # of unsupported delimiters rather than silently missing slugs.
                pieces = re.split(r"^---\s*$", path.read_text(encoding="utf-8-sig"), maxsplit=2, flags=re.M)
                if len(pieces) != 3 or pieces[0].strip():
                    raise RuntimeError(f"Unsupported Markdown frontmatter: {path}")
                metadata = yaml.load(pieces[1], Loader=YAML_LOADER) or {}
                slug = resolve_slug(metadata, metadata.get("title") or path.stem, source=str(path))
                if slug in items:
                    raise RuntimeError(f"Duplicate canonical identity: {front}/{slug}")
                items[slug] = {"metadata": metadata, "source_sha256": file_hash(path),
                               "path": path.relative_to(root).as_posix()}
        else:
            if front == "doencas_especializadas":
                rows = module(root, "disease_manifest").load_disease_records(source)
            elif front == "triagem_sintomas":
                rows = module(root, "triage_manifest").load_triage_records(source)
            else:
                rows = json.loads(source.read_text())
            for row in rows:
                slug = row.get("slug")
                if not isinstance(slug, str) or not slug.strip() or slug != slug.strip() or slug in items:
                    raise RuntimeError(f"Invalid or duplicate canonical identity: {front}/{slug}")
                items[slug] = {"metadata": row, "source_sha256": json_hash(row), "path": relative}
        statuses = {slug: item["metadata"].get("review_status") for slug, item in items.items()}
        fingerprint_source = source.parent if front in {"doencas_especializadas", "triagem_sintomas"} else source
        fingerprints[front] = auth.build_front_fingerprint(fingerprint_source, set(items), statuses)
        records[front] = items
    return records, fingerprints



def theme_normalization(root, baseline):
    theme_code = git(root, "show", f"{THEME_ANCHOR}:{THEME_MODULE}")
    if theme_code != (root / THEME_MODULE).read_bytes():
        raise RuntimeError("Canonical theme domain differs from authorized normalization anchor")
    canonical = module(root, "canonical_themes").TEMAS_CANONICOS
    if len(canonical) != 30:
        raise RuntimeError("Unexpected canonical theme domain")
    proof, hashes, previous_themes = {}, {}, set()
    for front in ("estudos", "evidencias"):
        rows = json.loads(git(root, "show", f"{THEME_ANCHOR}:{FRONTS[front]}"))
        proof[front], hashes[front] = {}, {}
        for row in rows:
            slug = row["slug"]
            old = baseline[front].get(slug, {}).get("metadata")
            if old is None or row == old:
                continue
            changed = [key for key in set(old) | set(row) if old.get(key) != row.get(key)]
            old_other = {key: value for key, value in old.items() if key != "theme"}
            new_other = {key: value for key, value in row.items() if key != "theme"}
            if changed != ["theme"] or old_other != new_other or row["theme"] not in canonical:
                raise RuntimeError(f"Theme exception would include unrelated change: {front}/{slug}")
            hashes[front][slug] = json_hash(row)
            previous_themes.add(old["theme"])
            proof[front][slug] = {"before_theme": old["theme"], "after_theme": row["theme"],
                "baseline_source_sha256": json_hash(old), "anchor_source_sha256": json_hash(row),
                "unchanged_other_fields_sha256": json_hash(old_other)}
        if len(proof[front]) != 152:
            raise RuntimeError(f"Unexpected theme normalization scope for {front}")
    if len(previous_themes) != 138:
        raise RuntimeError("Unexpected original theme scope")
    data = {"schema_version": 1, "decision": "authorized_tct_theme_normalization",
        "approval_basis": "Correção técnica Tudo com Tudo autorizada pelo proprietário nesta sessão e confirmada "
        "pelo coordenador; apenas theme muda em fontes clínicas já cobertas pelo baseline válido. Não é revisão clínica nova.",
        "baseline_commit": BASELINE, "normalization_commit": THEME_ANCHOR, "normalized_total": 304,
        "distinct_previous_themes": 138, "canonical_domain_count": 30, "canonical_themes": list(canonical),
        "canonical_theme_module_sha256": sha256(theme_code).hexdigest(), "items": proof}
    return hashes, (json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def sidecar_references(root):
    directories = sorted({Path(path).parts[0] for path in FRONTS.values()} - {"content"})
    def objects(commit):
        result = {}
        for entry in git(root, "ls-tree", "-rz", commit, "--", *directories).split(b"\0"):
            if not entry: continue
            metadata, path = entry.split(b"\t", 1)
            mode, kind, oid = metadata.split()
            if kind != b"blob" or mode == b"120000":
                raise RuntimeError("Unsupported canonical sidecar object")
            result[path.decode()] = oid.decode()
        return result
    base, before_pr, after_pr = objects(BASELINE), objects(PR_BASE), objects(PR_FINAL)
    refs, details = [], {}
    seen = set()
    for directory in directories:
        for path in sorted((root / directory).rglob("*")):
            if not path.is_file(): continue
            relative = path.relative_to(root).as_posix()
            if relative in FRONTS.values(): continue
            seen.add(relative)
            if path.is_symlink(): raise RuntimeError("Symlink in canonical sidecars")
            content = path.read_bytes()
            blob = sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
            if blob == base.get(relative):
                basis = "baseline_unchanged"
            elif (blob == after_pr.get(relative) and before_pr.get(relative) == base.get(relative)
                  and after_pr.get(relative) != before_pr.get(relative)):
                basis = "approved_package"
            else:
                raise RuntimeError(f"Sidecar has no exact authorization: {relative}")
            digest = sha256(content).hexdigest()
            refs.append({"path": relative, "sha256": digest, "basis": basis})
            details[relative] = {"basis": basis, "sha256": digest, "git_blob": blob}
    expected_sidecars = set(after_pr) - set(FRONTS.values())
    if seen != expected_sidecars:
        raise RuntimeError("Canonical sidecar membership differs from authorized snapshot")
    relations = "doencas/relacoes-explicitas.json"
    old = json.loads(git(root, "show", f"{BASELINE}:{relations}"))
    current = json.loads((root / relations).read_text())
    old_counts, new_counts = Counter(map(json_hash, old)), Counter(map(json_hash, current))
    if old_counts - new_counts:
        raise RuntimeError("PR915 removed or changed an existing explicit relation")
    relation_proof = {"unchanged_previous_relations": sum(old_counts.values()),
                      "exact_authorized_added_relations": sum((new_counts - old_counts).values()),
                      "final_total": len(current), "final_equals_pr915_round2": True}
    return refs, details, relation_proof



def build(root):
    auth = module(root, "corpus_release_authorization")
    pack_path = root / PACK
    if file_hash(pack_path) != PACK_SHA:
        raise RuntimeError("Authorized package hash changed")
    for commit in (BASELINE, PR_BASE, PR_FINAL, THEME_ANCHOR):
        git(root, "merge-base", "--is-ancestor", commit, "HEAD")
    # Existing handoff and exact-application evidence must be the approved
    # versions, not later documentation accidentally widening the package.
    for reference in (HANDOFF, ROUND2):
        if (root / reference).read_bytes() != git(root, "show", f"{PR_FINAL}:{reference}"):
            raise RuntimeError(f"PR915 authorization evidence changed: {reference}")
    current, fingerprints = inventory(root)
    additional_sources, additional_refs = reviewed_september_10_sources(root, current)
    previous_partition = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    with temporary_source_tree("corvia-scoped-release-") as temp:
        trees = {}
        for label, commit in (("baseline", BASELINE), ("pr_base", PR_BASE), ("pr_final", PR_FINAL)):
            target = Path(temp) / label
            target.mkdir()
            snapshot(root, commit, target)
            trees[label] = (target, *inventory(target))
        baseline_root, baseline, baseline_fingerprints = trees["baseline"]
        historical = baseline_root / MANIFEST_V1
        if (root / MANIFEST_V1).read_bytes() != historical.read_bytes():
            raise RuntimeError("Historical authorization changed")
        _, historical_meta = auth.validate_full_corpus_authorization(historical,
            canonical_slugs={front: set(rows) for front, rows in baseline.items()}, fingerprints=baseline_fingerprints)
        if historical_meta["authorized_total"] != 11581:
            raise RuntimeError("Unexpected historical baseline total")
        # Patient corrections are applied after raw metadata inventory. They
        # cannot inherit approval if changed; their exact bytes are references.
        def overlays(tree):
            return {p.relative_to(tree).as_posix(): file_hash(p)
                    for p in sorted((tree / "material-paciente/correcoes").glob("*.json"))}
        overlay_hashes = overlays(root)
        if overlay_hashes != overlays(baseline_root):
            raise RuntimeError("Patient overlays changed outside the proven immutable baseline")
        theme_hashes, theme_bytes = theme_normalization(root, baseline)
        sidecar_refs, sidecar_details, relation_proof = sidecar_references(root)
        pack = json.loads(pack_path.read_text())
        package_sources = {front: {} for front in FRONTS}
        for entry in pack["source_inventory"]:
            relative = entry["path"]
            if relative.startswith("content/"):
                package_sources["documentos"][entry["slug"]] = entry["sha256"]
        for item in pack["items"]:
            front = KINDS.get(item["kind"])
            if front and front != "documentos":
                package_sources[front][item["data"]["slug"]] = json_hash(item["data"])
        exclusions = {(KINDS[x["kind"]], x["slug"]): x for x in pack["merged_duplicates"] if x["kind"] in KINDS}
        supersessions = {}
        for slug, decision in REVIEW_SUPERSESSIONS.items():
            item = current["documentos"][slug]
            previous = exclusions.get(("documentos", slug))
            if (previous is None or previous["merge_into"] != decision["previous_merge_into"]
                    or item["metadata"].get("kind") != "estudo"
                    or item["source_sha256"] != decision["source_sha256"]
                    or additional_sources["documentos"].get(slug) != decision["source_sha256"]):
                raise RuntimeError(f"Supersession is not bound to its exact new reviewed source: {slug}")
            body = re.split(r"^---\s*$", (root / item["path"]).read_text(encoding="utf-8-sig"), maxsplit=2, flags=re.M)[2].strip()
            supersessions[slug] = {**decision, "body_sha256": sha256(body.encode()).hexdigest(),
                "previous_exclusion_package_sha256": PACK_SHA, "new_reviewed_package_sha256": REVIEWED_391_SHA,
                "source_path": item["path"], "kind": "estudo"}
        supersession_data = {"decision": "supersede_two_previous_duplicate_exclusions",
            "approval_basis": "Publicação emergencial de todo o conteúdo revisado autorizada pelo proprietário. Decisão editorial explícita do coordenador após comparação integral das quatro fontes em 10/09/2026: manter as duas fichas de estudo complementares às sínteses. Revisão assistida por IA, sem assinatura humana atribuída.",
            "scope": "Somente as duas fontes e hashes finais listados; todas as demais exclusões anteriores continuam vigentes.",
            "items": supersessions}
        supersession_bytes = (json.dumps(supersession_data, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
        pr_base, pr_final = trees["pr_base"][1], trees["pr_final"][1]
        approved, quarantined, claims, details = {}, {}, {}, {}
        basis_counts = Counter()
        for front, items in current.items():
            approved[front], quarantined[front], claims[front], details[front] = [], [], {}, {}
            for slug, item in sorted(items.items()):
                digest = item["source_sha256"]
                base_item = baseline[front].get(slug, {})
                before_pr = pr_base[front].get(slug, {})
                after_pr = pr_final[front].get(slug, {})
                reason, basis, anchor = "no_matching_authorized_source", None, None
                if (front, slug) in exclusions and not (front == "documentos" and slug in supersessions):
                    reason = "explicit_merged_duplicate_do_not_republish"
                elif item["metadata"].get("review_status") != "revisado":
                    reason = "canonical_review_status_not_revisado"
                elif digest == additional_sources[front].get(slug):
                    basis, anchor = "approved_package", "reviewed-391-and-benzatina-7-20260910"
                elif digest == base_item.get("source_sha256"):
                    basis, anchor = "baseline_unchanged", BASELINE
                elif digest == theme_hashes.get(front, {}).get(slug):
                    basis, anchor = "authorized_tct_theme_normalization", THEME_ANCHOR
                elif digest == package_sources[front].get(slug):
                    basis, anchor = "approved_package", PACK
                elif (digest == after_pr.get("source_sha256")
                      and after_pr.get("source_sha256") != before_pr.get("source_sha256")):
                    basis, anchor = "approved_package", PR_FINAL
                if basis:
                    approved[front].append(slug)
                    claims[front][slug] = digest
                    basis_counts[anchor] += 1
                    details[front][slug] = {"basis": basis, "authorization_anchor": anchor,
                        "path": item["path"], "source_sha256": digest}
                else:
                    quarantined[front].append(slug)
                    details[front][slug] = {"reason": reason, "path": item["path"], "source_sha256": digest}
        references = []
        for path, basis in [(MANIFEST_V1, "baseline_unchanged"), (PACK, "approved_package"),
                            (HANDOFF, "approved_package"), (ROUND2, "approved_package")]:
            references.append({"path": path, "sha256": file_hash(root / path), "basis": basis})
        references.extend(sidecar_refs)
        references.extend(additional_refs)
        references.append({"path": SUPERSESSIONS, "sha256": sha256(supersession_bytes).hexdigest(), "basis": "approved_package"})
        references.extend([{ "path": THEME_PROOF, "sha256": sha256(theme_bytes).hexdigest(),
                             "basis": "authorized_tct_theme_normalization"},
                           {"path": THEME_MODULE, "sha256": file_hash(root / THEME_MODULE),
                            "basis": "authorized_tct_theme_normalization"}])
        # Preserve prior publication decisions outside this exact new scope.
        for front in FRONTS:
            scope = set(additional_sources[front])
            old_approved = set(previous_partition["approved"][front]) - scope
            old_quarantined = set(previous_partition["quarantined"][front]) - scope
            if set(approved[front]) - scope != old_approved or not old_quarantined <= set(quarantined[front]):
                raise RuntimeError(f"Publication partition outside the 398 changed: {front}")
            if not scope <= set(approved[front]):
                raise RuntimeError(f"Additional reviewed source not approved: {front}")
        evidence = {"schema_version": 1, "decision": "reconciled_publication_evidence",
                    "approval_basis": APPROVAL_BASIS, "approved_sources": claims,
                    "approved_bases": {front: {slug: details[front][slug]["basis"] for slug in approved[front]}
                                       for front in FRONTS}, "references": references}
        evidence_bytes = (json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
        evidence_hash = sha256(evidence_bytes).hexdigest()
        manifest = {"schema_version": 2, "release": "corvia-scoped-corpus-20260910",
            "decision": "approved_snapshot_with_quarantine", "scope": "exact_canonical_snapshot",
            "approval_basis": APPROVAL_BASIS, "expected_total": sum(len(x) for x in current.values()),
            "inventory_sha256": auth.corpus_inventory_sha256(fingerprints), "fronts": fingerprints,
            "approved": approved, "quarantined": quarantined,
            "provenance": {front: {slug: {"basis": details[front][slug]["basis"], "evidence_path": EVIDENCE,
                "evidence_sha256": evidence_hash, "source_sha256": claims[front][slug]}
                for slug in approved[front]} for front in FRONTS}}
        report = {"schema_version": 1, "scientific_review_performed": False,
            "human_clinical_signature_claimed": False, "authorization_anchors": {"baseline": BASELINE,
            "pr915_parent": PR_BASE, "pr915_and_round2": PR_FINAL, "theme_normalization": THEME_ANCHOR, "package_sha256": PACK_SHA},
            "baseline_validated_total": 11581, "expected_total": manifest["expected_total"],
            "additional_reviewed_20260910": {"records": 398, "reviewed_drafts": 391, "benzatina_supplement": 7,
                "reviewed_package_sha256": REVIEWED_391_SHA, "canonical_integration_sha256": INTEGRATED_391_SHA,
                "supplement_package_sha256": SUPPLEMENT_7_SHA, "supplement_manifest_sha256": INTEGRATED_7_SHA},
            "approved_total": sum(map(len, approved.values())), "quarantined_total": sum(map(len, quarantined.values())),
            "approval_source_counts": dict(basis_counts), "inventory_sha256": manifest["inventory_sha256"],
            "evidence_sha256": evidence_hash, "sidecars": sidecar_details,
            "superseded_duplicate_exclusions": supersessions,
            "explicit_relation_proof": relation_proof, "items": details}
    lines = ["# Reconciliação documental da release científica — 10/09/2026", "",
        APPROVAL_BASIS, "", f"Snapshot: **{report['expected_total']}** itens; **{report['approved_total']}** autorizados; "
        f"**{report['quarantined_total']}** em quarentena.", "",
        "| Frente | Total | Autorizados | Quarentena |", "|---|---:|---:|---:|"]
    lines.extend(f"| {front} | {len(current[front])} | {len(approved[front])} | {len(quarantined[front])} |" for front in sorted(FRONTS))
    lines += ["", "O baseline foi reconstruído de objetos Git e seu manifesto v1 validado integralmente antes de reutilizar "
        "somente registros imutáveis. Alterações do PR915 são calculadas por registro entre seu pai e o resultado da "
        "rodada2; alterações em catálogos agregados não aprovam outros registros desses arquivos. O pacote de 09/09 "
        "exige seu SHA-256 fixo e correspondência exata da fonte. Exclusões de duplicatas prevalecem, salvo as duas "
        "fichas kind=estudo reavaliadas expressamente em 10/09, complementares às sínteses multifuentes e vinculadas "
        "aos novos hashes no registro separado de supersessões.", "",
        "As 304 fichas normalizadas pelo commit800a159e receberam prova separada: somente theme mudou, "
        "todos os demais campos são idênticos ao baseline válido e o registro final inteiro bate com o anchor autorizado. "
        "138 temas anteriores foram enquadrados no domínio de 30 temas canônicos. Nenhum campo foi ignorado na comparação.", "",
        "A extensão de 10/09 autoriza exatamente 398 registros revisados: 391 rascunhos e sete itens do suplemento "
        "Claude sobre benzatina. Pacotes e manifestos de integração têm hashes fixos; corpos e metadados "
        "correspondem às fontes finais com published=true. Em JSON agregado, somente os três registros do suplemento "
        "recebem a nova aprovação. Aprovações e quarentenas anteriores fora desses 398 são preservadas.", "",
        "Os arquivos auxiliares, inclusive mídias da galeria e relações explícitas, também foram comparados contra "
        "baseline ou delta exato PR915 e vinculados por hash no índice de evidências. As 3054 relações anteriores "
        "permanecem intactas, com 105 novas relações do PR915/rodada2, total 3159.", "",
        "Documentos usam SHA-256 dos bytes completos. Registros JSON usam serialização canônica do registro completo; "
        "doenças e triagem usam seus compositores canônicos. O overlay de material ao paciente foi confirmado "
        "imutável desde o baseline e seus arquivos são referências hashadas obrigatórias. Nenhum conteúdo ou status "
        "foi editado; `revisado` isoladamente não concede autorização.", "",
        "A evidência registra autorização de publicação existente e revisão assistida por IA dos pacotes; "
        "não declara nova revisão médica nem assinatura humana. Slugs runtime-only não pertencem a este inventário.", "",
        "Reprodução: `python3 scripts/build_scoped_corpus_release.py --check` (Git e PyYAML; sem banco ou IA paga). "
        "O ledger JSON ao lado registra a fonte de autorização ou o motivo de quarentena de cada identidade.", ""]
    return {THEME_PROOF: theme_bytes, SUPERSESSIONS: supersession_bytes, EVIDENCE: evidence_bytes, MANIFEST: (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(),
            REPORT: (json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(), MEMO: "\n".join(lines).encode()}, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true", help="Compare reproducible artifacts without writing")
    parser.add_argument("--from-index", action="store_true", help="Read exact staged Git bytes, avoiding working-tree CRLF conversion")
    args = parser.parse_args()
    root = args.root.resolve()
    if args.from_index:
        global GIT_OBJECT_ROOT
        GIT_OBJECT_ROOT = root
        tree = git(root, "write-tree").decode().strip()
        staged_manifest = json.loads(git(root, "show", f"{tree}:{INTEGRATED_7}"))
        paths = {str(Path(path).parts[0]) for path in FRONTS.values()} | set(MODULES) | {
            THEME_MODULE, MANIFEST_V1, MANIFEST, PACK, HANDOFF, ROUND2,
            REVIEWED_391, INTEGRATED_391, SUPPLEMENT_7, INTEGRATED_7,
        }
        for item in staged_manifest:
            paths.update(item[k].replace("\\", "/") for k in ("reviewed_proof_path", "source_proof_path"))
        with temporary_source_tree("corvia-staged-review-") as temp:
            frozen = Path(temp)
            archive = git(root, "archive", tree, "--", *sorted(paths))
            extract_snapshot(archive, frozen)
            artifacts, report = build(frozen)
            # Validate schema 2 and every evidence reference before writing
            # any generated authorization back to the working checkout.
            for relative, content in artifacts.items():
                path = frozen / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
            records, fingerprints = inventory(frozen)
            module(frozen, "corpus_release_authorization").validate_snapshot_authorization(
                frozen / MANIFEST, canonical_slugs={front: set(rows) for front, rows in records.items()},
                fingerprints=fingerprints,
                review_statuses={front: {slug: item["metadata"].get("review_status") for slug, item in rows.items()} for front, rows in records.items()},
                source_fingerprints={front: {slug: item["source_sha256"] for slug, item in rows.items()} for front, rows in records.items()},
                repository_root=frozen)
        current_tree = git(root, "write-tree").decode().strip()
        if current_tree != tree and git(root, "diff", "--name-only", tree, current_tree, "--", *sorted(paths)).strip():
            raise RuntimeError("Git index changed during preparation; retry from a frozen staged snapshot")
    else:
        artifacts, report = build(root)
    for relative, content in artifacts.items():
        path = root / relative
        if args.check:
            if not path.is_file() or path.read_bytes() != content:
                raise RuntimeError(f"Reproducibility mismatch: {relative}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    print(json.dumps({key: value for key, value in report.items() if key not in {"items", "sidecars"}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
