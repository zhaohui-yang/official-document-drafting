#!/usr/bin/env python3
"""Renderer entrypoint for Markdown-to-docx export."""

from __future__ import annotations

import pathlib
import runpy


TARGET = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "generate_docx.py"


if __name__ == "__main__":
    runpy.run_path(str(TARGET), run_name="__main__")
