"""路径常量与最小 IO/文本工具，仓库根为上溯三层。"""

from __future__ import annotations

import pathlib
import tomllib


# 代码统一放在 src/ 下：paths.py 位于 src/adapters/paths.py，仓库根为上溯三层。
REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PROMPTS_DIR = REPO_ROOT / "prompts"
PROFILES_DIR = PROMPTS_DIR / "profiles"
DOC_TYPES_DIR = PROMPTS_DIR / "doc-types"
FONT_PROFILES_DIR = PROMPTS_DIR / "font-profiles"
LAYOUT_PROFILES_DIR = PROMPTS_DIR / "layout-profiles"
DIST_DIR = REPO_ROOT / "dist"
ROOT_SKILL_PATH = REPO_ROOT / "SKILL.md"
# agent 接口产物只保留在 dist/skill/agents/openai.yaml（见 skill/build.py 的 DIST_AGENT_PATH）。
ROOT_TEMPLATES_DIR = REPO_ROOT / "assets" / "templates"
DOC_TYPE_GUARDRAILS_PATH = PROMPTS_DIR / "core" / "doc-type-guardrails.md"
FONT_CATALOG_PATH = REPO_ROOT / "assets" / "fonts" / "catalog.toml"


def read_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def write_text(path: pathlib.Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def load_toml(path: pathlib.Path) -> dict:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def format_twips_as_pt(twips: int) -> str:
    points = twips / 20
    points_text = f"{points:.2f}".rstrip("0").rstrip(".")
    return f"{twips} twips / {points_text}pt"


def format_chars(chars_hundredths: int) -> str:
    chars = chars_hundredths / 100
    chars_text = f"{chars:.2f}".rstrip("0").rstrip(".")
    return f"{chars_text} 字符"


def shift_markdown_headings(text: str, levels: int = 1) -> str:
    if levels <= 0:
        return text

    shifted_lines: list[str] = []
    for line in text.splitlines():
        if line.startswith("#"):
            hashes, _, rest = line.partition(" ")
            if rest:
                shifted_lines.append(f"{hashes}{'#' * levels} {rest}")
                continue
        shifted_lines.append(line)
    return "\n".join(shifted_lines)
