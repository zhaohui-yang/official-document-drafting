---
name: ministry-news-daily
description: 浏览中央国家部委官网的最新动态，汇总成一份每日《报告》，用于快速了解国家大事与各部委政策要求。Use when the user wants 部委/政府每日动态、政务新闻日报、了解国家大事、各部委最新政策与要求的汇总报告。采集→核实→按「报告」文种成稿，可导出 Word。文体固定为报告。
---

# 部委新闻动态日报

从**中央国家部委官网**采集最新政务动态（新闻、政策发布、通知公告），汇总成一份当日《报告》，帮助快速掌握国家大事和各部委的最新要求。这是「公文写作」skill 的一个应用流程：输入是实时检索到的部委动态，输出是「报告」文种的成稿。

## 文件索引

```
prompts/doc-types/report-报告/spec.md       # 「报告」文种的写作规则、撰写思路与模板（成稿依据）
prompts/core/doc-type-guardrails.md         # 防编造强制约束（采集核实的底线）
skills/_common/web-collection.md               # 采集类共享约束（信源/访问/保存/降级/底线）
src/scripts/generate_docx.py                    # 成稿导出机关版式 .docx（--doc-type 报告）
样例/online/ministry-news-daily-部委动态日报/  # 完整样例：task / materials / 成稿 / README
```

## 共享约束（硬性）

采集类 skill 的硬性底线：只用只读 `WebSearch` / `WebFetch`、逐站串行低频、遵守 robots 与版权、有来源才写绝不编造。完整条款（信源基线/访问约束/保存路径/离线降级/边界底线）见 `../_common/web-collection.md`，冲突时以该文件为准。按单 skill 目录 symlink/拷贝安装本 skill 时，须把 `skills/_common/` 一并链入同一父目录，否则该相对路径失效（见 `skills/README.md`「约定」）。本 skill 的任务差异：

- **信源侧重**：按日全量部委动态——中国政府网 `www.gov.cn`（国务院、政策、新闻、最新文件）及各部委官网，例如：发展改革委、财政部、工业和信息化部、商务部、教育部、科技部、人力资源社会保障部、生态环境部、农业农村部、交通运输部、住房城乡建设部、国家卫生健康委、国家市场监督管理总局等。
- **采集规模**：默认覆盖当日或最近 1–2 个工作日，6–10 条为宜。
- **子目录**：`news-reports/`（高频日报可再按 `news-reports/YYYYMMDD/` 分日）。
- **成稿命名**：`YYYYMMDD-中央国家部委政务动态每日报告-vNN.{md,docx}`。
- **研判分段**：研判性内容（`需要关注的问题`、`下一步建议`）要与已核实事实分段，并明示是判断而非新事实。
- **离线降级**：人工采集素材后，用 [dist/offline/default/doc-types/report-报告/prompt.md](../../dist/offline/default/doc-types/report-%E6%8A%A5%E5%91%8A/prompt.md)成稿。
- **校验**：需要校验成稿结构时，转 `document-qa` skill（`src/scripts/check_sections.py report`）。

## 默认流程

1. **采集**：用 WebSearch / WebFetch 浏览上述官网最近发布，逐条记录「发布机关 + 标题 + 核心内容一句话 + 发布日期 + 来源 URL」。默认覆盖当日或最近 1–2 个工作日，6–10 条为宜。
2. **核实**：每条都要有可追溯的来源 URL；**检索不到或无法确认的，宁可不写，绝不编造**机关、数字、文号、日期（见 `doc-type-guardrails.md`）。先把核实过的事实落成 `materials.md` 式的「事实摘要」。
3. **成稿（报告文种）**：按 `prompts/doc-types/report-报告/spec.md` 的撰写思路谋篇——
   - 标题：《关于〔日期〕中央国家部委政务动态的报告》；主送写 `[报送对象]：` 占位。
   - 开头：「现将〔日期〕中央国家部委主要政务动态报告如下」。
   - 主体：`一、总体情况`（概述当日动态总体特征）→ `二、重点动态`（按部委分条，每条点明机关、事项、要点，括注或脚注标来源）→ `三、需要关注的问题` → `四、下一步关注建议`。
   - 结尾：`特此报告。`；落款与日期按 `[发文单位]`、当日日期占位。
4. **导出（可选）**：

```bash
python3 src/scripts/generate_docx.py <成稿>.md -o <成稿>.docx --doc-type 报告
```
