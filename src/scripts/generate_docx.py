#!/usr/bin/env python3
"""将公文 Markdown 稿件转换为零依赖的 Word .docx 文件。

实现已拆分至 src/docgen/，本文件保留为兼容入口与再导出层。
"""

from __future__ import annotations

import pathlib
import sys

# 把 src/ 插入 sys.path，使 docgen、adapters 等顶层包在裸子进程与 runpy 执行下均可解析。
SRC_DIR = pathlib.Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# 历史兼容再导出：拆分前的单体脚本曾在模块顶层暴露这批 adapters.shared 符号，
# 外部调用方可能仍 from scripts.generate_docx import 它们；canonical 主源在 adapters.shared。
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
from docgen.constants import (  # noqa: E402
    CHARS_PER_LINE,
    CP_NS,
    DC_NS,
    DCTERMS_NS,
    DEFAULT_BODY_LINE_SPACING_TWIPS,
    DEFAULT_FONT_SETTINGS,
    DEFAULT_LAYOUT_SETTINGS,
    END_MATTER_HEADINGS,
    EP_NS,
    IMAGE_MAX_WIDTH_RATIO,
    IMAGE_PARAGRAPH_SPACING_TWIPS,
    MARGIN_BOTTOM_TWIPS,
    MARGIN_LEFT_TWIPS,
    MARGIN_RIGHT_TWIPS,
    MARGIN_TOP_TWIPS,
    MIN_SIGNING_UNIT_RIGHT_CHARS,
    PAGE_HEIGHT_TWIPS,
    PAGE_NUMBER_FONT,
    PAGE_NUMBER_FOOTER_TWIPS,
    PAGE_NUMBER_SIZE_PT,
    PAGE_WIDTH_TWIPS,
    PRINTABLE_HEIGHT_TWIPS,
    PRINTABLE_WIDTH_TWIPS,
    R_NS,
    SIGNING_DATE_RIGHT_CHARS,
    VT_NS,
    W_NS,
    XSI_NS,
    chars_to_twips,
    twips_to_emu,
)
from docgen.models import Block, ImageAsset, Section, TextRun  # noqa: E402
from docgen.settings import (  # noqa: E402
    apply_font_preset,
    apply_font_profile,
    apply_layout_profile,
    body_line_spacing_twips,
    finalize_export_settings,
    format_font_profile_catalog,
    format_layout_profile_catalog,
    render_current_export_plan,
    render_current_font_plan,
    render_current_layout_plan,
    resolve_selected_doc_type,
    title_line_spacing_twips,
)
from docgen.markdown import (  # noqa: E402
    collect_image_sources,
    extract_title_and_sections,
    is_date_line,
    normalize_annotation_text,
    paragraph_kind,
    parse_markdown,
    wrap_title_text,
)
from docgen.oxml import (  # noqa: E402
    POINT_MARKER_BOUNDARIES,
    POINT_MARKER_RE,
    emphasize_point_markers,
    merge_text_runs,
    page_break_xml,
    paragraph_xml,
    run_properties,
    run_xml,
    xml_text_runs,
)
from docgen.images import (  # noqa: E402
    build_image_assets,
    compute_image_size_emu,
    content_type_for_image_extension,
    estimate_image_twips,
    image_paragraph_xml,
    read_image_dimensions,
    read_jpeg_dimensions,
    read_png_dimensions,
)
from docgen.pagination import (  # noqa: E402
    compute_end_matter_position,
    estimate_paragraph_twips,
    estimate_rendered_body_paragraph_twips,
    estimate_section_height_twips,
    estimate_text_lines,
    section_contains_image,
    signed_right_indent_chars,
)
from docgen.sections import (  # noqa: E402
    render_body_paragraph,
    render_generic,
    render_numbered_heading,
    render_section_content,
)
from docgen.document import build_document_xml  # noqa: E402
from docgen.package import (  # noqa: E402
    build_app_xml,
    build_content_types_xml,
    build_core_xml,
    build_document_relationships_xml,
    build_font_table_xml,
    build_footer_xml,
    build_root_relationships_xml,
    build_styles_xml,
    collect_fonts,
    resolve_output_path,
    write_docx_package,
)
from docgen.cli import main, parse_args  # noqa: E402

__all__ = [
    # adapters.shared（历史兼容再导出）
    "FontProfile",
    "LayoutProfile",
    "load_doc_types",
    "load_font_profiles",
    "load_layout_profiles",
    "render_font_profile_markdown",
    "render_layout_profile_markdown",
    "resolve_doc_type",
    "resolve_font_profile",
    "resolve_layout_profile",
    # docgen.constants
    "W_NS",
    "R_NS",
    "CP_NS",
    "DC_NS",
    "DCTERMS_NS",
    "XSI_NS",
    "EP_NS",
    "VT_NS",
    "DEFAULT_BODY_LINE_SPACING_TWIPS",
    "PAGE_WIDTH_TWIPS",
    "PAGE_HEIGHT_TWIPS",
    "MARGIN_TOP_TWIPS",
    "MARGIN_BOTTOM_TWIPS",
    "MARGIN_LEFT_TWIPS",
    "MARGIN_RIGHT_TWIPS",
    "PRINTABLE_WIDTH_TWIPS",
    "PRINTABLE_HEIGHT_TWIPS",
    "CHARS_PER_LINE",
    "IMAGE_MAX_WIDTH_RATIO",
    "IMAGE_PARAGRAPH_SPACING_TWIPS",
    "SIGNING_DATE_RIGHT_CHARS",
    "MIN_SIGNING_UNIT_RIGHT_CHARS",
    "PAGE_NUMBER_FONT",
    "PAGE_NUMBER_SIZE_PT",
    "PAGE_NUMBER_FOOTER_TWIPS",
    "END_MATTER_HEADINGS",
    "DEFAULT_FONT_SETTINGS",
    "DEFAULT_LAYOUT_SETTINGS",
    "chars_to_twips",
    "twips_to_emu",
    # docgen.models
    "Block",
    "ImageAsset",
    "Section",
    "TextRun",
    # docgen.settings
    "apply_font_preset",
    "apply_font_profile",
    "apply_layout_profile",
    "resolve_selected_doc_type",
    "finalize_export_settings",
    "body_line_spacing_twips",
    "title_line_spacing_twips",
    "render_current_font_plan",
    "render_current_layout_plan",
    "render_current_export_plan",
    "format_font_profile_catalog",
    "format_layout_profile_catalog",
    # docgen.markdown
    "parse_markdown",
    "extract_title_and_sections",
    "collect_image_sources",
    "wrap_title_text",
    "is_date_line",
    "normalize_annotation_text",
    "paragraph_kind",
    # docgen.oxml
    "xml_text_runs",
    "run_properties",
    "run_xml",
    "paragraph_xml",
    "page_break_xml",
    "POINT_MARKER_RE",
    "POINT_MARKER_BOUNDARIES",
    "merge_text_runs",
    "emphasize_point_markers",
    # docgen.images
    "content_type_for_image_extension",
    "read_png_dimensions",
    "read_jpeg_dimensions",
    "read_image_dimensions",
    "compute_image_size_emu",
    "estimate_image_twips",
    "build_image_assets",
    "image_paragraph_xml",
    # docgen.pagination
    "estimate_text_lines",
    "section_contains_image",
    "estimate_paragraph_twips",
    "signed_right_indent_chars",
    "estimate_rendered_body_paragraph_twips",
    "estimate_section_height_twips",
    "compute_end_matter_position",
    # docgen.sections
    "render_body_paragraph",
    "render_numbered_heading",
    "render_section_content",
    "render_generic",
    # docgen.document
    "build_document_xml",
    # docgen.package
    "collect_fonts",
    "build_styles_xml",
    "build_font_table_xml",
    "build_content_types_xml",
    "build_root_relationships_xml",
    "build_document_relationships_xml",
    "build_core_xml",
    "build_app_xml",
    "build_footer_xml",
    "resolve_output_path",
    "write_docx_package",
    # docgen.cli
    "parse_args",
    "main",
]

if __name__ == "__main__":
    raise SystemExit(main())
