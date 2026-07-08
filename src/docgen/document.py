"""组装 word/document.xml：标题与章节渲染、版记定位、分页与页面设置。"""

from __future__ import annotations

import argparse

from docgen.constants import (
    END_MATTER_HEADINGS,
    MARGIN_BOTTOM_TWIPS,
    MARGIN_LEFT_TWIPS,
    MARGIN_RIGHT_TWIPS,
    MARGIN_TOP_TWIPS,
    PAGE_HEIGHT_TWIPS,
    PAGE_NUMBER_FOOTER_TWIPS,
    PAGE_WIDTH_TWIPS,
    PRINTABLE_HEIGHT_TWIPS,
    R_NS,
    W_NS,
)
from docgen.markdown import extract_title_and_sections, wrap_title_text
from docgen.models import Block, ImageAsset, Section
from docgen.oxml import page_break_xml, paragraph_xml
from docgen.pagination import (
    compute_end_matter_position,
    estimate_paragraph_twips,
    estimate_section_height_twips,
    section_contains_image,
)
from docgen.sections import render_generic, render_section_content
from docgen.settings import title_line_spacing_twips


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
            section_height = estimate_section_height_twips(
                section,
                args=args,
                hidden_sections=hidden_sections,
                image_assets=image_assets,
            )
            if section_contains_image(section) and section_height <= PRINTABLE_HEIGHT_TWIPS:
                current_mod = consumed_twips % PRINTABLE_HEIGHT_TWIPS
                remaining_twips = PRINTABLE_HEIGHT_TWIPS - current_mod if current_mod else PRINTABLE_HEIGHT_TWIPS
                if current_mod and section_height > remaining_twips:
                    body_parts.append(page_break_xml())
                    consumed_twips += remaining_twips
            body_parts.extend(
                render_section_content(
                    section,
                    args=args,
                    hidden_sections=hidden_sections,
                    image_assets=image_assets,
                    drawing_id_counter=drawing_id_counter,
                )
            )
            consumed_twips += section_height
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
                    f'w:header="720" w:footer="{PAGE_NUMBER_FOOTER_TWIPS}" w:gutter="0"/>'
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
