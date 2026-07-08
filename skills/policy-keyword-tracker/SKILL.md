---
name: policy-keyword-tracker
description: 围绕一个关键词/主题（如「创新药」「低空经济」「数据要素」）检索各中央国家部委的相关政策、措施与动态，汇总成一份《情况专报》。Use when 用户想跟踪某一主题在各部委的政策口径、做专题政策梳理与研判。采集→核实→按「情况专报」文种成稿，可导出 Word。文体固定为情况专报。
---

# 关键词政策跟踪

给定一个关键词或主题，跨中央国家部委官网检索该主题的**相关政策、措施、规划与动态**，汇总成一份《情况专报》，用于专题政策梳理与研判。与 `ministry-news-daily`（按日汇总全量动态）互补：本 skill 是**按主题纵向聚焦**。

## 文件索引

```
prompts/doc-types/special-report-情况专报/spec.md   # 「情况专报」文种的写作规则、撰写思路与模板（成稿依据）
prompts/core/doc-type-guardrails.md                 # 防编造强制约束（采集核实的底线）
skills/_common/web-collection.md               # 采集类共享约束（信源/访问/保存/降级/底线）
src/scripts/generate_docx.py                            # 成稿导出机关版式 .docx（--doc-type 情况专报）
样例/online/policy-keyword-tracker-创新药政策跟踪/   # 完整样例：task / materials / 成稿 / README
```

## 共享约束（硬性）

采集类 skill 的硬性底线：只用只读 `WebSearch` / `WebFetch`、逐站串行低频、遵守 robots 与版权、有来源才写绝不编造。完整条款（信源基线/访问约束/保存路径/离线降级/边界底线）见 `../_common/web-collection.md`，冲突时以该文件为准。按单 skill 目录 symlink/拷贝安装本 skill 时，须把 `skills/_common/` 一并链入同一父目录，否则该相对路径失效（见 `skills/README.md`「约定」）。本 skill 的任务差异：

- **信源侧重**：按主题对口部委——中国政府网 `www.gov.cn`（政策库、最新文件、部门文件检索），以及与主题相关的对口部委官网，例如「创新药」对应：国家药监局、国家卫生健康委、国家医保局、科技部、工业和信息化部、国家发展改革委等。
- **检索方式**：先用 `WebSearch` 以「关键词 + 部委/政策」命中具体页面，再用 `WebFetch` 取该页，减少无谓请求。
- **子目录**：`policy-tracking/<关键词>/`（如 `.../policy-tracking/创新药/`），按主题归档；同一主题多次跟踪 `-vNN` 递增、不覆盖，便于对比政策演进。
- **成稿命名**：`YYYYMMDD-关于<关键词>相关政策动态的情况专报-vNN.{md,docx}`。
- **离线降级**：人工围绕关键词检索素材后，用 [dist/offline/default/doc-types/special-report-情况专报/prompt.md](../../dist/offline/default/doc-types/special-report-%E6%83%85%E5%86%B5%E4%B8%93%E6%8A%A5/prompt.md)成稿。
- **校验**：成稿后可转 `document-qa` 校验（`src/scripts/check_sections.py special-report`）。

## 默认流程

1. **定主题与口径**：确认关键词（如「创新药」）、时间范围（如近 1–3 年）、关注角度（审评审批、医保支付、产业支持等）。
2. **检索**：围绕关键词逐个对口部委检索相关政策与动态，逐条记录「发布机关 + 政策标题 + 核心要点 + 发布日期 + 来源 URL」，落成 `materials.md`。
3. **核实**：每条都要有可追溯来源 URL；**检索不到或无法确认的，宁可不写，绝不编造**机关、数字、文号、日期（见 `doc-type-guardrails.md`）；存疑项标「待核实」。
4. **成稿（情况专报）**：按 `prompts/doc-types/special-report-情况专报/spec.md` 谋篇——`标题`（《关于「关键词」相关政策动态的情况专报》）、`报送对象`、`一、事项概况`（主题与政策总体格局）、`二、最新进展`（按部委/时间梳理最新政策，括注来源）、`三、风险研判`（趋势、影响、待关注问题，与事实分开）、`四、工作建议`，结尾「特此报告。」。
5. **导出（可选）**：

```bash
python3 src/scripts/generate_docx.py <成稿>.md -o <成稿>.docx --doc-type 情况专报
```
