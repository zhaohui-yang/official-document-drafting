---
name: skill-build
description: 从 prompts/ 单一主源生成并校验本项目的 skill 产物。Use when working on 构建/重新生成 SKILL.md、agent 接口、dist 副本、assets/templates/ 模板或离线提示词，校验产物是否与 prompts/ 主源同步（--check / 防漂移），或维护 prompts/ → 产物 的单一信息源构建范式。
---

# skill 产物构建与同步守护

本项目的 `SKILL.md`、agent 接口、`dist/` 副本、`assets/templates/` 模板和离线提示词**都不是手写**，而是从 `prompts/` 单一主源生成。本 skill 管「生成 + 校验同步」，防止改了主源忘了重新 build 导致产物漂移。

## 文件索引

```
src/adapters/skill/build.py      # 生成 SKILL.md / agent / dist 副本 / assets/templates/；--check 校验同步
src/adapters/offline/build.py    # 生成离线提示词（见 offline-prompt-packager skill）
src/adapters/shared.py           # 主源读取与渲染（再导出层，实现在同目录 paths/profiles/doc_types/rendering，含 render_skill_markdown / build_template_outputs 等）
src/scripts/build_all.py         # 一键重建：skill 产物 + default 离线产物
prompts/                     # 唯一主源：core/ 规则、doc-types/ 文种、font/layout-profiles、profiles
```

## 调用方式

```bash
python3 src/adapters/skill/build.py            # 重新生成全部 skill 产物（含 54 个文件）
python3 src/adapters/skill/build.py --check    # 只校验产物是否与 prompts/ 主源同步（漂移则非零退出）
python3 src/scripts/build_all.py               # 一键重建 skill 产物 + 全部离线产物
python3 -m pytest -q                       # 含 test_build_sync 同步守卫与 references 一致性守卫
```

## 默认流程

1. **改主源**：任何规则、文种、字体/版式方案、profile 的修改都只改 `prompts/`（及 `*.toml`、`spec.md`），不直接手改 `SKILL.md` / `dist/` / 模板。
2. **重新生成**：`python3 src/adapters/skill/build.py`（涉及离线用 `src/scripts/build_all.py`）。
3. **校验同步**：`python3 src/adapters/skill/build.py --check` 必须通过；CI（`.github/workflows/ci.yml`）会强制跑 `--check` + `pytest`。
4. **跑测试**：`test_build_sync` 断言「主源渲染 == 落盘」，`test_reference_consistency` 守 references 不与主源漂移。

## 单一信息源原则

- 产物（`SKILL.md`、`dist/`、`assets/templates/`、`docs/references/` 里列出的数值）一律不手写、不复制；冲突时以 `prompts/` 主源为准。
- 新增生成目标时把它加进 `src/adapters/skill/build.py` 的 `build_targets`，自动纳入 `--check` 与同步测试。
- 这套范式可复用到其它「prompts/ 主源 → 多宿主产物」的 skill 构建。

## 边界

- 本 skill 不改写公文内容规则本身——那是「公文写作」skill 的事；本 skill 只负责把主源可靠地生成成各宿主产物并守住同步。
