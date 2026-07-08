"""图片资产处理：尺寸识别、EMU 换算、资产收集（含同目录安全检查）与图片段落 XML。"""

from __future__ import annotations

import argparse
import pathlib
from xml.sax.saxutils import escape

from docgen.constants import (
    IMAGE_MAX_WIDTH_RATIO,
    IMAGE_PARAGRAPH_SPACING_TWIPS,
    PRINTABLE_WIDTH_TWIPS,
    twips_to_emu,
)
from docgen.markdown import collect_image_sources
from docgen.models import Block, ImageAsset


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
    max_width_emu = twips_to_emu(round(PRINTABLE_WIDTH_TWIPS * IMAGE_MAX_WIDTH_RATIO))
    width_emu = max_width_emu
    height_emu = max(1, round(width_emu * height_px / width_px))
    return width_emu, height_emu


def estimate_image_twips(asset: ImageAsset, args: argparse.Namespace) -> int:
    return round(asset.height_emu / 635) + 2 * IMAGE_PARAGRAPH_SPACING_TWIPS


def build_image_assets(
    blocks: list[Block],
    markdown_path: pathlib.Path,
    *,
    show_page_number: bool,
) -> dict[str, ImageAsset]:
    assets: dict[str, ImageAsset] = {}
    # rId 编号与 docgen.package.build_document_relationships_xml 保持一致：开启页码时 rId3 被页脚占用，图片自 rId4 起编号。
    next_rel_id = 4 if show_page_number else 3
    base_dir = markdown_path.parent.resolve()
    for index, src in enumerate(collect_image_sources(blocks), start=1):
        source_path = (markdown_path.parent / src).resolve()
        # 业务素材同目录（最小授权）：引用的图片必须位于成稿 .md 同目录或其子目录，
        # 不允许 ../ 越级或绝对路径跳出，避免导出时需要更大的文件系统读取授权。
        if source_path != base_dir and base_dir not in source_path.parents:
            raise ValueError(
                f"图片必须位于成稿同目录或子目录内，不得跨目录（../ 或绝对路径）引用：{src}"
            )
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
    image_height_twips = max(1, round(asset.height_emu / 635))
    return (
        "<w:p>"
        '<w:pPr><w:jc w:val="center"/>'
        f'<w:spacing w:before="{IMAGE_PARAGRAPH_SPACING_TWIPS}" '
        f'w:after="{IMAGE_PARAGRAPH_SPACING_TWIPS}" '
        f'w:line="{image_height_twips}" w:lineRule="atLeast"/>'
        "</w:pPr>"
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
