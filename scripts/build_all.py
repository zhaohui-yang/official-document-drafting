#!/usr/bin/env python3
"""从 prompts/ 主源构建（或 --check 校验）全部生成产物。

离线 profile 清单由 `adapters/offline/build.py --all-profiles` 统一维护，
这里不再各自写死，避免新增 profile 时两处脱节。
"""

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
    extra = ["--check"] if "--check" in sys.argv[1:] else []
    run([python, str(REPO_ROOT / "adapters" / "skill" / "build.py"), *extra])
    run([python, str(REPO_ROOT / "adapters" / "offline" / "build.py"), "--all-profiles", *extra])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
