"""Focal offline importer checks: no database, network, AI or production writes."""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import hashlib
import json

import pytest

from app.services import scientific_publication_import as importer

RELEASE_DIR = Path(__file__).resolve().parents[2] / "releases" / "cardiol-20260910"


@pytest.fixture(scope="module")
def originals():
    return importer.load_release(RELEASE_DIR)


def test_actual_release_integrity_identity_license_and_native_pt(originals):
    assert len(originals) == 13
    assert len({x.metadata["doi"] for x in originals}) == 13
    assert sum(x.metadata["format"] == "jats_xml" for x in originals) == 12
    assert sum(x.metadata["format"] == "pdf" for x in originals) == 1
    assert all(x.parsed["language"] == "pt" for x in originals)
    for item in originals:
        assert hashlib.sha256(item.content).hexdigest() == item.metadata["sha256"]
        assert item.parsed["license_url"] in importer.LICENSE_URLS
    pdf = next(x for x in originals if x.metadata["format"] == "pdf")
    assert pdf.summary is None
    assert pdf.metadata["corrects_doi"] == "10.36660/abc.20250619"
    assert "20260222" not in str([x.metadata["doi"] for x in originals])


def test_offline_plan_never_loads_database_identity(monkeypatch, originals):
    monkeypatch.setattr(importer, "_identity", lambda *a: pytest.fail("Offline plan must not load database module"))
    plan = importer.plan_import(originals)
    assert plan["mode"] == "offline_validation"
    assert plan["count"] == 13
    assert plan["paid_calls"] == plan["clinical_changes"] == 0
    assert all(x["database_state"] == "not_inspected" for x in plan["items"])


def copy_release(tmp_path):
    # Independent temporary fixtures; never mutate versioned release files.
    import shutil
    target = tmp_path / "release"
    shutil.copytree(RELEASE_DIR, target)
    return target


@pytest.mark.parametrize("kind", ["original", "source_manifest", "missing_original"])
def test_any_tampered_or_missing_file_blocks_whole_release(tmp_path, kind):
    root = copy_release(tmp_path)
    if kind == "source_manifest":
        p = root / "checksums.json"
        p.write_bytes(p.read_bytes() + b" ")
    else:
        p = root / "originals/10.36660-abc.20250621.xml"
        if kind == "missing_original":
            p.unlink()
        else:
            p.write_bytes(p.read_bytes() + b" ")
    with pytest.raises(ValueError):
        importer.load_release(root)


@pytest.mark.parametrize("change", ["doi", "traversal", "wrong_license", "missing_proof", "future_license"])
def test_manifest_identity_license_and_path_attacks(tmp_path, change):
    root = copy_release(tmp_path)
    p = root / "import-manifest.json"
    manifest = json.loads(p.read_text())
    entry = next(x for x in manifest["documents"] if x["doi"] == "10.36660/abc.20260220")
    if change == "doi":
        entry["doi"] = "10.36660/abc.20260999"
    elif change == "traversal":
        entry["file"] = "../outside.xml"
    elif change == "wrong_license":
        entry["license_url"] = "https://creativecommons.org/licenses/by-nc/4.0/"
    elif change == "missing_proof":
        entry["license_evidence"]["evidence"] = {}
    else:
        for license in entry["license_evidence"]["evidence"]["licenses"]:
            license["start"]["date-time"] = "2099-01-01T00:00:00Z"
    p.write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        importer.load_release(root)


def asset(**changes):
    values = dict(id=1, source_key="key", doi="10.36660/abc.20250621", source_url="",
                  original_storage_key=None, translated_storage_key=None, summary_pt=None,
                  progress={}, coverage={}, attempts=0, status="pending", retry_at=None)
    values.update(changes)
    return SimpleNamespace(**values)


@pytest.mark.parametrize("changes,reason", [
    ({"status": "cost_unknown"}, "protected_state"),
    ({"status": "ai_processing"}, "protected_state"),
    ({"status": "translating"}, "protected_state"),
    ({"status": "budget_wait"}, "protected_state"),
    ({"original_storage_key": "old-original"}, "existing_stored_artifact"),
    ({"translated_storage_key": "old-translation"}, "existing_stored_artifact"),
    ({"summary_pt": "prior summary"}, "existing_processing_history"),
    ({"attempts": 1}, "existing_processing_history"),
    ({"progress": {"active_operation_key": "paid-operation"}}, "existing_processing_history"),
    ({"progress": {"completed_chunks": [{"storage_key": "paid-chunk"}]}}, "existing_processing_history"),
])
def test_preserves_existing_artifacts_and_processing_history(changes, reason):
    original = asset(**changes)
    before = deepcopy(original.__dict__)
    assert importer.protected_reason(original) == reason
    assert original.__dict__ == before


@pytest.fixture
def fake_runtime(monkeypatch):
    class DB:
        def __init__(self):
            self.assets, self.guidelines, self.stored = {}, {}, []
            self.commits, self.rollbacks, self.locks = 0, 0, 0
        def commit(self): self.commits += 1
        def rollback(self): self.rollbacks += 1
    db = DB()
    monkeypatch.setattr(importer, "_identity", lambda item: {
        "doi": item.metadata["doi"], "url": "https://doi.org/" + item.metadata["doi"],
        "key": hashlib.sha256(("doi:" + item.metadata["doi"]).encode()).hexdigest()})
    def find(db, key, lock=False):
        return db.assets.get(key)
    def create(db, source):
        value = asset(id=len(db.assets)+1, source_key=source["key"], doi=source["doi"], source_url=source["url"])
        db.assets[source["key"]] = value
        return value
    def guideline(db, item):
        db.guidelines[item.metadata["doi"]] = {"org": "SBC", "detection_status": "detected"}
    def lock(db): db.locks += 1
    def store(content, owner):
        db.stored.append((owner, content))
        return f"encrypted-{len(db.stored)}"
    monkeypatch.setattr(importer, "_find_asset", find)
    monkeypatch.setattr(importer, "_new_asset", create)
    monkeypatch.setattr(importer, "_find_guideline", lambda db, doi: db.guidelines.get(doi))
    monkeypatch.setattr(importer, "_new_guideline", guideline)
    monkeypatch.setattr(importer, "_acquire_lock", lock)
    monkeypatch.setattr(importer, "_store", store)
    monkeypatch.setattr(importer, "_trusted_metadata", lambda row: row.get("org") == "SBC")
    return db


def test_apply_is_idempotent_original_only_and_never_enqueues_paid_work(fake_runtime, originals):
    db = fake_runtime
    first = importer.apply_import(db, originals)
    assert db.locks == db.commits == 1
    assert len(db.stored) == 14  # 13 originals plus the erratum readable text
    assert len(db.assets) == len(db.guidelines) == 13
    assert all(row["action"] == "created" for row in first["items"])
    before = deepcopy([x.__dict__ for x in db.assets.values()])
    second = importer.apply_import(db, originals)
    assert all(row["action"] == "preserved" for row in second["items"])
    assert len(db.stored) == 14
    assert before == [x.__dict__ for x in db.assets.values()]
    for value in db.assets.values():
        assert value.status == "original_ready" and value.retry_at is None
        assert value.translated_storage_key is None
        assert value.coverage["native_pt"] is True
        assert value.coverage["language"] == "pt"
        proof = value.progress["import_provenance"]
        assert proof["source_sha256"] == value.source_sha256
        assert proof["license_url"] == value.license_url
        assert ("active_operation_key" not in value.progress and "completed_chunks" not in value.progress)
        if value.summary_pt:
            assert value.progress["summary_origin"] == "publisher_abstract"


def test_apply_preserves_cost_unknown_byte_for_byte(fake_runtime, originals):
    db = fake_runtime
    original = originals[0]
    key = importer._identity(original)["key"]
    protected = asset(source_key=key, doi=original.metadata["doi"], status="cost_unknown",
                      progress={"active_operation_key": "uncertain-paid-receipt"}, attempts=5)
    db.assets[key] = protected
    before = deepcopy(protected.__dict__)
    result = importer.apply_import(db, [original])
    assert result["items"][0]["action"] == "preserved"
    assert protected.__dict__ == before
    assert not db.stored and not db.guidelines


def test_database_plan_performs_no_mutation(fake_runtime, originals):
    db = fake_runtime
    report = importer.plan_import(originals, db)
    assert report["mode"] == "database_read_only"
    assert all(row["action"] == "create" for row in report["items"])
    assert not db.assets and not db.guidelines and not db.stored
    assert db.commits == db.rollbacks == db.locks == 0


def test_storage_failure_rolls_back_without_returning_success(monkeypatch, fake_runtime, originals):
    db = fake_runtime
    def failure(*args): raise OSError("bounded test storage failure")
    monkeypatch.setattr(importer, "_store", failure)
    with pytest.raises(OSError):
        importer.apply_import(db, [originals[0]])
    assert db.rollbacks == 1 and db.commits == 0


def test_busy_worker_prevents_every_write(monkeypatch, fake_runtime, originals):
    db = fake_runtime
    def busy(db): raise RuntimeError("busy")
    monkeypatch.setattr(importer, "_acquire_lock", busy)
    with pytest.raises(RuntimeError, match="busy"):
        importer.apply_import(db, originals)
    assert not db.assets and not db.guidelines and not db.stored and db.commits == 0


def test_untrusted_existing_metadata_is_reported_and_not_promoted(fake_runtime, originals):
    db = fake_runtime
    original = originals[0]
    db.guidelines[original.metadata["doi"]] = {"org": "UNVERIFIED", "detection_status": "manual"}
    planned = importer.plan_import([original], db)
    assert planned["items"][0]["reason"] == "existing_source_metadata_requires_review"
    with pytest.raises(ValueError, match="metadata requires review"):
        importer.apply_import(db, [original])
    assert not db.stored and not db.assets and db.commits == 0
    assert db.guidelines[original.metadata["doi"]]["org"] == "UNVERIFIED"


def test_commit_failure_retains_unreferenced_encrypted_object_for_reconciliation(fake_runtime, originals):
    db = fake_runtime
    def fail_commit():
        raise RuntimeError("commit result unknown")
    db.commit = fail_commit
    with pytest.raises(RuntimeError, match="commit result unknown"):
        importer.apply_import(db, [originals[0]])
    assert db.rollbacks == 1
    assert len(db.stored) == 1  # Never delete after uncertain commit; no success reported.


@pytest.mark.parametrize("corrected_doi", [None, "10.36660/abc.20250640"])
def test_pdf_erratum_must_preserve_verified_correction_target(originals, corrected_doi):
    original = next(x for x in originals if x.metadata["format"] == "pdf")
    entry = deepcopy(original.metadata)
    entry["corrects_doi"] = corrected_doi
    checks = {entry["file"]: {"file": entry["file"], "bytes": entry["bytes"], "sha256": entry["sha256"]}}
    recovery = json.loads((RELEASE_DIR / "source-recovery.json").read_text())
    with pytest.raises(ValueError, match="verified erratum"):
        importer.validate_document(RELEASE_DIR, entry, checks, recovery, original.manifest_sha256)


def test_curated_has_original_recovers_source_only_failure_without_resetting_attempts(fake_runtime, originals):
    db = fake_runtime
    original = next(x for x in originals if x.metadata["doi"] == "10.36660/abc.20250624")
    key = importer._identity(original)["key"]
    value = asset(id=27, source_key=key, doi=original.metadata["doi"],
                  status="blocked_fulltext", attempts=1, progress={})
    db.assets[key] = value
    assert importer.protected_reason(value) is None
    result = importer.apply_import(db, [original])
    assert result["items"][0]["action"] == "attached"
    assert value.status == "original_ready" and value.attempts == 1
    assert value.original_storage_key and value.translated_storage_key is None
    assert value.coverage["native_pt"] is True
    assert "active_operation_key" not in value.progress
    assert len(db.stored) == 1 and db.commits == 1


def test_attempts_on_failed_state_are_still_protected(fake_runtime, originals):
    db = fake_runtime
    original = originals[0]
    key = importer._identity(original)["key"]
    value = asset(source_key=key, doi=original.metadata["doi"], status="failed", attempts=1, progress={})
    db.assets[key] = value
    before = deepcopy(value.__dict__)
    result = importer.apply_import(db, [original])
    assert result["items"][0]["action"] == "preserved"
    assert value.__dict__ == before
    assert not db.stored and not db.guidelines


def test_altered_pdf_readable_text_is_rejected(tmp_path, originals):
    root = copy_release(tmp_path)
    p = root / "readable/10.36660-abc.20260565.txt"
    content = p.read_bytes()
    p.write_bytes(content.replace(b"20250619", b"20250640"))
    with pytest.raises(ValueError, match="Readable PDF text SHA256/size mismatch"):
        importer.load_release(root)


def test_pdf_readable_artifact_has_independent_hash_and_source_binding(fake_runtime, originals):
    db = fake_runtime
    original = next(x for x in originals if x.metadata["format"] == "pdf")
    importer.apply_import(db, [original])
    value = next(iter(db.assets.values()))
    assert value.original_storage_key == "encrypted-1"
    assert db.stored[0] == (value.id, original.content)
    proof = value.progress["original_text"]
    assert proof["storage_key"] == "encrypted-2"
    assert db.stored[1] == (value.id, original.parsed["text"].encode("utf-8"))
    assert proof["sha256"] == hashlib.sha256(db.stored[1][1]).hexdigest()
    assert proof["sha256"] == original.metadata["original_text_sha256"]
    assert proof["source_sha256"] == value.source_sha256 == original.metadata["sha256"]
    assert proof["source_format"] == "pdf"
    assert value.translated_storage_key is None and value.summary_pt is None
    assert value.status == "original_ready" and value.coverage["native_pt"]
    assert "10.36660/abc.20260565" in original.parsed["text"]
    assert "10.36660/abc.20250619" in original.parsed["text"]
