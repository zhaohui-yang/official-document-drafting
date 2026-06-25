#!/usr/bin/env python3
"""在线 skill 产物构建脚本。

功能说明：
- 从 `prompts/` 主源生成在线 skill 场景所需的正式产物。
- 同步更新仓库根目录的 `SKILL.md`、`agents/openai.yaml`，以及 `dist/skill/` 下的构建产物。
- 可通过 `--check` 检查当前产物是否与主源规则保持同步。

主要产物：
- `SKILL.md`
- `agents/openai.yaml`
- `dist/skill/SKILL.md`
- `dist/skill/agents/openai.yaml`

适用场景：
- Codex
- agents
- Claude Code 等兼容 skill / agent 入口的在线宿主

Author: official-document-drafting maintainers
"""

from __future__ import annotations

import argparse
import pathlib
import sys


__author__ = "official-document-drafting maintainers"
__maintainer__ = "official-document-drafting maintainers"


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from adapters.shared import (  # noqa: E402
    DIST_DIR,
    ROOT_AGENT_PATH,
    ROOT_SKILL_PATH,
    Profile,
    DocType,
    build_template_outputs,
    load_doc_types,
    load_profile,
    render_agent_yaml,
    render_skill_markdown,
    write_text,
)


DIST_SKILL_PATH = DIST_DIR / "skill" / "SKILL.md"
DIST_AGENT_PATH = DIST_DIR / "skill" / "agents" / "openai.yaml"


def build_targets(profile: Profile, doc_types: list[DocType]) -> dict[pathlib.Path, str]:
    """构建本 profile 下所有由 prompts/ 主源生成的产物（路径 -> 期望内容）。

    既用于写盘，也用于 `--check` 和同步测试。覆盖 SKILL.md、agent 接口、dist 副本，
    以及 `assets/templates/` 下所有模板，确保它们都不会脱离主源悄悄漂移。
    """
    skill_md = render_skill_markdown(profile, doc_types)
    agent_yaml = render_agent_yaml(profile)

    targets: dict[pathlib.Path, str] = {
        ROOT_SKILL_PATH: skill_md,
        ROOT_AGENT_PATH: agent_yaml,
        DIST_SKILL_PATH: skill_md,
        DIST_AGENT_PATH: agent_yaml,
    }
    targets.update(build_template_outputs(doc_types, profile.default_template))
    return targets


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="从 prompts/ 主源生成 skill 产物。")
    parser.add_argument("--profile", default="default", help="profile 名称，默认 default")
    parser.add_argument("--check", action="store_true", help="只检查产物是否与当前主源同步")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    profile = load_profile(args.profile)
    doc_types = load_doc_types()
    targets = build_targets(profile, doc_types)

    if args.check:
        mismatched: list[pathlib.Path] = []
        for path, expected in targets.items():
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                mismatched.append(path)
        if mismatched:
            print("[ERROR] 以下文件未与 prompts/ 主源同步：", file=sys.stderr)
            for path in mismatched:
                print(f"- {path}", file=sys.stderr)
            return 1
        print(f"[OK] skill 产物已与 prompts/ 主源同步（共 {len(targets)} 个文件）。")
        return 0

    for path, content in targets.items():
        write_text(path, content)

    print(f"[OK] 已生成 {len(targets)} 个产物，包含 SKILL.md、agent 接口、dist 副本和 assets/templates/。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
