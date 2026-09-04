#!/usr/bin/env python3
"""Compatibilidade do workflow: delega a execução ao reconciliador v4."""
from __future__ import annotations

import reconcile_open_science_prs_v4 as v4

if __name__ == "__main__":
    raise SystemExit(v4.base.main())
