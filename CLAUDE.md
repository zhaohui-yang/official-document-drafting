# CLAUDE.md

本文件是 Claude Code 等宿主的**兼容入口**，本身不维护规则，只指明从哪里加载本仓的要求。

## 先加载（必读，按顺序）

1. **[AGENTS.md](./AGENTS.md)** — 全局 Agent 基线：单一信息源纪律、改完必跑的验证命令、`skills/` 关系、防编造底线、规则优先级、复杂任务并行执行约定。**所有约定以 AGENTS.md 为准，本文件不重复。**
2. **[prompts/](./prompts)** — 唯一权威主源：公文写作的全部规则与模板（`core/` 共享规则、`doc-types/<id>-<文种>/` 各文种 `spec.md`＋`meta.toml`＋`examples.md`、`font-profiles/`、`layout-profiles/`、`profiles/`）。

## 各文档分工（唯一权威来源，其余只引用或摘要）

- 写作/版式**规则**与文种**撰写思路**：`prompts/`（主源）。不要在散文或代码里另写规则。
- **Agent 工作纪律**（构建、验证、并行、Git、防编造）：`AGENTS.md`。
- **人类导读**（安装、使用、规则体系总览、样例索引）：`README.md`。
- **面向读者的说明文档**：`docs/references/`（与主源冲突时以 `prompts/` 为准，每个文件顶部已声明）。
- **抽出的薄路由能力**：`skills/*/SKILL.md`（手写路由，指向既有入口，不复制规则）。

## 最常用命令

```bash
python3 src/scripts/build_all.py          # 改了 prompts/ 后重建在线 + 全部离线产物
python3 src/scripts/build_all.py --check  # 校验在线与离线产物均与主源同步（漂移则非零退出）
python3 -m pytest -q                   # 全部测试必须通过
python3 -m ruff check .                # 保持 lint 干净
```

改动默认只落本地，未经明确要求不 `git push`；说明与注释默认用中文。
