---
name: official-document-drafting
description: 起草、改写、润色、扩写、压缩、规范并导出中文公文与行政正式文本。Use when the user asks to write, revise, summarize, standardize, or convert 公文、决议、决定、命令、公告、公报、通告、意见、通知、通报、报告、请示、批复、议案、函、纪要，以及总结、简报、新闻简报、信息专报、舆情专报、汇报材料、讲话稿、工作方案、实施方案、回复函等正式机关或单位文稿，尤其适用于需要固定文种结构、正式机关语气、统一口径、规范标题、层级编号、落款日期、模板套用、Word docx 导出，或将当前新闻材料整理为正式公文和正式汇报材料的场景。
metadata: {"openclaw": {"homepage": "https://github.com/zhaohui-yang/official-document-drafting", "requires": {"bins": ["bash", "python3", "curl"]}}}
---

<!-- Generated from prompts/ and adapters/skill/build.py. -->

# 公文写作

`official-document-drafting` 的统一入口：把新闻素材、零散信息或既有文稿整理成规范的中文公文与正式材料，并可导出 Word。本文件只保留入口、任务路由、默认流程和文种目录；详细规则按需读取 `prompts/core/*.md` 和对应文种 `spec.md`，不在此重复展开。

核心原则：真实性优先于文采；不编造事实、政策依据、数字、文件号、会议结论；信息不足时保留占位符或标注待核实。完整边界见 `prompts/core/policy.md` 与 `prompts/core/doc-type-guardrails.md`。

## 调用方式

- 先按下方“任务路由”读取本次任务需要的共享规则，无需一次性加载全部规则。
- 判断当前任务最匹配的文种（见“文种目录”与 `prompts/core/workflow.md` 的文种路由规则）。
- 文种确定后，先应用 `prompts/core/doc-type-guardrails.md`，再读取对应文种目录的 `spec.md`，按其中“写作规则”“版式要求”“模板”章节处理，并按 `meta.toml` 中的 `font_profile` 和 `layout_profile` 应用字体与版式参数。
- 如存在 `examples.md`，并且用户明确要求更贴近既有样稿或单位写法，再按需参考。
- 用户要求 Word 时，先形成结构正确的 Markdown 成稿，再调用 `scripts/generate_docx.py` 导出。

## 文件索引

```
official-document-drafting/
├── SKILL.md                       # 本文件：入口、任务路由、默认流程、文种目录（由 prompts/ 生成）
├── prompts/
│   ├── core/                      # 共享总规则主源（在线按需读取，离线提示词内联）
│   │   ├── policy.md              # 政策与交付边界
│   │   ├── doc-type-guardrails.md # 防编造强制约束
│   │   ├── workflow.md            # 文种判断、文种路由规则、保存与命名约定
│   │   ├── style.md               # 语言风格、标题层级、正文结尾、落款、主送/附件/版记
│   │   ├── layout.md              # 基线版式与 Word 导出约定
│   │   └── fallback-template.md   # 无独立文种模板时的兜底骨架
│   ├── doc-types/<id>-<文种>/     # 各文种 spec.md（写作规则/版式要求/模板）、meta.toml、examples.md
│   ├── font-profiles/*.toml       # 字体方案
│   ├── layout-profiles/*.toml     # 版式参数方案
│   └── profiles/*.toml            # 在线/离线构建 profile
├── scripts/generate_docx.py       # Markdown 成稿导出 .docx（--doc-type 自动套用字体与版式）
├── adapters/skill/build.py        # 由 prompts/ 生成 SKILL.md 等在线产物（--check 校验同步）
└── references/                    # 面向读者的说明文档，操作性规则以 prompts/core 为准
```

## 任务路由

根据本次请求读取对应文件（可一次读取多个）：

| 请求类型 | 读取 |
| --- | --- |
| 任何起草、改写、润色前的事实与政策底线 | `prompts/core/policy.md`、`prompts/core/doc-type-guardrails.md` |
| 文种判断、行文方向、文种路由规则、保存与命名约定 | `prompts/core/workflow.md` |
| 撰写思路与语域 | `prompts/core/drafting-thinking.md` |
| 语言风格、标题与层级编号、正文与结尾、落款、主送/附件/版记 | `prompts/core/style.md` |
| 基线版式、字体字号、Word 导出参数与脚本约定 | `prompts/core/layout.md` |
| 具体文种的写作规则、版式要求、模板 | 下方“文种目录”对应的 `spec.md` |
| 字体与版式精确参数 | `prompts/font-profiles/<方案>.toml`、`prompts/layout-profiles/<方案>.toml` |
| 没有独立文种模板时的兜底骨架 | `prompts/core/fallback-template.md` |

## 默认流程

1. 先读事实与政策底线（`policy.md`、`doc-type-guardrails.md`）；任何起草都以真实性优先于文采。
2. 判断文种：先判断是否法定公文 15 种，否则落到常见正式材料；判断行文方向（上行/下行/平行/公开）、发文主体、主送对象、事项性质与时间要求。详细文种路由规则见 `prompts/core/workflow.md`。
3. 按任务类型从“任务路由”读取语言（`style.md`）、版式（`layout.md`）等共享规则，只加载本次需要的部分，不一次性全量加载。
4. 读取目标文种 `spec.md` 的“写作规则”“版式要求”“模板”，并按 `meta.toml` 的 `font_profile`、`layout_profile` 应用字体与版式；无独立模板时退回 `prompts/core/fallback-template.md`。
5. 默认直接输出最终 Markdown 成稿；用户只要求提纲时输出提纲。信息不足时保留 `[发文单位]`、`[日期]`、`[待核实]` 等占位符，不虚构。
6. 需要 Word 时，确认 Markdown 结构正确后调用 `scripts/generate_docx.py`，按文种 `meta.toml` 的字体与版式方案导出。
7. 成稿前校对错别字、病句、标点、数字、日期、称谓和机构名称。

## 相关 skill

本入口负责「起草」。以下同源 skill（在 `skills/`，共用同一份 `prompts/` 主源，不复制规则）处理相邻能力：

- `skills/docx-export`：成稿后导出机关版式 `.docx`、调字体/页边距/页码。
- `skills/document-qa`：校验成稿章节是否齐全、层级是否规范、有无无依据表述。
- `skills/offline-prompt-packager`：打包断网单机/弱模型可用的离线提示词。
- `skills/skill-build`：从 `prompts/` 主源重新生成并 `--check` 校验产物同步。

## 文种目录

下表中文种的规则文件位于 `prompts/doc-types/<id>-<文种>/spec.md`，字体方案位于 `prompts/font-profiles/<方案>.toml`，版式方案位于 `prompts/layout-profiles/<方案>.toml`。

### 法定公文

- `announcement` / 公告 / 别名：公告 / 字体方案：`official-standard` / 版式方案：`official-standard` / 向国内外宣布重要事项或者法定事项。
- `approval` / 批复 / 别名：批复 / 字体方案：`official-standard` / 版式方案：`official-standard` / 用于答复下级机关请示事项。
- `circular` / 通报 / 别名：通报 / 字体方案：`official-standard` / 版式方案：`official-standard` / 用于表彰先进、批评错误或传达重要情况。
- `communique` / 公报 / 别名：公报 / 字体方案：`official-standard` / 版式方案：`official-standard` / 公开发布重要决定、重大事项或重要会议情况。
- `decision` / 决定 / 别名：决定 / 字体方案：`official-standard` / 版式方案：`official-standard` / 对重要事项作出部署、奖惩、处理或调整。
- `letter` / 函 / 别名：函 / 字体方案：`official-standard` / 版式方案：`official-standard` / 用于平行机关或不相隶属机关之间商洽、询问、答复。
- `minutes` / 纪要 / 别名：纪要、会议纪要 / 字体方案：`official-standard` / 版式方案：`official-standard` / 用于记载会议主要情况和议定事项。
- `motion` / 议案 / 别名：议案 / 字体方案：`official-standard` / 版式方案：`official-standard` / 具有特定法定主体和程序要求的议案。
- `notice` / 通知 / 别名：通知 / 字体方案：`official-standard` / 版式方案：`official-standard` / 用于发布、传达、转发事项或安排部署工作。
- `opinion` / 意见 / 别名：意见 / 字体方案：`official-standard` / 版式方案：`official-standard` / 对重要问题提出见解和处理办法。
- `order` / 命令（令） / 别名：命令、令、命令令 / 字体方案：`official-standard` / 版式方案：`official-standard` / 用于公布规章、施行重大强制性措施等。
- `public-notice` / 通告 / 别名：通告 / 字体方案：`official-standard` / 版式方案：`official-standard` / 在一定范围内公布应当遵守或者周知的事项。
- `report` / 报告 / 别名：报告 / 字体方案：`official-standard` / 版式方案：`official-standard` / 用于向上级汇报工作、反映情况、回复询问。
- `request` / 请示 / 别名：请示 / 字体方案：`official-standard` / 版式方案：`official-standard` / 用于向上级请求指示、批准。
- `resolution` / 决议 / 别名：决议 / 字体方案：`official-standard` / 版式方案：`official-standard` / 会议讨论通过的重要决策事项。

### 常见正式材料

- `briefing` / 简报 / 别名：简报、信息简报、新闻简报 / 字体方案：`internal-readable` / 版式方案：`internal-readable` / 用于简要报送动态、会议情况、阶段成果和新闻整理。
- `presentation` / 汇报材料 / 别名：汇报材料、汇报稿 / 字体方案：`internal-readable` / 版式方案：`internal-readable` / 用于向领导、检查组或上级进行阶段性工作汇报。
- `reply` / 回复函 / 别名：回复函、复函 / 字体方案：`official-standard` / 版式方案：`official-standard` / 用于对来函、来文、咨询事项作出正式回复。
- `special-report` / 情况专报 / 别名：情况专报、信息专报、舆情专报、专报 / 字体方案：`internal-readable` / 版式方案：`internal-readable` / 用于向领导或上级报送专题信息、风险情况和舆情态势。
- `speech` / 讲话稿 / 别名：讲话稿、发言稿 / 字体方案：`speech-readable` / 版式方案：`speech-readable` / 用于领导讲话、会议发言、动员部署和总结点评。
- `summary` / 工作总结 / 别名：工作总结、总结、总结材料 / 字体方案：`internal-readable` / 版式方案：`internal-readable` / 用于阶段性复盘、年度总结、专项工作总结。
- `work-plan` / 工作方案 / 别名：工作方案、实施方案、方案 / 字体方案：`internal-readable` / 版式方案：`internal-readable` / 用于专项行动、阶段性工作、制度落地和项目推进。
