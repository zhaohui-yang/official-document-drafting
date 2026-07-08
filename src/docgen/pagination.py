"""影子渲染器：不产出 XML，只估算各章节渲染后的高度，用于分页与版记定位。

注意：estimate_section_height_twips 必须与 docgen.sections.render_section_content
的按标题分派规则（版头/发文字号/版记/标题/主送单位/落款/附注）逐条镜像，
任一侧新增或调整分支时必须同步另一侧，防止高度估算与实际渲染漂移。
"""

from __future__ import annotations

import argparse

from docgen.constants import (
    CHARS_PER_LINE,
    END_MATTER_HEADINGS,
    MIN_SIGNING_UNIT_RIGHT_CHARS,
    PRINTABLE_HEIGHT_TWIPS,
)
from docgen.images import estimate_image_twips
from docgen.markdown import normalize_annotation_text, paragraph_kind, wrap_title_text
from docgen.models import ImageAsset, Section
from docgen.settings import body_line_spacing_twips, title_line_spacing_twips


def estimate_text_lines(text: str, max_chars: int = CHARS_PER_LINE) -> int:
    total = 0
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        total += max(1, (len(stripped) + max_chars - 1) // max_chars)
    return max(1, total)


def section_contains_image(section: Section) -> bool:
    return any(block.kind == "image" for block in section.blocks)


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
