"""Markdown 解析与文本启发式：分块、抽取标题章节、标题断行与段落类型识别。"""

from __future__ import annotations

import re
from typing import Iterable

from docgen.models import Block, Section


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


def collect_image_sources(blocks: Iterable[Block]) -> list[str]:
    seen: set[str] = set()
    sources: list[str] = []
    for block in blocks:
        if block.kind == "image" and block.src and block.src not in seen:
            seen.add(block.src)
            sources.append(block.src)
    return sources
