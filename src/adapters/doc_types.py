"""文种（doc-type）的数据结构、加载校验、检索与目录渲染。"""

from __future__ import annotations

import pathlib
import re
from dataclasses import dataclass

from adapters.paths import DOC_TYPES_DIR, load_toml, read_text
from adapters.profiles import (
    load_font_profiles,
    load_layout_profiles,
    normalize_doc_type_key,
)


@dataclass(frozen=True)
class DocTypeSpec:
    writing_rules: str
    layout_rules: str
    template: str
    writing_guide: str = ""
    drafting_inputs: str = ""


@dataclass(frozen=True)
class DocType:
    id: str
    title: str
    display_name: str
    dir_label: str
    font_profile_id: str
    layout_profile_id: str
    aliases: list[str]
    category: str
    description: str
    dir_path: pathlib.Path
    spec_path: pathlib.Path
    examples_path: pathlib.Path | None

    @property
    def prompt_dir(self) -> pathlib.Path:
        return DOC_TYPES_DIR / f"{self.id}-{self.dir_label}"


def load_doc_types() -> list[DocType]:
    font_profiles = load_font_profiles()
    layout_profiles = load_layout_profiles()
    items: list[DocType] = []
    for dir_path in sorted(DOC_TYPES_DIR.iterdir()):
        if not dir_path.is_dir():
            continue
        meta_path = dir_path / "meta.toml"
        if not meta_path.exists():
            continue

        raw = load_toml(meta_path)
        examples_path = dir_path / "examples.md"
        spec_path = dir_path / "spec.md"
        if not spec_path.exists():
            raise ValueError(f"缺少文种规范文件：{spec_path}")
        display_name = raw.get("display_name", raw["title"])
        dir_label = raw.get("dir_label", display_name)
        expected_dir_name = f"{raw['id']}-{dir_label}"
        if dir_path.name != expected_dir_name:
            raise ValueError(
                f"文种目录名与 meta.toml 不一致：{dir_path.name} != {expected_dir_name}"
            )
        font_profile_id = raw["font_profile"]
        if font_profile_id not in font_profiles:
            raise ValueError(f"文种 {raw['id']} 引用了未定义的字体方案：{font_profile_id}")
        layout_profile_id = raw.get("layout_profile", font_profile_id)
        if layout_profile_id not in layout_profiles:
            raise ValueError(f"文种 {raw['id']} 引用了未定义的版式方案：{layout_profile_id}")
        items.append(
            DocType(
                id=raw["id"],
                title=raw["title"],
                display_name=display_name,
                dir_label=dir_label,
                font_profile_id=font_profile_id,
                layout_profile_id=layout_profile_id,
                aliases=list(raw.get("aliases", [])),
                category=raw["category"],
                description=raw["description"],
                dir_path=dir_path,
                spec_path=spec_path,
                examples_path=examples_path if examples_path.exists() else None,
            )
        )

    return items


def sort_doc_types(doc_types: list[DocType], category_order: list[str]) -> list[DocType]:
    category_rank = {name: index for index, name in enumerate(category_order)}
    return sorted(doc_types, key=lambda item: (category_rank.get(item.category, len(category_rank)), item.id))


def build_doc_type_lookup(doc_types: list[DocType]) -> dict[str, DocType]:
    lookup: dict[str, DocType] = {}
    for item in doc_types:
        for key in {item.id, item.title, item.display_name, *item.aliases}:
            normalized = normalize_doc_type_key(key)
            if normalized:
                lookup[normalized] = item
    return lookup


def resolve_doc_type(raw_doc_type: str | None, doc_types: list[DocType]) -> DocType | None:
    if not raw_doc_type:
        return None

    lookup = build_doc_type_lookup(doc_types)
    doc_type = lookup.get(normalize_doc_type_key(raw_doc_type))
    if doc_type is None:
        supported = ", ".join(sorted({item.display_name for item in doc_types}))
        raise ValueError(f"未识别文种：{raw_doc_type}。当前支持：{supported}")
    return doc_type


def parse_doc_type_spec(path: pathlib.Path) -> DocTypeSpec:
    text = read_text(path)
    sections: dict[str, list[str]] = {}
    current: str | None = None

    # 必备三段 + 可选「撰写思路」「起草要点」（每文种可在自己的 spec 里统一配置，留空则不输出）。
    known_sections = {"写作规则", "起草要点", "撰写思路", "版式要求", "模板"}
    for line in text.splitlines():
        heading = re.match(r"^##\s+(.*)$", line)
        if heading and heading.group(1).strip() in known_sections:
            current = heading.group(1).strip()
            sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(line)

    missing = [name for name in ("写作规则", "版式要求", "模板") if name not in sections]
    if missing:
        raise ValueError(f"文种规范缺少章节 {missing}：{path}")

    template_block = "\n".join(sections["模板"]).strip()
    template_match = re.fullmatch(r"```(?:markdown)?\n(.*)\n```", template_block, flags=re.DOTALL)
    if template_match is None:
        raise ValueError(f"文种规范的模板章节必须使用 markdown 代码块包裹：{path}")

    return DocTypeSpec(
        writing_rules="\n".join(sections["写作规则"]).strip(),
        layout_rules="\n".join(sections["版式要求"]).strip(),
        template=template_match.group(1).strip(),
        writing_guide="\n".join(sections.get("撰写思路", [])).strip(),
        drafting_inputs="\n".join(sections.get("起草要点", [])).strip(),
    )


def format_doc_type_catalog(doc_types: list[DocType], category_order: list[str]) -> str:
    # 路径规约（spec.md、font-profiles、layout-profiles）在 SKILL.md / 离线提示词里统一声明一次，
    # 目录每行只保留 id、文种、别名、方案名和说明，不再逐行重复全路径。
    grouped: dict[str, list[DocType]] = {}
    for item in sort_doc_types(doc_types, category_order):
        grouped.setdefault(item.category, []).append(item)

    ordered_categories = category_order + sorted(name for name in grouped if name not in category_order)
    lines: list[str] = []
    for category in ordered_categories:
        if category not in grouped:
            continue
        lines.append(f"### {category}")
        lines.append("")
        for item in grouped[category]:
            aliases = "、".join(item.aliases) if item.aliases else item.display_name
            lines.append(
                f"- `{item.id}` / {item.display_name} / 别名：{aliases} / "
                f"字体方案：`{item.font_profile_id}` / 版式方案：`{item.layout_profile_id}` / {item.description}"
            )
        lines.append("")

    return "\n".join(lines).strip()
