#!/usr/bin/env python3
"""Shared prompt-source loading and rendering helpers."""

from __future__ import annotations

import json
import pathlib
import re
import tomllib
from dataclasses import dataclass


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PROMPTS_DIR = REPO_ROOT / "prompts"
PROFILES_DIR = PROMPTS_DIR / "profiles"
DOC_TYPES_DIR = PROMPTS_DIR / "doc-types"
FONT_PROFILES_DIR = PROMPTS_DIR / "font-profiles"
LAYOUT_PROFILES_DIR = PROMPTS_DIR / "layout-profiles"
DIST_DIR = REPO_ROOT / "dist"
ROOT_SKILL_PATH = REPO_ROOT / "SKILL.md"
ROOT_AGENT_PATH = REPO_ROOT / "agents" / "openai.yaml"
ROOT_TEMPLATES_DIR = REPO_ROOT / "assets" / "templates"
DOC_TYPE_GUARDRAILS_PATH = PROMPTS_DIR / "core" / "doc-type-guardrails.md"
FONT_CATALOG_PATH = REPO_ROOT / "assets" / "fonts" / "catalog.toml"


@dataclass(frozen=True)
class CoreSection:
    title: str
    path: pathlib.Path


@dataclass(frozen=True)
class Profile:
    name: str
    skill_name: str
    skill_title: str
    skill_description: str
    skill_metadata: dict[str, object]
    agent_display_name: str
    agent_short_description: str
    agent_default_prompt: str
    allow_implicit_invocation: bool
    default_template: pathlib.Path
    category_order: list[str]
    webui_system_preamble: str
    core_sections: list[CoreSection]


@dataclass(frozen=True)
class FontFamily:
    id: str
    display_name: str
    font_name: str
    files: tuple[pathlib.Path, ...]
    usage: str
    license_note: str


@dataclass(frozen=True)
class FontProfile:
    id: str
    display_name: str
    description: str
    header_family: FontFamily
    title_family: FontFamily
    heading_family: FontFamily
    subheading_family: FontFamily
    body_family: FontFamily
    header_size: int
    title_size: int
    heading_size: int
    body_size: int
    notes: list[str]


@dataclass(frozen=True)
class LayoutProfile:
    id: str
    display_name: str
    description: str
    body_line_spacing_twips: int
    title_line_spacing_twips: int
    header_after_twips: int
    doc_number_after_twips: int
    title_after_twips: int
    recipient_after_twips: int
    signing_before_twips: int
    body_first_line_chars: int
    notes: list[str]


@dataclass(frozen=True)
class DocTypeSpec:
    writing_rules: str
    layout_rules: str
    template: str


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


def load_profile(profile_name: str = "default") -> Profile:
    path = PROFILES_DIR / f"{profile_name}.toml"
    raw = load_toml(path)
    core_sections = [
        CoreSection(title=item["title"], path=REPO_ROOT / item["file"])
        for item in raw["core_sections"]
    ]

    return Profile(
        name=raw["name"],
        skill_name=raw["skill_name"],
        skill_title=raw["skill_title"],
        skill_description=raw["skill_description"],
        skill_metadata=dict(raw.get("skill_metadata", {})),
        agent_display_name=raw["agent_display_name"],
        agent_short_description=raw["agent_short_description"],
        agent_default_prompt=raw["agent_default_prompt"],
        allow_implicit_invocation=bool(raw["allow_implicit_invocation"]),
        default_template=REPO_ROOT / raw["default_template"],
        category_order=list(raw.get("category_order", [])),
        webui_system_preamble=raw["webui_system_preamble"].strip(),
        core_sections=core_sections,
    )


def load_font_families() -> dict[str, FontFamily]:
    raw = load_toml(FONT_CATALOG_PATH)
    families_raw = raw.get("families", {})
    families: dict[str, FontFamily] = {}

    for family_id, item in families_raw.items():
        files = tuple((REPO_ROOT / "assets" / "fonts" / name) for name in item["files"])
        families[family_id] = FontFamily(
            id=family_id,
            display_name=item["display_name"],
            font_name=item["font_name"],
            files=files,
            usage=item.get("usage", ""),
            license_note=item.get("license_note", ""),
        )

    return families


def load_font_profiles() -> dict[str, FontProfile]:
    font_families = load_font_families()
    profiles: dict[str, FontProfile] = {}

    for path in sorted(FONT_PROFILES_DIR.glob("*.toml")):
        raw = load_toml(path)

        def family(key: str) -> FontFamily:
            family_id = raw[key]
            if family_id not in font_families:
                raise ValueError(f"未识别字体族：{family_id}（来自 {path}）")
            return font_families[family_id]

        profile = FontProfile(
            id=raw["id"],
            display_name=raw["display_name"],
            description=raw["description"],
            header_family=family("header_family"),
            title_family=family("title_family"),
            heading_family=family("heading_family"),
            subheading_family=family("subheading_family"),
            body_family=family("body_family"),
            header_size=int(raw.get("header_size", 26)),
            title_size=int(raw.get("title_size", 22)),
            heading_size=int(raw.get("heading_size", 16)),
            body_size=int(raw.get("body_size", 16)),
            notes=list(raw.get("notes", [])),
        )
        profiles[profile.id] = profile

    return profiles


def load_layout_profiles() -> dict[str, LayoutProfile]:
    profiles: dict[str, LayoutProfile] = {}

    for path in sorted(LAYOUT_PROFILES_DIR.glob("*.toml")):
        raw = load_toml(path)
        profile = LayoutProfile(
            id=raw["id"],
            display_name=raw["display_name"],
            description=raw["description"],
            body_line_spacing_twips=int(raw["body_line_spacing_twips"]),
            title_line_spacing_twips=int(raw.get("title_line_spacing_twips", raw["body_line_spacing_twips"])),
            header_after_twips=int(raw.get("header_after_twips", raw["body_line_spacing_twips"] // 2)),
            doc_number_after_twips=int(raw.get("doc_number_after_twips", raw["body_line_spacing_twips"] // 2)),
            title_after_twips=int(raw.get("title_after_twips", raw["body_line_spacing_twips"])),
            recipient_after_twips=int(raw.get("recipient_after_twips", raw["body_line_spacing_twips"])),
            signing_before_twips=int(raw.get("signing_before_twips", raw["body_line_spacing_twips"])),
            body_first_line_chars=int(raw.get("body_first_line_chars", 200)),
            notes=list(raw.get("notes", [])),
        )
        profiles[profile.id] = profile

    return profiles


def build_font_profile_lookup(font_profiles: dict[str, FontProfile]) -> dict[str, FontProfile]:
    lookup: dict[str, FontProfile] = {}
    for profile in font_profiles.values():
        for key in {profile.id, profile.display_name}:
            normalized = normalize_doc_type_key(key)
            if normalized:
                lookup[normalized] = profile
    return lookup


def resolve_font_profile(raw_font_profile: str, font_profiles: dict[str, FontProfile]) -> FontProfile:
    lookup = build_font_profile_lookup(font_profiles)
    profile = lookup.get(normalize_doc_type_key(raw_font_profile))
    if profile is None:
        supported = ", ".join(sorted(font_profiles))
        raise ValueError(f"未识别字体方案：{raw_font_profile}。当前支持：{supported}")
    return profile


def build_layout_profile_lookup(layout_profiles: dict[str, LayoutProfile]) -> dict[str, LayoutProfile]:
    lookup: dict[str, LayoutProfile] = {}
    for profile in layout_profiles.values():
        for key in {profile.id, profile.display_name}:
            normalized = normalize_doc_type_key(key)
            if normalized:
                lookup[normalized] = profile
    return lookup


def resolve_layout_profile(raw_layout_profile: str, layout_profiles: dict[str, LayoutProfile]) -> LayoutProfile:
    lookup = build_layout_profile_lookup(layout_profiles)
    profile = lookup.get(normalize_doc_type_key(raw_layout_profile))
    if profile is None:
        supported = ", ".join(sorted(layout_profiles))
        raise ValueError(f"未识别版式方案：{raw_layout_profile}。当前支持：{supported}")
    return profile


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


def normalize_doc_type_key(value: str) -> str:
    return value.strip().lower().replace("_", "-")


def resolve_doc_type(raw_doc_type: str | None, doc_types: list[DocType]) -> DocType | None:
    if not raw_doc_type:
        return None

    lookup = build_doc_type_lookup(doc_types)
    doc_type = lookup.get(normalize_doc_type_key(raw_doc_type))
    if doc_type is None:
        supported = ", ".join(sorted({item.display_name for item in doc_types}))
        raise ValueError(f"未识别文种：{raw_doc_type}。当前支持：{supported}")
    return doc_type


def render_core_sections(profile: Profile) -> str:
    blocks: list[str] = []
    for section in profile.core_sections:
        blocks.append(f"## {section.title}\n\n{shift_markdown_headings(read_text(section.path), levels=1)}")
    return "\n\n".join(blocks).strip()


def render_doc_type_guardrails() -> str:
    return read_text(DOC_TYPE_GUARDRAILS_PATH)


def parse_doc_type_spec(path: pathlib.Path) -> DocTypeSpec:
    text = read_text(path)
    sections: dict[str, list[str]] = {}
    current: str | None = None

    for line in text.splitlines():
        heading = re.match(r"^##\s+(.*)$", line)
        if heading and heading.group(1).strip() in {"写作规则", "版式要求", "模板"}:
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
    )


def format_font_family_files(family: FontFamily) -> str:
    if not family.files:
        return "系统字体，未绑定仓库内字体文件"
    return "、".join(f"`{path.relative_to(REPO_ROOT).as_posix()}`" for path in family.files)


def render_font_profile_markdown(font_profile: FontProfile) -> str:
    lines = [
        f"- 字体方案：{font_profile.display_name}（{font_profile.id}）",
        f"- 版头：{font_profile.header_family.font_name} / {font_profile.header_size}pt / 文件：{format_font_family_files(font_profile.header_family)}",
        f"- 标题：{font_profile.title_family.font_name} / {font_profile.title_size}pt / 文件：{format_font_family_files(font_profile.title_family)}",
        f"- 一级标题：{font_profile.heading_family.font_name} / {font_profile.heading_size}pt / 文件：{format_font_family_files(font_profile.heading_family)}",
        f"- 二级标题：{font_profile.subheading_family.font_name} / {font_profile.heading_size}pt / 文件：{format_font_family_files(font_profile.subheading_family)}",
        f"- 正文：{font_profile.body_family.font_name} / {font_profile.body_size}pt / 文件：{format_font_family_files(font_profile.body_family)}",
    ]
    if font_profile.description:
        lines.insert(1, f"- 适用说明：{font_profile.description}")
    for note in font_profile.notes:
        lines.append(f"- 备注：{note}")
    return "\n".join(lines)


def render_layout_profile_markdown(layout_profile: LayoutProfile) -> str:
    lines = [
        f"- 版式方案：{layout_profile.display_name}（{layout_profile.id}）",
        f"- 正文固定行距：{format_twips_as_pt(layout_profile.body_line_spacing_twips)}",
        f"- 标题行距：{format_twips_as_pt(layout_profile.title_line_spacing_twips)}",
        f"- 版头后距：{format_twips_as_pt(layout_profile.header_after_twips)}",
        f"- 发文字号后距：{format_twips_as_pt(layout_profile.doc_number_after_twips)}",
        f"- 标题后距：{format_twips_as_pt(layout_profile.title_after_twips)}",
        f"- 主送机关后距：{format_twips_as_pt(layout_profile.recipient_after_twips)}",
        f"- 落款前距：{format_twips_as_pt(layout_profile.signing_before_twips)}",
        f"- 正文首行缩进：{format_chars(layout_profile.body_first_line_chars)}",
    ]
    if layout_profile.description:
        lines.insert(1, f"- 适用说明：{layout_profile.description}")
    for note in layout_profile.notes:
        lines.append(f"- 备注：{note}")
    return "\n".join(lines)


def format_doc_type_catalog(doc_types: list[DocType], category_order: list[str], include_paths: bool) -> str:
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
            line = (
                f"- `{item.id}` / {item.display_name} / 别名：{aliases} / "
                f"字体方案：`{item.font_profile_id}` / 版式方案：`{item.layout_profile_id}` / {item.description}"
            )
            if include_paths:
                line += (
                    f" / 字体：`prompts/font-profiles/{item.font_profile_id}.toml`"
                    f" / 版式：`prompts/layout-profiles/{item.layout_profile_id}.toml`"
                    f" / 规范：`{item.prompt_dir.relative_to(REPO_ROOT).as_posix()}/spec.md`"
                )
            lines.append(line)
        lines.append("")

    return "\n".join(lines).strip()


def render_skill_markdown(profile: Profile, doc_types: list[DocType]) -> str:
    blocks = [
        "---",
        f"name: {profile.skill_name}",
        f"description: {profile.skill_description}",
    ]
    if profile.skill_metadata:
        blocks.append(f"metadata: {json.dumps(profile.skill_metadata, ensure_ascii=False)}")
    blocks.extend(
        [
            "---",
            "",
            "<!-- Generated from prompts/ and adapters/skill/build.py. -->",
            "",
            f"# {profile.skill_title}",
            "",
            "## 调用方式",
            "",
            "- 先读取共享总规则。",
            "- 判断当前任务最匹配的文种。",
            "- 文种确定后，先应用共享的防编造约束 `prompts/core/doc-type-guardrails.md`，再读取对应文种目录中的 `spec.md`，按其中的“写作规则”“版式要求”“模板”章节处理，并按 `meta.toml` 中的 `font_profile` 和 `layout_profile` 应用字体与版式参数。",
            "- 如存在 `examples.md`，并且用户明确要求更贴近既有样稿或单位写法，再按需参考。",
            "- 用户要求 Word 时，先形成 Markdown 成稿，再调用导出脚本。",
            "",
            render_core_sections(profile),
            "",
            "## 文种目录",
            "",
            format_doc_type_catalog(doc_types, profile.category_order, include_paths=True),
            "",
        ]
    )
    return "\n".join(blocks).rstrip() + "\n"


def render_agent_yaml(profile: Profile) -> str:
    allow_implicit = "true" if profile.allow_implicit_invocation else "false"
    return "\n".join(
        [
            "# Generated from prompts/profiles/default.toml and adapters/skill/build.py.",
            "interface:",
            f"  display_name: {json.dumps(profile.agent_display_name, ensure_ascii=False)}",
            f"  short_description: {json.dumps(profile.agent_short_description, ensure_ascii=False)}",
            f"  default_prompt: {json.dumps(profile.agent_default_prompt, ensure_ascii=False)}",
            "",
            "policy:",
            f"  allow_implicit_invocation: {allow_implicit}",
            "",
        ]
    )


def render_webui_system_prompt(profile: Profile, doc_types: list[DocType], doc_type: DocType | None, include_examples: bool) -> str:
    font_profiles = load_font_profiles()
    layout_profiles = load_layout_profiles()
    parts = [
        profile.webui_system_preamble,
        "## 共享总规则\n\n" + render_core_sections(profile),
    ]

    if doc_type is None:
        parts.append(
            "\n".join(
                [
                    "## 当前未指定文种",
                    "- 你需要先根据任务内容判断文种，再选择最匹配的文种规则和模板。",
                    "",
                    "## 可用文种目录",
                    format_doc_type_catalog(doc_types, profile.category_order, include_paths=False),
                    "",
                    "## 兜底骨架",
                    "```markdown",
                    read_text(profile.default_template),
                    "```",
                ]
            )
        )
        return "\n\n".join(part.strip() for part in parts if part.strip())

    doc_type_spec = parse_doc_type_spec(doc_type.spec_path)
    doc_blocks = [
        "## 当前文种",
        f"- 文种：{doc_type.display_name}",
        f"- 文种 ID：{doc_type.id}",
        f"- 分类：{doc_type.category}",
        f"- 适用说明：{doc_type.description}",
        f"- 规范文件：`{doc_type.spec_path.relative_to(REPO_ROOT).as_posix()}`",
        "",
        "## 当前文种强制约束",
        "```markdown",
        render_doc_type_guardrails(),
        "```",
        "",
        "## 当前文种专项规则",
        "```markdown",
        doc_type_spec.writing_rules,
        "```",
        "",
        "## 当前文种字体要求",
        render_font_profile_markdown(font_profiles[doc_type.font_profile_id]),
        "",
        "## 当前文种版式参数",
        render_layout_profile_markdown(layout_profiles[doc_type.layout_profile_id]),
        "",
        "## 当前文种版式要求",
        "```markdown",
        doc_type_spec.layout_rules,
        "```",
        "",
        "## 当前文种模板",
        "```markdown",
        doc_type_spec.template,
        "```",
    ]
    parts.append("\n".join(doc_blocks))

    if include_examples and doc_type.examples_path:
        parts.append(
            "\n".join(
                [
                    "## 当前文种示例",
                    "```markdown",
                    read_text(doc_type.examples_path),
                    "```",
                ]
            )
        )

    return "\n\n".join(part.strip() for part in parts if part.strip())


def export_templates(doc_types: list[DocType], fallback_template: pathlib.Path) -> None:
    ROOT_TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    for item in doc_types:
        write_text(ROOT_TEMPLATES_DIR / f"{item.id}.md", parse_doc_type_spec(item.spec_path).template + "\n")
    write_text(ROOT_TEMPLATES_DIR / "official-types-outline.md", read_text(fallback_template) + "\n")
