#!/usr/bin/env python3
"""Build skill-facing artifacts from prompts/ source."""

from __future__ import annotations

import argparse
import pathlib
import sys


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from adapters.shared import (  # noqa: E402
    DIST_DIR,
    ROOT_AGENT_PATH,
    ROOT_SKILL_PATH,
    export_templates,
    load_doc_types,
    load_profile,
    render_agent_yaml,
    render_skill_markdown,
    write_text,
)


DIST_SKILL_PATH = DIST_DIR / "skill" / "SKILL.md"
DIST_AGENT_PATH = DIST_DIR / "skill" / "agents" / "openai.yaml"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="从 prompts/ 主源生成 skill 产物。")
    parser.add_argument("--profile", default="default", help="profile 名称，默认 default")
    parser.add_argument("--check", action="store_true", help="只检查产物是否与当前主源同步")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    profile = load_profile(args.profile)
    doc_types = load_doc_types()
    skill_md = render_skill_markdown(profile, doc_types)
    agent_yaml = render_agent_yaml(profile)

    targets = {
        ROOT_SKILL_PATH: skill_md,
        ROOT_AGENT_PATH: agent_yaml,
        DIST_SKILL_PATH: skill_md,
        DIST_AGENT_PATH: agent_yaml,
    }

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
        print("[OK] skill 产物已与 prompts/ 主源同步。")
        return 0

    for path, content in targets.items():
        write_text(path, content)

    export_templates(doc_types, profile.default_template)
    print(f"[OK] 已生成 {ROOT_SKILL_PATH}")
    print(f"[OK] 已生成 {ROOT_AGENT_PATH}")
    print(f"[OK] 已生成 {DIST_SKILL_PATH}")
    print(f"[OK] 已生成 {DIST_AGENT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
