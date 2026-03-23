# 离线 WebUI / Qwen 使用说明

本目录保留为离线使用文档入口。

当前项目的唯一主源已经切换为：

- `prompts/core/`
- `prompts/doc-types/`
- `prompts/profiles/default.toml`

也就是说：

- 在线 `skill` 使用 [adapters/skill/build.py](../adapters/skill/build.py) 从 `prompts/` 生成
- 离线 WebUI / Qwen 使用 [adapters/webui/build.py](../adapters/webui/build.py) 从同一套 `prompts/` 生成
- [SKILL.md](../SKILL.md)、[agents/openai.yaml](../agents/openai.yaml)、`dist/` 和 `assets/templates/` 都视为生成产物

## 常用命令

一键构建在线 skill 和离线基础系统提示词：

```bash
python3 scripts/build_all.py
```

列出支持的文种：

```bash
python3 adapters/webui/build.py --list-doc-types
```

生成一份“通知”离线提示词：

```bash
python3 adapters/webui/build.py \
  --doc-type 通知 \
  --instruction "起草一份关于开展2026年春季安全检查工作的通知，语气正式、结构清晰。" \
  --material-file ./素材.md \
  -o /tmp/offline_notice_prompt.md
```

生成一份“情况专报”离线提示词，并附带少量示例：

```bash
python3 adapters/webui/build.py \
  --doc-type 专报 \
  --instruction "根据材料整理一份领导看的情况专报，先事实后研判。" \
  --material-file ./news.md \
  --include-examples \
  -o /tmp/offline_special_report_prompt.md
```

兼容旧命令时，也可以继续使用：

```bash
python3 scripts/build_offline_prompt.py --doc-type 通知 --instruction "..."
```

## 粘贴到 WebUI 的方式

脚本输出分为两部分：

- `# System Prompt`
- `# User Prompt`

如果你的 WebUI 支持单独的系统提示词框：

- 把 `# System Prompt` 下的内容粘到系统提示词
- 把 `# User Prompt` 下的内容粘到用户输入

如果你的 WebUI 只有一个输入框：

- 直接把整个输出一起粘进去即可

## 推荐维护方式

- 共享总规则：改 `prompts/core/`
- 某个文种的专项规范：改 `prompts/doc-types/<英文-中文目录>/` 下的 `spec.md` 和 `meta.toml`
- profile 元数据和系统前言：改 `prompts/profiles/default.toml`

你不需要同时维护一套 `skill` 文案和一套离线 prompt 文案；两者都从同一套主源生成。
