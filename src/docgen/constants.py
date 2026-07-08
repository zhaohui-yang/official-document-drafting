"""docx 导出的版式常量与单位换算（页面、页边距、字号、默认方案等执行值）。"""

from __future__ import annotations

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CP_NS = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DC_NS = "http://purl.org/dc/elements/1.1/"
DCTERMS_NS = "http://purl.org/dc/terms/"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
EP_NS = "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
VT_NS = "http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"


DEFAULT_BODY_LINE_SPACING_TWIPS = 579
PAGE_WIDTH_TWIPS = 11906
PAGE_HEIGHT_TWIPS = 16838
# 默认页边距按 GB/T 9704-2012：上 37mm、下 35mm、左 28mm、右 26mm（1mm ≈ 56.6929 twips）。
# 据此版心为 156mm×225mm（宽=210-28-26，高=297-37-35），与国标一致。
# 同一组数值以 prompts/layout-profiles/*.toml 的 margin_*_twips 字段为声明主源；
# 本处常数是导出时实际生效的执行值，两处数值由 tests/test_generate_docx.py 的
# 防漂移用例（test_layout_profile_margins_match_code_constants）保证一致。
MARGIN_TOP_TWIPS = 2098  # 37mm
MARGIN_BOTTOM_TWIPS = 1984  # 35mm
MARGIN_LEFT_TWIPS = 1587  # 28mm
MARGIN_RIGHT_TWIPS = 1474  # 26mm
PRINTABLE_WIDTH_TWIPS = PAGE_WIDTH_TWIPS - MARGIN_LEFT_TWIPS - MARGIN_RIGHT_TWIPS
PRINTABLE_HEIGHT_TWIPS = PAGE_HEIGHT_TWIPS - MARGIN_TOP_TWIPS - MARGIN_BOTTOM_TWIPS
CHARS_PER_LINE = 28
IMAGE_MAX_WIDTH_RATIO = 0.85
IMAGE_PARAGRAPH_SPACING_TWIPS = 120
SIGNING_DATE_RIGHT_CHARS = 400
MIN_SIGNING_UNIT_RIGHT_CHARS = 200
# 页码按 GB/T 9704-2012：4 号（14 磅）宋体阿拉伯数字，两侧加一字线（— 1 —）。
PAGE_NUMBER_FONT = "宋体"
PAGE_NUMBER_SIZE_PT = 14
# 页码位于版心下边缘之下 7mm：版心下边缘距页面底边 = 下页边距 35mm，故页脚距底边约 35-7=28mm。
PAGE_NUMBER_FOOTER_TWIPS = 1587  # ≈28mm
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
    "recipient_after_twips": 0,
    "signing_before_twips": DEFAULT_BODY_LINE_SPACING_TWIPS,
    "body_first_line_chars": 200,
}


def chars_to_twips(chars_hundredths: int) -> int:
    return round((chars_hundredths / 100) * PRINTABLE_WIDTH_TWIPS / CHARS_PER_LINE)


def twips_to_emu(value: int) -> int:
    return value * 635
