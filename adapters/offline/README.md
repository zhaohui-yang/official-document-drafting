# 离线提示词适配器使用说明

本目录用于承载离线提示词相关的 adapter 代码和使用说明，适用于 WebUI、AnythingLLM、Qwen 本地前端、Claude.ai / Claude Desktop 等“只接收提示词、不直接安装 skill”的宿主环境。

## 主源和产物

当前项目的唯一主源是：

- [prompts/core/](../../prompts/core/)：共享规则主源，负责文种判断、通用写法、版式边界、占位符和输出习惯。
- [prompts/doc-types/](../../prompts/doc-types/)：单文种规则主源，按文种分别维护 `spec.md`、`meta.toml` 等专项要求。
- [prompts/profiles/default.toml](../../prompts/profiles/default.toml)：完整版离线 profile，适合中强模型，保留全量共享规则。
- [prompts/profiles/small-local.toml](../../prompts/profiles/small-local.toml)：弱模型离线 profile，适合小模型、本地模型和容易丢上下文的宿主。

同一套主源会被编译成两类产物：

- 在线 `skill` 使用 [../skill/build.py](../skill/build.py) 生成：面向 Codex、agents、Claude Code 等宿主。
- 离线提示词使用 [build.py](./build.py) 生成：面向 WebUI、AnythingLLM、Qwen、Claude.ai 等宿主。

与离线适配器直接相关的关键文件有：

- [build.py](./build.py)：离线提示词构建入口，从 `prompts/` 主源拼装 `System Prompt + User Prompt`。
- [../../dist/offline/default/system_prompt.md](../../dist/offline/default/system_prompt.md)：默认 profile 的正式离线全量 `system_prompt` 产物。
- [../../dist/offline/small-local/system_prompt.md](../../dist/offline/small-local/system_prompt.md)：弱模型 profile 的正式离线全量 `system_prompt` 产物。
- [../../dist/offline/default/doc-types/](../../dist/offline/default/doc-types/)：每个文种单独可用的离线 prompt 产物目录。
- [../../dist/offline/small-local/doc-types/](../../dist/offline/small-local/doc-types/)：弱模型优先使用的单文种 prompt 产物目录。
- [../../demo/offline/](../../demo/offline/)：离线场景完整样例目录，包含原始素材、提炼材料、提示词、成稿和 `.docx`。
- [../../scripts/build_all.py](../../scripts/build_all.py)：一键重建在线 skill 和离线基础产物。

## 推荐离线流程

建议先在下面 3 条路径里选一条，再决定用哪份 prompt。

### 路径 A：短素材直接成稿

适合素材不长、模型中等以上的场景。

1. 直接打开当前文种的单文种 prompt。
2. 把任务说明和素材粘进去。
3. 让本地前端输出最终 Markdown 成稿。
4. 再导出 `.docx`。

### 路径 B：长素材先提炼，再成稿

适合“手里有很多网页摘录、截图转文字、原始材料很长”的场景。

1. 先准备长原始素材汇编。
2. 再为目标文种提炼一份 `materials.md`。
3. 再生成当前文种的 prompt。
4. 再喂给本地前端。

### 路径 C：弱模型先提纲，再写正文

适合小模型、本地模型、容易跑偏或容易忘规则的模型。

1. 先用 `--task outline` 只生成提纲任务。
2. 审一遍提纲后，再让模型按提纲扩写全文。
3. 最后再做格式化和导出。

如果你的原始素材很多、很长，建议按下面的顺序组织：

1. 先准备一份长原始素材汇编
   参考 [../../demo/offline/raw-materials/](../../demo/offline/raw-materials/)，这里模拟的是“已经下载到本地、不再联网”的网页摘要、截图摘录和事实汇编。
2. 再为目标文种提炼一份 `materials.md`
   参考 [../../demo/offline/report-报告/materials.md](../../demo/offline/report-%E6%8A%A5%E5%91%8A/materials.md) 或 [../../demo/offline/request-请示/materials.md](../../demo/offline/request-%E8%AF%B7%E7%A4%BA/materials.md)，把真正要用到的事实压成短材料。
3. 准备一份 `task.md`
   用一句到几句说明你要起草什么文种、围绕什么主题、是否需要正式语气、是否需要导出 Word。
4. 选择提示词模式
   可以直接使用全量 `system_prompt`，也可以直接打开某个文种的独立 prompt。
5. 如需按当前任务即时拼装，再用离线适配器生成提示词
   提示词会包含完整 `System Prompt` 和本次任务的 `User Prompt`。
6. 把提示词粘贴到本地前端
   WebUI、AnythingLLM、Qwen、Claude.ai 等场景都按这个方式处理。
7. 拿到 Markdown 成稿后再导出 `.docx`
   用 [../../renderers/docx.py](../../renderers/docx.py) 或 [../../scripts/generate_docx.py](../../scripts/generate_docx.py) 生成正式 Word 文件。

## 常用命令

直接运行 `build.py`，默认会同时重建 `default` 和 `small-local` 两套离线产物，包括：

- 两套全量 `system_prompt`
- 两套每个文种的 `system_prompt.md`
- 两套每个文种的 `user_prompt_template.md`
- 两套每个文种的 `prompt.md`

最常用命令：

```bash
python3 build.py
```

如果你要显式重建弱模型 profile：

```bash
python3 build.py --profile small-local
```

列出支持的文种：

```bash
python3 build.py --list-doc-types
```

如果是从仓库根目录一键重建在线 skill 和全部离线产物：

```bash
python3 ../../scripts/build_all.py
```

只有在你想“只生成某一部分”时，才需要特殊参数。

只生成当前 profile 的全量 `system_prompt`：

```bash
python3 build.py --emit-system
```

为所有文种生成独立可用的 prompt 产物：

```bash
python3 build.py --emit-doc-type-prompts
```

如果想显式写清“同时更新当前 profile 的全量 `system_prompt` 和所有单文种 prompt”：

```bash
python3 build.py --emit-system --emit-doc-type-prompts
```

弱模型建议优先使用 `small-local`：

```bash
python3 build.py --profile small-local --emit-system --emit-doc-type-prompts
```

按“长原始素材 + 当前文种提炼材料”生成一份离线提示词：

```bash
python3 build.py \
  --doc-type 报告 \
  --instruction-file ../../demo/offline/report-报告/task.md \
  --material-file ../../demo/offline/raw-materials/20260404-我的刀盾-原始素材汇编-v01.md \
  --material-file ../../demo/offline/report-报告/materials.md \
  -o ../../demo/offline/report-报告/20260404-关于“我的刀盾”网络传播情况的报告-v01-提示词.md
```

再看一个请示示例：

```bash
python3 build.py \
  --doc-type 请示 \
  --instruction-file ../../demo/offline/request-请示/task.md \
  --material-file ../../demo/offline/raw-materials/20260404-我的刀盾-原始素材汇编-v01.md \
  --material-file ../../demo/offline/request-请示/materials.md \
  -o ../../demo/offline/request-请示/20260404-关于申请开展“我的刀盾”传播案例梳理工作的请示-v01-提示词.md
```

弱模型先提纲后正文的建议命令：

```bash
python3 build.py \
  --profile small-local \
  --task outline \
  --doc-type 报告 \
  --instruction "先根据材料生成一份报告提纲，不展开全文。" \
  --material-file ../../demo/offline/report-报告/materials.md \
  -o ../../demo/offline/report-报告/20260405-关于“我的刀盾”网络传播情况的报告-v02-提纲提示词.md
```

兼容旧命令时，也可以继续使用：

```bash
python3 ../../scripts/build_offline_prompt.py --doc-type 通知 --instruction "..."
```

## 如何粘贴到前端

模型强度选择建议：

- 中强模型、上下文较稳：优先使用 [../../dist/offline/default/system_prompt.md](../../dist/offline/default/system_prompt.md) 或 [../../dist/offline/default/doc-types/](../../dist/offline/default/doc-types/)。
- 弱模型、小模型、本地模型：优先使用 [../../dist/offline/small-local/doc-types/](../../dist/offline/small-local/doc-types/) 下当前文种的 `prompt.md`，不要先从全量 `system_prompt` 开始。

脚本即时生成的输出分为两部分：

- `# System Prompt`
- `# User Prompt`

如果你的前端支持单独的系统提示词框：

1. 把 `# System Prompt` 下的内容粘到系统提示词。
2. 把 `# User Prompt` 下的内容粘到本次任务输入。

如果前端只有一个输入框：

1. 直接把整份输出一起粘进去即可。

## 与 demo/offline 的对应关系

如果你想直接照着仓库里的例子走，可以看：

- [../../demo/offline/raw-materials/README.md](../../demo/offline/raw-materials/README.md)：长原始素材怎么组织。
- [../../dist/offline/default/doc-types/report-报告/prompt.md](../../dist/offline/default/doc-types/report-%E6%8A%A5%E5%91%8A/prompt.md)：报告文种的默认单独可用 prompt。
- [../../dist/offline/default/doc-types/notice-通知/prompt.md](../../dist/offline/default/doc-types/notice-%E9%80%9A%E7%9F%A5/prompt.md)：通知文种的默认单独可用 prompt。
- [../../dist/offline/default/doc-types/request-请示/prompt.md](../../dist/offline/default/doc-types/request-%E8%AF%B7%E7%A4%BA/prompt.md)：请示文种的默认单独可用 prompt。
- [../../dist/offline/default/doc-types/minutes-纪要/prompt.md](../../dist/offline/default/doc-types/minutes-%E7%BA%AA%E8%A6%81/prompt.md)：纪要文种的默认单独可用 prompt。
- [../../dist/offline/small-local/doc-types/](../../dist/offline/small-local/doc-types/)：弱模型专用的全部单文种 prompt 目录。
- [../../demo/offline/report-报告/README.md](../../demo/offline/report-%E6%8A%A5%E5%91%8A/README.md)：离线报告完整流程。
- [../../demo/offline/notice-通知/README.md](../../demo/offline/notice-%E9%80%9A%E7%9F%A5/README.md)：离线通知完整流程。
- [../../demo/offline/request-请示/README.md](../../demo/offline/request-%E8%AF%B7%E7%A4%BA/README.md)：离线请示完整流程。
- [../../demo/offline/minutes-纪要/README.md](../../demo/offline/minutes-%E7%BA%AA%E8%A6%81/README.md)：离线纪要完整流程。

## 推荐维护方式

- 共享总规则：改 [../../prompts/core/](../../prompts/core/)
- 某个文种的专项规范：改 [../../prompts/doc-types/](../../prompts/doc-types/) 下对应目录的 `spec.md` 和 `meta.toml`
- profile 元数据和系统前言：改 [../../prompts/profiles/](../../prompts/profiles) 下对应的 `default.toml` 或 `small-local.toml`

你不需要同时维护一套 `skill` 文案和一套离线 prompt 文案；两者都从同一套主源生成。
