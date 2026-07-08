"""docx 导出流程中流转的数据结构（Markdown 块、图片资产、章节、文本运行）。"""

from __future__ import annotations

import pathlib
from dataclasses import dataclass


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
