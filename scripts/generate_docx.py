#!/usr/bin/env python3
"""将公文 Markdown 稿件转换为零依赖的 Word .docx 文件。"""

from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re
import sys
import zipfile
from dataclasses import dataclass
from typing import Iterable
from xml.sax.saxutils import escape


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from adapters.shared import (  # noqa: E402
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

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CP_NS = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DC_NS = "http://purl.org/dc/elements/1.1/"
DCTERMS_NS = "http://purl.org/dc/terms/"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
EP_NS = "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
VT_NS = "http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"


@dataclass
class Block:
    kind: str
    text: str
    level: int = 0
    src: str | None = None


@dataclass
class ImageAsset:
    source: pathlib.Path
    rel_id: str
    target_name: str
    content_type: str
    width_emu: int
    height_emu: int


@dataclass
class Section:
    heading: str
    blocks: list[Block]


@dataclass
class TextRun:
    text: str
    font_name: str
    size_pt: int
    bold: bool = False
    color: str | None = None


DEFAULT_BODY_LINE_SPACING_TWIPS = 580
PAGE_WIDTH_TWIPS = 11906
PAGE_HEIGHT_TWIPS = 16838
MARGIN_TOP_TWIPS = 2098
MARGIN_BOTTOM_TWIPS = 1984
MARGIN_LEFT_TWIPS = 1587
MARGIN_RIGHT_TWIPS = 1474
PRINTABLE_WIDTH_TWIPS = PAGE_WIDTH_TWIPS - MARGIN_LEFT_TWIPS - MARGIN_RIGHT_TWIPS
PRINTABLE_HEIGHT_TWIPS = PAGE_HEIGHT_TWIPS - MARGIN_TOP_TWIPS - MARGIN_BOTTOM_TWIPS
CHARS_PER_LINE = 28
SIGNING_DATE_RIGHT_CHARS = 400
MIN_SIGNING_UNIT_RIGHT_CHARS = 200
END_MATTER_HEADINGS = {"版记", "版记（可选）"}
DEFAULT_FONT_SETTINGS = {
    "header_font": "方正小标宋简体",
    "title_font": "方正小标宋简体",
    "heading_font": "黑体",
    "subheading_font": "楷体_GB2312",
    "body_font": "仿宋_GB2312",
    "header_size": 26,
    "title_size": 22,
    "heading_size": 16,
    "body_size": 16,
}
DEFAULT_LAYOUT_SETTINGS = {
    "body_line_spacing_twips": DEFAULT_BODY_LINE_SPACING_TWIPS,
    "title_line_spacing_twips": DEFAULT_BODY_LINE_SPACING_TWIPS,
    "header_after_twips": DEFAULT_BODY_LINE_SPACING_TWIPS // 2,
    "doc_number_after_twips": DEFAULT_BODY_LINE_SPACING_TWIPS // 2,
    "title_after_twips": DEFAULT_BODY_LINE_SPACING_TWIPS,
    "recipient_after_twips": DEFAULT_BODY_LINE_SPACING_TWIPS,
    "signing_before_twips": DEFAULT_BODY_LINE_SPACING_TWIPS,
    "body_first_line_chars": 200,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="将 Markdown 公文稿导出为 .docx。")
    parser.add_argument("input", nargs="?", type=pathlib.Path, help="输入 Markdown 文件")
    parser.add_argument("-o", "--output", type=pathlib.Path, help="输出 docx 文件，默认与输入同名")
    font_source_group = parser.add_mutually_exclusive_group()
    font_source_group.add_argument("--doc-type", help="按文种自动应用在 prompts/doc-types 中配置的字体方案")
    font_source_group.add_argument("--font-profile", help="直接应用 prompts/font-profiles 中定义的字体方案")
    parser.add_argument("--layout-profile", help="直接应用 prompts/layout-profiles 中定义的版式方案")
    parser.add_argument(
        "--font-preset",
        choices=["system-cn", "source-han", "noto-cjk", "fandol"],
        help="字体预设。仅在未被文种/字体方案和手工字体参数覆盖时补齐对应槽位。",
    )
    parser.add_argument("--list-font-profiles", action="store_true", help="列出当前可用字体方案并退出")
    parser.add_argument("--list-layout-profiles", action="store_true", help="列出当前可用版式方案并退出")
    parser.add_argument("--show-font-plan", action="store_true", help="打印当前解析后的字体与版式方案并退出")
    parser.add_argument("--show-layout-plan", action="store_true", help="仅打印当前解析后的版式方案并退出")
    parser.add_argument("--title-font", help="标题字体名称")
    parser.add_argument("--heading-font", help="小标题字体名称")
    parser.add_argument("--subheading-font", help="二级标题字体名称")
    parser.add_argument("--body-font", help="正文字体名称")
    parser.add_argument("--header-font", help="版头字体名称")
    parser.add_argument("--title-size", type=int, help="标题字号，单位 pt，默认接近 2 号")
    parser.add_argument("--heading-size", type=int, help="小标题字号，单位 pt，默认接近 3 号")
    parser.add_argument("--body-size", type=int, help="正文字号，单位 pt，默认接近 3 号")
    parser.add_argument("--header-size", type=int, help="版头字号，单位 pt")
    parser.add_argument("--line-spacing-pt", type=float, help="粗粒度固定行距，单位 pt；未显式指定 twips 时可作为快捷覆盖")
    parser.add_argument("--body-line-spacing-twips", type=int, help="正文固定行距，单位 twips")
    parser.add_argument("--title-line-spacing-twips", type=int, help="标题行距，单位 twips")
    parser.add_argument("--header-after-twips", type=int, help="版头段后间距，单位 twips")
    parser.add_argument("--doc-number-after-twips", type=int, help="发文字号段后间距，单位 twips")
    parser.add_argument("--title-after-twips", type=int, help="标题段后间距，单位 twips")
    parser.add_argument("--recipient-after-twips", type=int, help="主送机关段后间距，单位 twips")
    parser.add_argument("--signing-before-twips", type=int, help="落款前段距，单位 twips")
    parser.add_argument("--body-first-line-chars", type=int, help="正文首行缩进，单位为百分之一字符，默认 200")
    parser.set_defaults(show_page_number=True)
    parser.add_argument(
        "--show-page-number",
        dest="show_page_number",
        action="store_true",
        help="在页脚中显示页码（默认开启）",
    )
    parser.add_argument(
        "--hide-page-number",
        dest="show_page_number",
        action="store_false",
        help="隐藏页脚页码",
    )
    parser.add_argument("--title-wrap", choices=["auto", "off"], default="auto", help="长标题是否自动断行")
    parser.add_argument("--title-max-chars", type=int, default=20, help="长标题自动断行时每行目标字符数")
    parser.add_argument(
        "--hide-sections",
        default="标题,主送单位,正文,落款",
        help="这些二级标题只作为结构标记，不直接写入文档，使用逗号分隔",
    )
    return parser.parse_args()


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
            args.recipient_after_twips = coarse_line_spacing_twips
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


def parse_markdown(text: str) -> list[Block]:
    blocks: list[Block] = []
    paragraph_lines: list[str] = []

    def flush_paragraph() -> None:
        if not paragraph_lines:
            return
        blocks.append(Block(kind="paragraph", text="\n".join(line.rstrip() for line in paragraph_lines).strip()))
        paragraph_lines.clear()

    for raw_line in text.splitlines():
        heading_match = re.match(r"^(#{1,6})\s+(.*)$", raw_line)
        if heading_match:
            flush_paragraph()
            blocks.append(
                Block(
                    kind="heading",
                    level=len(heading_match.group(1)),
                    text=heading_match.group(2).strip(),
                )
            )
            continue

        image_match = re.match(r"^!\[(.*?)\]\((.+?)\)\s*$", raw_line.strip())
        if image_match:
            flush_paragraph()
            blocks.append(Block(kind="image", text=image_match.group(1).strip(), src=image_match.group(2).strip()))
            continue

        if not raw_line.strip():
            flush_paragraph()
            continue

        paragraph_lines.append(raw_line)

    flush_paragraph()
    return blocks


def extract_title_and_sections(blocks: list[Block]) -> tuple[str | None, list[Section]]:
    top_title: str | None = None
    sections: list[Section] = []
    current: Section | None = None

    for block in blocks:
        if block.kind == "heading" and block.level == 1 and top_title is None:
            top_title = block.text
            continue

        if block.kind == "heading" and block.level == 2:
            current = Section(heading=block.text, blocks=[])
            sections.append(current)
            continue

        if current is not None:
            current.blocks.append(block)

    return top_title, sections


def collect_fonts(args: argparse.Namespace) -> list[str]:
    fonts = [args.header_font, args.title_font, args.heading_font, args.subheading_font, args.body_font]
    return list(dict.fromkeys(fonts))


def xml_text_runs(text: str) -> str:
    pieces = []
    for index, part in enumerate(text.split("\n")):
        if index:
            pieces.append("<w:br/>")
        tab_parts = part.split("\t")
        for tab_index, tab_part in enumerate(tab_parts):
            if tab_index:
                pieces.append("<w:tab/>")
            pieces.append(f'<w:t xml:space="preserve">{escape(tab_part)}</w:t>')
    return "".join(pieces)


def run_properties(font_name: str, size_pt: int, bold: bool = False, color: str | None = None) -> str:
    size_half_points = size_pt * 2
    bold_xml = "<w:b/><w:bCs/>" if bold else ""
    color_xml = "" if color is None else f'<w:color w:val="{color}"/>'
    return (
        "<w:rPr>"
        f'<w:rFonts w:ascii="{escape(font_name)}" w:hAnsi="{escape(font_name)}" '
        f'w:eastAsia="{escape(font_name)}" w:cs="{escape(font_name)}"/>'
        f"{bold_xml}"
        f"{color_xml}"
        f'<w:sz w:val="{size_half_points}"/>'
        f'<w:szCs w:val="{size_half_points}"/>'
        "</w:rPr>"
    )


def run_xml(text: str, font_name: str, size_pt: int, bold: bool = False, color: str | None = None) -> str:
    return f"<w:r>{run_properties(font_name, size_pt, bold, color)}{xml_text_runs(text)}</w:r>"


def paragraph_xml(
    text: str,
    *,
    font_name: str,
    size_pt: int,
    bold: bool = False,
    color: str | None = None,
    align: str = "left",
    first_line: int = 0,
    first_line_chars: int | None = None,
    left_chars: int | None = None,
    right_chars: int | None = None,
    right_tab_stop: int | None = None,
    line: int | None = None,
    line_rule: str = "exact",
    before: int = 0,
    after: int = 0,
    top_border_color: str | None = None,
    bottom_border_color: str | None = None,
    runs: list[TextRun] | None = None,
) -> str:
    if line is None:
        line = DEFAULT_BODY_LINE_SPACING_TWIPS
    align_xml = "" if align == "left" else f'<w:jc w:val="{align}"/>'
    ind_parts = []
    if first_line > 0:
        ind_parts.append(f'w:firstLine="{first_line}"')
    if first_line_chars is not None:
        ind_parts.append(f'w:firstLineChars="{first_line_chars}"')
        if first_line == 0:
            ind_parts.append(f'w:firstLine="{chars_to_twips(first_line_chars)}"')
    if left_chars is not None:
        ind_parts.append(f'w:leftChars="{left_chars}"')
        ind_parts.append(f'w:left="{chars_to_twips(left_chars)}"')
    if right_chars is not None:
        ind_parts.append(f'w:rightChars="{right_chars}"')
        ind_parts.append(f'w:right="{chars_to_twips(right_chars)}"')
    ind_xml = "" if not ind_parts else f"<w:ind {' '.join(ind_parts)}/>"
    tabs_xml = ""
    if right_tab_stop is not None:
        tabs_xml = f'<w:tabs><w:tab w:val="right" w:pos="{right_tab_stop}"/></w:tabs>'
    border_xml = ""
    if top_border_color is not None or bottom_border_color is not None:
        top_xml = ""
        bottom_xml = ""
        if top_border_color is not None:
            top_xml = f'<w:top w:val="single" w:sz="16" w:space="4" w:color="{top_border_color}"/>'
        if bottom_border_color is not None:
            bottom_xml = f'<w:bottom w:val="single" w:sz="16" w:space="4" w:color="{bottom_border_color}"/>'
        border_xml = (
            "<w:pBdr>"
            f"{top_xml}"
            f"{bottom_xml}"
            "</w:pBdr>"
        )
    ppr = (
        "<w:pPr>"
        f"{align_xml}"
        f"{ind_xml}"
        f"{tabs_xml}"
        f"{border_xml}"
        f'<w:spacing w:before="{before}" w:after="{after}" w:line="{line}" w:lineRule="{line_rule}"/>'
        "</w:pPr>"
    )
    if runs is None:
        runs = [TextRun(text=text, font_name=font_name, size_pt=size_pt, bold=bold, color=color)]
    rendered_runs = "".join(
        run_xml(run.text, run.font_name, run.size_pt, run.bold, run.color)
        for run in runs
        if run.text
    )
    return f"<w:p>{ppr}{rendered_runs}</w:p>"


def page_break_xml() -> str:
    return "<w:p><w:r><w:br w:type=\"page\"/></w:r></w:p>"


def wrap_title_text(text: str, max_chars: int, enabled: bool) -> str:
    stripped = text.strip()
    if not enabled or "\n" in stripped or len(stripped) <= max_chars:
        return stripped
    line_count = (len(stripped) + max_chars - 1) // max_chars
    min_segment = 4 if len(stripped) >= 8 else 2
    boundaries: list[int] = []
    consumed = 0
    remaining_chars = len(stripped)
    remaining_lines = line_count
    previous_segment_len: int | None = None

    for _ in range(line_count - 1):
        target_len = (remaining_chars + remaining_lines - 1) // remaining_lines
        target = consumed + target_len
        min_pos = consumed + min_segment
        max_pos = len(stripped) - (remaining_lines - 1) * min_segment
        if max_pos < min_pos:
            min_pos = consumed + 2
            max_pos = len(stripped) - (remaining_lines - 1) * 2

        best_pos: int | None = None
        best_score = float("inf")
        for pos in range(max(min_pos, target - 4), min(max_pos, target + 4) + 1):
            segment_len = pos - consumed
            if segment_len < target_len:
                continue
            if previous_segment_len is not None and segment_len > previous_segment_len:
                continue
            prev_char = stripped[pos - 1]
            next_char = stripped[pos]
            score = abs(pos - target) * 10
            if prev_char in "，、：；":
                score -= 12
            if prev_char in "（《【“":
                score += 40
            if next_char in "，。！？、：；）》】”":
                score += 40
            if next_char in "的了和与及并或等":
                score += 8
            if best_score > score:
                best_score = score
                best_pos = pos

        if best_pos is None:
            for pos in range(max(min_pos, target), max_pos + 1):
                segment_len = pos - consumed
                if previous_segment_len is not None and segment_len > previous_segment_len:
                    continue
                best_pos = pos
                break

        if best_pos is None:
            fallback_pos = max(min_pos, min(max_pos, consumed + (previous_segment_len or target_len)))
            best_pos = fallback_pos

        boundaries.append(best_pos)
        previous_segment_len = best_pos - consumed
        consumed = best_pos
        remaining_chars = len(stripped) - consumed
        remaining_lines -= 1

    segments = []
    start = 0
    for boundary in boundaries:
        segments.append(stripped[start:boundary])
        start = boundary
    segments.append(stripped[start:])
    return "\n".join(segment for segment in segments if segment)


def is_date_line(text: str) -> bool:
    normalized = text.strip()
    return bool(re.fullmatch(r"\d{4}年\d{1,2}月\d{1,2}日", normalized))


def normalize_annotation_text(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return stripped
    if stripped.startswith("（") and stripped.endswith("）"):
        return stripped
    return f"（{stripped}）"


def chars_to_twips(chars_hundredths: int) -> int:
    return round((chars_hundredths / 100) * PRINTABLE_WIDTH_TWIPS / CHARS_PER_LINE)


def twips_to_emu(value: int) -> int:
    return value * 635


def content_type_for_image_extension(suffix: str) -> str:
    normalized = suffix.lower().lstrip(".")
    if normalized == "png":
        return "image/png"
    if normalized in {"jpg", "jpeg"}:
        return "image/jpeg"
    raise ValueError(f"暂不支持的图片格式：.{normalized}")


def read_png_dimensions(data: bytes) -> tuple[int, int]:
    if not data.startswith(b"\x89PNG\r\n\x1a\n") or len(data) < 24:
        raise ValueError("PNG 文件头无效。")
    return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")


def read_jpeg_dimensions(data: bytes) -> tuple[int, int]:
    if len(data) < 4 or data[:2] != b"\xff\xd8":
        raise ValueError("JPEG 文件头无效。")

    index = 2
    while index + 1 < len(data):
        if data[index] != 0xFF:
            index += 1
            continue
        marker = data[index + 1]
        index += 2
        if marker in {0xD8, 0xD9}:
            continue
        if index + 2 > len(data):
            break
        segment_length = int.from_bytes(data[index:index + 2], "big")
        if segment_length < 2 or index + segment_length > len(data):
            break
        if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
            if segment_length < 7:
                break
            height = int.from_bytes(data[index + 3:index + 5], "big")
            width = int.from_bytes(data[index + 5:index + 7], "big")
            return width, height
        index += segment_length
    raise ValueError("无法识别 JPEG 图片尺寸。")


def read_image_dimensions(path: pathlib.Path) -> tuple[int, int]:
    data = path.read_bytes()
    suffix = path.suffix.lower()
    if suffix == ".png":
        return read_png_dimensions(data)
    if suffix in {".jpg", ".jpeg"}:
        return read_jpeg_dimensions(data)
    raise ValueError(f"暂不支持的图片格式：{path.suffix}")


def compute_image_size_emu(path: pathlib.Path) -> tuple[int, int]:
    width_px, height_px = read_image_dimensions(path)
    max_width_emu = twips_to_emu(PRINTABLE_WIDTH_TWIPS - chars_to_twips(200))
    width_emu = max_width_emu
    height_emu = max(1, round(width_emu * height_px / width_px))
    return width_emu, height_emu


def estimate_text_lines(text: str, max_chars: int = CHARS_PER_LINE) -> int:
    total = 0
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        total += max(1, (len(stripped) + max_chars - 1) // max_chars)
    return max(1, total)


def estimate_image_twips(asset: ImageAsset, args: argparse.Namespace) -> int:
    return max(body_line_spacing_twips(args), round(asset.height_emu / 635))


def estimate_paragraph_twips(
    text: str,
    *,
    line_twips: int,
    before: int = 0,
    after: int = 0,
    max_chars: int = CHARS_PER_LINE,
) -> int:
    return before + after + estimate_text_lines(text, max_chars=max_chars) * line_twips


def signed_right_indent_chars(signing_unit: str, signing_date: str) -> int:
    indent_chars = len(signing_date.strip()) - len(signing_unit.strip()) + 4
    return max(MIN_SIGNING_UNIT_RIGHT_CHARS, indent_chars * 100)


def paragraph_kind(text: str) -> str | None:
    first_line = text.split("\n", 1)[0].strip()
    if re.match(r"^[一二三四五六七八九十百千]+、", first_line):
        return "level1"
    if re.match(r"^（[一二三四五六七八九十百千]+）", first_line):
        return "level2"
    if re.match(r"^\d+[\.．]", first_line):
        return "level3"
    if re.match(r"^（\d+）", first_line):
        return "level4"
    return None


def estimate_rendered_body_paragraph_twips(text: str, args: argparse.Namespace) -> int:
    lines = [line for line in text.split("\n") if line.strip()]
    if not lines:
        return 0

    kind = paragraph_kind(text)
    if kind and len(lines) > 1:
        heading_line = lines[0]
        body_text = "\n".join(lines[1:])
        return (
            estimate_paragraph_twips(heading_line, line_twips=body_line_spacing_twips(args))
            + estimate_paragraph_twips(body_text, line_twips=body_line_spacing_twips(args))
        )

    return estimate_paragraph_twips(text, line_twips=body_line_spacing_twips(args))


def estimate_section_height_twips(
    section: Section,
    *,
    args: argparse.Namespace,
    hidden_sections: set[str],
    image_assets: dict[str, ImageAsset] | None = None,
) -> int:
    heading = section.heading.strip()

    if heading in {"版头", "版头（可选）"}:
        return sum(
            estimate_paragraph_twips(
                block.text,
                line_twips=body_line_spacing_twips(args),
                after=args.header_after_twips,
            )
            for block in section.blocks
            if block.kind == "paragraph" and block.text
        )

    if heading in {"发文字号", "发文字号（可选）"}:
        return sum(
            estimate_paragraph_twips(
                block.text,
                line_twips=body_line_spacing_twips(args),
                after=args.doc_number_after_twips,
            )
            for block in section.blocks
            if block.kind == "paragraph" and block.text
        )

    if heading in END_MATTER_HEADINGS:
        return sum(
            estimate_paragraph_twips(block.text, line_twips=body_line_spacing_twips(args))
            for block in section.blocks
            if block.kind == "paragraph" and block.text
        )

    if heading == "标题":
        return sum(
            estimate_paragraph_twips(
                wrap_title_text(
                    block.text,
                    max_chars=args.title_max_chars,
                    enabled=args.title_wrap == "auto",
                ),
                line_twips=title_line_spacing_twips(args),
                after=args.title_after_twips,
                max_chars=args.title_max_chars,
            )
            for block in section.blocks
            if block.kind == "paragraph" and block.text
        )

    if heading == "主送单位":
        return sum(
            estimate_paragraph_twips(
                block.text,
                line_twips=body_line_spacing_twips(args),
                after=args.recipient_after_twips,
            )
            for block in section.blocks
            if block.kind == "paragraph" and block.text
        )

    if heading == "落款":
        lines = [
            line.strip()
            for block in section.blocks
            if block.kind == "paragraph"
            for line in block.text.split("\n")
            if line.strip()
        ]
        if not lines:
            return 0
        total = 0
        for index, line in enumerate(lines):
            total += estimate_paragraph_twips(
                line,
                line_twips=body_line_spacing_twips(args),
                before=args.signing_before_twips if index == 0 else 0,
            )
        return total

    if heading in {"附注", "附注（可选）"}:
        return sum(
            estimate_paragraph_twips(
                normalize_annotation_text(block.text),
                line_twips=body_line_spacing_twips(args),
            )
            for block in section.blocks
            if block.kind == "paragraph" and block.text
        )

    total = 0
    if heading not in hidden_sections:
        total += estimate_paragraph_twips(heading, line_twips=body_line_spacing_twips(args))

    for block in section.blocks:
        if block.kind == "paragraph" and block.text:
            total += estimate_rendered_body_paragraph_twips(block.text, args)
        elif block.kind == "image" and block.src and image_assets and block.src in image_assets:
            total += estimate_image_twips(image_assets[block.src], args)
        elif block.kind == "heading":
            total += estimate_paragraph_twips(block.text, line_twips=body_line_spacing_twips(args))

    return total


def compute_end_matter_position(consumed_twips: int, end_matter_twips: int) -> tuple[bool, int]:
    if end_matter_twips <= 0:
        return False, 0
    if end_matter_twips >= PRINTABLE_HEIGHT_TWIPS:
        return (consumed_twips % PRINTABLE_HEIGHT_TWIPS) != 0, 0

    remaining_twips = PRINTABLE_HEIGHT_TWIPS - (consumed_twips % PRINTABLE_HEIGHT_TWIPS)
    if end_matter_twips <= remaining_twips:
        return False, remaining_twips - end_matter_twips
    return True, PRINTABLE_HEIGHT_TWIPS - end_matter_twips


POINT_MARKER_RE = re.compile(r"[一二三四五六七八九十]+是")
POINT_MARKER_BOUNDARIES = "。；\n"


def merge_text_runs(runs: list[TextRun]) -> list[TextRun]:
    merged: list[TextRun] = []
    for run in runs:
        if not run.text:
            continue
        if (
            merged
            and merged[-1].font_name == run.font_name
            and merged[-1].size_pt == run.size_pt
            and merged[-1].bold == run.bold
            and merged[-1].color == run.color
        ):
            merged[-1].text += run.text
        else:
            merged.append(run)
    return merged


def emphasize_point_markers(text: str, args: argparse.Namespace) -> list[TextRun]:
    runs: list[TextRun] = []
    cursor = 0

    for match in POINT_MARKER_RE.finditer(text):
        start, end = match.span()
        if start != 0 and text[start - 1] not in POINT_MARKER_BOUNDARIES:
            continue
        if start > cursor:
            runs.append(TextRun(text=text[cursor:start], font_name=args.body_font, size_pt=args.body_size))
        runs.append(TextRun(text=match.group(0), font_name=args.heading_font, size_pt=args.body_size))
        cursor = end

    if not runs:
        return [TextRun(text=text, font_name=args.body_font, size_pt=args.body_size)]

    if cursor < len(text):
        runs.append(TextRun(text=text[cursor:], font_name=args.body_font, size_pt=args.body_size))
    return merge_text_runs(runs)


def render_body_paragraph(text: str, args: argparse.Namespace) -> list[str]:
    lines = [line for line in text.split("\n") if line.strip()]
    if not lines:
        return []

    kind = paragraph_kind(text)
    if kind and len(lines) > 1:
        heading_line = lines[0]
        body_text = "\n".join(lines[1:])
        xml_parts = [render_numbered_heading(heading_line, kind, args)]
        if body_text.strip():
            xml_parts.append(
                paragraph_xml(
                    body_text,
                    font_name=args.body_font,
                    size_pt=args.body_size,
                    first_line_chars=args.body_first_line_chars,
                    line=body_line_spacing_twips(args),
                    runs=emphasize_point_markers(body_text, args),
                )
            )
        return xml_parts

    if kind:
        return [render_numbered_heading(lines[0], kind, args)]

    return [
        paragraph_xml(
            text,
            font_name=args.body_font,
            size_pt=args.body_size,
            first_line_chars=args.body_first_line_chars,
            line=body_line_spacing_twips(args),
            runs=emphasize_point_markers(text, args),
        )
    ]


def render_numbered_heading(text: str, kind: str, args: argparse.Namespace) -> str:
    if kind == "level1":
        return paragraph_xml(
            text,
            font_name=args.heading_font,
            size_pt=args.heading_size,
            first_line_chars=200,
            line=body_line_spacing_twips(args),
        )
    if kind == "level2":
        return paragraph_xml(
            text,
            font_name=args.subheading_font,
            size_pt=args.heading_size,
            line=body_line_spacing_twips(args),
        )
    if kind == "level3":
        return paragraph_xml(
            text,
            font_name=args.body_font,
            size_pt=args.body_size,
            bold=True,
            line=body_line_spacing_twips(args),
        )
    return paragraph_xml(
        text,
        font_name=args.body_font,
        size_pt=args.body_size,
        line=body_line_spacing_twips(args),
    )


def collect_image_sources(blocks: Iterable[Block]) -> list[str]:
    seen: set[str] = set()
    sources: list[str] = []
    for block in blocks:
        if block.kind == "image" and block.src and block.src not in seen:
            seen.add(block.src)
            sources.append(block.src)
    return sources


def build_image_assets(
    blocks: list[Block],
    markdown_path: pathlib.Path,
    *,
    show_page_number: bool,
) -> dict[str, ImageAsset]:
    assets: dict[str, ImageAsset] = {}
    next_rel_id = 4 if show_page_number else 3
    for index, src in enumerate(collect_image_sources(blocks), start=1):
        source_path = (markdown_path.parent / src).resolve()
        if not source_path.exists():
            raise FileNotFoundError(f"图片文件不存在：{src}")
        if not source_path.is_file():
            raise ValueError(f"图片路径不是文件：{src}")
        width_emu, height_emu = compute_image_size_emu(source_path)
        assets[src] = ImageAsset(
            source=source_path,
            rel_id=f"rId{next_rel_id}",
            target_name=f"image{index}{source_path.suffix.lower()}",
            content_type=content_type_for_image_extension(source_path.suffix),
            width_emu=width_emu,
            height_emu=height_emu,
        )
        next_rel_id += 1
    return assets


def image_paragraph_xml(asset: ImageAsset, *, alt_text: str, drawing_id: int) -> str:
    safe_alt = escape(alt_text or f"图片{drawing_id}")
    return (
        "<w:p>"
        '<w:pPr><w:jc w:val="center"/></w:pPr>'
        "<w:r><w:drawing>"
        '<wp:inline xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"'
        ' distT="0" distB="0" distL="0" distR="0">'
        f'<wp:extent cx="{asset.width_emu}" cy="{asset.height_emu}"/>'
        '<wp:effectExtent l="0" t="0" r="0" b="0"/>'
        f'<wp:docPr id="{drawing_id}" name="图片 {drawing_id}" descr="{safe_alt}"/>'
        '<wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/></wp:cNvGraphicFramePr>'
        '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        '<pic:nvPicPr>'
        f'<pic:cNvPr id="{drawing_id}" name="{safe_alt}" descr="{safe_alt}"/>'
        '<pic:cNvPicPr/>'
        '</pic:nvPicPr>'
        '<pic:blipFill>'
        f'<a:blip r:embed="{asset.rel_id}"/>'
        '<a:stretch><a:fillRect/></a:stretch>'
        '</pic:blipFill>'
        '<pic:spPr>'
        '<a:xfrm>'
        '<a:off x="0" y="0"/>'
        f'<a:ext cx="{asset.width_emu}" cy="{asset.height_emu}"/>'
        '</a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
        '</pic:spPr>'
        '</pic:pic>'
        '</a:graphicData>'
        '</a:graphic>'
        '</wp:inline>'
        "</w:drawing></w:r>"
        "</w:p>"
    )


def render_section_content(
    section: Section,
    *,
    args: argparse.Namespace,
    hidden_sections: set[str],
    image_assets: dict[str, ImageAsset] | None = None,
    drawing_id_counter: list[int] | None = None,
    first_paragraph_before_override: int = 0,
    prepend_page_break: bool = False,
) -> list[str]:
    xml_parts: list[str] = []
    heading = section.heading.strip()

    if heading in {"版头", "版头（可选）"}:
        for block in section.blocks:
            if block.kind == "paragraph" and block.text:
                xml_parts.append(
                    paragraph_xml(
                        block.text,
                        font_name=args.header_font,
                        size_pt=args.header_size,
                        color="C00000",
                        align="center",
                        line=body_line_spacing_twips(args),
                        after=args.header_after_twips,
                    )
                )
        return xml_parts

    if heading in {"发文字号", "发文字号（可选）"}:
        for block in section.blocks:
            if block.kind == "paragraph" and block.text:
                has_tab = "\t" in block.text
                xml_parts.append(
                    paragraph_xml(
                        block.text,
                        font_name=args.body_font,
                        size_pt=args.body_size,
                        align="left" if has_tab else "center",
                        right_tab_stop=(
                            PAGE_WIDTH_TWIPS - MARGIN_LEFT_TWIPS - MARGIN_RIGHT_TWIPS if has_tab else None
                        ),
                        line=body_line_spacing_twips(args),
                        after=args.doc_number_after_twips,
                        bottom_border_color="FF0000",
                    )
                )
        return xml_parts

    if heading in END_MATTER_HEADINGS:
        if prepend_page_break:
            xml_parts.append(page_break_xml())
        paragraph_index = 0
        for block in section.blocks:
            if block.kind == "paragraph" and block.text:
                xml_parts.append(
                    paragraph_xml(
                        block.text,
                        font_name=args.body_font,
                        size_pt=14,
                        first_line=0,
                        line=body_line_spacing_twips(args),
                        before=first_paragraph_before_override if paragraph_index == 0 else 0,
                        top_border_color="000000",
                    )
                )
                paragraph_index += 1
        return xml_parts

    if heading == "标题":
        for block in section.blocks:
            if block.kind == "paragraph" and block.text:
                xml_parts.append(
                    paragraph_xml(
                        wrap_title_text(
                            block.text,
                            max_chars=args.title_max_chars,
                            enabled=args.title_wrap == "auto",
                        ),
                        font_name=args.title_font,
                        size_pt=args.title_size,
                        align="center",
                        first_line=0,
                        line=title_line_spacing_twips(args),
                        line_rule="exact",
                        before=0,
                        after=args.title_after_twips,
                    )
                )
        return xml_parts

    if heading == "主送单位":
        for block in section.blocks:
            if block.kind == "paragraph" and block.text:
                xml_parts.append(
                    paragraph_xml(
                        block.text,
                        font_name=args.body_font,
                        size_pt=args.body_size,
                        first_line=0,
                        line=body_line_spacing_twips(args),
                        after=args.recipient_after_twips,
                    )
                )
        return xml_parts

    if heading == "落款":
        lines = [
            line.strip()
            for block in section.blocks
            if block.kind == "paragraph"
            for line in block.text.split("\n")
            if line.strip()
        ]
        if not lines:
            return xml_parts

        if len(lines) == 1:
            right_chars = SIGNING_DATE_RIGHT_CHARS if is_date_line(lines[0]) else MIN_SIGNING_UNIT_RIGHT_CHARS
            xml_parts.append(
                paragraph_xml(
                    lines[0],
                    font_name=args.body_font,
                    size_pt=args.body_size,
                    align="right",
                    right_chars=right_chars,
                    line=body_line_spacing_twips(args),
                    before=args.signing_before_twips,
                )
            )
            return xml_parts

        signing_date = lines[-1]
        signing_units = lines[:-1]
        for index, signing_unit in enumerate(signing_units):
            xml_parts.append(
                paragraph_xml(
                    signing_unit,
                    font_name=args.body_font,
                    size_pt=args.body_size,
                    align="right",
                    right_chars=signed_right_indent_chars(signing_unit, signing_date),
                    line=body_line_spacing_twips(args),
                    before=args.signing_before_twips if index == 0 else 0,
                )
            )
        xml_parts.append(
            paragraph_xml(
                signing_date,
                font_name=args.body_font,
                size_pt=args.body_size,
                align="right",
                right_chars=SIGNING_DATE_RIGHT_CHARS,
                line=body_line_spacing_twips(args),
            )
        )
        return xml_parts

    if heading in {"附注", "附注（可选）"}:
        for block in section.blocks:
            if block.kind == "paragraph" and block.text:
                xml_parts.append(
                    paragraph_xml(
                        normalize_annotation_text(block.text),
                        font_name=args.body_font,
                        size_pt=args.body_size,
                        first_line=0,
                        left_chars=200,
                        line=body_line_spacing_twips(args),
                    )
                )
        return xml_parts

    if heading not in hidden_sections:
        heading_kind = paragraph_kind(heading)
        if heading_kind:
            xml_parts.append(render_numbered_heading(heading, heading_kind, args))
        else:
            xml_parts.append(
                paragraph_xml(
                    heading,
                    font_name=args.heading_font,
                    size_pt=args.heading_size,
                    first_line=0,
                    line=body_line_spacing_twips(args),
                )
            )

    for block in section.blocks:
        if block.kind == "paragraph" and block.text:
            xml_parts.extend(render_body_paragraph(block.text, args))
        elif block.kind == "image" and block.src and image_assets and block.src in image_assets:
            if drawing_id_counter is None:
                drawing_id_counter = [1]
            xml_parts.append(
                image_paragraph_xml(
                    image_assets[block.src],
                    alt_text=block.text,
                    drawing_id=drawing_id_counter[0],
                )
            )
            drawing_id_counter[0] += 1
        elif block.kind == "heading":
            heading_kind = paragraph_kind(block.text)
            if heading_kind:
                xml_parts.append(render_numbered_heading(block.text, heading_kind, args))
            else:
                xml_parts.append(
                    paragraph_xml(
                        block.text,
                        font_name=args.subheading_font if block.level >= 3 else args.heading_font,
                        size_pt=args.heading_size,
                        first_line=0,
                        line=body_line_spacing_twips(args),
                    )
                )

    return xml_parts


def render_generic(
    blocks: list[Block],
    args: argparse.Namespace,
    *,
    image_assets: dict[str, ImageAsset] | None = None,
) -> list[str]:
    xml_parts: list[str] = []
    drawing_id_counter = [1]
    for block in blocks:
        if block.kind == "heading" and block.level == 1:
            xml_parts.append(
                paragraph_xml(
                    block.text,
                    font_name=args.title_font,
                    size_pt=args.title_size,
                    align="center",
                    line=title_line_spacing_twips(args),
                    after=args.title_after_twips,
                )
            )
        elif block.kind == "heading":
            heading_kind = paragraph_kind(block.text)
            if heading_kind:
                xml_parts.append(render_numbered_heading(block.text, heading_kind, args))
            else:
                xml_parts.append(
                    paragraph_xml(
                        block.text,
                        font_name=args.subheading_font if block.level >= 3 else args.heading_font,
                        size_pt=args.heading_size,
                        first_line=0,
                        line=body_line_spacing_twips(args),
                    )
                )
        elif block.kind == "image" and block.src and image_assets and block.src in image_assets:
            xml_parts.append(
                image_paragraph_xml(
                    image_assets[block.src],
                    alt_text=block.text,
                    drawing_id=drawing_id_counter[0],
                )
            )
            drawing_id_counter[0] += 1
        elif block.kind == "paragraph" and block.text:
            xml_parts.extend(render_body_paragraph(block.text, args))
    return xml_parts


def build_document_xml(
    blocks: list[Block],
    args: argparse.Namespace,
    *,
    image_assets: dict[str, ImageAsset] | None = None,
) -> str:
    top_title, sections = extract_title_and_sections(blocks)
    hidden_sections = {item.strip() for item in args.hide_sections.split(",") if item.strip()}

    body_parts: list[str] = []
    consumed_twips = 0
    drawing_id_counter = [1]
    if sections:
        section_headings = {section.heading for section in sections}
        if "标题" not in section_headings and top_title:
            body_parts.append(
                paragraph_xml(
                    wrap_title_text(
                        top_title,
                        max_chars=args.title_max_chars,
                        enabled=args.title_wrap == "auto",
                    ),
                    font_name=args.title_font,
                    size_pt=args.title_size,
                    align="center",
                    line=title_line_spacing_twips(args),
                    after=args.title_after_twips,
                )
            )
            consumed_twips += estimate_paragraph_twips(
                wrap_title_text(
                    top_title,
                    max_chars=args.title_max_chars,
                    enabled=args.title_wrap == "auto",
                ),
                line_twips=title_line_spacing_twips(args),
                after=args.title_after_twips,
                max_chars=args.title_max_chars,
            )
        end_matter_sections: list[Section] = []
        for section in sections:
            if section.heading.strip() in END_MATTER_HEADINGS:
                end_matter_sections.append(section)
                continue
            body_parts.extend(
                render_section_content(
                    section,
                    args=args,
                    hidden_sections=hidden_sections,
                    image_assets=image_assets,
                    drawing_id_counter=drawing_id_counter,
                )
            )
            consumed_twips += estimate_section_height_twips(
                section,
                args=args,
                hidden_sections=hidden_sections,
                image_assets=image_assets,
            )
        for section in end_matter_sections:
            section_height = estimate_section_height_twips(
                section,
                args=args,
                hidden_sections=hidden_sections,
                image_assets=image_assets,
            )
            prepend_page_break, before_twips = compute_end_matter_position(consumed_twips, section_height)
            body_parts.extend(
                render_section_content(
                    section,
                    args=args,
                    hidden_sections=hidden_sections,
                    image_assets=image_assets,
                    drawing_id_counter=drawing_id_counter,
                    first_paragraph_before_override=before_twips,
                    prepend_page_break=prepend_page_break,
                )
            )
            if prepend_page_break:
                current_mod = consumed_twips % PRINTABLE_HEIGHT_TWIPS
                if current_mod != 0:
                    consumed_twips += PRINTABLE_HEIGHT_TWIPS - current_mod
            consumed_twips += before_twips + section_height
    else:
        body_parts.extend(render_generic(blocks, args, image_assets=image_assets))

    body_parts.append(
        "".join(
            [
                "<w:sectPr>",
                '<w:footerReference w:type="default" r:id="rId3"/>' if args.show_page_number else "",
                "<w:titlePg/>" if args.show_page_number else "",
                '<w:pgNumType w:start="1"/>' if args.show_page_number else "",
                f'<w:pgSz w:w="{PAGE_WIDTH_TWIPS}" w:h="{PAGE_HEIGHT_TWIPS}"/>',
                (
                    f'<w:pgMar w:top="{MARGIN_TOP_TWIPS}" w:right="{MARGIN_RIGHT_TWIPS}" '
                    f'w:bottom="{MARGIN_BOTTOM_TWIPS}" w:left="{MARGIN_LEFT_TWIPS}" '
                    'w:header="720" w:footer="720" w:gutter="0"/>'
                ),
                "</w:sectPr>",
            ]
        )
    )

    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{W_NS}" xmlns:r="{R_NS}" '
        'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        f"<w:body>{''.join(body_parts)}</w:body>"
        "</w:document>"
    )


def build_styles_xml(args: argparse.Namespace) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:styles xmlns:w="{W_NS}">'
        "<w:docDefaults>"
        "<w:rPrDefault><w:rPr>"
        f'<w:rFonts w:ascii="{escape(args.body_font)}" w:hAnsi="{escape(args.body_font)}" '
        f'w:eastAsia="{escape(args.body_font)}" w:cs="{escape(args.body_font)}"/>'
        f'<w:sz w:val="{args.body_size * 2}"/>'
        f'<w:szCs w:val="{args.body_size * 2}"/>'
        "</w:rPr></w:rPrDefault>"
        "<w:pPrDefault><w:pPr>"
        f'<w:spacing w:line="{body_line_spacing_twips(args)}" w:lineRule="exact"/>'
        "</w:pPr></w:pPrDefault>"
        "</w:docDefaults>"
        '<w:style w:type="paragraph" w:default="1" w:styleId="Normal">'
        '<w:name w:val="Normal"/>'
        "</w:style>"
        "</w:styles>"
    )


def build_font_table_xml(fonts: list[str]) -> str:
    items = []
    for font_name in fonts:
        items.append(
            f'<w:font w:name="{escape(font_name)}">'
            '<w:charset w:val="86"/>'
            '<w:family w:val="auto"/>'
            '<w:pitch w:val="variable"/>'
            "</w:font>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:fonts xmlns:w="{W_NS}">{"".join(items)}</w:fonts>'
    )


def build_content_types_xml(
    show_page_number: bool = False,
    *,
    image_content_types: Iterable[str] = (),
) -> str:
    footer_override = ""
    if show_page_number:
        footer_override = (
            '<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>'
        )
    image_defaults = []
    seen: set[str] = set()
    for content_type in image_content_types:
        if content_type in seen:
            continue
        seen.add(content_type)
        if content_type == "image/png":
            image_defaults.append('<Default Extension="png" ContentType="image/png"/>')
        elif content_type == "image/jpeg":
            image_defaults.append('<Default Extension="jpg" ContentType="image/jpeg"/>')
            image_defaults.append('<Default Extension="jpeg" ContentType="image/jpeg"/>')
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        f"{''.join(image_defaults)}"
        '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
        '<Override PartName="/word/fontTable.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.fontTable+xml"/>'
        f"{footer_override}"
        "</Types>"
    )


def build_root_relationships_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
        "</Relationships>"
    )


def build_document_relationships_xml(
    show_page_number: bool = False,
    *,
    image_assets: dict[str, ImageAsset] | None = None,
) -> str:
    relationships = [
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>',
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/fontTable" Target="fontTable.xml"/>',
    ]
    if show_page_number:
        relationships.append(
            '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>'
        )
    if image_assets:
        for asset in image_assets.values():
            relationships.append(
                f'<Relationship Id="{asset.rel_id}" '
                'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
                f'Target="media/{asset.target_name}"/>'
            )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f"{''.join(relationships)}"
        "</Relationships>"
    )


def build_core_xml(title: str) -> str:
    timestamp = dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    safe_title = escape(title or "公文稿件")
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<cp:coreProperties xmlns:cp="{CP_NS}" xmlns:dc="{DC_NS}" xmlns:dcterms="{DCTERMS_NS}" xmlns:xsi="{XSI_NS}">'
        f"<dc:title>{safe_title}</dc:title>"
        "<dc:creator>Codex</dc:creator>"
        "<cp:lastModifiedBy>Codex</cp:lastModifiedBy>"
        f'<dcterms:created xsi:type="dcterms:W3CDTF">{timestamp}</dcterms:created>'
        f'<dcterms:modified xsi:type="dcterms:W3CDTF">{timestamp}</dcterms:modified>'
        "</cp:coreProperties>"
    )


def build_app_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<Properties xmlns="{EP_NS}" xmlns:vt="{VT_NS}">'
        "<Application>Codex</Application>"
        "</Properties>"
    )


def build_footer_xml(args: argparse.Namespace) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:ftr xmlns:w="{W_NS}">'
        '<w:p><w:pPr><w:jc w:val="center"/></w:pPr>'
        f'<w:r>{run_properties(args.body_font, 14)}<w:t>— </w:t></w:r>'
        f'<w:r>{run_properties(args.body_font, 14)}<w:fldChar w:fldCharType="begin"/></w:r>'
        '<w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
        f'<w:r>{run_properties(args.body_font, 14)}<w:fldChar w:fldCharType="separate"/></w:r>'
        f'<w:r>{run_properties(args.body_font, 14)}<w:t>1</w:t></w:r>'
        f'<w:r>{run_properties(args.body_font, 14)}<w:fldChar w:fldCharType="end"/></w:r>'
        f'<w:r>{run_properties(args.body_font, 14)}<w:t> —</w:t></w:r>'
        '</w:p></w:ftr>'
    )


def resolve_output_path(input_path: pathlib.Path, explicit_output: pathlib.Path | None) -> pathlib.Path:
    if explicit_output:
        return explicit_output
    return input_path.with_suffix(".docx")


def main() -> int:
    args = parse_args()
    if args.list_font_profiles:
        print(format_font_profile_catalog())
        return 0
    if args.list_layout_profiles:
        print(format_layout_profile_catalog())
        return 0

    selected_font_profile, selected_layout_profile = finalize_export_settings(args)

    if args.show_font_plan:
        print(render_current_export_plan(args, selected_font_profile, selected_layout_profile))
        return 0
    if args.show_layout_plan:
        print(render_current_layout_plan(args, selected_layout_profile))
        return 0

    if args.input is None:
        raise SystemExit("缺少输入 Markdown 文件。")

    markdown = args.input.read_text(encoding="utf-8")
    blocks = parse_markdown(markdown)
    if not blocks:
        raise SystemExit("输入文件为空，无法生成 docx。")

    image_assets = build_image_assets(blocks, args.input, show_page_number=args.show_page_number)
    document_xml = build_document_xml(blocks, args, image_assets=image_assets)
    top_title, sections = extract_title_and_sections(blocks)
    if sections:
        title = next(
            (
                block.text
                for section in sections
                if section.heading == "标题"
                for block in section.blocks
                if block.kind == "paragraph" and block.text
            ),
            top_title or "公文稿件",
        )
    else:
        title = top_title or "公文稿件"

    output_path = resolve_output_path(args.input, args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "[Content_Types].xml",
            build_content_types_xml(
                args.show_page_number,
                image_content_types=[asset.content_type for asset in image_assets.values()],
            ),
        )
        archive.writestr("_rels/.rels", build_root_relationships_xml())
        archive.writestr("docProps/core.xml", build_core_xml(title))
        archive.writestr("docProps/app.xml", build_app_xml())
        archive.writestr("word/document.xml", document_xml)
        archive.writestr("word/styles.xml", build_styles_xml(args))
        archive.writestr("word/fontTable.xml", build_font_table_xml(collect_fonts(args)))
        archive.writestr(
            "word/_rels/document.xml.rels",
            build_document_relationships_xml(args.show_page_number, image_assets=image_assets),
        )
        for asset in image_assets.values():
            archive.writestr(f"word/media/{asset.target_name}", asset.source.read_bytes())
        if args.show_page_number:
            archive.writestr("word/footer1.xml", build_footer_xml(args))

    print(f"[OK] 已生成 {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
