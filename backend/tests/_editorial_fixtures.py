"""Synthetic, hash-bound empty metadata ledger; never a publication approval."""
from hashlib import sha256
import json


def write_empty_editorial_registry(root):
    directory = root / 'backend/app/services'
    directory.mkdir(parents=True, exist_ok=True)
    scope = 'editorial_metadata_only_no_publication_authorization'
    evidence = directory / 'editorial-test-evidence.json'
    evidence.write_text(json.dumps({'schema_version': 1, 'scope': scope, 'claims': {}}), encoding='utf-8')
    registry = directory / 'editorial_kind_registry.json'
    registry.write_text(json.dumps({'schema_version': 1, 'scope': scope, 'entries': [],
        'evidence_file': evidence.name, 'evidence_sha256': sha256(evidence.read_bytes()).hexdigest()}), encoding='utf-8')
    return registry
