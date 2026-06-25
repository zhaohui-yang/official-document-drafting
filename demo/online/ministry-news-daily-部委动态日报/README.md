# online / 部委动态日报（ministry-news-daily skill）

这是 `ministry-news-daily` skill 的完整样例：浏览中央国家部委官网最新动态，汇总成一份当日《报告》，用于了解国家大事。**文体为报告。**

> **占位示例：** 本样例用占位内容演示「采集 → 提炼 → 成稿 → 导出」的完整链路，**不含真实新闻数据**。真实运行时由 skill 按「访问约束」联网检索，把占位替换为带来源 URL 的真实动态。

文件说明：

- [task.md](./task.md)：任务说明（在线浏览部委官网，目标文种=报告）。
- [materials.md](./materials.md)：采集底稿，逐条记录「发布机关 + 标题 + 要点 + 日期 + 来源 URL」。
- [20260624-中央国家部委政务动态每日报告-v01.md](./20260624-%E4%B8%AD%E5%A4%AE%E5%9B%BD%E5%AE%B6%E9%83%A8%E5%A7%94%E6%94%BF%E5%8A%A1%E5%8A%A8%E6%80%81%E6%AF%8F%E6%97%A5%E6%8A%A5%E5%91%8A-v01.md)：按报告文种成稿的 Markdown 日报。
- `20260624-中央国家部委政务动态每日报告-v01.docx`：用导出器生成的 Word 文件。

推荐流程：

1. 先读 [task.md](./task.md) 明确场景与成稿要求。
2. 调用 `ministry-news-daily` skill，按其「访问约束」低频、串行检索各部委官网，把动态逐条落成 [materials.md](./materials.md) 式的事实摘要（每条带来源 URL，无法核实的标「待核实」）。
3. 按 [prompts/doc-types/report-报告/spec.md](../../../prompts/doc-types/report-%E6%8A%A5%E5%91%8A/spec.md) 的报告文种谋篇成稿（基本情况—重点动态—需要关注的问题—下一步关注建议—特此报告）。
4. 导出 `.docx`。

> 板块说明：政务动态日报属**信息汇总类报告**，板块为「总体情况—重点动态—需要关注的问题—下一步关注建议」，与 `check_sections.py` 内置「工作报告」的必备板块（基本情况/工作开展情况/存在问题/下一步建议）不同，因此不套用 `check_sections report` 校验；真实性核对仍以 `prompts/core/doc-type-guardrails.md` 为准（逐条附来源、无法核实标「待核实」）。

从当前 Markdown 成稿重新导出 `.docx`：

```bash
python3 scripts/generate_docx.py \
  "demo/online/ministry-news-daily-部委动态日报/20260624-中央国家部委政务动态每日报告-v01.md" \
  -o "demo/online/ministry-news-daily-部委动态日报/20260624-中央国家部委政务动态每日报告-v01.docx" \
  --doc-type 报告
```
