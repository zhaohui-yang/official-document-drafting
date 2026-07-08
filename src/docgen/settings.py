"""字体与版式方案解析：把 CLI 参数、文种配置与方案目录合并为最终导出设置。"""

from __future__ import annotations

import argparse

from adapters.shared import (
    FontProfile,
    LayoutProfile,
    load_doc_types,
    load_font_profiles,
    load_layout_profiles,
    render_font_profile_markdown,
    render_layout_profile_markdown,
    resolve_doc_type,
    resolve_font_profile,
    resolve_layout_profile,
)
from docgen.constants import DEFAULT_FONT_SETTINGS, DEFAULT_LAYOUT_SETTINGS


def apply_font_preset(args: argparse.Namespace) -> None:
    presets = {
        "system-cn": ("方正小标宋简体", "黑体", "楷体_GB2312", "仿宋_GB2312"),
        "source-han": ("Source Han Serif SC", "Source Han Sans SC", "Source Han Serif SC", "Source Han Serif SC"),
        "noto-cjk": ("Noto Serif SC", "Noto Sans SC", "Noto Serif SC", "FandolFang"),
        "fandol": ("FandolSong", "FandolHei", "FandolSong", "FandolFang"),
    }

    if not args.font_preset:
        return

    title_font, heading_font, subheading_font, body_font = presets[args.font_preset]
    if args.header_font is None:
        args.header_font = title_font
    if args.title_font is None:
        args.title_font = title_font
    if args.heading_font is None:
        args.heading_font = heading_font
    if args.subheading_font is None:
        args.subheading_font = subheading_font
    if args.body_font is None:
        args.body_font = body_font


def apply_font_profile(args: argparse.Namespace, font_profile: FontProfile) -> None:
    if args.header_font is None:
        args.header_font = font_profile.header_family.font_name
    if args.title_font is None:
        args.title_font = font_profile.title_family.font_name
    if args.heading_font is None:
        args.heading_font = font_profile.heading_family.font_name
    if args.subheading_font is None:
        args.subheading_font = font_profile.subheading_family.font_name
    if args.body_font is None:
        args.body_font = font_profile.body_family.font_name
    if args.header_size is None:
        args.header_size = font_profile.header_size
    if args.title_size is None:
        args.title_size = font_profile.title_size
    if args.heading_size is None:
        args.heading_size = font_profile.heading_size
    if args.body_size is None:
        args.body_size = font_profile.body_size


def apply_layout_profile(args: argparse.Namespace, layout_profile: LayoutProfile) -> None:
    if args.body_line_spacing_twips is None:
        args.body_line_spacing_twips = layout_profile.body_line_spacing_twips
    if args.title_line_spacing_twips is None:
        args.title_line_spacing_twips = layout_profile.title_line_spacing_twips
    if args.header_after_twips is None:
        args.header_after_twips = layout_profile.header_after_twips
    if args.doc_number_after_twips is None:
        args.doc_number_after_twips = layout_profile.doc_number_after_twips
    if args.title_after_twips is None:
        args.title_after_twips = layout_profile.title_after_twips
    if args.recipient_after_twips is None:
        args.recipient_after_twips = layout_profile.recipient_after_twips
    if args.signing_before_twips is None:
        args.signing_before_twips = layout_profile.signing_before_twips
    if args.body_first_line_chars is None:
        args.body_first_line_chars = layout_profile.body_first_line_chars


def resolve_selected_doc_type(args: argparse.Namespace):
    if not args.doc_type:
        return None
    doc_type = resolve_doc_type(args.doc_type, load_doc_types())
    if doc_type is None:
        raise ValueError(f"未识别文种：{args.doc_type}")
    return doc_type


def finalize_export_settings(args: argparse.Namespace) -> tuple[FontProfile | None, LayoutProfile | None]:
    selected_font_profile: FontProfile | None = None
    selected_layout_profile: LayoutProfile | None = None
    font_profiles = load_font_profiles()
    layout_profiles = load_layout_profiles()
    doc_type = resolve_selected_doc_type(args)

    if doc_type is not None:
        selected_font_profile = font_profiles[doc_type.font_profile_id]
        selected_layout_profile = layout_profiles[doc_type.layout_profile_id]
        apply_font_profile(args, selected_font_profile)
        apply_layout_profile(args, selected_layout_profile)
    else:
        if args.font_profile:
            selected_font_profile = resolve_font_profile(args.font_profile, font_profiles)
            apply_font_profile(args, selected_font_profile)
        if args.layout_profile:
            selected_layout_profile = resolve_layout_profile(args.layout_profile, layout_profiles)
            apply_layout_profile(args, selected_layout_profile)

    apply_font_preset(args)

    coarse_line_spacing_twips = None
    if args.line_spacing_pt is not None:
        coarse_line_spacing_twips = round(float(args.line_spacing_pt) * 20)
        if args.body_line_spacing_twips is None:
            args.body_line_spacing_twips = coarse_line_spacing_twips
        if args.title_line_spacing_twips is None:
            args.title_line_spacing_twips = coarse_line_spacing_twips
        if args.header_after_twips is None:
            args.header_after_twips = coarse_line_spacing_twips // 2
        if args.doc_number_after_twips is None:
            args.doc_number_after_twips = coarse_line_spacing_twips // 2
        if args.title_after_twips is None:
            args.title_after_twips = coarse_line_spacing_twips
        if args.recipient_after_twips is None:
            args.recipient_after_twips = 0
        if args.signing_before_twips is None:
            args.signing_before_twips = coarse_line_spacing_twips

    for key, default_value in DEFAULT_FONT_SETTINGS.items():
        if getattr(args, key) is None:
            setattr(args, key, default_value)
    for key, default_value in DEFAULT_LAYOUT_SETTINGS.items():
        if getattr(args, key) is None:
            setattr(args, key, default_value)

    return selected_font_profile, selected_layout_profile


def body_line_spacing_twips(args: argparse.Namespace) -> int:
    return args.body_line_spacing_twips


def title_line_spacing_twips(args: argparse.Namespace) -> int:
    return args.title_line_spacing_twips


def render_current_font_plan(args: argparse.Namespace, font_profile: FontProfile | None) -> str:
    if font_profile is not None:
        return render_font_profile_markdown(font_profile)

    lines = [
        "- 当前未指定文种字体方案，以下为解析后的导出字体设置。",
        f"- 版头：{args.header_font} / {args.header_size}pt",
        f"- 标题：{args.title_font} / {args.title_size}pt",
        f"- 一级标题：{args.heading_font} / {args.heading_size}pt",
        f"- 二级标题：{args.subheading_font} / {args.heading_size}pt",
        f"- 正文：{args.body_font} / {args.body_size}pt",
    ]
    return "\n".join(lines)


def render_current_layout_plan(args: argparse.Namespace, layout_profile: LayoutProfile | None) -> str:
    if layout_profile is not None:
        return render_layout_profile_markdown(layout_profile)

    lines = [
        "- 当前未指定文种版式方案，以下为解析后的导出版式设置。",
        f"- 正文固定行距：{args.body_line_spacing_twips} twips / {args.body_line_spacing_twips / 20:.2f}pt",
        f"- 标题行距：{args.title_line_spacing_twips} twips / {args.title_line_spacing_twips / 20:.2f}pt",
        f"- 版头后距：{args.header_after_twips} twips / {args.header_after_twips / 20:.2f}pt",
        f"- 发文字号后距：{args.doc_number_after_twips} twips / {args.doc_number_after_twips / 20:.2f}pt",
        f"- 标题后距：{args.title_after_twips} twips / {args.title_after_twips / 20:.2f}pt",
        f"- 主送机关后距：{args.recipient_after_twips} twips / {args.recipient_after_twips / 20:.2f}pt",
        f"- 落款前距：{args.signing_before_twips} twips / {args.signing_before_twips / 20:.2f}pt",
        f"- 正文首行缩进：{args.body_first_line_chars / 100:.2f} 字符",
    ]
    return "\n".join(lines)


def render_current_export_plan(
    args: argparse.Namespace,
    font_profile: FontProfile | None,
    layout_profile: LayoutProfile | None,
) -> str:
    return "\n\n".join(
        [
            "## 字体方案",
            render_current_font_plan(args, font_profile),
            "## 版式方案",
            render_current_layout_plan(args, layout_profile),
        ]
    )


def format_font_profile_catalog() -> str:
    lines: list[str] = []
    for profile in load_font_profiles().values():
        lines.append(f"- `{profile.id}` / {profile.display_name} / {profile.description}")
    return "\n".join(lines)


def format_layout_profile_catalog() -> str:
    lines: list[str] = []
    for profile in load_layout_profiles().values():
        lines.append(f"- `{profile.id}` / {profile.display_name} / {profile.description}")
    return "\n".join(lines)
