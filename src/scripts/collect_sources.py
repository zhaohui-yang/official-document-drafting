#!/usr/bin/env python3
"""汇总各文种「撰写思路」对标的真实样例来源，供核对 README「公开参考来源」节。

各 `prompts/doc-types/<id>/spec.md` 顶部 HTML 注释里记着该文种撰写思路对标的真实
`.gov.cn` 样例 URL（取证主源）。本脚本把它们按文种汇总为紧凑 Markdown 清单；
README 该节现以表格呈现（链接文本人工维护），改了 spec 注释后重跑本脚本，
用输出逐文种核对 README 表格的 URL 集合并手工同步。

用法：`python3 src/scripts/collect_sources.py`（打印到标准输出）。
"""

from __future__ import annotations

import pathlib
import re
import sys


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
DOC_TYPES_DIR = REPO_ROOT / "prompts" / "doc-types"

# 全国通行的根本依据（权威 .gov.cn 全文，已核实）。
STANDARDS = [
    (
        "GB/T 9704-2012《党政机关公文格式》（国家标准全文公开平台）",
        "https://openstd.samr.gov.cn/bzgk/std/newGbInfo?hcno=F3CC9BEF482524C895FDA7A08BB4A70E",
    ),
    (
        "《党政机关公文处理工作条例》（中办发〔2012〕14号，中国政府网）",
        "https://www.gov.cn/zwgk/2013-02/22/content_2337704.htm",
    ),
]

_COMMENT_RE = re.compile(r"<!--(.*?)-->", re.DOTALL)
_URL_RE = re.compile(r"https?://[^\s)\]）】\"'，。、]+")


def _display_name(dir_name: str) -> str:
    """`report-报告` -> `报告（report）`；兼容 `public-notice-通告` 等带连字符 id。"""
    eng, _, zh = dir_name.rpartition("-")
    return f"{zh}（{eng}）" if eng else dir_name


def collect() -> list[tuple[str, list[str]]]:
    """返回 [(文种显示名, [URL…])]，按目录名排序；无 URL（依通则）的列表为空。"""
    rows: list[tuple[str, list[str]]] = []
    for spec in sorted(DOC_TYPES_DIR.glob("*/spec.md"), key=lambda p: p.parent.name):
        comment = _COMMENT_RE.search(spec.read_text(encoding="utf-8"))
        urls = _URL_RE.findall(comment.group(1)) if comment else []
        rows.append((_display_name(spec.parent.name), urls))
    return rows


def render_readme_block() -> str:
    lines = ["**根本依据（全国通行）：**", ""]
    lines += [f"- {name}：{url}" for name, url in STANDARDS]
    lines += [
        "",
        "**各文种撰写思路对标的真实样例（部委以上级别 `.gov.cn` 公开来源，可核实；"
        "权威全文稀缺者依《党政机关公文处理工作条例》等通则归纳，无具体网址）：**",
        "",
    ]
    for name, urls in collect():
        value = " · ".join(urls) if urls else "依权威通则归纳（无具体网址）"
        lines.append(f"- **{name}**：{value}")
    return "\n".join(lines)


def main() -> int:
    print(render_readme_block())
    return 0


if __name__ == "__main__":
    sys.exit(main())
