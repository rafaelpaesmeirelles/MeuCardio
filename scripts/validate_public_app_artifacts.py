#!/usr/bin/env python3
"""Validate public Android and Windows artifacts without changing production."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import ssl
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

DEFAULT_BASE_URL = "https://corvia.med.br"
ALLOWED_PUBLIC_HOSTS = {"corvia.med.br"}
SHA256_RE = re.compile(r"\b([0-9a-fA-F]{64})\b")
MAX_ARTIFACT_BYTES = 350 * 1024 * 1024

@dataclass(frozen=True)
class ArtifactSpec:
    name: str
    path: str
    minimum_bytes: int
    mime_types: tuple[str, ...]
    magic: bytes
    pinned_sha_env: str

SPECS = (
    ArtifactSpec("android", "/downloads/corvia-cardiology-spaces-android-1.2.0.apk", 1_000_000,
                 ("application/vnd.android.package-archive", "application/octet-stream"),
                 b"PK\x03\x04", "CORVIA_ANDROID_EXPECTED_SHA256"),
    ArtifactSpec("windows", "/downloads/corvia-cardiology-spaces-windows-1.2.0.exe", 20_000_000,
                 ("application/vnd.microsoft.portable-executable", "application/x-msdownload", "application/octet-stream"),
                 b"MZ", "CORVIA_WINDOWS_EXPECTED_SHA256"),
)

def _request(url: str) -> urllib.request.Request:
    return urllib.request.Request(url, headers={
        "User-Agent": "CorVIA-Public-Artifact-Gate/1.0",
        "Accept": "application/octet-stream,text/plain;q=0.8,*/*;q=0.1",
        "Cache-Control": "no-cache, no-store, max-age=0", "Pragma": "no-cache",
    })

def _require_https(url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise AssertionError(f"URL pública deve usar HTTPS: {url}")
    if parsed.hostname not in ALLOWED_PUBLIC_HOSTS:
        raise AssertionError(f"Host público não autorizado para este gate: {parsed.hostname}")

def _cache_busted(url: str, cache_buster: str | None) -> str:
    if not cache_buster: return url
    parsed = urllib.parse.urlsplit(url)
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    query.append(("release", cache_buster))
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path,
                                    urllib.parse.urlencode(query), parsed.fragment))

def _read_sidecar(url: str, context: ssl.SSLContext, cache_buster: str | None) -> str:
    url = _cache_busted(url, cache_buster); _require_https(url)
    with urllib.request.urlopen(_request(url), timeout=45, context=context) as response:
        _require_https(response.geturl())
        body = response.read(4096).decode("ascii", errors="replace")
    match = SHA256_RE.search(body)
    if not match: raise AssertionError(f"Sidecar SHA-256 inválido: {url}")
    return match.group(1).lower()

def _download_and_hash(url: str, destination: Path, spec: ArtifactSpec,
                       context: ssl.SSLContext, cache_buster: str | None) -> dict[str, object]:
    url = _cache_busted(url, cache_buster); _require_https(url)
    digest = hashlib.sha256(); total = 0; first_bytes = b""
    with urllib.request.urlopen(_request(url), timeout=180, context=context) as response:
        final_url = response.geturl(); _require_https(final_url)
        content_type = response.headers.get_content_type().lower()
        if content_type not in spec.mime_types:
            raise AssertionError(f"{spec.name}: MIME {content_type!r} não permitido")
        declared = response.headers.get("Content-Length")
        if declared and int(declared) < spec.minimum_bytes:
            raise AssertionError(f"{spec.name}: Content-Length abaixo do mínimo")
        with destination.open("wb") as target:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk: break
                if not first_bytes: first_bytes = chunk[:max(4, len(spec.magic))]
                total += len(chunk)
                if total > MAX_ARTIFACT_BYTES:
                    raise AssertionError(f"{spec.name}: artefato excede limite de segurança")
                digest.update(chunk); target.write(chunk)
    if total < spec.minimum_bytes: raise AssertionError(f"{spec.name}: tamanho abaixo do mínimo")
    if not first_bytes.startswith(spec.magic): raise AssertionError(f"{spec.name}: assinatura binária incompatível")
    return {"final_url": final_url, "mime": content_type, "bytes": total, "sha256": digest.hexdigest()}

def validate(base_url: str, specs: tuple[ArtifactSpec, ...] = SPECS,
             expected_shas: dict[str, str] | None = None,
             cache_buster: str | None = None) -> dict[str, object]:
    base_url = base_url.rstrip("/"); _require_https(base_url)
    context = ssl.create_default_context()
    report: dict[str, object] = {"base_url": base_url, "artifacts": {}}
    artifacts = report["artifacts"]; assert isinstance(artifacts, dict)
    with tempfile.TemporaryDirectory(prefix="corvia-public-artifacts-") as temp_dir:
        for spec in specs:
            url = f"{base_url}{spec.path}"
            sidecar_sha = _read_sidecar(f"{url}.sha256", context, cache_buster)
            result = _download_and_hash(url, Path(temp_dir) / Path(spec.path).name, spec, context, cache_buster)
            actual_sha = str(result["sha256"])
            if actual_sha != sidecar_sha:
                raise AssertionError(f"{spec.name}: binário difere do sidecar")
            pinned_sha = ((expected_shas or {}).get(spec.name, "") or os.getenv(spec.pinned_sha_env, "")).strip().lower()
            if pinned_sha:
                if not SHA256_RE.fullmatch(pinned_sha): raise AssertionError(f"{spec.pinned_sha_env} inválido")
                if actual_sha != pinned_sha: raise AssertionError(f"{spec.name}: digest difere do release esperado")
            result.update({"source_url": url, "sidecar_sha256": sidecar_sha,
                           "pinned_sha_verified": bool(pinned_sha), "expected_sha256": pinned_sha or None})
            artifacts[spec.name] = result
    return report

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--expected-android-sha256")
    parser.add_argument("--expected-windows-sha256")
    parser.add_argument("--cache-buster")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        report = validate(args.base_url, expected_shas={"android": args.expected_android_sha256 or "",
                                                        "windows": args.expected_windows_sha256 or ""},
                          cache_buster=args.cache_buster)
    except (AssertionError, OSError, urllib.error.URLError, ValueError) as exc:
        print(f"ERRO: validação pública dos apps falhou: {exc}", file=sys.stderr); return 1
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__": raise SystemExit(main())
