# offline 示例

本目录对应 README 中的离线使用场景，例如：

- WebUI
- Qwen 本地前端
- AnythingLLM
- Claude.ai / Claude Desktop

建议按下面的顺序理解和使用：

1. 先看 [raw-materials/](./raw-materials)
   这里存放已经下载到本地的长原始素材，模拟断网环境下用户手里已有的一大批网页资料、截图摘录和事实汇编。
2. 再看具体文种目录
   每个文种目录都会从长原始素材中提炼出一份 `materials.md`，再配套 `task.md`、`提示词.md`、最终成稿和 `.docx`。
3. 最后按自己的本地前端习惯使用
   用 [../../src/adapters/offline/build.py](../../src/adapters/offline/build.py) 生成提示词，粘贴到本地前端即可模拟离线生成。

离线产物为 [../../dist/offline/default/](../../dist/offline/default/)（粘贴到 WebUI / AnythingLLM / Qwen 等离线宿主使用）。如果模型容易跑偏，可先用 `--task outline` 生成提纲，再扩写全文。

对应的最小流程是：

1. （可选，仅供提炼参考）先翻一下 [raw-materials/20260404-我的刀盾-原始素材汇编-v01.md](./raw-materials/20260404-%E6%88%91%E7%9A%84%E5%88%80%E7%9B%BE-%E5%8E%9F%E5%A7%8B%E7%B4%A0%E6%9D%90%E6%B1%87%E7%BC%96-v01.md)，了解素材出处。
2. 进入某个文种目录，看它自己的 `task.md` 和 `materials.md`（已从原始素材提炼好）。
3. **只用该文种目录内的文件**生成提示词，不读 `raw-materials/`：`--instruction-file ./task.md --material-file ./materials.md`（素材已被打进 `...-提示词.md`）。
4. 把生成的 `...-提示词.md` 粘进本地前端，得到最终 `Markdown` 成稿。
5. 最后再用 [../../src/renderers/docx.py](../../src/renderers/docx.py) 导出 `.docx`。

当前已提供完整样例：

- [raw-materials/](./raw-materials)
- [report-报告/](./report-%E6%8A%A5%E5%91%8A)
- [notice-通知/](./notice-%E9%80%9A%E7%9F%A5)
- [request-请示/](./request-%E8%AF%B7%E7%A4%BA)
- [minutes-纪要/](./minutes-%E7%BA%AA%E8%A6%81)
- [briefing-简报/](./briefing-%E7%AE%80%E6%8A%A5)
- [special-report-情况专报/](./special-report-%E6%83%85%E5%86%B5%E4%B8%93%E6%8A%A5)
- [presentation-汇报材料/](./presentation-%E6%B1%87%E6%8A%A5%E6%9D%90%E6%96%99)
- [summary-工作总结/](./summary-%E5%B7%A5%E4%BD%9C%E6%80%BB%E7%BB%93)
- [work-plan-工作方案/](./work-plan-%E5%B7%A5%E4%BD%9C%E6%96%B9%E6%A1%88)
- [speech-讲话稿/](./speech-%E8%AE%B2%E8%AF%9D%E7%A8%BF)
- [reply-回复函/](./reply-%E5%9B%9E%E5%A4%8D%E5%87%BD)

如果你不想只看这 4 个完整离线样例，也可以直接打开已经生成好的更多单文种 prompt：

- 法定公文高频：[../../dist/offline/default/doc-types/report-报告/prompt.md](../../dist/offline/default/doc-types/report-%E6%8A%A5%E5%91%8A/prompt.md)、[../../dist/offline/default/doc-types/notice-通知/prompt.md](../../dist/offline/default/doc-types/notice-%E9%80%9A%E7%9F%A5/prompt.md)、[../../dist/offline/default/doc-types/request-请示/prompt.md](../../dist/offline/default/doc-types/request-%E8%AF%B7%E7%A4%BA/prompt.md)、[../../dist/offline/default/doc-types/minutes-纪要/prompt.md](../../dist/offline/default/doc-types/minutes-%E7%BA%AA%E8%A6%81/prompt.md)、[../../dist/offline/default/doc-types/letter-函/prompt.md](../../dist/offline/default/doc-types/letter-%E5%87%BD/prompt.md)、[../../dist/offline/default/doc-types/approval-批复/prompt.md](../../dist/offline/default/doc-types/approval-%E6%89%B9%E5%A4%8D/prompt.md)。
- 常见正式材料：[../../dist/offline/default/doc-types/briefing-简报/prompt.md](../../dist/offline/default/doc-types/briefing-%E7%AE%80%E6%8A%A5/prompt.md)、[../../dist/offline/default/doc-types/special-report-情况专报/prompt.md](../../dist/offline/default/doc-types/special-report-%E6%83%85%E5%86%B5%E4%B8%93%E6%8A%A5/prompt.md)、[../../dist/offline/default/doc-types/presentation-汇报材料/prompt.md](../../dist/offline/default/doc-types/presentation-%E6%B1%87%E6%8A%A5%E6%9D%90%E6%96%99/prompt.md)、[../../dist/offline/default/doc-types/summary-工作总结/prompt.md](../../dist/offline/default/doc-types/summary-%E5%B7%A5%E4%BD%9C%E6%80%BB%E7%BB%93/prompt.md)、[../../dist/offline/default/doc-types/work-plan-工作方案/prompt.md](../../dist/offline/default/doc-types/work-plan-%E5%B7%A5%E4%BD%9C%E6%96%B9%E6%A1%88/prompt.md)、[../../dist/offline/default/doc-types/speech-讲话稿/prompt.md](../../dist/offline/default/doc-types/speech-%E8%AE%B2%E8%AF%9D%E7%A8%BF/prompt.md)、[../../dist/offline/default/doc-types/reply-回复函/prompt.md](../../dist/offline/default/doc-types/reply-%E5%9B%9E%E5%A4%8D%E5%87%BD/prompt.md)。
- 全部目录：[../../dist/offline/default/doc-types/](../../dist/offline/default/doc-types/)。

统一文件结构：

- `task.md`：离线用户任务说明。
- `materials.md`：从长原始素材中提炼出的当前文种可用事实。
- `YYYYMMDD-标题-vNN-提示词.md`：喂给离线宿主的完整提示词。
- `YYYYMMDD-标题-vNN.md`：模拟离线生成后的 Markdown 成稿。
- `YYYYMMDD-标题-vNN.docx`：用 Python 导出的 Word 文件。

进一步查看：

- [../../src/adapters/offline/README.md](../../src/adapters/offline/README.md)：离线适配器的完整使用说明。
- [../../dist/offline/default/system_prompt.md](../../dist/offline/default/system_prompt.md)：正式离线 `system_prompt` 产物。
- [../../dist/offline/default/doc-types/](../../dist/offline/default/doc-types/)：单文种离线 prompt 目录。
