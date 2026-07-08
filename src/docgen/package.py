"""OPC 包各部件（内容类型、关系、样式、页脚、属性）的生成与 .docx 原子落盘。"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import pathlib
import zipfile
from typing import Iterable
from xml.sax.saxutils import escape

from docgen.constants import (
    CP_NS,
    DC_NS,
    DCTERMS_NS,
    EP_NS,
    PAGE_NUMBER_FONT,
    PAGE_NUMBER_SIZE_PT,
    VT_NS,
    W_NS,
    XSI_NS,
)
from docgen.models import ImageAsset
from docgen.oxml import run_properties
from docgen.settings import body_line_spacing_twips


def collect_fonts(args: argparse.Namespace) -> list[str]:
    fonts = [args.header_font, args.title_font, args.heading_font, args.subheading_font, args.body_font]
    return list(dict.fromkeys(fonts))


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
    # rId 编号与 docgen.images.build_image_assets 保持一致：开启页码时页脚占用 rId3，图片自 rId4 起编号。
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
        f'<w:r>{run_properties(PAGE_NUMBER_FONT, PAGE_NUMBER_SIZE_PT)}<w:t>— </w:t></w:r>'
        '<w:fldSimple w:instr=" PAGE ">'
        f'<w:r>{run_properties(PAGE_NUMBER_FONT, PAGE_NUMBER_SIZE_PT)}<w:t>1</w:t></w:r>'
        '</w:fldSimple>'
        f'<w:r>{run_properties(PAGE_NUMBER_FONT, PAGE_NUMBER_SIZE_PT)}<w:t> —</w:t></w:r>'
        '</w:p></w:ftr>'
    )


def resolve_output_path(input_path: pathlib.Path, explicit_output: pathlib.Path | None) -> pathlib.Path:
    if explicit_output:
        return explicit_output
    return input_path.with_suffix(".docx")


def write_docx_package(
    output_path: pathlib.Path,
    *,
    args: argparse.Namespace,
    title: str,
    document_xml: str,
    image_assets: dict[str, ImageAsset],
) -> None:
    """把全部 docx 包内容先写入同目录临时文件，成功后原子改名为目标文件。

    这样即使写包过程中途失败（磁盘满、图片读取失败等），也不会留下半截损坏的
    .docx 覆盖旧成品；失败时会清理临时文件并把异常原样抛给上层统一报告。
    """
    tmp_path = output_path.with_name(output_path.name + ".tmp")
    try:
        with zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
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
        os.replace(tmp_path, output_path)
    except BaseException:
        tmp_path.unlink(missing_ok=True)
        raise
