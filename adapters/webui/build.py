#!/usr/bin/env python3
"""Build WebUI / offline prompt artifacts from prompts/ source."""

from __future__ import annotations

import argparse
import pathlib
import sys


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from adapters.shared import (  # noqa: E402
    DIST_DIR,
    format_doc_type_catalog,
    load_doc_types,
    load_profile,
    read_text,
    render_webui_system_prompt,
    resolve_doc_type,
    sort_doc_types,
    write_text,
)


TASK_LABELS = {
    "draft": "起草成稿",
    "rewrite": "改写润色",
    "summarize": "整理摘要",
    "normalize": "规范化整理",
    "outline": "生成提纲",
}

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="从 prompts/ 主源生成离线 WebUI / Qwen 提示词。")
    parser.add_argument("--profile", default="default", help="profile 名称，默认 default")
    parser.add_argument("--doc-type", help="目标文种，可传英文 ID 或中文别名")
    parser.add_argument("--task", choices=sorted(TASK_LABELS), default="draft", help="任务类型，默认 draft")
    parser.add_argument("--instruction", help="用户当前任务说明或额外要求")
    parser.add_argument("--instruction-file", type=pathlib.Path, help="从文件读取任务说明")
    parser.add_argument("--material-file", action="append", default=[], type=pathlib.Path, help="素材文件，可重复传入多次")
    parser.add_argument("--include-examples", action="store_true", help="附带当前文种示例")
    parser.add_argument("--list-doc-types", action="store_true", help="列出支持的文种并退出")
    parser.add_argument("--emit-system", action="store_true", help="只生成基础系统提示词并写入 dist/webui/")
    parser.add_argument("-o", "--output", type=pathlib.Path, help="将生成结果写入指定文件")
    return parser.parse_args()


def load_instruction(args: argparse.Namespace) -> str:
    parts: list[str] = []
    if args.instruction:
        parts.append(args.instruction.strip())
    if args.instruction_file:
        parts.append(read_text(args.instruction_file))
    return "\n\n".join(part for part in parts if part)


def load_materials(files: list[pathlib.Path]) -> str:
    blocks: list[str] = []
    for path in files:
        blocks.append(f"### 素材文件：{path}\n\n{read_text(path)}")
    return "\n\n".join(blocks)


def build_user_prompt(
    profile_name: str,
    task: str,
    doc_type_label: str,
    instruction: str,
    materials: str,
) -> str:
    instruction_block = instruction or "[未单独提供任务说明，请结合素材自行判断主题和成稿目标。]"
    materials_block = materials or "[未附素材文件，请根据当前对话中的其他文字整理。]"
    lines = [
        "请按上面的固定规则和模板处理本次任务。",
        f"- 当前任务类型：{TASK_LABELS[task]}",
        f"- 当前 profile：{profile_name}",
        f"- 目标文种：{doc_type_label}",
        "",
        "## 用户任务说明",
        instruction_block,
        "",
        "## 原始材料",
        materials_block,
        "",
        "## 输出要求",
        "- 默认直接输出最终 Markdown 成稿。",
        "- 不要输出分析过程、思维链或与正文无关的解释。",
        "- 信息不足时保留占位符或标注待核实。",
        "- 如果当前任务更适合提纲而非全文，应明确按提纲格式输出。",
    ]
    return "\n".join(lines).strip()


def main() -> int:
    args = parse_args()
    profile = load_profile(args.profile)
    doc_types = sort_doc_types(load_doc_types(), profile.category_order)

    if args.list_doc_types:
        print(format_doc_type_catalog(doc_types, profile.category_order, include_paths=False))
        return 0

    doc_type = resolve_doc_type(args.doc_type, doc_types)

    if args.emit_system:
        output = DIST_DIR / "webui" / profile.name / "system_prompt.md"
        system_prompt = render_webui_system_prompt(profile, doc_types, None, include_examples=False)
        write_text(output, system_prompt + "\n")
        print(f"[OK] 已生成 {output}")
        return 0

    instruction = load_instruction(args)
    materials = load_materials(args.material_file)
    system_prompt = render_webui_system_prompt(profile, doc_types, doc_type, include_examples=args.include_examples)
    doc_type_label = f"{doc_type.display_name}（{doc_type.id}）" if doc_type else "请先判断，再按最匹配的文种或材料类型成稿"
    user_prompt = build_user_prompt(profile.name, args.task, doc_type_label, instruction, materials)
    final_text = f"# System Prompt\n\n{system_prompt}\n\n# User Prompt\n\n{user_prompt}\n"

    if args.output:
        write_text(args.output, final_text)
    else:
        print(final_text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
