#!/usr/bin/env python3
"""Valida um certificado backend reutilizavel retornado pela API do GitHub."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any


SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")


def has_reusable_suite(
    payload: dict[str, Any],
    *,
    candidate_sha: str,
    job_name: str,
    suite_key: str,
) -> bool:
    """Aceita somente job e step certificados, verdes e do SHA exato."""
    if not SHA_PATTERN.fullmatch(candidate_sha):
        return False
    expected_step = f"Backend suite certificate {suite_key}"
    jobs = payload.get("jobs")
    if not isinstance(jobs, list):
        return False
    return any(
        isinstance(job, dict)
        and job.get("name") == job_name
        and job.get("head_sha") == candidate_sha
        and job.get("status") == "completed"
        and job.get("conclusion") == "success"
        and any(
            isinstance(step, dict)
            and step.get("name") == expected_step
            and step.get("status") == "completed"
            and step.get("conclusion") == "success"
            for step in (job.get("steps") or [])
        )
        for job in jobs
    )


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs-json", type=Path, required=True)
    parser.add_argument("--candidate-sha", required=True)
    parser.add_argument("--job-name", required=True)
    parser.add_argument("--suite-key", required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    with args.jobs_json.open(encoding="utf-8") as stream:
        payload = json.load(stream)
    reusable = has_reusable_suite(
        payload,
        candidate_sha=args.candidate_sha,
        job_name=args.job_name,
        suite_key=args.suite_key,
    )
    print(json.dumps({"reusable": reusable}, sort_keys=True))
    return 0 if reusable else 1


if __name__ == "__main__":
    raise SystemExit(main())
