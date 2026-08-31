#!/usr/bin/env python3
"""Deep static inventory for release regression detection.

Counts backend endpoints and frontend routes, pages, interactive controls,
event bindings and API references. On pull requests, materializes the base
commit in a temporary directory and rejects meaningful feature loss.
"""

from __future__ import annotations

import argparse
import io
import json
import re
import subprocess
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENDPOINT_RE = re.compile(r"@(?:router|app)\.(?:get|post|put|patch|delete|options|head|websocket)\s*\(")
ROUTE_RE = re.compile(r"<Route\s+(?:[^>]*?\s)?path=[\"']([^\"']+)[\"']")
PAGE_IMPORT_RE = re.compile(r"(?:from\s+[\"']\./pages/|import\s*\(\s*[\"']\./pages/)([^\"']+)")
CONTROL_RE = re.compile(r"<(?:button|a|input|select|textarea|form|NavLink|Link)\b")
EVENT_RE = re.compile(r"\bon(?:Click|Submit|Change|Input|KeyDown|KeyUp|PointerDown|TouchStart)\s*=")
API_LITERAL_RE = re.compile(
    r"(?:api\.(?:get|post|put|patch|delete)\s*(?:<[^;()]+>)?\s*\(|fetch\s*\()\s*"
    r"[\"'`]([^\"'`]+)"
)
HANDLER_RE = re.compile(
    r"\b(?:async\s+)?function\s+[A-Za-z_$][\w$]*\s*\(|"
    r"\bconst\s+[A-Za-z_$][\w$]*\s*=\s*(?:async\s*)?\([^)]*\)\s*=>"
)

def sources(root: Path, pattern: str) -> list[Path]:
    return [path for path in root.glob(pattern) if path.is_file()]

def read_many(paths: list[Path]) -> str:
    chunks = []
    for path in paths:
        try: chunks.append(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError: continue
    return "\n".join(chunks)

def inventory(root: Path) -> dict[str, object]:
    backend = read_many(sources(root, "backend/app/**/*.py"))
    frontend_paths = sources(root, "frontend/src/**/*.tsx") + sources(root, "frontend/src/**/*.ts")
    frontend = read_many(frontend_paths)
    app_path = root / "frontend/src/App.tsx"
    app = app_path.read_text(encoding="utf-8") if app_path.is_file() else ""
    api_references = API_LITERAL_RE.findall(frontend)
    api_paths = sorted(set(match.rstrip("?&") for match in api_references))
    routes = sorted(set(ROUTE_RE.findall(app)))
    pages = sorted(set(PAGE_IMPORT_RE.findall(app)))
    return {
        "backend_endpoints": len(ENDPOINT_RE.findall(backend)),
        "frontend_routes": len(routes),
        "imported_pages": len(pages),
        "interactive_controls": len(CONTROL_RE.findall(frontend)),
        "event_bindings": len(EVENT_RE.findall(frontend)),
        "named_handlers": len(HANDLER_RE.findall(frontend)),
        "api_calls": len(api_references),
        "unique_api_paths": len(api_paths),
        "routes": routes,
        "api_paths": api_paths,
    }

def extract_ref(ref: str, destination: Path) -> None:
    archive = subprocess.run(["git", "archive", "--format=tar", ref], cwd=ROOT,
                             check=True, stdout=subprocess.PIPE).stdout
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as bundle:
        for member in bundle.getmembers():
            target = (destination / member.name).resolve()
            if destination.resolve() not in target.parents and target != destination.resolve():
                raise RuntimeError("unsafe path in git archive")
        bundle.extractall(destination, filter="data")

def compare(current: dict[str, object], baseline: dict[str, object]) -> None:
    strict = ("backend_endpoints", "frontend_routes", "imported_pages", "unique_api_paths")
    tolerant = ("interactive_controls", "event_bindings", "named_handlers", "api_calls")
    failures = []
    for key in strict:
        if int(current[key]) < int(baseline[key]):
            failures.append(f"{key}: {current[key]} < baseline {baseline[key]}")
    for key in tolerant:
        minimum = int(int(baseline[key]) * 0.90)
        if int(current[key]) < minimum:
            failures.append(f"{key}: {current[key]} < 90% baseline ({baseline[key]})")
    if failures:
        raise AssertionError("deep functional regression: " + "; ".join(failures))

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compare-ref")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result: dict[str, object] = {"current": inventory(ROOT)}
    if args.compare_ref:
        with tempfile.TemporaryDirectory(prefix="corvia-feature-base-") as tmp:
            base_root = Path(tmp)
            extract_ref(args.compare_ref, base_root)
            baseline = inventory(base_root)
        result["baseline"] = baseline
        compare(result["current"], baseline)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["current"], ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    try: raise SystemExit(main())
    except (AssertionError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"ERRO: {exc}")
        raise SystemExit(1)
