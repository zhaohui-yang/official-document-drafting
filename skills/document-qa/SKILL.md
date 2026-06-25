---
name: document-qa
description: 对已成稿的中文公文做结构与质量校验。Use when the user wants to check/review/lint a 公文 draft——校验章节是否齐全、标题层级是否跳级或混编、篇幅与标题深度是否匹配、一是/二是 是否被误用为正式标题、文种是否用对、结尾用语是否匹配、有无未经提供的事实。是「检查」而非「起草」。
---

# 公文质检

对**已成稿**的中文公文做结构与质量校验。和「起草」相反方向：不生成内容，只检查稿子哪里不齐、哪里不规范。

## 文件索引

```
src/scripts/check_sections.py        # 章节齐全度 + 层级结构 + 篇幅自动校验（CLI）
docs/references/style-rules.md         # 「质量检查清单」与行文规范（人工核对项）
prompts/core/doc-type-guardrails.md  # 防编造强制约束（事实性核对的依据）
prompts/doc-types/<id>-<文种>/spec.md  # 各文种应有板块与职责（结构核对依据）
```

## 自动校验（脚本）

`src/scripts/check_sections.py` 覆盖全部 22 个文种（与 `assets/templates/` 下 22 份文种模板一一对应），自动检查：

- **章节齐全度**：缺少约定板块直接报错。
- **层级结构**：标题跳级、`一是/二是/三是` 被当正式标题、10 页以内却下钻到三级标题等给出提醒。
- **内容机检**：占位符残留、结尾用语是否与文种匹配。
- **格式红线**（GB/T 9704）：发文字号是否用六角括号〔〕且不加「第」不补零、成文日期月日是否补零、标题是否误加句号、是否残留「主题词」。
- `--strict-structure` 把结构提醒按错误处理。

```bash
python3 src/scripts/check_sections.py notice 成稿.md
python3 src/scripts/check_sections.py report 成稿.md --strict-structure
```

## 人工核对（清单）

脚本覆盖不到的语义项，按 `docs/references/style-rules.md` 的「质量检查清单」逐条核对：

- 文种是否正确、行文方向是否合理
- 标题是否单一聚焦、有无不必要标点或回行不当
- 段落层级是否清楚、结尾用语是否匹配文种
- 落款和日期是否齐全、日期书写是否规范
- 是否出现未经用户提供的事实、数据、依据（对照 `prompts/core/doc-type-guardrails.md`）

## 默认流程

1. 判断稿子文种 → 先跑 `check_sections.py <文种> 成稿.md` 拿结构结论（22 个文种均覆盖）。
2. 再按「质量检查清单」做语义和事实核对。
3. 输出「缺什么板块 / 哪里结构不规范 / 哪些表述疑似无依据」，并指明对应主源规则。
4. 只报问题与依据，不擅自改写；需要修订时交回「公文写作」skill。

## 边界

- 脚本覆盖全部 22 个文种的**必备章节**，但只校验结构、不判断语义；内容是否成立仍需人工核对清单。
- `REQUIRED_SECTIONS` 只收必备板块，`（可选）` 板块（附件、附注等）不计；章节名以模板主源 `spec.md` 为准，若脚本与模板脱节，以 `spec.md` 为准并视为脚本待补项（`tests/test_template_sections.py` 守护两者同步）。
