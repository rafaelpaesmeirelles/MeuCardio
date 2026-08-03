#!/usr/bin/env python3
"""Impede regressão para Actions baseadas em runtimes Node obsoletos."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
MINIMUM_MAJORS = {
    "actions/checkout": 6,
    "actions/setup-python": 6,
    "actions/setup-node": 6,
    "actions/dependency-review-action": 5,
}
USES_PATTERN = re.compile(
    r"uses:\s*(actions/(?:checkout|setup-python|setup-node|dependency-review-action))@v(\d+)"
)


def main() -> int:
    failures: list[str] = []
    checked = 0

    for workflow in sorted(WORKFLOWS.glob("*.y*ml")):
        content = workflow.read_text(encoding="utf-8")
        for match in USES_PATTERN.finditer(content):
            action, major_text = match.groups()
            major = int(major_text)
            checked += 1
            minimum = MINIMUM_MAJORS[action]
            if major < minimum:
                failures.append(
                    f"{workflow.relative_to(ROOT)}: {action}@v{major} "
                    f"deve ser >= v{minimum}"
                )

    if checked == 0:
        failures.append("Nenhuma Action oficial monitorada foi encontrada nos workflows.")

    if failures:
        print("Política de runtime das GitHub Actions reprovada:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"Política de runtime aprovada: {checked} uso(s) verificado(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
