#!/usr/bin/env python3
"""Compatibility wrapper for the AI Worktrees read-only inspector."""

from __future__ import annotations

import runpy
from pathlib import Path


TARGET = (
    Path(__file__).resolve().parents[2]
    / "com.actionfit.ai-worktrees"
    / "Tools"
    / "inspect_worktrees.py"
)

if not TARGET.is_file():
    raise SystemExit(
        "AI Worktrees inspector was not found. Install com.actionfit.ai-worktrees or use its package path."
    )

runpy.run_path(str(TARGET), run_name="__main__")
