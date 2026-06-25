---
name: official-document-drafting
description: 起草、改写、润色、扩写、压缩、规范并导出中文公文与行政正式文本。Use when the user asks to write, revise, summarize, standardize, or convert 公文、决议、决定、命令、公告、公报、通告、意见、通知、通报、报告、请示、批复、议案、函、纪要，以及总结、简报、新闻简报、信息专报、舆情专报、汇报材料、讲话稿、工作方案、实施方案、回复函等正式机关或单位文稿，尤其适用于需要固定文种结构、正式机关语气、统一口径、规范标题、层级编号、落款日期、模板套用、Word docx 导出，或将当前新闻材料整理为正式公文和正式汇报材料的场景。
metadata: {"openclaw": {"homepage": "https://github.com/zhaohui-yang/official-document-drafting", "requires": {"bins": ["bash", "python3", "curl"]}}}
---

<!-- Generated from prompts/ and src/adapters/skill/build.py. 自包含包，详情在 references/。 -->

# 公文写作

把新闻素材、零散信息或既有文稿整理成规范的中文公文与正式材料，并可导出 Word。本文件只保留入口、流程和文种目录；详细规则按需读取 `references/` 下对应文件，不在此重复展开。

核心原则：真实性优先于文采；不编造事实、政策依据、数字、文件号、会议结论；信息不足时保留占位符或标注待核实。完整边界见 `references/core-政策边界.md` 与 `references/core-事实核验与防编造.md`。

## 调用方式

- 先按需读取 `references/` 下相关文件，无需一次性加载全部。
- 判断文种（见“文种目录”与 `references/core-处理流程.md` 的文种路由），再读对应 `references/文种-<文种>.md`。
- 每个文种参考已含：起草要点（用户需提供什么）、撰写思路、写作规则、字体/版式方案、模板。
- 用户要求 Word 时，先形成结构正确的 Markdown 成稿，再用导出脚本生成 `.docx`。

## References（按需读取）

共享规则：

- [政策边界](./references/core-政策边界.md)
- [事实核验与防编造](./references/core-事实核验与防编造.md)
- [处理流程](./references/core-处理流程.md)
- [撰写思路与语域](./references/core-撰写思路与语域.md)
- [语言与输出](./references/core-语言与输出.md)
- [版式与导出](./references/core-版式与导出.md)

各文种（每篇含起草要点/撰写思路/写作规则/字体版式/模板）：

- [公告](./references/文种-公告.md)、[批复](./references/文种-批复.md)、[简报](./references/文种-简报.md)、[通报](./references/文种-通报.md)、[公报](./references/文种-公报.md)、[决定](./references/文种-决定.md)、[函](./references/文种-函.md)、[纪要](./references/文种-纪要.md)、[议案](./references/文种-议案.md)、[通知](./references/文种-通知.md)、[意见](./references/文种-意见.md)、[命令（令）](./references/文种-命令（令）.md)、[汇报材料](./references/文种-汇报材料.md)、[通告](./references/文种-通告.md)、[回复函](./references/文种-回复函.md)、[报告](./references/文种-报告.md)、[请示](./references/文种-请示.md)、[决议](./references/文种-决议.md)、[情况专报](./references/文种-情况专报.md)、[讲话稿](./references/文种-讲话稿.md)、[工作总结](./references/文种-工作总结.md)、[工作方案](./references/文种-工作方案.md)

## 默认流程

1. 先读 `references/core-政策边界.md` 与 `references/core-事实核验与防编造.md` 的事实与政策底线；任何起草都以真实性优先于文采。
2. 判断文种：先判断是否法定公文 15 种，否则落到常见正式材料；判断行文方向（上行/下行/平行/公开）、发文主体、主送对象、事项性质与时间要求。详细文种路由见 `references/core-处理流程.md`。
3. 按需读取 `references/core-语言与输出.md`、`references/core-版式与导出.md`、`references/core-撰写思路与语域.md` 等共享规则，只加载本次需要的部分，不一次性全量加载。
4. 读取对应 `references/文种-<文种>.md`，其中已含起草要点、撰写思路、写作规则、字体/版式方案与模板。
5. 默认直接输出最终 Markdown 成稿；用户只要求提纲时输出提纲。信息不足时保留 `[发文单位]`、`[日期]`、`[待核实]` 等占位符，不虚构。
6. 需要 Word 时，确认 Markdown 结构正确后用仓库内的导出脚本 `src/scripts/generate_docx.py`，按文种字体与版式方案导出。
7. 成稿前校对错别字、病句、标点、数字、日期、称谓和机构名称。

## 文种目录

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
