"""profile、字体方案、版式方案的数据结构、加载与 Markdown 渲染。"""

from __future__ import annotations

import pathlib
from dataclasses import dataclass

from adapters.paths import (
    FONT_CATALOG_PATH,
    FONT_PROFILES_DIR,
    LAYOUT_PROFILES_DIR,
    PROFILES_DIR,
    REPO_ROOT,
    format_chars,
    format_twips_as_pt,
    load_toml,
)


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
    offline_system_preamble: str
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


# 字体/版式/文种的键归一化共用同一规则；文种侧（doc_types.py）从本模块导入复用。
def normalize_doc_type_key(value: str) -> str:
    return value.strip().lower().replace("_", "-")


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
        offline_system_preamble=raw["offline_system_preamble"].strip(),
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
