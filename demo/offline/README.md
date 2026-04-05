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
   每个文种目录都会从长原始素材中提炼出一份 `materials.md`，再配套 `task.md`、`提纲提示词.md`、`提纲.md`、`提示词.md`、最终成稿和 `.docx`。
3. 最后按自己的本地前端习惯使用
   用 [../../adapters/offline/build.py](../../adapters/offline/build.py) 生成提示词，粘贴到本地前端即可模拟离线生成。

离线产物默认分成两套：

- [../../dist/offline/default/](../../dist/offline/default/)：适合中强模型、上下文较稳的离线宿主。
- [../../dist/offline/small-local/](../../dist/offline/small-local/)：适合弱模型、小模型、本地模型和容易丢上下文的宿主。

弱模型建议优先这样走：

1. 先使用 [../../dist/offline/small-local/doc-types/](../../dist/offline/small-local/doc-types/) 下当前文种的 `prompt.md`。
2. 如果素材很长，先看 `raw-materials/`，再看对应文种目录下的 `materials.md`。
3. 如果模型仍然容易跑偏，先用 `--task outline` 生成提纲，再扩写全文。

对应的最小流程是：

1. 先打开 [raw-materials/20260404-我的刀盾-原始素材汇编-v01.md](./raw-materials/20260404-%E6%88%91%E7%9A%84%E5%88%80%E7%9B%BE-%E5%8E%9F%E5%A7%8B%E7%B4%A0%E6%9D%90%E6%B1%87%E7%BC%96-v01.md)。
2. 再进入某个文种目录，看 `task.md` 和 `materials.md`。
3. 用离线适配器生成 `...-提示词.md`。
4. 如模型偏弱，先使用 `...-提纲提示词.md` 得到 `...-提纲.md`。
5. 再把提纲和 `materials.md` 一起喂给本地前端，得到最终 `Markdown` 成稿。
6. 最后再用 [../../renderers/docx.py](../../renderers/docx.py) 导出 `.docx`。

当前已提供完整样例：

- [raw-materials/](./raw-materials)
- [report-报告/](./report-%E6%8A%A5%E5%91%8A)
- [notice-通知/](./notice-%E9%80%9A%E7%9F%A5)
- [request-请示/](./request-%E8%AF%B7%E7%A4%BA)
- [minutes-纪要/](./minutes-%E7%BA%AA%E8%A6%81)

统一文件结构：

- `task.md`：离线用户任务说明。
- `materials.md`：从长原始素材中提炼出的当前文种可用事实。
- `YYYYMMDD-标题-vNN-提纲提示词.md`：喂给弱模型、先产出提纲的第一步提示词。
- `YYYYMMDD-标题-vNN-提纲.md`：离线样例中的提纲输出示例。
- `YYYYMMDD-标题-vNN-提示词.md`：喂给离线宿主的完整提示词。
- `YYYYMMDD-标题-vNN.md`：模拟离线生成后的 Markdown 成稿。
- `YYYYMMDD-标题-vNN.docx`：用 Python 导出的 Word 文件。

进一步查看：

- [../../adapters/offline/README.md](../../adapters/offline/README.md)：离线适配器的完整使用说明。
- [../../dist/offline/default/system_prompt.md](../../dist/offline/default/system_prompt.md)：正式离线 `system_prompt` 产物。
- [../../dist/offline/small-local/system_prompt.md](../../dist/offline/small-local/system_prompt.md)：弱模型版正式离线 `system_prompt` 产物。
- [../../dist/offline/default/doc-types/](../../dist/offline/default/doc-types/)：默认单文种离线 prompt 目录。
- [../../dist/offline/small-local/doc-types/](../../dist/offline/small-local/doc-types/)：弱模型单文种离线 prompt 目录。
