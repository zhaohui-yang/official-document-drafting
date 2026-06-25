# 标题编号与样例重生成 实施计划

> **历史计划（已完成）。** 本文件是 2026-04-04 的实施计划记录，相关改动已落地。复选框标记为已完成 `[x]`，仅作过程留档。
> 面向执行者：可配合 superpowers:subagent-driven-development 或 superpowers:executing-plans 按任务逐项推进；步骤用复选框（`- [ ]`）跟踪。

**目标：** 让正文实质性小标题默认采用带编号的标题，并按「首行缩进两字符」的语义编排，再据此重生成受影响的样例。

**架构：** 先统一共享的写作与版式规则，使主源表述无歧义；再对齐高频文种模板与 Word 导出器，使 Markdown 结构与 `.docx` 渲染产生一致的视觉约定；最后重生成代表性样例，并重跑结构与导出校验。

**技术栈：** Markdown 提示词主源、Python 导出器与测试、git 跟踪的样例资产。

---

### 任务一：锁定共享规则与影响范围

**文件：**
- 修改：`prompts/core/style.md`
- 修改：`prompts/core/layout.md`
- 修改：`docs/references/style-rules.md`
- 修改：`docs/references/layout-rules.md`

- [x] **步骤 1：更新共享样式规则，明确编号式实质性标题**

补充或收紧表述：正文并列实质性板块默认用 `一、二、三、四`，下级标题默认用 `（一）（二）（三）`；`标题 / 主送单位 / 落款 / 附注 / 版记 / 附件` 不纳入正文编号体系。

- [x] **步骤 2：更新共享版式规则，明确标题缩进语义**

补充表述：正文一级标题在文本中体现「左起空两格」的常见写法；导出 Word 时优先通过标题段落格式体现，而非用字面空格。

- [x] **步骤 3：在面向读者的 references 中镜像同一规则**

更新 `docs/references/style-rules.md` 与 `docs/references/layout-rules.md`，使读者文档与主源规则一致。

- [x] **步骤 4：校验规则表述内部一致**

执行：`rg -n "左起空两格|一、二、三|正文编号体系|主送单位|落款|附注|版记|附件" prompts/core references`

预期：共享规则与 references 中出现一致表述，无相互矛盾的指引。

### 任务二：让高频模板对齐共享规则

**文件：**
- 修改：`prompts/doc-types/report-报告/spec.md`
- 修改：`prompts/doc-types/summary-工作总结/spec.md`
- 修改：`prompts/doc-types/presentation-汇报材料/spec.md`
- 修改：`prompts/doc-types/special-report-情况专报/spec.md`
- 修改：`prompts/doc-types/circular-通报/spec.md`
- 修改：`assets/templates/report.md`
- 修改：`assets/templates/summary.md`
- 修改：`assets/templates/presentation.md`
- 修改：`assets/templates/circular.md`

- [x] **步骤 1：将提示词 spec 中裸写的实质性板块标题改为编号标题**

把 `## 基本情况` 之类的实质性正文板块改写为 `## 一、基本情况` 形式（元信息或版记类不改）。

- [x] **步骤 2：在兼容模板中应用同样的改写**

更新 `assets/templates/` 下对应文件，使兜底样例与直接读取的模板产生一致的标题样式。

- [x] **步骤 3：保留例外项不动**

`标题 / 主送单位 / 落款 / 附注 / 版记 / 附件` 保持不编号；纪要的 `会议认为，……` / `会议决定，……` 保留为正文提示语，不改成同名标题。

- [x] **步骤 4：校验模板标题一致性**

执行：`rg -n "^## (基本情况|工作开展情况|工作进展|存在问题|下一步建议|下一步打算|下一步措施)$|^## [一二三四五六七八九十]+、" prompts/doc-types assets/templates`

预期：高频实质性板块以编号形式出现；元信息/版记类标题保持不编号。

### 任务三：更新导出器行为并补测试

**文件：**
- 修改：`src/scripts/generate_docx.py`
- 修改：`tests/test_generate_docx.py`

- [x] **步骤 1：为编号式实质性标题渲染补一个针对性测试**

新增或扩展测试，渲染如下 Markdown 并断言标题走标题渲染路径、应用编号正文标题的段落格式：

```markdown
## 一、基本情况

　　正文示例。
```

- [x] **步骤 2：实现最小的标题格式改动**

调整导出器，使实质性正文标题保留编号文字并应用新的段落格式约定，且不影响标题、主送单位、落款、附注、版记的处理。

- [x] **步骤 3：重跑导出器测试**

执行：`python3 -m unittest discover -s tests -p 'test_generate_docx.py'`

预期：全部测试通过。

- [x] **步骤 4：共享规则变更后重建生成产物**

执行：`python3 src/scripts/build_all.py`

预期：生成产物刷新成功。

### 任务四：按新规则重生成代表性样例

**文件：**
- 修改或重生成：`demo/online/` 下文件
- 修改或重生成：`demo/offline/` 下镜像样例（若受新规则影响）
- 修改：`demo/README.md`
- 修改：`README.md`（仅当样例描述措辞需要更新时）

- [x] **步骤 1：将样例 Markdown 标题改为新的编号样式**

对含实质性板块标题的代表性样例，将裸标题改为编号标题。

- [x] **步骤 2：重新导出受影响的 `.docx`**

对每个受影响样例使用既有导出命令，使 Markdown 与 Word 输出保持一致。

- [x] **步骤 3：在可用处重跑结构校验**

执行：

```bash
python3 src/renderers/validate.py report <报告-md>
python3 src/renderers/validate.py notice <通知-md>
python3 src/renderers/validate.py request <请示-md>
```

预期：各校验器报告 `[OK]`。

- [x] **步骤 4：最终核对**

执行：

```bash
git diff --check
git status --short
```

预期：无空白错误；变更文件仅反映既定的规则/模板/样例重生成范围。
