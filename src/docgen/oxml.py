"""WordprocessingML 底层拼装：文本运行、段落、分页与要点标记强调等 XML 原语。"""

from __future__ import annotations

import argparse
import re
from xml.sax.saxutils import escape

from docgen.constants import DEFAULT_BODY_LINE_SPACING_TWIPS, chars_to_twips
from docgen.models import TextRun


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
