#!/usr/bin/env python3
"""校验公文模板或示例稿是否包含约定章节。"""

from __future__ import annotations

import argparse
import math
import pathlib
import re
import sys


REQUIRED_SECTIONS = {
    "notice": ["标题", "主送单位", "正文", "落款"],
    "request": ["标题", "主送单位", "事项背景", "请示事项", "请示意见", "落款"],
    "report": ["标题", "主送单位", "基本情况", "工作开展情况", "存在问题", "下一步建议", "落款"],
    "reply": ["标题", "主送单位", "来文回顾", "答复意见", "执行要求", "落款"],
    "minutes": ["会议基本信息", "责任分工", "后续要求"],
}

LEVEL1_RE = re.compile(r"^[一二三四五六七八九十百千]+、")
LEVEL2_RE = re.compile(r"^（[一二三四五六七八九十百千]+）")
LEVEL3_RE = re.compile(r"^\d+[\.．]")
LEVEL4_RE = re.compile(r"^（\d+）")
PARAGRAPH_MARKERS = (
    (1, LEVEL1_RE),
    (2, LEVEL2_RE),
    (3, LEVEL3_RE),
    (4, LEVEL4_RE),
)
CHARS_PER_PAGE_ESTIMATE = 22 * 28


def normalize_heading_text(text: str) -> str:
    normalized = text.strip()
    normalized = re.sub(r"^#+\s*", "", normalized)
    normalized = re.sub(r"^[一二三四五六七八九十百千]+、", "", normalized)
    normalized = re.sub(r"^（[一二三四五六七八九十百千]+）", "", normalized)
    normalized = re.sub(r"^\d+[\.．]\s*", "", normalized)
    normalized = re.sub(r"^（\d+）", "", normalized)
    return normalized.strip()


def collect_markdown_headings(content: str) -> set[str]:
    headings: set[str] = set()
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line.startswith("#"):
            continue
        headings.add(normalize_heading_text(line))
    return headings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="校验公文模板或示例稿的章节完整性。")
    parser.add_argument("doc_type", choices=sorted(REQUIRED_SECTIONS), help="文种类型")
    parser.add_argument("file", type=pathlib.Path, help="待校验的 Markdown 文件")
    parser.add_argument("--strict-structure", action="store_true", help="将层级结构提醒按错误处理")
    return parser.parse_args()


def detect_heading_levels(content: str) -> list[tuple[int, int, str]]:
    results: list[tuple[int, int, str]] = []
    for lineno, raw_line in enumerate(content.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        for level, pattern in PARAGRAPH_MARKERS:
            if pattern.match(line):
                results.append((lineno, level, line))
                break
    return results


def estimate_pages(content: str) -> int:
    visible_chars = len(re.sub(r"\s+", "", content))
    if visible_chars == 0:
        return 0
    return math.ceil(visible_chars / CHARS_PER_PAGE_ESTIMATE)


def check_heading_structure(content: str) -> list[str]:
    warnings: list[str] = []
    headings = detect_heading_levels(content)
    seen_levels: set[int] = set()

    for lineno, level, text in headings:
        if level > 1 and (level - 1) not in seen_levels:
            warnings.append(f"第 {lineno} 行标题疑似跳级：`{text}`")
        seen_levels.add(level)

    estimated_pages = estimate_pages(content)
    deepest_level = max((level for _, level, _ in headings), default=0)
    if estimated_pages and estimated_pages <= 10 and deepest_level >= 3:
        warnings.append(
            f"估算篇幅约 {estimated_pages} 页，按当前规则 10 页以内统一控制到二级标题；当前检测到三级及以下标题。"
        )

    for lineno, _, text in headings:
        if text.startswith("一是") or text.startswith("二是") or text.startswith("三是"):
            warnings.append(f"第 {lineno} 行使用了 `一是/二是` 起头，建议作为段内分点而非正式层级标题：`{text}`")

    return warnings


def main() -> int:
    args = parse_args()
    content = args.file.read_text(encoding="utf-8")
    headings = collect_markdown_headings(content)
    missing = [section for section in REQUIRED_SECTIONS[args.doc_type] if section not in headings]
    structure_warnings = check_heading_structure(content)

    if missing:
        print(f"[ERROR] {args.file} 缺少以下章节：")
        for section in missing:
            print(f"- {section}")
        return 1

    if structure_warnings and args.strict_structure:
        print(f"[ERROR] {args.file} 层级结构存在以下问题：")
        for item in structure_warnings:
            print(f"- {item}")
        return 1

    print(f"[OK] {args.file} 章节完整，类型：{args.doc_type}")
    if structure_warnings:
        print("[WARN] 检测到以下层级结构提醒：")
        for item in structure_warnings:
            print(f"- {item}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
