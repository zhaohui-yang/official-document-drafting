# 离线提示词适配器使用说明

本目录用于承载离线提示词相关的 adapter 代码和使用说明。

当前项目的唯一主源已经切换为：

- `prompts/core/`
- `prompts/doc-types/`
- `prompts/profiles/default.toml`

也就是说：

- 在线 `skill` 使用 [../skill/build.py](../skill/build.py) 从 `prompts/` 生成
- 离线 WebUI / Qwen / AnythingLLM / Claude.ai 使用 [build.py](./build.py) 从同一套 `prompts/` 生成
- [../../SKILL.md](../../SKILL.md)、[../../agents/openai.yaml](../../agents/openai.yaml)、[../../dist/](../../dist) 和 [../../assets/templates/](../../assets/templates) 都视为生成产物

## 本目录内容

- [build.py](./build.py)：从 `prompts/` 主源生成离线提示词
- [../../dist/offline/default/system_prompt.md](../../dist/offline/default/system_prompt.md)：标准构建产物中的 `system_prompt`

## 常用命令

一键构建在线 skill 和离线基础系统提示词：

```bash
python3 ../../scripts/build_all.py
```

列出支持的文种：

```bash
python3 build.py --list-doc-types
```

只生成基础 `system_prompt`：

```bash
python3 build.py --emit-system
```

生成一份“通知”离线提示词：

```bash
python3 build.py \
  --doc-type 通知 \
  --instruction "起草一份关于开展2026年春季安全检查工作的通知，语气正式、结构清晰。" \
  --material-file ./素材.md \
  -o /tmp/20260404-春季安全检查通知-v01-提示词.md
```

生成一份“情况专报”离线提示词，并附带少量示例：

```bash
python3 build.py \
  --doc-type 专报 \
  --instruction "根据材料整理一份领导看的情况专报，先事实后研判。" \
  --material-file ./news.md \
  --include-examples \
  -o /tmp/20260404-热点舆情情况专报-v01-提示词.md
```

兼容旧命令时，也可以继续使用：

```bash
python3 ../../scripts/build_offline_prompt.py --doc-type 通知 --instruction "..."
```

## 粘贴到前端的方式

脚本输出分为两部分：

- `# System Prompt`
- `# User Prompt`

如果你的前端支持单独的系统提示词框：

- 把 `# System Prompt` 下的内容粘到系统提示词
- 把 `# User Prompt` 下的内容粘到用户输入

如果前端只有一个输入框：

- 直接把整个输出一起粘进去即可

## 推荐维护方式

- 共享总规则：改 `prompts/core/`
- 某个文种的专项规范：改 `prompts/doc-types/<英文-中文目录>/` 下的 `spec.md` 和 `meta.toml`
- profile 元数据和系统前言：改 `prompts/profiles/default.toml`

你不需要同时维护一套 `skill` 文案和一套离线 prompt 文案；两者都从同一套主源生成。
