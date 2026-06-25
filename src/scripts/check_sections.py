#!/usr/bin/env python3
"""校验公文模板或示例稿是否包含约定章节。"""

from __future__ import annotations

import argparse
import math
import pathlib
import re
import sys


# 每个文种的必备章节。取值来自 assets/templates/<id>.md 的板块标题，只收必备项——
# 标注「（可选）」的板块（如附件、附注、报送范围）与模板自身的标题行不计入。
# 改动须与模板保持同步，否则 tests/test_template_sections.py 会失败。
REQUIRED_SECTIONS = {
    "notice": ["标题", "主送单位", "正文", "落款"],
    "request": ["标题", "主送单位", "事项背景", "请示事项", "请示意见", "落款"],
    "report": ["标题", "主送单位", "基本情况", "工作开展情况", "存在问题", "下一步建议", "落款"],
    "reply": ["标题", "主送单位", "来文回顾", "答复意见", "执行要求", "落款"],
    "minutes": ["会议基本信息", "责任分工", "后续要求"],
    "announcement": ["标题", "公告事项", "执行说明", "落款"],
    "approval": ["标题", "来文依据", "批复意见", "执行要求", "落款"],
    "briefing": ["标题", "导语", "主要信息", "工作建议或提示"],
    "circular": ["标题", "基本情况", "评价分析", "工作要求", "落款"],
    "communique": ["标题", "背景概况", "主要内容", "结语"],
    "decision": ["标题", "背景依据", "决定事项", "执行要求", "落款"],
    "letter": ["标题", "主送单位", "事项缘由", "主要意见", "配合事项", "落款"],
    "motion": ["标题", "提请审议事项", "依据与理由", "议案内容", "落款"],
    "opinion": ["标题", "背景与总体要求", "基本原则", "主要意见", "组织实施", "落款"],
    "order": ["标题", "发布依据", "命令内容", "生效说明", "签署与日期"],
    "presentation": ["标题", "工作进展", "主要成效", "存在问题", "下一步措施"],
    "public-notice": ["标题", "发布缘由", "通告事项", "执行要求", "落款"],
    "resolution": ["标题", "会议背景", "决议事项", "落实要求", "落款"],
    "special-report": ["标题", "报送对象", "事项概况", "最新进展", "风险研判", "工作建议"],
    "speech": ["标题", "称谓", "开场说明", "形势判断", "重点任务", "工作要求", "结束语"],
    "summary": ["标题", "基本情况", "主要做法", "工作成效", "存在问题", "下一步打算"],
    "work-plan": ["标题", "制定背景", "总体要求", "工作目标", "主要任务", "实施步骤", "保障措施"],
}

# 各文种常见结尾用语（与 prompts/core/drafting-thinking.md、style.md 一致）。
# 只收录有明确套语的文种；用于成稿结尾用语核对，提示性、不作硬错误。
ENDING_PHRASES = {
    "notice": ["特此通知"],
    "request": ["请批示", "请批复"],
    "report": ["特此报告"],
    "reply": ["特此函复", "此复"],
    "approval": ["请遵照执行", "特此批复", "此复"],
    "letter": ["特此函复", "特此函达", "特此函商", "请予支持为盼"],
    "announcement": ["特此公告"],
    "public-notice": ["特此通告", "起施行"],
    "decision": ["特此决定"],
    "resolution": ["特作如下决议", "起施行"],
    "motion": ["特提请审议", "提请审议"],
    "order": ["现予公布", "起施行"],
    "opinion": ["请批转执行", "贯彻执行"],
}

# 成稿中疑似未替换的占位符：方括号/中括号占位、待核实/待补充、连续 X 或 ×。
PLACEHOLDER_RE = re.compile(r"[\[【][^\]】\n]{0,30}[\]】]|待核实|待补充|X{2,}|×{2,}")

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
# 附件清单区：`附件`、`附件：`、`附件（可选）` 等。该区内的 `1. xxx` 是清单序号，
# 不是三级标题——附件序号与 prompts/core/style.md 约定的三级标题 `1.` 写法相同，
# 只能靠所在板块区分，否则附件列表会被误判为跳级。
ATTACHMENT_SECTION_RE = re.compile(r"^附件")
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
    in_attachment = False
    for lineno, raw_line in enumerate(content.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            # 层级标记常内嵌在 Markdown 标题里，如 `## 二、形势判断`；剥离 # 后再判层级，
            # 否则后文 `（一）` 会因为「没见过一级」而被误判为跳级。
            marker_text = re.sub(r"^#+\s*", "", line)
            # 进入/离开附件清单区由板块标题决定（下一个非附件标题即离开）。
            in_attachment = ATTACHMENT_SECTION_RE.match(marker_text) is not None
        else:
            if ATTACHMENT_SECTION_RE.match(line):
                in_attachment = True
            # 附件清单区内的 `1. xxx` 是清单序号而非三级标题，跳过避免误判跳级。
            if in_attachment and LEVEL3_RE.match(line):
                continue
            marker_text = line
        for level, pattern in PARAGRAPH_MARKERS:
            if pattern.match(marker_text):
                results.append((lineno, level, marker_text))
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


def check_residual_placeholders(content: str) -> list[str]:
    """成稿不应保留未填占位符；检出 `[…]`、`【…】`、`待核实`、`××` 等并提示。"""
    found = PLACEHOLDER_RE.findall(content)
    if not found:
        return []
    samples = "、".join(sorted(set(found))[:8])
    return [f"检测到 {len(found)} 处疑似未填占位符（成稿不应保留）：{samples}"]


def check_ending_phrase(content: str, doc_type: str) -> list[str]:
    """核对结尾用语是否与文种匹配（如通知→特此通知、请示→请批示）。"""
    phrases = ENDING_PHRASES.get(doc_type)
    if not phrases or any(phrase in content for phrase in phrases):
        return []
    return [f"未检测到 `{doc_type}` 文种常见结尾用语（如「{phrases[0]}」），请确认结尾是否规范。"]


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

    content_warnings = check_residual_placeholders(content) + check_ending_phrase(content, args.doc_type)

    print(f"[OK] {args.file} 章节完整，类型：{args.doc_type}")
    if structure_warnings:
        print("[WARN] 检测到以下层级结构提醒：")
        for item in structure_warnings:
            print(f"- {item}")
    if content_warnings:
        print("[WARN] 检测到以下内容提示：")
        for item in content_warnings:
            print(f"- {item}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
