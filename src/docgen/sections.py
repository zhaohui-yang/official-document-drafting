"""章节渲染：把 Markdown 章节按公文结构标题分派渲染为 WordprocessingML 段落。

注意：render_section_content 的按标题分派规则（版头/发文字号/版记/标题/主送单位/
落款/附注）与 docgen.pagination.estimate_section_height_twips 互为孪生分发器，
任一侧新增或调整分支时必须同步另一侧，防止实际渲染与高度估算漂移。
"""

from __future__ import annotations

import argparse

from docgen.constants import (
    END_MATTER_HEADINGS,
    MARGIN_LEFT_TWIPS,
    MARGIN_RIGHT_TWIPS,
    MIN_SIGNING_UNIT_RIGHT_CHARS,
    PAGE_WIDTH_TWIPS,
    SIGNING_DATE_RIGHT_CHARS,
)
from docgen.images import image_paragraph_xml
from docgen.markdown import is_date_line, normalize_annotation_text, paragraph_kind, wrap_title_text
from docgen.models import Block, ImageAsset, Section
from docgen.oxml import emphasize_point_markers, page_break_xml, paragraph_xml
from docgen.pagination import signed_right_indent_chars
from docgen.settings import body_line_spacing_twips, title_line_spacing_twips


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
            first_line_chars=200,
            line=body_line_spacing_twips(args),
        )
    if kind == "level3":
        # GB/T 9704-2012：三级标题用 3 号仿宋体、不加粗、起首空二字。
        return paragraph_xml(
            text,
            font_name=args.body_font,
            size_pt=args.body_size,
            first_line_chars=200,
            line=body_line_spacing_twips(args),
        )
    return paragraph_xml(
        text,
        font_name=args.body_font,
        size_pt=args.body_size,
        line=body_line_spacing_twips(args),
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

    if heading in {"份号", "份号（可选）"}:
        # GB/T 9704：份号为版心左上角顶格的阿拉伯数字（一般 6 位），3 号字。
        for block in section.blocks:
            if block.kind == "paragraph" and block.text:
                xml_parts.append(
                    paragraph_xml(
                        block.text,
                        font_name=args.body_font,
                        size_pt=args.body_size,
                        first_line=0,
                        line=body_line_spacing_twips(args),
                    )
                )
        return xml_parts

    if heading in {"密级", "密级（可选）", "紧急程度", "紧急程度（可选）"}:
        # GB/T 9704：密级和保密期限、紧急程度均顶格、用 3 号黑体。
        for block in section.blocks:
            if block.kind == "paragraph" and block.text:
                xml_parts.append(
                    paragraph_xml(
                        block.text,
                        font_name=args.heading_font,
                        size_pt=args.body_size,
                        first_line=0,
                        line=body_line_spacing_twips(args),
                    )
                )
        return xml_parts

    if heading in {"签发人", "签发人（可选）"}:
        # GB/T 9704：上行文标注签发人，居右编排；当前整行用 3 号楷体（标签与姓名未分字体）。
        for block in section.blocks:
            if block.kind == "paragraph" and block.text:
                xml_parts.append(
                    paragraph_xml(
                        block.text,
                        font_name=args.subheading_font,
                        size_pt=args.body_size,
                        align="right",
                        right_chars=MIN_SIGNING_UNIT_RIGHT_CHARS,
                        line=body_line_spacing_twips(args),
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

        # GB/T 9704：加盖印章版成文日期右空 4 字（默认）；不加盖印章版（电子版 --unsealed）
        # 发文机关署名与成文日期均右空 2 字、上下两行编排。
        unsealed = getattr(args, "unsealed", False)
        date_right_chars = MIN_SIGNING_UNIT_RIGHT_CHARS if unsealed else SIGNING_DATE_RIGHT_CHARS

        if len(lines) == 1:
            right_chars = date_right_chars if is_date_line(lines[0]) else MIN_SIGNING_UNIT_RIGHT_CHARS
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
            unit_right_chars = (
                MIN_SIGNING_UNIT_RIGHT_CHARS if unsealed else signed_right_indent_chars(signing_unit, signing_date)
            )
            xml_parts.append(
                paragraph_xml(
                    signing_unit,
                    font_name=args.body_font,
                    size_pt=args.body_size,
                    align="right",
                    right_chars=unit_right_chars,
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
                right_chars=date_right_chars,
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
