# 样例：完整公文示例（想看效果，从这里翻）

本目录按**成稿时模型能不能联网**拆成两类——这是真正影响样例长相的维度（联网的直接出成稿，离线的还带 `materials.md`、`raw-materials/`、`-提示词.md`）。

- `online/`：**联网**场景示例
- `offline/`：**离线**场景示例

### 和「快速上手」三种模式怎么对应

三种用法模式里，前两种都是联网、产出同一类成稿，所以共用 `online/`，并不需要各开一个文件夹：

| 快速上手的模式 | 看哪个文件夹 |
|---|---|
| 模式一 · 能装 skill 的工具（Codex / Claude Code） | `online/`（含 `ministry-news-daily`、`policy-keyword-tracker` 两个 skill 样例） |
| 模式二 · 网页版 AI 助手（联网） | `online/` |
| 模式三 · 内网离线（WebUI / Qwen 等） | `offline/` |

> 一句话：**两个文件夹按「联网 / 离线」分，三种模式里联网的两种（一、二）共用 `online/`，离线的一种（三）用 `offline/`**——覆盖三种模式没有遗漏。

当前状态：

- `online/` 已提供完整样例：`报告`、`简报`、`通知`、`请示`、`纪要`
- `online/` 另含两个**联网采集类 skill** 的样例（演示「采集→核实→成稿→导出」全链路，样例为占位、非真实数据）：
  - `ministry-news-daily-部委动态日报/`：浏览各部委官网最新动态，汇总成每日《报告》（[skills/ministry-news-daily](../skills/ministry-news-daily)）
  - `policy-keyword-tracker-创新药政策跟踪/`：围绕关键词「创新药」跨部委检索政策，汇总成《情况专报》（[skills/policy-keyword-tracker](../skills/policy-keyword-tracker)）
- `offline/` 已提供完整样例：`报告`、`通知`、`请示`、`纪要`、`简报`、`情况专报`、`汇报材料`、`工作总结`、`工作方案`、`讲话稿`、`回复函`
- `offline/raw-materials/` 额外提供长原始素材汇编，用于演示断网情况下“先准备材料，再生成提示词，再成稿”的流程
- `offline/` 对应离线产物 [dist/offline/default/](../dist/offline/default/)（粘贴到 WebUI / AnythingLLM / Qwen 等离线宿主使用）

建议每个文种目录尽量保持同一结构：

- `task.md`：用户任务或使用场景说明
- `materials.md`：原始素材或可核实事实摘要
- `YYYYMMDD-标题-vNN-提示词.md`：仅离线场景保留，表示喂给离线宿主的完整提示词
- `YYYYMMDD-标题-vNN.md`：最终 Markdown 成稿
- `YYYYMMDD-标题-vNN.docx`：导出的 Word 文件
- 图片（如 `*.jpg`/`*.png`）：**就放在用到它的文种目录里**，成稿按 `![图1 标题](./图片文件名)` 本地引用——这样每个文种目录都自包含，可以整体拷走单独使用，不依赖外部共享目录。同一张图被多个文种用到时，各目录各存一份副本。

命名约定：

- `task.md`、`materials.md` 作为人工整理的输入文件，保留固定名称，便于查找和复用
- 项目生成的各类文稿、提示词和导出文件，统一按 `日期 + 标题 + 版本号` 命名
- 同一次任务若存在多个同名 Markdown 产物，则在版本号后追加产物类型后缀，如 `-提示词`

直接查看：

- [online/](./online)
- [offline/](./offline)
- [dist/offline/default/doc-types/](../dist/offline/default/doc-types/)：单文种离线 prompt 目录。
