#!/usr/bin/env python3
"""Validate published binaries or prove explicitly retired public apps are gone."""

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


# Canonical and previously advertised aliases. Sidecars are checked separately.
RETIRED_PATHS = {
    "android": (
        "/downloads/corvia-cardiology-spaces-android-1.2.0.apk",
        "/downloads/corvia-os-android.apk",
        "/downloads/corvia-os-android-1.0.1.apk",
        "/downloads/corvia-cardiology-spaces-android.apk",
        "/downloads/corvia-cardiology-spaces-android-1.1.0.apk",
    ),
    "windows": (
        "/downloads/corvia-cardiology-spaces-windows-1.2.0.exe",
        "/downloads/corvia-os-windows.exe",
        "/downloads/corvia-os-windows.zip",
    ),
}


class _NoRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        # A retired alias must itself return 410, not redirect to a live binary
        # or hide a stale route behind a terminal 410 on a different URL.
        return None


def validate_retired(
    base_url: str,
    apps: tuple[str, ...],
    cache_buster: str | None = None,
) -> dict[str, object]:
    """Require 410/no-store on every selected native route and its checksum.

    No binary is downloaded. Redirects are rejected, not followed. With a
    release marker, both the original and cache-busted URLs are tested so a
    stale CDN response cannot be hidden by testing only a new query string.
    """
    base_url = base_url.rstrip("/")
    _require_https(base_url)
    parsed = urllib.parse.urlsplit(base_url)
    if (parsed.path or parsed.query or parsed.fragment or parsed.username
            or parsed.password or parsed.port not in (None, 443)):
        raise AssertionError("Retirement gate requires the authorized HTTPS origin")
    selected = tuple(dict.fromkeys(apps))
    if not selected or any(name not in RETIRED_PATHS for name in selected):
        raise AssertionError("Select at least one known retired application")
    opener = urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=ssl.create_default_context()),
        _NoRedirects(),
    )
    checked: dict[str, list[dict[str, object]]] = {}
    for name in selected:
        checked[name] = []
        for path in RETIRED_PATHS[name]:
            for suffix in ("", ".sha256"):
                source_url = f"{base_url}{path}{suffix}"
                urls = tuple(dict.fromkeys((
                    source_url, _cache_busted(source_url, cache_buster),
                )))
                for url in urls:
                    try:
                        with opener.open(_request(url), timeout=30) as response:
                            status = response.getcode()
                            headers = response.headers
                    except urllib.error.HTTPError as exc:
                        status, headers = exc.code, exc.headers
                        exc.close()
                    if status != 410:
                        raise AssertionError(
                            f"{name}: expected retired status 410, got {status}: {url}"
                        )
                    if headers.get("Location"):
                        raise AssertionError(f"{name}: retired response has Location: {url}")
                    directives = {
                        value.strip().casefold().split("=", 1)[0]
                        for value in headers.get("Cache-Control", "").split(",")
                    }
                    if "no-store" not in directives:
                        raise AssertionError(f"{name}: retired response lacks no-store: {url}")
                    checked[name].append({
                        "url": url, "status": status, "cache_control": headers.get("Cache-Control"),
                    })
    return {
        "base_url": base_url,
        "retired_routes": checked,
        "release_status": {
            spec.name: "retired" if spec.name in selected else "not_checked"
            for spec in SPECS
        },
    }



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
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--artifacts", nargs="+", choices=tuple(spec.name for spec in SPECS),
        default=None,
        help="Artifacts to validate explicitly (default: all).",
    )
    mode.add_argument(
        "--retired", nargs="+", choices=tuple(RETIRED_PATHS),
        help="Require HTTP 410/no-store for cancelled apps and all known aliases.",
    )
    parser.add_argument("--expected-android-sha256")
    parser.add_argument("--expected-windows-sha256")
    parser.add_argument("--cache-buster")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if args.retired and (args.expected_android_sha256 or args.expected_windows_sha256):
        parser.error("Expected binary digests cannot be used with --retired")
    try:
        if args.retired:
            report = validate_retired(args.base_url, tuple(args.retired), args.cache_buster)
        else:
            names = args.artifacts or [spec.name for spec in SPECS]
            selected = tuple(spec for spec in SPECS if spec.name in set(names))
            report = validate(args.base_url, specs=selected,
                              expected_shas={"android": args.expected_android_sha256 or "",
                                             "windows": args.expected_windows_sha256 or ""},
                              cache_buster=args.cache_buster)
            report["release_status"] = {
                "android": "published" if "android" in names else "not_checked",
                "windows": "published" if "windows" in names else "pending",
            }
    except (AssertionError, OSError, urllib.error.URLError, ValueError) as exc:
        print(f"ERRO: validação pública dos apps falhou: {exc}", file=sys.stderr); return 1
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__": raise SystemExit(main())
