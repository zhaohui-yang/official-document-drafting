# 贡献指南

感谢你为「公文写作 Skill」做贡献。本仓的协作统一通过 GitHub Issues 与 Pull Request 进行。

项目地址：https://github.com/zhaohui-yang/official-document-drafting

## 提问题 / 报 bug / 提建议

到 [Issues](https://github.com/zhaohui-yang/official-document-drafting/issues) 提交，并尽量说明：

- 使用场景：在线 skill / 离线提示词 / Word 导出 / 文种判定 等。
- 复现步骤或输入、期望结果与实际结果。
- 涉及的文种、文件路径或命令。

## 改代码或规则前请先读（最重要）

- **单一信息源**：`prompts/` 是唯一权威主源。规则、撰写思路、模板都改 `prompts/`，**不要手改生成产物**（`SKILL.md`、`dist/`、`assets/templates/`、`dist/skill/agents/openai.yaml` 都是构建产物）。详见 [AGENTS.md](./AGENTS.md)、[CLAUDE.md](./CLAUDE.md)。
- 代码在 `src/`（`src/adapters`、`src/scripts`、`src/renderers`）；说明文档在 `docs/`；薄路由 skill 在 `skills/`。
- 说明、注释、提交信息默认用中文。

## 提交前的本地校验（必须通过）

```bash
python3 src/scripts/build_all.py          # 改了 prompts/ 后重建产物
python3 src/scripts/build_all.py --check  # 校验产物与主源同步
python3 -m pytest -q                       # 全部测试通过
python3 -m ruff check .                    # lint 干净
```

## Pull Request

- 从最新 `main` 切分支，提交粒度清晰、提交信息用中文。
- PR 描述写清动机、改动范围、验证结果与剩余风险。
- 不引入第三方 Python 依赖（脚本只用标准库，需 `tomllib`，Python 3.11+）。
- 改了 `prompts/` 主源的，记得把重建后的 `dist/` 产物一并提交（`--check` 须通过）。

## 行为准则

请保持友善、就事论事。本仓采用 [MIT License](./LICENSE)，贡献即视为以该协议授权。
