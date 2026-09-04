#!/usr/bin/env python3
"""Compatibilidade do workflow: delega a execução ao reconciliador v3."""
from __future__ import annotations

import reconcile_open_science_prs_v3 as v3

if __name__ == "__main__":
    raise SystemExit(v3.base.main())
