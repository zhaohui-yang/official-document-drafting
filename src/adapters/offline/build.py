#!/usr/bin/env python3
"""离线提示词适配器构建脚本。

功能说明：
- 从 `prompts/` 主源读取共享规则、文种规则和 profile 配置。
- 生成适用于 WebUI、AnythingLLM、Qwen、Claude.ai 等提示词宿主的离线提示词。
- 支持仅输出正式 `system_prompt`，也支持按文种拼装完整 `System Prompt + User Prompt`。

主要产物：
- `dist/offline/<profile>/system_prompt.md`
- `dist/offline/<profile>/doc-types/<文种>/system_prompt.md`
- `dist/offline/<profile>/doc-types/<文种>/user_prompt_template.md`
- `dist/offline/<profile>/doc-types/<文种>/prompt.md`
- 命令行 `-o` 指定的完整离线提示词文件

适用场景：
- 单机离线模型前端
- 仅支持粘贴提示词、不支持 skill 安装的宿主环境

Author: official-document-drafting maintainers
"""

from __future__ import annotations

import argparse
import pathlib
import sys
from collections.abc import Sequence


__author__ = "official-document-drafting maintainers"
__maintainer__ = "official-document-drafting maintainers"


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from adapters.shared import (  # noqa: E402
    DIST_DIR,
    format_doc_type_catalog,
    load_doc_types,
    load_profile,
    parse_doc_type_spec,
    read_text,
    render_offline_system_prompt,
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

DEFAULT_OFFLINE_PROFILES = ("default",)

def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(description="从 prompts/ 主源生成离线提示词。")
    parser.add_argument("--profile", default="default", help="profile 名称，默认 default")
    parser.add_argument("--all-profiles", action="store_true", help="同时重建仓库内置的全部离线 profiles")
    parser.add_argument("--check", action="store_true", help="只检查 dist/offline 产物是否与主源同步，不写盘")
    parser.add_argument("--doc-type", help="目标文种，可传英文 ID 或中文别名")
    parser.add_argument("--task", choices=sorted(TASK_LABELS), default="draft", help="任务类型，默认 draft")
    parser.add_argument("--instruction", help="用户当前任务说明或额外要求")
    parser.add_argument("--instruction-file", type=pathlib.Path, help="从文件读取任务说明")
    parser.add_argument("--material-file", action="append", default=[], type=pathlib.Path, help="素材文件，可重复传入多次")
    parser.add_argument("--include-examples", action="store_true", help="附带当前文种示例")
    parser.add_argument("--list-doc-types", action="store_true", help="列出支持的文种并退出")
    parser.add_argument("--emit-system", action="store_true", help="只生成基础系统提示词并写入 dist/offline/")
    parser.add_argument(
        "--emit-doc-type-prompts",
        action="store_true",
        help="为每个文种生成独立可用的 prompt 产物并写入 dist/offline/<profile>/doc-types/",
    )
    parser.add_argument("-o", "--output", type=pathlib.Path, help="将生成结果写入指定文件")
    args = parser.parse_args(argv)
    explicit_profile = "--profile" in argv

    has_task_inputs = bool(
        args.doc_type
        or args.instruction
        or args.instruction_file
        or args.material_file
        or args.output
        or args.include_examples
    )
    if args.check:
        # --check 默认核对全部内置 profile，除非显式 --profile 指定单个。
        args.all_profiles = args.all_profiles or not explicit_profile
    elif (
        not args.list_doc_types
        and not has_task_inputs
        and not args.emit_system
        and not args.emit_doc_type_prompts
    ):
        args.emit_system = True
        args.emit_doc_type_prompts = True
        args.all_profiles = not explicit_profile
    return args


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


def build_user_prompt_template(profile_name: str, doc_type_label: str, drafting_inputs: str = "") -> str:
    lines = [
        "请按上面的固定规则和模板处理本次任务。",
        "",
        "## 配置项（已是默认值，想改哪项就改哪项，其余保持默认即可）",
        "- 任务类型：起草成稿（可改：提纲 / 改写 / 摘要 / 规范化整理）",
        f"- 目标文种：{doc_type_label}",
        f"- 当前 profile：{profile_name}",
        "- 语域：中央·国家部委正式行文（可改：省级机关 / 一般单位）",
        "- 篇幅：完整结构（可改：只要提纲 / 精简）",
        "- 导出 Word：否（可改：是，则成稿后再用 generate_docx.py 导出）",
    ]
    if drafting_inputs:
        lines += [
            "",
            "## 本文种起草要点（按此准备下面的「需你提供」，缺哪项就补哪项）",
            "```markdown",
            drafting_inputs,
            "```",
        ]
    lines += [
        "",
        "## 需你提供",
        "- 主送对象：[填写收文机关；公布性文种可留空，未定写 [主送单位]]",
        "- 任务说明：[填写要写什么、主题与目的、时间要求]",
        "- 原始材料：[逐条粘贴已确认的事实，带来源/日期；较长先压成要点；未确认的留占位、标待核实]",
        "",
        "## 输出要求",
        "- 默认直接输出最终 Markdown 成稿。",
        "- 不要输出分析过程、思维链或与正文无关的解释。",
        "- 信息不足时保留占位符或标注待核实。",
        "- 未经材料明确支持的事实不得擅自补写。",
    ]
    return "\n".join(lines).strip()


def doc_type_artifact_dir(profile_name: str, doc_type) -> pathlib.Path:
    return DIST_DIR / "offline" / profile_name / "doc-types" / f"{doc_type.id}-{doc_type.dir_label}"


def build_doc_type_prompt_bundle(profile, doc_types, doc_type) -> dict[str, str]:
    system_prompt = render_offline_system_prompt(profile, doc_types, doc_type, include_examples=False)
    doc_type_label = f"{doc_type.display_name}（{doc_type.id}）"
    drafting_inputs = parse_doc_type_spec(doc_type.spec_path).drafting_inputs
    user_prompt_template = build_user_prompt_template(profile.name, doc_type_label, drafting_inputs)
    prompt = f"# System Prompt\n\n{system_prompt}\n\n# User Prompt\n\n{user_prompt_template}\n"
    return {
        "system_prompt.md": system_prompt + "\n",
        "user_prompt_template.md": user_prompt_template + "\n",
        "prompt.md": prompt,
    }


def emit_doc_type_prompts(profile, doc_types) -> list[pathlib.Path]:
    written: list[pathlib.Path] = []
    for doc_type in doc_types:
        out_dir = doc_type_artifact_dir(profile.name, doc_type)
        bundle = build_doc_type_prompt_bundle(profile, doc_types, doc_type)
        for filename, content in bundle.items():
            path = out_dir / filename
            write_text(path, content)
            written.append(path)
    return written


def build_profile_targets(profile_name: str) -> dict[pathlib.Path, str]:
    """本 profile 下全部离线产物（路径 -> 期望内容），既用于写盘也用于 `--check`。"""
    profile = load_profile(profile_name)
    doc_types = sort_doc_types(load_doc_types(), profile.category_order)
    targets: dict[pathlib.Path, str] = {
        DIST_DIR / "offline" / profile.name / "system_prompt.md": (
            render_offline_system_prompt(profile, doc_types, None, include_examples=False) + "\n"
        )
    }
    for doc_type in doc_types:
        out_dir = doc_type_artifact_dir(profile.name, doc_type)
        for filename, content in build_doc_type_prompt_bundle(profile, doc_types, doc_type).items():
            targets[out_dir / filename] = content
    return targets


def check_profiles(profile_names: Sequence[str]) -> int:
    """检查 dist/offline 产物是否与 prompts/ 主源同步，不写盘。"""
    mismatched: list[pathlib.Path] = []
    total = 0
    for profile_name in profile_names:
        for path, expected in build_profile_targets(profile_name).items():
            total += 1
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                mismatched.append(path)
    if mismatched:
        print("[ERROR] 以下离线产物未与 prompts/ 主源同步：", file=sys.stderr)
        for path in mismatched:
            print(f"- {path}", file=sys.stderr)
        return 1
    print(f"[OK] 离线产物已与 prompts/ 主源同步（共 {total} 个文件）。")
    return 0


def emit_profile_artifacts(profile_name: str, emit_system: bool, emit_doc_type_prompts_flag: bool) -> None:
    profile = load_profile(profile_name)
    doc_types = sort_doc_types(load_doc_types(), profile.category_order)

    if emit_system:
        output = DIST_DIR / "offline" / profile.name / "system_prompt.md"
        system_prompt = render_offline_system_prompt(profile, doc_types, None, include_examples=False)
        write_text(output, system_prompt + "\n")
        print(f"[OK] 已生成 {output}")

    if emit_doc_type_prompts_flag:
        written = emit_doc_type_prompts(profile, doc_types)
        for path in written:
            print(f"[OK] 已生成 {path}")


def main() -> int:
    args = parse_args()

    if args.check:
        target_profiles = DEFAULT_OFFLINE_PROFILES if args.all_profiles else (args.profile,)
        return check_profiles(target_profiles)

    profile = load_profile(args.profile)
    doc_types = sort_doc_types(load_doc_types(), profile.category_order)

    if args.list_doc_types:
        print(format_doc_type_catalog(doc_types, profile.category_order))
        return 0

    doc_type = resolve_doc_type(args.doc_type, doc_types)

    if args.emit_system or args.emit_doc_type_prompts:
        target_profiles = DEFAULT_OFFLINE_PROFILES if args.all_profiles else (args.profile,)
        for profile_name in target_profiles:
            emit_profile_artifacts(profile_name, args.emit_system, args.emit_doc_type_prompts)
        if args.emit_system or args.emit_doc_type_prompts:
            return 0

    instruction = load_instruction(args)
    materials = load_materials(args.material_file)
    system_prompt = render_offline_system_prompt(profile, doc_types, doc_type, include_examples=args.include_examples)
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
