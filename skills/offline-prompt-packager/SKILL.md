---
name: offline-prompt-packager
description: 把基于 prompts/ 主源的 skill 打包成断网单机可用的离线提示词包。Use when the user wants to export/package offline prompts for disconnected or weak local models (WebUI、Qwen、AnythingLLM、Claude.ai), generate self-contained system_prompt / user_prompt bundles, build a per-文种 prompt, or produce a small-local lite profile for weaker models.
---

# 离线提示词打包器

把一个基于 `prompts/` 主源的 skill 打包成**断网单机也能用**的提示词包——目标是只能粘贴提示词、装不了 skill、且模型较弱的宿主（WebUI / Qwen / AnythingLLM / Claude.ai）。

这是「打包」元能力，不改写规则：所有内容都从 `prompts/` 主源内联，保证离线包和在线 skill 同源、不漂移。

## 文件索引

```
adapters/offline/build.py        # 离线打包主入口（CLI）
adapters/shared.py               # render_offline_system_prompt 等共享渲染（在线/离线共用）
prompts/profiles/default.toml    # 标准离线 profile（system 分层、文种目录、兜底骨架）
prompts/profiles/small-local.toml# 弱模型 lite profile（更短更硬的约束、固定文种）
prompts/core/*.md                # 共享总规则主源（离线内联）
prompts/core/offline-lite/*.md   # 弱模型精简版规则
dist/offline/<profile>/...       # 打包产物
```

## 调用方式

- 全量重建仓库内置离线产物：`python3 adapters/offline/build.py`（不传参=全 profile、全文种）。
- 只出基础系统提示词：`--emit-system`。
- 按文种拼 `System + User` 完整提示词：`--doc-type <文种>`，可加 `--instruction`/`--material-file`/`--include-examples`。
- 指定 profile：`--profile default` 或 `--profile small-local`（弱模型）。
- 列出支持文种：`--list-doc-types`；写到单文件：`-o 输出.md`。

```bash
python3 adapters/offline/build.py                                   # 全量重建
python3 adapters/offline/build.py --profile small-local --doc-type 通知 -o 通知-离线.md
```

## 默认流程

1. 选 profile：标准模型用 `default`，弱模型用 `small-local`（不自行判断文种、不补写事实、只出最终成稿）。
2. 选任务：基础 system（`--emit-system`）或按文种完整提示词（`--doc-type`）。
3. 生成后产物落 `dist/offline/<profile>/`；分发时整包提示词粘进宿主即可。
4. 改了 `prompts/` 主源后重新打包，保证离线包与在线 skill 同源。

## 复用到其它 skill

打包逻辑（system/user/profile 分层、内联主源、弱模型 lite profile）与公文内容无强绑定。把另一个 skill 的规则也组织成 `prompts/core/*` + `prompts/profiles/*.toml` + 文种/任务目录后，可复用本入口打包成离线提示词。

## 边界

- 离线包是「快照」：主源更新后必须重新打包，否则会和在线 skill 漂移。
- 弱模型 profile 不做文种判断和事实补全；需要这些能力时用标准 profile 或在线 skill。
