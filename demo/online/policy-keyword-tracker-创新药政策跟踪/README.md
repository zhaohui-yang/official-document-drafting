# online / 关键词政策跟踪（policy-keyword-tracker skill）

这是 `policy-keyword-tracker` skill 的完整样例：围绕一个关键词（本例为「创新药」），跨中央国家部委检索相关政策，汇总成一份《情况专报》。**文体为情况专报。**

> **占位示例：** 本样例用占位内容演示「定主题 → 围绕关键词检索 → 提炼 → 成稿 → 导出」的完整链路，**不含真实政策数据**。真实运行时由 skill 按「访问约束」联网检索，把占位替换为带来源 URL 的真实政策条目。

文件说明：

- [task.md](./task.md)：任务说明（关键词=创新药，目标文种=情况专报）。
- [materials.md](./materials.md)：采集底稿，逐条记录「发布机关 + 政策标题 + 要点 + 日期 + 来源 URL」。
- [20260624-关于创新药相关政策动态的情况专报-v01.md](./20260624-%E5%85%B3%E4%BA%8E%E5%88%9B%E6%96%B0%E8%8D%AF%E7%9B%B8%E5%85%B3%E6%94%BF%E7%AD%96%E5%8A%A8%E6%80%81%E7%9A%84%E6%83%85%E5%86%B5%E4%B8%93%E6%8A%A5-v01.md)：按情况专报文种成稿的 Markdown 专报。
- `20260624-关于创新药相关政策动态的情况专报-v01.docx`：用导出器生成的 Word 文件。

推荐流程：

1. 先读 [task.md](./task.md)，确认关键词、时间范围与关注角度。
2. 调用 `policy-keyword-tracker` skill，按其「访问约束」围绕「创新药」逐个对口部委低频、串行检索，把政策逐条落成 [materials.md](./materials.md) 式的事实摘要（每条带来源 URL，无法核实标「待核实」）。
3. 按 [prompts/doc-types/special-report-情况专报/spec.md](../../../prompts/doc-types/special-report-%E6%83%85%E5%86%B5%E4%B8%93%E6%8A%A5/spec.md) 的情况专报文种谋篇成稿（事项概况—最新进展—风险研判—工作建议），研判与建议与已核实事实分段。
4. 导出 `.docx`。

从当前 Markdown 成稿重新导出 `.docx`：

```bash
python3 scripts/generate_docx.py \
  "demo/online/policy-keyword-tracker-创新药政策跟踪/20260624-关于创新药相关政策动态的情况专报-v01.md" \
  -o "demo/online/policy-keyword-tracker-创新药政策跟踪/20260624-关于创新药相关政策动态的情况专报-v01.docx" \
  --doc-type 情况专报
```

把本样例换成其它关键词（如「低空经济」「数据要素」）即可复用同一流程。
