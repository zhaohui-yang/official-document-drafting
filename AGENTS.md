# AGENTS.md

面向在本仓工作的 AI agent 的全局规则。本仓是「中文公文起草」skill：从 `prompts/` 单一主源生成在线 `SKILL.md`、agent 接口、`assets/templates/` 模板和离线提示词，并能把成稿导出为机关版式 `.docx`。

## 单一信息源（最重要）

- `prompts/` 是唯一权威主源：`core/` 共享规则、`doc-types/<id>-<文种>/`（`spec.md` + `meta.toml` + `examples.md`）、`font-profiles/`、`layout-profiles/`、`profiles/`。
- **不要手改生成产物**：`SKILL.md`、`dist/`、`assets/templates/`、`dist/skill/agents/openai.yaml` 都由 `src/adapters/skill/build.py` 生成。改了主源要重新 build。
- `docs/references/` 是面向读者的说明文档，不是主源；与 `prompts/` 冲突时以主源为准（每个 reference 顶部已声明）。
- 版式数值（行距等）只存在于 `prompts/layout-profiles/*.toml`；页边距默认值（按 GB/T 9704：上 37mm、下 35mm、左 28mm、右 26mm）在 `src/scripts/generate_docx.py` 的 `MARGIN_*_TWIPS`。不要在散文里重复硬编码这些数值。
- 文种的「撰写思路」写在各自 `spec.md` 的可选 `## 撰写思路` 段（思路为核心、结构可调），由 `src/adapters/shared.py` 注入产物；不要把思路散写进散文或代码。
- 新增生成目标时，加进 `src/adapters/skill/build.py` 的 `build_targets`（在线）或 `src/adapters/offline/build.py` 的 `build_profile_targets`（离线），使其自动纳入 `--check` 与同步测试。

## 改完必须做的验证

```bash
python3 src/adapters/skill/build.py            # 改了 prompts/ 后重新生成产物
python3 src/adapters/skill/build.py --check    # 校验产物与主源同步（漂移则非零退出）
python3 -m pytest -q                        # 全部测试必须通过
python3 -m ruff check .                     # 保持 lint 干净
```

- CI（`.github/workflows/ci.yml`）会强制跑 `--check` + `pytest`；本地先过再声称完成。
- 涉及离线产物时用 `python3 src/scripts/build_all.py` 一键重建在线 + 全部离线产物；`python3 src/scripts/build_all.py --check` 一键校验在线与离线产物均与主源同步。

## skills/

- `skills/` 下是从本仓抽出的同源薄路由 skill（`docx-export`、`document-qa`、`offline-prompt-packager`、`skill-build`、`doc-type-routing`、`ministry-news-daily`、`policy-keyword-tracker`）。它们**共用** `prompts/`、`src/scripts/`、`src/adapters/`，不复制规则。
- 这些 `SKILL.md` 是手写路由、不由主源生成，因此不进 `--check`；由 `tests/test_skill_routers.py` 守护其引用的入口存在。

## 业务素材同目录与最小授权

- 生成单个产物（一份成稿/文档）所需的全部**用户业务输入素材**——任务说明、素材摘要 `materials.md`、所引用的图片/附件等——必须集中在该产物所在的**同一个子目录**内，并以本地相对路径（`./`）引用。不得跨目录、向上级目录（`../`）或从共享目录拉取「生成该产物所需」的业务素材。
- 目的是**最小授权**：运行时只需对该产物所在的单一目录授读取权即可完成生成；跨目录拼接业务素材会放大所需的文件系统授权范围，禁止。一条生成命令只喂该目录内的素材，典型即 `--instruction-file ./task.md --material-file ./materials.md`。
- 共享/原始语料（如长原始素材汇编 `raw-materials/`）只供**人工提炼阶段**参考；提炼结果须落入该产物目录自己的 `materials.md`，**生成阶段不再读取共享目录**。
- **适用边界**：本约束只约束「用户业务素材」。skill 读取自身**规则主源**（`prompts/`、字体/版式 profile 等）和维护者的**构建操作**（`build.py` 从 `prompts/` 生成产物、`--check`）不在此列——那是 skill 固有规则与元构建，本就需要读主源树，不算「跨目录拼业务素材」。
- 图片落地已在代码层强制：`src/scripts/generate_docx.py` 要求 Markdown 引用的图片位于该 `.md` 同目录或其子目录，`../` 越级引用会报错。完整路径/素材约定见 `prompts/core/workflow.md`。

## 防编造底线（0 幻觉）

- 0 幻觉是最高内容纪律：成稿里每个具体值（事实、数据、文件号、机关与人名、日期、会议结论、政策依据）要么有来源（用户提供，或经核实、可溯源的公开来源），要么是占位符／待核实，没有第三种。
- 可借鉴、不可瞎编：允许引用、借鉴真实且可溯源的公开材料与体例写法（这正是各 `prompts/doc-types/*/spec.md` 顶部「真实样例来源」注释、两个采集类 skill 与 `workflow.md` 联网取材的依据）；借鉴的是真实公开事实与写法，不是凭空生成。
- 信息不足一律占位或标「待核实」，不把推测/常识补全写成事实。完整约束见 `prompts/core/policy.md`、`prompts/core/doc-type-guardrails.md`；可用 `python3 src/scripts/check_sections.py <文种> 成稿.md --strict-facts` 列出未溯源的具体值逐项核对。

## 规则优先级

- 用户当次明确要求 > 本文件（AGENTS.md）> `skills/*/SKILL.md`、`docs/references/` 等下游说明中的可选建议。
- 冲突时优先采用更安全、影响更小、边界更清晰的做法，并先说明冲突点。
- 唯一权威来源是 `prompts/` 主源与本文件；`README.md`、`docs/references/`、`CLAUDE.md`、各 `SKILL.md` 只引用或摘要，不平行维护完整规则。

## 复杂任务并行执行（workflows / agents）

- 任务复杂、可拆分、或包含多个互不依赖的步骤时，默认主动开启多个 agents 并行推进，把工作拆成互不依赖的子任务同时执行，大幅缩短完成时间。本仓适合并行的典型场景：跨多文种/多文件的审查或改写、对多个部委或来源的资料检索、规范（如 GB/T 9704）对标核查、为每个文种分别补写 `## 撰写思路` 或范文。
- 不必顾虑开启了多少 agents，也不必为并行的计算开销做权衡：正确且快速拿到结果优先。
- 写文件的并行子任务要划清边界、各改各的文件，避免同一文件并发写冲突；汇总、去重、跨文件一致性判断等需要全部结果的步骤再设一道汇合点。
- 只有当子任务之间存在真实依赖、必须串行时才退回顺序执行；其余能并行的部分一律并行，不为「省资源」把本可并行的工作串行化。
- 并行子任务一律只读或只改自己负责的文件，不擅自 `git push`、不重建产物；产物重建与 `--check`、`pytest` 验证由主流程统一收口。

## 语言（中文优先）

- 默认用中文沟通、中文说明。本仓是中文公文项目，**一切面向人读的内容默认中文**。
- 文档与说明：`README.md`、`AGENTS.md`、`CLAUDE.md`、`docs/references/`、`skills/*/SKILL.md`、`docs/` 下的设计/计划文档、样例说明等正文一律中文；**历史遗留的英文文档应改写为中文**，不保留中英混排的旧稿。
- 代码注释与 docstring：新增或修改的注释、docstring 默认中文；仅外部 API 协议、第三方固定术语、英文异常原文，或用户明确要求时才保留英文。
- 终端输出与日志：新增或修改 `print`、`echo`、`logging` 等用户可见输出时，能用中文说明的地方默认中文；保留必要的字段名、JSON key、`key=value` 机器可解析片段、CLI 参数、API 名称、类名、异常类型、文件路径和第三方英文原文，不为翻译破坏可解析契约。
- 提交信息：commit 标题与正文默认中文，可保留必要的英文专有名词、API 名称和 conventional 类型前缀。
- 标识符例外：变量名、函数名、类名、CLI 参数、配置键、文件路径等代码标识符按既有英文风格，不强行中文化。

## 约定

- 未经明确要求不要 `git push`；改动默认只落本地。
- 不引入第三方 Python 依赖（脚本只用标准库，需要 `tomllib`，Python 3.11+）。
- Claude Code 等宿主从根目录 `CLAUDE.md` 入口加载本仓约定；`CLAUDE.md` 只是兼容入口，指回本文件（AGENTS.md），不重复维护规则。
