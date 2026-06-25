# skills 目录

本目录把仓库里几块**自包含、触发场景与「起草」不同**的能力抽成独立的薄路由 skill。它们**共用根目录同一份 `prompts/` 主源和 `scripts/`、`adapters/` 代码，不复制规则**——每个 `SKILL.md` 只是入口路由，指向既有文件，冲突时一律以主源为准。

| skill | 能力 | 主要入口 | 触发 |
|---|---|---|---|
| 根 `SKILL.md`（公文写作） | 起草、改写、规范中文公文 | `prompts/`、`adapters/skill/build.py` | 写/改一份公文 |
| `docx-export` | 公文 Markdown → 机关版式 `.docx` | `scripts/generate_docx.py` | 导出 Word、调字体/页边距/页码 |
| `offline-prompt-packager` | 打包断网单机离线提示词包 | `adapters/offline/build.py` | 给弱模型/离线宿主导出提示词 |
| `document-qa` | 成稿结构与质量校验 | `scripts/check_sections.py` | 检查/校验一份稿子 |
| `skill-build` | 从 `prompts/` 主源生成并校验产物 | `adapters/skill/build.py --check` | 重新生成/防漂移构建 |
| `ministry-news-daily` | 浏览部委官网最新动态→汇总成每日《报告》 | `prompts/doc-types/report-报告/spec.md`、`scripts/generate_docx.py` | 了解国家大事/政务动态日报 |
| `doc-type-routing` | 起草前判定该用哪个文种、什么行文方向 | `prompts/core/workflow.md`、`prompts/core/drafting-thinking.md` | 不确定文种/行文方向 |
| `policy-keyword-tracker` | 围绕关键词跨部委检索政策→汇总成《情况专报》 | `prompts/doc-types/special-report-情况专报/spec.md`、`scripts/generate_docx.py` | 跟踪某主题（如创新药）的部委政策 |

## 约定

- 这些 `SKILL.md` 是**手写薄路由**，不是 `prompts/` 生成的产物，因此不进 `adapters/skill/build.py --check`。
- 但它们引用的入口路径由 `tests/test_skill_routers.py` 守护：路径被移走/改名时测试会失败，避免路由腐烂。
- 安装/分发（symlink 到全局 skill 目录）是环境相关的，本目录只作权威源。
