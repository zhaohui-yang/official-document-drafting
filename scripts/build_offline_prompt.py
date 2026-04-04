#!/usr/bin/env python3
"""Backward-compatible wrapper for the new offline adapter builder."""

from __future__ import annotations

import pathlib
import runpy


TARGET = pathlib.Path(__file__).resolve().parent.parent / "adapters" / "offline" / "build.py"


if __name__ == "__main__":
    runpy.run_path(str(TARGET), run_name="__main__")
