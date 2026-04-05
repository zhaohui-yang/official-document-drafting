#!/usr/bin/env python3
"""Build all generated artifacts from prompts/ source."""

from __future__ import annotations

import pathlib
import subprocess
import sys


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


def run(args: list[str]) -> None:
    completed = subprocess.run(args, cwd=REPO_ROOT)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> int:
    python = sys.executable
    run([python, str(REPO_ROOT / "adapters" / "skill" / "build.py")])
    run([python, str(REPO_ROOT / "adapters" / "offline" / "build.py"), "--profile", "default"])
    run([python, str(REPO_ROOT / "adapters" / "offline" / "build.py"), "--profile", "small-local"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
