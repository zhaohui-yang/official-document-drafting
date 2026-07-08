"""skill 侧与 offline 侧共用的文本渲染与模板导出（SKILL.md、references、离线提示词等）。"""

from __future__ import annotations

import json
import pathlib

from adapters.doc_types import (
    DocType,
    format_doc_type_catalog,
    parse_doc_type_spec,
)
from adapters.paths import (
    DOC_TYPE_GUARDRAILS_PATH,
    REPO_ROOT,
    ROOT_TEMPLATES_DIR,
    read_text,
    shift_markdown_headings,
    write_text,
)
from adapters.profiles import (
    Profile,
    load_font_profiles,
    load_layout_profiles,
    render_font_profile_markdown,
    render_layout_profile_markdown,
)


def render_core_sections(profile: Profile) -> str:
    blocks: list[str] = []
    for section in profile.core_sections:
        blocks.append(f"## {section.title}\n\n{shift_markdown_headings(read_text(section.path), levels=1)}")
    return "\n\n".join(blocks).strip()


def render_doc_type_guardrails() -> str:
    return read_text(DOC_TYPE_GUARDRAILS_PATH)


SKILL_FILE_INDEX = "\n".join(
    [
        "```",
        "official-document-drafting/",
        "├── SKILL.md                       # 本文件：入口、任务路由、默认流程、文种目录（由 prompts/ 生成）",
        "├── prompts/",
        "│   ├── core/                      # 共享总规则主源（在线按需读取，离线提示词内联）",
        "│   │   ├── policy.md              # 政策与交付边界",
        "│   │   ├── doc-type-guardrails.md # 防编造强制约束",
        "│   │   ├── workflow.md            # 文种判断、文种路由规则、保存与命名约定",
        "│   │   ├── style.md               # 语言风格、标题层级、正文结尾、落款、主送/附件/版记",
        "│   │   ├── layout.md              # 基线版式与 Word 导出约定",
        "│   │   └── fallback-template.md   # 无独立文种模板时的兜底骨架",
        "│   ├── doc-types/<id>-<文种>/     # 各文种 spec.md（写作规则/版式要求/模板）、meta.toml、examples.md",
        "│   ├── font-profiles/*.toml       # 字体方案",
        "│   ├── layout-profiles/*.toml     # 版式参数方案",
        "│   └── profiles/*.toml            # 在线/离线构建 profile",
        "├── src/scripts/generate_docx.py       # Markdown 成稿导出 .docx（--doc-type 自动套用字体与版式）",
        "├── src/adapters/skill/build.py        # 由 prompts/ 生成 SKILL.md 等在线产物（--check 校验同步）",
        "└── docs/references/                    # 面向读者的说明文档，操作性规则以 prompts/core 为准",
        "```",
    ]
)


# 任务路由中，policy.md 与 doc-type-guardrails.md 合并进“事实与政策底线”首行，其余 core 段
# 按文件名给出更易检索的提示语；缺省回退到 section 标题。
_ROUTING_SECTION_HINTS = {
    "workflow.md": "文种判断、行文方向、文种路由规则、保存与命名约定",
    "style.md": "语言风格、标题与层级编号、正文与结尾、落款、主送/附件/版记",
    "layout.md": "基线版式、字体字号、Word 导出参数与脚本约定",
}
_ROUTING_BASELINE_FILES = {"policy.md", "doc-type-guardrails.md"}


def render_skill_routing_table(profile: Profile) -> str:
    rows = [
        "| 请求类型 | 读取 |",
        "| --- | --- |",
        "| 任何起草、改写、润色前的事实与政策底线 | `prompts/core/policy.md`、`prompts/core/doc-type-guardrails.md` |",
    ]
    for section in profile.core_sections:
        rel = section.path.relative_to(REPO_ROOT).as_posix()
        if section.path.name in _ROUTING_BASELINE_FILES:
            continue
        hint = _ROUTING_SECTION_HINTS.get(section.path.name, section.title)
        rows.append(f"| {hint} | `{rel}` |")
    rows.extend(
        [
            "| 具体文种的写作规则、版式要求、模板 | 下方“文种目录”对应的 `spec.md` |",
            "| 字体与版式精确参数 | `prompts/font-profiles/<方案>.toml`、`prompts/layout-profiles/<方案>.toml` |",
            "| 没有独立文种模板时的兜底骨架 | `prompts/core/fallback-template.md` |",
        ]
    )
    return "\n".join(rows)


SKILL_DEFAULT_FLOW = "\n".join(
    [
        "1. 先读事实与政策底线（`policy.md`、`doc-type-guardrails.md`）；任何起草都以真实性优先于文采。",
        "2. 判断文种：先判断是否法定公文 15 种，否则落到常见正式材料；判断行文方向（上行/下行/平行/公开）、发文主体、主送对象、事项性质与时间要求。详细文种路由规则见 `prompts/core/workflow.md`。",
        "3. 按任务类型从“任务路由”读取语言（`style.md`）、版式（`layout.md`）等共享规则，只加载本次需要的部分，不一次性全量加载。",
        "4. 读取目标文种 `spec.md` 的“写作规则”“版式要求”“模板”，并按 `meta.toml` 的 `font_profile`、`layout_profile` 应用字体与版式；无独立模板时退回 `prompts/core/fallback-template.md`。",
        "5. 默认直接输出最终 Markdown 成稿；用户只要求提纲时输出提纲。信息不足时保留 `[发文单位]`、`[日期]`、`[待核实]` 等占位符，不虚构。",
        "6. 需要 Word 时，确认 Markdown 结构正确后调用 `src/scripts/generate_docx.py`，按文种 `meta.toml` 的字体与版式方案导出。",
        "7. 成稿前校对错别字、病句、标点、数字、日期、称谓和机构名称。",
    ]
)

# 自包含 references 包用的默认流程：路径全部指向 references/，不引用 prompts/。
SKILL_DEFAULT_FLOW_REFERENCE = "\n".join(
    [
        "1. 先读 `references/core-政策边界.md` 与 `references/core-事实核验与防编造.md` 的事实与政策底线；任何起草都以真实性优先于文采。",
        "2. 判断文种：先判断是否法定公文 15 种，否则落到常见正式材料；判断行文方向（上行/下行/平行/公开）、发文主体、主送对象、事项性质与时间要求。详细文种路由见 `references/core-处理流程.md`。",
        "3. 按需读取 `references/core-语言与输出.md`、`references/core-版式与导出.md`、`references/core-撰写思路与语域.md` 等共享规则，只加载本次需要的部分，不一次性全量加载。",
        "4. 读取对应 `references/文种-<文种>.md`，其中已含起草要点、撰写思路、写作规则、字体/版式方案与模板。",
        "5. 默认直接输出最终 Markdown 成稿；用户只要求提纲时输出提纲。信息不足时保留 `[发文单位]`、`[日期]`、`[待核实]` 等占位符，不虚构。",
        "6. 需要 Word 时，确认 Markdown 结构正确后用仓库内的导出脚本 `src/scripts/generate_docx.py`，按文种字体与版式方案导出。",
        "7. 成稿前校对错别字、病句、标点、数字、日期、称谓和机构名称。",
    ]
)


def render_skill_markdown(profile: Profile, doc_types: list[DocType]) -> str:
    blocks = [
        "---",
        f"name: {profile.skill_name}",
        f"description: {profile.skill_description}",
    ]
    if profile.skill_metadata:
        blocks.append(f"metadata: {json.dumps(profile.skill_metadata, ensure_ascii=False)}")
    blocks.extend(
        [
            "---",
            "",
            "<!-- Generated from prompts/ and src/adapters/skill/build.py. -->",
            "",
            f"# {profile.skill_title}",
            "",
            "`official-document-drafting` 的统一入口：把新闻素材、零散信息或既有文稿整理成规范的中文公文与正式材料，并可导出 Word。本文件只保留入口、任务路由、默认流程和文种目录；详细规则按需读取 `prompts/core/*.md` 和对应文种 `spec.md`，不在此重复展开。",
            "",
            "核心原则：真实性优先于文采；不编造事实、政策依据、数字、文件号、会议结论；信息不足时保留占位符或标注待核实。完整边界见 `prompts/core/policy.md` 与 `prompts/core/doc-type-guardrails.md`。",
            "",
            "## 调用方式",
            "",
            "- 先按下方“任务路由”读取本次任务需要的共享规则，无需一次性加载全部规则。",
            "- 判断当前任务最匹配的文种（见“文种目录”与 `prompts/core/workflow.md` 的文种路由规则）。",
            "- 文种确定后，先应用 `prompts/core/doc-type-guardrails.md`，再读取对应文种目录的 `spec.md`，按其中“写作规则”“版式要求”“模板”章节处理，并按 `meta.toml` 中的 `font_profile` 和 `layout_profile` 应用字体与版式参数。",
            "- 如存在 `examples.md`，并且用户明确要求更贴近既有样稿或单位写法，再按需参考。",
            "- 用户要求 Word 时，先形成结构正确的 Markdown 成稿，再调用 `src/scripts/generate_docx.py` 导出。",
            "",
            "## 文件索引",
            "",
            SKILL_FILE_INDEX,
            "",
            "## 任务路由",
            "",
            "根据本次请求读取对应文件（可一次读取多个）：",
            "",
            render_skill_routing_table(profile),
            "",
            "## 默认流程",
            "",
            SKILL_DEFAULT_FLOW,
            "",
            "## 相关 skill",
            "",
            "本入口负责「起草」。以下同源 skill（在 `skills/`，共用同一份 `prompts/` 主源，不复制规则）处理相邻能力：",
            "",
            "- `skills/docx-export`：成稿后导出机关版式 `.docx`、调字体/页边距/页码。",
            "- `skills/document-qa`：校验成稿章节是否齐全、层级是否规范、有无无依据表述。",
            "- `skills/offline-prompt-packager`：打包断网单机可用的离线提示词。",
            "- `skills/skill-build`：从 `prompts/` 主源重新生成并 `--check` 校验产物同步。",
            "",
            "## 文种目录",
            "",
            "下表中文种的规则文件位于 `prompts/doc-types/<id>-<文种>/spec.md`，字体方案位于 `prompts/font-profiles/<方案>.toml`，版式方案位于 `prompts/layout-profiles/<方案>.toml`。",
            "",
            format_doc_type_catalog(doc_types, profile.category_order),
            "",
        ]
    )
    return "\n".join(blocks).rstrip() + "\n"


def render_doc_type_reference(
    profile: Profile,
    doc_type: DocType,
    font_profiles: dict,
    layout_profiles: dict,
) -> str:
    """单文种自包含参考：起草要点＋撰写思路＋写作规则＋字体/版式＋模板，供 skill references/ 使用。"""
    spec = parse_doc_type_spec(doc_type.spec_path)
    blocks = [
        f"# {doc_type.display_name}",
        "",
        f"- 文种 ID：{doc_type.id}",
        f"- 分类：{doc_type.category}",
        f"- 适用说明：{doc_type.description}",
        "",
    ]
    if spec.drafting_inputs:
        blocks += ["## 起草要点（用户需提供什么）", "", spec.drafting_inputs, ""]
    if spec.writing_guide:
        blocks += ["## 撰写思路", "", spec.writing_guide, ""]
    blocks += [
        "## 写作规则",
        "",
        spec.writing_rules,
        "",
        "## 字体方案",
        "",
        render_font_profile_markdown(font_profiles[doc_type.font_profile_id]),
        "",
        "## 版式参数",
        "",
        render_layout_profile_markdown(layout_profiles[doc_type.layout_profile_id]),
        "",
        "## 版式要求",
        "",
        spec.layout_rules,
        "",
        "## 模板",
        "",
        "```markdown",
        spec.template,
        "```",
    ]
    return "\n".join(blocks).rstrip() + "\n"


def build_skill_references(profile: Profile, doc_types: list[DocType]) -> dict[str, str]:
    """生成自包含 skill 的 references/ 内容（相对 skill 根的路径 -> 内容），全部从 prompts/ 主源编译。"""
    font_profiles = load_font_profiles()
    layout_profiles = load_layout_profiles()
    refs: dict[str, str] = {}
    for section in profile.core_sections:
        refs[f"references/core-{section.title}.md"] = read_text(section.path)
    for doc_type in doc_types:
        refs[f"references/文种-{doc_type.display_name}.md"] = render_doc_type_reference(
            profile, doc_type, font_profiles, layout_profiles
        )
    return refs


def render_skill_markdown_reference_mode(profile: Profile, doc_types: list[DocType]) -> str:
    """references 模式的 SKILL.md：短入口 + 指向自包含 references/ 的清单（用于 dist/skill 包）。"""
    core_links = [f"- [{s.title}](./references/core-{s.title}.md)" for s in profile.core_sections]
    doc_links = [f"[{dt.display_name}](./references/文种-{dt.display_name}.md)" for dt in doc_types]
    blocks = [
        "---",
        f"name: {profile.skill_name}",
        f"description: {profile.skill_description}",
    ]
    if profile.skill_metadata:
        blocks.append(f"metadata: {json.dumps(profile.skill_metadata, ensure_ascii=False)}")
    blocks.extend(
        [
            "---",
            "",
            "<!-- Generated from prompts/ and src/adapters/skill/build.py. 自包含包，详情在 references/。 -->",
            "",
            f"# {profile.skill_title}",
            "",
            "把新闻素材、零散信息或既有文稿整理成规范的中文公文与正式材料，并可导出 Word。"
            "本文件只保留入口、流程和文种目录；详细规则按需读取 `references/` 下对应文件，不在此重复展开。",
            "",
            "核心原则：真实性优先于文采；不编造事实、政策依据、数字、文件号、会议结论；信息不足时保留占位符或标注待核实。"
            "完整边界见 `references/core-政策边界.md` 与 `references/core-事实核验与防编造.md`。",
            "",
            "## 调用方式",
            "",
            "- 先按需读取 `references/` 下相关文件，无需一次性加载全部。",
            "- 判断文种（见“文种目录”与 `references/core-处理流程.md` 的文种路由），再读对应 `references/文种-<文种>.md`。",
            "- 每个文种参考已含：起草要点（用户需提供什么）、撰写思路、写作规则、字体/版式方案、模板。",
            "- 用户要求 Word 时，先形成结构正确的 Markdown 成稿，再用导出脚本生成 `.docx`。",
            "",
            "## References（按需读取）",
            "",
            "共享规则：",
            "",
            *core_links,
            "",
            "各文种（每篇含起草要点/撰写思路/写作规则/字体版式/模板）：",
            "",
            "- " + "、".join(doc_links),
            "",
            "## 默认流程",
            "",
            SKILL_DEFAULT_FLOW_REFERENCE,
            "",
            "## 文种目录",
            "",
            format_doc_type_catalog(doc_types, profile.category_order),
            "",
        ]
    )
    return "\n".join(blocks).rstrip() + "\n"


def render_agent_yaml(profile: Profile) -> str:
    allow_implicit = "true" if profile.allow_implicit_invocation else "false"
    return "\n".join(
        [
            "# Generated from prompts/profiles/default.toml and src/adapters/skill/build.py.",
            "interface:",
            f"  display_name: {json.dumps(profile.agent_display_name, ensure_ascii=False)}",
            f"  short_description: {json.dumps(profile.agent_short_description, ensure_ascii=False)}",
            f"  default_prompt: {json.dumps(profile.agent_default_prompt, ensure_ascii=False)}",
            "",
            "policy:",
            f"  allow_implicit_invocation: {allow_implicit}",
            "",
        ]
    )


def render_offline_system_prompt(profile: Profile, doc_types: list[DocType], doc_type: DocType | None, include_examples: bool) -> str:
    font_profiles = load_font_profiles()
    layout_profiles = load_layout_profiles()
    parts = [
        profile.offline_system_preamble,
        "## 共享总规则\n\n" + render_core_sections(profile),
    ]

    if doc_type is None:
        parts.append(
            "\n".join(
                [
                    "## 当前未指定文种",
                    "- 你需要先根据任务内容判断文种，再选择最匹配的文种规则和模板。",
                    "",
                    "## 可用文种目录",
                    format_doc_type_catalog(doc_types, profile.category_order),
                    "",
                    "## 兜底骨架",
                    "```markdown",
                    read_text(profile.default_template),
                    "```",
                ]
            )
        )
        return "\n\n".join(part.strip() for part in parts if part.strip())

    doc_type_spec = parse_doc_type_spec(doc_type.spec_path)
    doc_blocks = [
        "## 当前文种",
        f"- 文种：{doc_type.display_name}",
        f"- 文种 ID：{doc_type.id}",
        f"- 分类：{doc_type.category}",
        f"- 适用说明：{doc_type.description}",
        f"- 规范文件：`{doc_type.spec_path.relative_to(REPO_ROOT).as_posix()}`",
        "",
        "## 当前文种强制约束",
        "```markdown",
        render_doc_type_guardrails(),
        "```",
        "",
        *(
            [
                "## 当前文种起草要点",
                "```markdown",
                doc_type_spec.drafting_inputs,
                "```",
                "",
            ]
            if doc_type_spec.drafting_inputs
            else []
        ),
        *(
            [
                "## 当前文种撰写思路",
                "```markdown",
                doc_type_spec.writing_guide,
                "```",
                "",
            ]
            if doc_type_spec.writing_guide
            else []
        ),
        "## 当前文种专项规则",
        "```markdown",
        doc_type_spec.writing_rules,
        "```",
        "",
        "## 当前文种字体要求",
        render_font_profile_markdown(font_profiles[doc_type.font_profile_id]),
        "",
        "## 当前文种版式参数",
        render_layout_profile_markdown(layout_profiles[doc_type.layout_profile_id]),
        "",
        "## 当前文种版式要求",
        "```markdown",
        doc_type_spec.layout_rules,
        "```",
        "",
        "## 当前文种模板",
        "```markdown",
        doc_type_spec.template,
        "```",
    ]
    parts.append("\n".join(doc_blocks))

    if include_examples and doc_type.examples_path:
        parts.append(
            "\n".join(
                [
                    "## 当前文种示例",
                    "```markdown",
                    read_text(doc_type.examples_path),
                    "```",
                ]
            )
        )

    return "\n\n".join(part.strip() for part in parts if part.strip())


def build_template_outputs(
    doc_types: list[DocType], fallback_template: pathlib.Path
) -> dict[pathlib.Path, str]:
    """构建 `assets/templates/` 下应落盘的模板内容（路径 -> 内容）。

    返回结构供 `src/adapters/skill/build.py` 统一写盘与 `--check` 校验，确保模板与
    各文种 `spec.md` 的“模板”章节、兜底骨架保持同步、不漂移。
    """
    outputs: dict[pathlib.Path, str] = {}
    for item in doc_types:
        outputs[ROOT_TEMPLATES_DIR / f"{item.id}.md"] = parse_doc_type_spec(item.spec_path).template + "\n"
    outputs[ROOT_TEMPLATES_DIR / "official-types-outline.md"] = read_text(fallback_template) + "\n"
    return outputs


# 目前无调用方，保留兼容，后续可单独清理。
def export_templates(doc_types: list[DocType], fallback_template: pathlib.Path) -> None:
    for path, content in build_template_outputs(doc_types, fallback_template).items():
        write_text(path, content)
