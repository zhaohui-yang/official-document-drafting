# 公文写作 Skill

<a id="toc"></a>

## 目录

- [一、安装](#install)
- [二、使用](#usage)
- [三、项目概览](#overview)
- [四、当前能力](#capabilities)
- [五、Word 导出与版式](#word-export)
- [六、图片、附件与附录](#images-attachments-appendices)
- [七、结构校验](#validation)
- [八、规则体系](#rules)
- [九、构建与目录说明](#build-and-maintain)
- [十、字体与依赖](#fonts-and-deps)
- [十一、合规与使用声明](#compliance)
- [十二、设计原则](#principles)
- [十三、License](#license)
- [十四、公开参考来源](#references)

<a id="install"></a>

## 一、安装

### （一）在线工具中的 Skill 安装

适用于 Codex、agents 或其他兼容 `~/.codex/skills/` 目录的宿主环境。

从 GitHub 安装：

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
python3 "$CODEX_HOME/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo zhaohui-yang/official-document-drafting \
  --path . \
  --name official-document-drafting
```

如果你的宿主把 Codex 安装在其他目录，优先改 `CODEX_HOME`，不要把路径写死成某一台机器上的绝对路径。

从本地复制安装：

```bash
mkdir -p ~/.codex/skills
cp -R ./official-document-drafting ~/.codex/skills/
```

安装后，目标目录通常是：

- Linux / macOS / UOS / 麒麟等类 Unix 系统：`~/.codex/skills/official-document-drafting`
- Windows：`%USERPROFILE%\\.codex\\skills\\official-document-drafting`

### （二）Claude Code 安装

如果你的宿主是 Claude Code，更接近的安装目录通常是 Claude 自己的 skills 目录，而不是 `~/.codex/skills/`。

个人级安装：

```bash
mkdir -p ~/.claude/skills
cp -R ./official-document-drafting ~/.claude/skills/
```

项目级安装：

```bash
mkdir -p ./.claude/skills
cp -R ./official-document-drafting ./.claude/skills/
```

安装完成后，目标目录通常是：

- Linux / macOS / UOS / 麒麟等类 Unix 系统：`~/.claude/skills/official-document-drafting`
- Windows：`%USERPROFILE%\\.claude\\skills\\official-document-drafting`

### （三）不同操作系统说明

Linux、UOS、麒麟等类 Linux 系统可直接使用上面的 `bash` 命令。

Windows 如使用 PowerShell，可按同样目录结构复制：

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills" | Out-Null
Copy-Item -Recurse -Force .\official-document-drafting "$env:USERPROFILE\.codex\skills\official-document-drafting"
```

如在 Windows 上通过 WSL 运行 Codex 或 Python，优先沿用 Linux 方式安装和执行脚本。

Windows 如需通过 `skill-installer` 从 GitHub 安装，可使用：

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }
python "$codexHome\skills\.system\skill-installer\scripts\install-skill-from-github.py" `
  --repo zhaohui-yang/official-document-drafting `
  --path . `
  --name official-document-drafting
```

### （四）单机离线模式

这一节只对应 `adapters/offline/` 这一类离线提示词适配器，不代表整个 `adapters/` 目录都只服务离线场景。

进一步查看：

- [adapters/offline/README.md](./adapters/offline/README.md)：离线适配器的单独使用说明。
- [adapters/offline/build.py](./adapters/offline/build.py)：离线提示词构建入口脚本。
- [dist/offline/default/system_prompt.md](./dist/offline/default/system_prompt.md)：默认 profile 生成的正式离线全量 `system_prompt` 产物。
- [dist/offline/default/doc-types/](./dist/offline/default/doc-types/)：每个文种单独可用的离线 prompt 产物目录。

如果你的环境是 WebUI、AnythingLLM、Qwen 本地前端或其他单机模型前端，通常不需要先安装为 skill；保留仓库目录即可，直接使用离线提示词构建器：

```bash
python3 adapters/offline/build.py
```

如果你想先看看离线模式下正式使用的 `system_prompt` 大致长什么样、包含哪些规则，可以直接参考：

- 全量规则产物：[dist/offline/default/system_prompt.md](./dist/offline/default/system_prompt.md)
- 单文种 prompt 目录：[dist/offline/default/doc-types/](./dist/offline/default/doc-types/)

如果你的单机模型偏弱，优先直接使用当前文种目录下的 `prompt.md`，例如：

- [报告 prompt](./dist/offline/default/doc-types/report-%E6%8A%A5%E5%91%8A/prompt.md)
- [通知 prompt](./dist/offline/default/doc-types/notice-%E9%80%9A%E7%9F%A5/prompt.md)
- [请示 prompt](./dist/offline/default/doc-types/request-%E8%AF%B7%E7%A4%BA/prompt.md)
- [纪要 prompt](./dist/offline/default/doc-types/minutes-%E7%BA%AA%E8%A6%81/prompt.md)

直接运行 `python3 adapters/offline/build.py` 时，默认会重建：

- [dist/offline/default/system_prompt.md](./dist/offline/default/system_prompt.md)：全量离线 `system_prompt`
- [dist/offline/default/doc-types/](./dist/offline/default/doc-types/)：各文种单独可用的离线 prompt

只有在你想“只生成某一部分”或“按当前任务即时拼装提示词”时，才需要再传特殊参数。

更准确地说：

- `Codex / agents / 兼容 skill 宿主`：按上面的方式安装到 `~/.codex/skills/`
- `Claude Code`：按上面的方式安装到 `~/.claude/skills/` 或项目内 `./.claude/skills/`
- `WebUI / AnythingLLM / 本地问答前端`：一般不走 skill 安装，直接使用 `adapters/offline/build.py` 生成提示词

如果你想按仓库内置样例完整走一遍“长原始素材 -> 提炼材料 -> 生成提示词 -> 本地宿主 -> Word 导出”的流程，可以直接看：

- [demo/offline/raw-materials/](./demo/offline/raw-materials/)：断网场景下已下载到本地的长原始素材汇编。
- [demo/offline/report-报告/](./demo/offline/report-%E6%8A%A5%E5%91%8A)：离线报告样例目录。
- [demo/offline/notice-通知/](./demo/offline/notice-%E9%80%9A%E7%9F%A5)：离线通知样例目录。
- [demo/offline/request-请示/](./demo/offline/request-%E8%AF%B7%E7%A4%BA)：离线请示样例目录。
- [demo/offline/minutes-纪要/](./demo/offline/minutes-%E7%BA%AA%E8%A6%81)：离线纪要样例目录。

<a id="usage"></a>

## 二、使用

### （一）联网场景：Codex / agents

显式触发 skill：

```text
$official-document-drafting
请根据材料起草一份情况专报
```

常见示例：

- `搜索网络，生成一份关于“我的刀盾”网络传播情况的正式报告，并导出 Word。`
- `搜索网络，生成一份关于“我的刀盾”网络动态简报，并导出 Word。`
- `根据公开网络材料，起草一份关于开展“我的刀盾”传播素材整理工作的通知。`
- `根据公开网络材料和内部安排，起草一份关于申请开展“我的刀盾”传播案例梳理工作的请示。`
- `根据会议材料整理一份关于研究“刀盾”网络传播情况的专题会议纪要。`

使用建议：

- 联网场景更适合处理新闻、政策动态、公开网页材料整理
- 涉及“当前”“最新”“今日”等时效词时，应先核验来源和日期
- 如需保存文件但未指定路径，默认会写入 `~/official-document-drafting-output/`

对应的在线示例目录：

- [demo/online/report-报告/](./demo/online/report-%E6%8A%A5%E5%91%8A)：联网场景下围绕“我的刀盾”网络传播情况的报告样例目录。
- [demo/online/briefing-简报/](./demo/online/briefing-%E7%AE%80%E6%8A%A5)：联网场景下围绕“我的刀盾”网络动态的简报样例目录。
- [demo/online/notice-通知/](./demo/online/notice-%E9%80%9A%E7%9F%A5)：联网场景下围绕“我的刀盾”传播素材整理工作的通知样例目录。
- [demo/online/request-请示/](./demo/online/request-%E8%AF%B7%E7%A4%BA)：联网场景下围绕“我的刀盾”传播案例梳理工作的请示样例目录。
- [demo/online/minutes-纪要/](./demo/online/minutes-%E7%BA%AA%E8%A6%81)：联网场景下围绕“刀盾”传播情况研究的纪要完整样例目录。

### （二）联网场景：Claude Code

如果已安装到 `~/.claude/skills/` 或项目内 `./.claude/skills/`，可在 Claude Code 中直接调用对应 skill，或按宿主支持情况让其自动匹配到公文写作任务。

最小示例：

```text
/official-document-drafting
请根据材料起草一份正式报告
```

如果你的 Claude Code 当前项目依赖 `CLAUDE.md` 或项目说明文件，也可以把本仓库生成的规则和模板作为项目说明的一部分引入，但这不等同于 skill 安装。

### （三）单机场景：WebUI / Qwen

列出支持的文种：

```bash
python3 adapters/offline/build.py --list-doc-types
```

直接重建全部离线产物：

```bash
python3 adapters/offline/build.py
```

生成可直接粘贴到 WebUI 的离线提示词：

```bash
python3 adapters/offline/build.py \
  --doc-type 通知 \
  --instruction "起草一份关于开展2026年春季安全检查工作的通知，语气正式、结构清晰。" \
  --material-file ./素材.md \
  -o /tmp/20260404-春季安全检查通知-v01-提示词.md
```

如需附带当前文种示例：

```bash
python3 adapters/offline/build.py \
  --doc-type 专报 \
  --instruction "根据材料整理一份领导看的情况专报，先事实后研判。" \
  --material-file ./news.md \
  --include-examples \
  -o /tmp/20260404-热点舆情情况专报-v01-提示词.md
```

如果前端支持单独的系统提示词输入框，就把输出中的 `# System Prompt` 和 `# User Prompt` 分开使用；如果只有一个输入框，就把整份内容一起粘贴。

如果你不想每次临时拼装，也可以直接打开已生成好的单文种产物：

- [dist/offline/default/doc-types/report-报告/prompt.md](./dist/offline/default/doc-types/report-%E6%8A%A5%E5%91%8A/prompt.md)
- [dist/offline/default/doc-types/notice-通知/prompt.md](./dist/offline/default/doc-types/notice-%E9%80%9A%E7%9F%A5/prompt.md)
- [dist/offline/default/doc-types/request-请示/prompt.md](./dist/offline/default/doc-types/request-%E8%AF%B7%E7%A4%BA/prompt.md)
- [dist/offline/default/doc-types/minutes-纪要/prompt.md](./dist/offline/default/doc-types/minutes-%E7%BA%AA%E8%A6%81/prompt.md)

如需按仓库里的完整离线样例模拟，可以直接照这个流程：

1. 先看 [demo/offline/raw-materials/20260404-我的刀盾-原始素材汇编-v01.md](./demo/offline/raw-materials/20260404-%E6%88%91%E7%9A%84%E5%88%80%E7%9B%BE-%E5%8E%9F%E5%A7%8B%E7%B4%A0%E6%9D%90%E6%B1%87%E7%BC%96-v01.md)，确认你手里已有的长原始素材。
2. 再看目标文种目录里的 `task.md` 和 `materials.md`，例如 [demo/offline/report-报告/](./demo/offline/report-%E6%8A%A5%E5%91%8A)。
3. 用同一批本地素材生成提示词：

```bash
python3 adapters/offline/build.py \
  --doc-type 报告 \
  --instruction-file demo/offline/report-报告/task.md \
  --material-file demo/offline/raw-materials/20260404-我的刀盾-原始素材汇编-v01.md \
  --material-file demo/offline/report-报告/materials.md \
  -o demo/offline/report-报告/20260404-关于“我的刀盾”网络传播情况的报告-v01-提示词.md
```

4. 把生成好的 `...-提示词.md` 粘贴到本地前端。
5. 拿到 Markdown 成稿后，用 Python 再导出 `.docx`：

```bash
python3 renderers/docx.py \
  demo/offline/report-报告/20260404-关于“我的刀盾”网络传播情况的报告-v01.md \
  -o demo/offline/report-报告/20260404-关于“我的刀盾”网络传播情况的报告-v01.docx \
  --doc-type 报告
```

### （四）AnythingLLM 场景

AnythingLLM 一般也不需要安装为 skill，更适合按“离线提示词宿主”来使用：

1. 先用 `python3 adapters/offline/build.py ...` 生成提示词
2. 将 `System Prompt` 放入 workspace instructions 或 system prompt
3. 将 `User Prompt` 作为当前任务输入
4. 素材可直接上传到 workspace，或先用 `--material-file` 拼入生成结果

如果你不想自己准备测试材料，可以直接拿 [demo/offline/](./demo/offline) 下现成的 `task.md`、`materials.md` 和 `...-提示词.md` 做本地验证。

最小示例：

```bash
python3 adapters/offline/build.py \
  --doc-type 报告 \
  --instruction "根据上传材料整理一份正式报告，语气稳、结构清晰。" \
  --material-file ./材料.md
```

### （五）Claude.ai / Claude Desktop 场景

Claude.ai 或 Claude Desktop 一般不走 skills 目录安装，更适合按“提示词宿主”来使用：

1. 先用 `python3 adapters/offline/build.py ...` 生成提示词
2. 如前端支持单独 system prompt，就把 `System Prompt` 和 `User Prompt` 分开使用
3. 如前端只有一个输入框，就把整份输出一起粘贴
4. 素材可直接粘贴上传，也可预先通过 `--material-file` 拼入生成结果

如果你想看离线提示词在真实仓库中的完整样子，可直接参考：

- [dist/offline/default/system_prompt.md](./dist/offline/default/system_prompt.md)：正式离线 `system_prompt`
- [dist/offline/default/doc-types/](./dist/offline/default/doc-types/)：按文种拆开的独立离线 prompt 产物
- [demo/offline/README.md](./demo/offline/README.md)：按“原始素材 -> 提炼材料 -> 提示词 -> 成稿 -> Word”组织的完整离线样例索引

### （六）不同文体的最小示例

进一步查看：

- [references/document-types.md](./references/document-types.md)：各文种适用场景与边界说明。
- [prompts/doc-types/](./prompts/doc-types)：全部单文种规则目录。
- [assets/templates/](./assets/templates)：各文种兼容模板和骨架示例。
- [demo/README.md](./demo/README.md)：按在线/离线和文种组织的示例索引。

报告：

```text
根据以下材料整理一份情况报告，重点写清基本情况、主要问题和下一步打算。
```

通知：

```text
起草一份关于开展节前安全检查的通知，写明总体要求、重点任务和有关要求。
```

请示：

```text
根据项目推进情况，起草一份关于申请专项经费支持的请示，写明背景、依据和请示事项。
```

纪要：

```text
根据会议材料整理一份专题会议纪要，写清会议认为、会议决定、责任分工和后续要求。
```

### （七）默认输出约定

- 新闻报告默认目录：`~/official-document-drafting-output/news-reports/`
- 一般公文草稿默认目录：`~/official-document-drafting-output/drafts/`
- 同名 `Markdown` 与 `Word` 文件默认放在同一目录
- 用户任务生成的最终成稿默认采用 `YYYYMMDD-标题-vNN` 命名；如同一次任务还会生成离线提示词、导出说明等辅助文件，则在版本号后追加产物类型后缀，如 `-提示词`、`-说明`

命名示例：

- Markdown：`~/official-document-drafting-output/news-reports/20260404-当前热点新闻报告-v01.md`
- Word：`~/official-document-drafting-output/news-reports/20260404-当前热点新闻报告-v01.docx`
- 离线提示词：`~/official-document-drafting-output/drafts/20260404-专项检查通知-v01-提示词.md`

<a id="overview"></a>

## 三、项目概览

这是一个面向 agents、Codex、Claude Code 以及 WebUI / AnythingLLM / Qwen / Claude.ai 等提示词宿主的中文公文与正式材料仓库。它以 `prompts/` 为单一主源，统一生成：

- 在线 skill 入口 [SKILL.md](./SKILL.md)
- agents 元数据 [agents/openai.yaml](./agents/openai.yaml)
- 离线系统提示词 [dist/offline/default/system_prompt.md](./dist/offline/default/system_prompt.md)
- 单文种离线 prompt 目录 [dist/offline/default/doc-types/](./dist/offline/default/doc-types/)
- 各文种兼容模板 [assets/templates/](./assets/templates)
- 在线与离线完整样例 [demo/](./demo)

其中，`adapters/` 不是“离线目录”，而是“面向不同消费端的适配层”：

- `adapters/skill/`：把 `prompts/` 主源适配成 Codex、agents、Claude Code 等在线 skill / agent 宿主可直接使用的产物
- `adapters/offline/`：把 `prompts/` 主源适配成 WebUI、AnythingLLM、Qwen、Claude.ai 等提示词宿主可直接使用的离线或半离线提示词产物

进一步查看：

- [prompts/](./prompts)：全部规则和 profile 的主源目录。
- [adapters/](./adapters)：不同宿主环境的适配层目录。
- [dist/](./dist)：正式构建产物目录。
- [assets/templates/](./assets/templates)：按文种导出的兼容模板目录。

### （一）文种覆盖范围

法定公文 `15` 种：决议、决定、命令（令）、公报、公告、通告、意见、通知、通报、报告、请示、批复、议案、函、纪要。

常见正式材料 `7` 种：工作总结、工作方案 / 实施方案、讲话稿 / 发言稿、汇报材料、回复函、简报 / 信息简报 / 新闻简报、情况专报 / 信息专报 / 舆情专报。

所有文种的适用场景和差异边界见 [references/document-types.md](./references/document-types.md)。

<a id="capabilities"></a>

## 四、当前能力

可以处理：

- 文种判断与路由：根据事项性质、行文方向、主送对象判断通知、报告、请示、函、纪要等文种
- 共享规则 + 单文种规则：共享规则在 [prompts/core/](./prompts/core)，每个文种在 [prompts/doc-types/](./prompts/doc-types) 下有独立 `spec.md`
- 要素分层：每类文体的结构元素按 `必备 / 常见 / 条件项 / 地方或系统样式 / 项目自定义` 分层，而不是无脑堆砌
- 占位符补齐：用户未提供主送单位、落款、日期、联系人等信息时，默认保留占位符，不擅自虚构
- Markdown 结构校验：检查必备章节、标题层级、常见漏项
- `.docx` 导出：支持按文种自动套用字体方案和版式方案，导出结构化 Word 文件
- 真实图片嵌入：当前已支持在 Markdown 中用独立图片块把本地 `png / jpg / jpeg` 嵌入 `.docx`
- 附件 / 附图 / 附录图片说明：可为图片补充 `图号 / 标题 / 说明 / 注 / 来源 / 截至时间`
- 版记下沉：如当前文种设置版记，导出时会尽量把版记整体压到最后一页底部

当前不保证：

- 未经核验的“最新新闻”真实性和完整性
- 最终对外正式红头件版式完全符合某一单位内部模板
- 未提供依据情况下的真实政策条款、文件号、会议结论和统计数据
- 远程图片 URL、正文行内图片、复杂图文混排

进一步查看：

- [prompts/core/](./prompts/core)：共享规则主源目录。
- [prompts/doc-types/](./prompts/doc-types)：单文种规则主源目录。
- [renderers/docx.py](./renderers/docx.py)：Word 导出语义化入口。
- [renderers/validate.py](./renderers/validate.py)：结构校验语义化入口。

<a id="word-export"></a>

## 五、Word 导出与版式

### （一）导出入口

- 语义化入口：[renderers/docx.py](./renderers/docx.py)
- 核心实现：[scripts/generate_docx.py](./scripts/generate_docx.py)

最小导出：

```bash
python3 renderers/docx.py \
  ~/official-document-drafting-output/drafts/20260404-专项检查通知-v01.md \
  -o ~/official-document-drafting-output/drafts/20260404-专项检查通知-v01.docx
```

按文种自动套用字体和版式：

```bash
python3 renderers/docx.py \
  ~/official-document-drafting-output/drafts/20260404-专项检查通知-v01.md \
  -o ~/official-document-drafting-output/drafts/20260404-专项检查通知-v01.docx \
  --doc-type 通知
```

查看当前解析后的字体与版式方案：

```bash
python3 scripts/generate_docx.py --doc-type 通知 --show-font-plan
python3 scripts/generate_docx.py --doc-type 通知 --show-layout-plan
```

列出当前可用方案：

```bash
python3 scripts/generate_docx.py --list-font-profiles
python3 scripts/generate_docx.py --list-layout-profiles
```

### （二）当前排版行为

当前 `.docx` 导出已支持：

- A4 页面
- 按文种套用字体与版式方案
- 标题、一级标题、二级标题、正文分字体字号
- 正文首行缩进 2 字符
- 标题自动均衡断行
- 页脚页码默认自第二页起显示，首页不显示页脚，且页脚本身不写入显式底纹或高亮
- 主送单位后不额外加段后距、落款前距、成文日期右空 4 字
- 正文与落款之间默认空 3 行
- 附注默认位于成文日期下一行左空 2 字
- 如存在版记，版记整体压到最后一页底部，空间不足时整块移页

当前基线版式和边界说明见 [references/layout-rules.md](./references/layout-rules.md)。

如需关闭页码，可在导出时增加：

```bash
python3 renderers/docx.py \
  ~/official-document-drafting-output/drafts/20260404-专项检查通知-v01.md \
  -o ~/official-document-drafting-output/drafts/20260404-专项检查通知-v01.docx \
  --hide-page-number
```

### （三）版头、发文字号、版记

导出器支持以下结构块：

- `## 版头（可选）`
- `## 发文字号（可选）`
- `## 版记（可选）`

示例：

```md
## 版头（可选）
XX市教育局文件

## 发文字号（可选）
X教发〔2026〕3号	签发人：张三

## 标题
关于开展2026年春季校园安全联合检查工作的通知
```

注意：

- 版记不是所有文种的默认结构
- 是否保留版记，取决于文种 `spec.md`、用户模板或系统样式
- 标准公文常见版记要素通常是 `抄送机关、印发机关、印发日期`
- `主送移入版记`、`分送`、`报/送/发` 属地方或系统样式
- `审核` 属本项目内部模板字段

进一步查看：

- [references/layout-rules.md](./references/layout-rules.md)：当前基线版式与边界说明。
- [prompts/layout-profiles/](./prompts/layout-profiles)：各版式方案配置目录。
- [prompts/font-profiles/](./prompts/font-profiles)：各字体方案配置目录。
- [scripts/generate_docx.py](./scripts/generate_docx.py)：Word 导出底层实现。

<a id="images-attachments-appendices"></a>

## 六、图片、附件与附录

### （一）当前支持的图片方式

当前版本已经支持在 Markdown 中用独立图片块把本地图片真实嵌入 `.docx`：

```md
![图1 现场照片](./demo/sample.png)
```

支持范围：

本地文件、`png / jpg / jpeg`、独立图片块、路径相对当前 Markdown 文件解析。

当前限制：

不支持远程 URL、不支持正文行内图片、不支持 `webp`、不支持复杂环绕排版。

### （二）推荐放置位置

普通公文和内部材料中，图片默认更适合放在：

`附件`、`附图`、`附表`。

只有技术指南、操作手册、标准性说明、规范附表等更偏技术资料的文本，才默认允许使用：

`附录A`、`附录B`。

### （三）图片说明建议

图片不要裸放，至少应包含：

图片编号、图片标题、说明文字。

按需要再补：

`注`、`来源`、`截至时间`、`仅供示意，以正式图件为准`。

示例：

```md
## 附件1（可选）

图1：现场宣传海报

![图1 现场宣传海报](./demo/poster.png)

说明：活动现场设置的主题宣传海报。
来源：项目组现场拍摄。
截至时间：2026年4月。
```

进一步查看：

- [prompts/core/style.md](./prompts/core/style.md)：图片说明和文字风格相关规则。
- [prompts/core/workflow.md](./prompts/core/workflow.md)：附件、附图、附录等处理流程规则。
- [demo/README.md](./demo/README.md)：带图片或附件结构的示例文稿索引。

<a id="validation"></a>

## 七、结构校验

校验入口：

- 语义化入口：[renderers/validate.py](./renderers/validate.py)
- 核心实现：[scripts/check_sections.py](./scripts/check_sections.py)

最小校验：

```bash
python3 renderers/validate.py notice ~/official-document-drafting-output/drafts/20260404-专项检查通知-v01.md
```

当前校验器会检查：

- 必备章节是否缺失
- 标题层级是否混乱
- 一级 / 二级 / 三级标题写法是否明显异常
- 是否存在常见结构漏项

进一步查看：

- [renderers/validate.py](./renderers/validate.py)：结构校验入口脚本。
- [scripts/check_sections.py](./scripts/check_sections.py)：章节校验底层实现。

<a id="rules"></a>

## 八、规则体系

### （一）共享规则

共享规则位于 [prompts/core/](./prompts/core)，主要负责：

- 文种判断流程
- 防编造与防幻觉约束
- 通用语言风格
- 标题与层级编号
- 通用版式与导出边界
- 附件、附注、版记、图片等共性要求

关键文件：

- [workflow.md](./prompts/core/workflow.md)：文种判断、结构补齐和处理流程总规则。
- [style.md](./prompts/core/style.md)：通用语言风格和表达约束。
- [layout.md](./prompts/core/layout.md)：通用版式、导出和排版边界。
- [doc-type-guardrails.md](./prompts/core/doc-type-guardrails.md)：防编造与事实核验总约束。

联系人与附注规则：

- 当前项目默认将 `请示、报告、通知、函、回复函、公告、通告` 设为保留附注联系人信息的文种。
- 默认格式为：`（联系人：[联系人] 联系电话：[固定电话]，[手机号]）`
- 这是本项目的默认起草口径，不等于所有公开样例都统一默认带联系人。
- 如用户明确要求删除，可在生成后手动删减。
- 是否最终保留，仍以具体文种规则、用户模板和单位制度为准。

进一步查看：

- [prompts/core/workflow.md](./prompts/core/workflow.md)：联系人、附注和结构保留的共享流程规则。
- [prompts/core/layout.md](./prompts/core/layout.md)：附注位置与版式的共享规则。
- [prompts/doc-types/request-请示/spec.md](./prompts/doc-types/request-请示/spec.md)：请示文种中的附注与联系人规则。
- [prompts/doc-types/notice-通知/spec.md](./prompts/doc-types/notice-通知/spec.md)：通知文种中的联系人和附注规则。

### （二）单文种规则

每个文种目录都包含：

- `meta.toml`：绑定 `font_profile` 与 `layout_profile`
- `spec.md`：写作规则、版式要求、模板
- `examples.md`：按需提供示例

例如：

- [prompts/doc-types/notice-通知/](./prompts/doc-types/notice-通知)：通知文种规则目录。
- [prompts/doc-types/report-报告/](./prompts/doc-types/report-报告)：报告文种规则目录。
- [prompts/doc-types/request-请示/](./prompts/doc-types/request-请示)：请示文种规则目录。
- [prompts/doc-types/minutes-纪要/](./prompts/doc-types/minutes-纪要)：纪要文种规则目录。

### （三）要素分层

当前版本不再把所有“可能出现的元素”都视为默认项，而是按文种分层解释：

- `必备`：相对稳定、默认保留
- `常见`：公开样例中高频出现，默认优先保留
- `条件项`：只在特定场景出现，例如会议通知里的联系人、技术资料里的附录
- `地方或系统样式`：属于地方、系统或单位模板习惯，不上升为全国通行必备项
- `项目自定义`：本项目为了目标模板定制的口径，不冒充通用规范

例如 `纪要` 中的 `主送 / 抄送 / 审核`，当前被明确标注为项目自定义内部模板字段，而不是所有纪要的通用国标版记。

<a id="build-and-maintain"></a>
<a id="repo-layout"></a>

## 九、构建与目录说明

### （一）单一主源维护顺序

推荐维护顺序：

1. 共享总规则：修改 [prompts/core](./prompts/core)
2. 共享防编造约束：修改 [prompts/core/doc-type-guardrails.md](./prompts/core/doc-type-guardrails.md)
3. 字体族和文件映射：修改 [assets/fonts/catalog.toml](./assets/fonts/catalog.toml)
4. 复用型字体方案：修改 [prompts/font-profiles](./prompts/font-profiles)
5. 复用型版式方案：修改 [prompts/layout-profiles](./prompts/layout-profiles)
6. 单个文种规则：修改 [prompts/doc-types](./prompts/doc-types) 下对应目录
7. profile 元数据和系统前言：修改 [prompts/profiles/default.toml](./prompts/profiles/default.toml)
8. 补充说明：按需修改 [references/](./references)

### （二）构建命令

一键构建：

```bash
python3 scripts/build_all.py
```

只构建在线 skill：

```bash
python3 adapters/skill/build.py
```

只构建离线基础系统提示词：

```bash
python3 adapters/offline/build.py --emit-system
```

进一步查看：

- [scripts/build_all.py](./scripts/build_all.py)：一键构建全部正式产物。
- [adapters/skill/build.py](./adapters/skill/build.py)：在线 skill 产物构建入口。
- [adapters/offline/build.py](./adapters/offline/build.py)：离线提示词产物构建入口。
- [dist/](./dist)：构建完成后的正式产物目录。

### （三）目录结构（tree 视图）

如需直接跳到具体目录，可优先查看：

- [prompts/](./prompts)：规则、profile 和文种主源目录。
- [assets/](./assets)：字体和模板等静态资源目录。
- [adapters/](./adapters)：在线与离线适配层目录。
- [renderers/](./renderers)：导出与校验的语义化入口目录。
- [scripts/](./scripts)：底层构建、导出和校验脚本目录。
- [dist/](./dist)：正式构建产物目录。
- [demo/README.md](./demo/README.md)：示例文稿和导出样稿索引。

```text
.
├── prompts/                             规则主源目录
│   ├── core/                            共享规则主源
│   ├── doc-types/                       单文种规则主源
│   ├── font-profiles/                   字体方案主源
│   ├── layout-profiles/                 版式方案主源
│   └── profiles/default.toml            构建 profile 和系统前言
├── assets/                              静态资源目录
│   ├── fonts/                           本地字体目录
│   ├── fonts/catalog.toml               字体名称到字体文件的映射
│   └── templates/                       由各文种模板导出的兼容模板
├── adapters/                            不同宿主环境的适配层
│   ├── shared.py                        适配层共用读取与渲染辅助模块
│   ├── skill/build.py                   在线 skill 产物构建入口
│   └── offline/
│       ├── README.md                    离线提示词适配器使用说明
│       └── build.py                     离线或半离线提示词构建入口
├── renderers/                           语义化渲染入口
│   ├── docx.py                          Word 导出入口
│   └── validate.py                      结构校验入口
├── scripts/                             底层脚本实现
│   ├── build_all.py                     一键构建在线与离线产物
│   ├── generate_docx.py                 Word 导出核心实现
│   └── check_sections.py                章节校验核心实现
├── dist/                                正式构建产物目录
│   ├── skill/                           在线 skill 正式产物
│   └── offline/                         离线提示词正式产物
└── demo/                                示例文稿和导出样稿
    ├── README.md                        在线/离线示例索引
    ├── online/                          联网在线场景示例
    └── offline/                         离线提示词场景示例
```

<a id="fonts-and-deps"></a>

## 十、字体与依赖

### （一）Python 依赖

当前版本的脚本只使用 Python 标准库，[requirements.txt](./requirements.txt) 仍保留为统一依赖入口。

如需按统一流程准备环境：

```bash
python3 -m pip install -r requirements.txt
```

### （二）字体安装

当前推荐做法：

1. 下载字体到 [assets/fonts](./assets/fonts)
2. 运行安装脚本
3. 再执行 Word 导出

下载最小字体集：

```bash
bash scripts/download_fonts.sh minimal
```

安装字体：

```bash
bash scripts/install_fonts.sh
```

也可以直接使用字体预设：

```bash
python3 renderers/docx.py \
  ~/official-document-drafting-output/drafts/20260404-专项检查通知-v01.md \
  -o ~/official-document-drafting-output/drafts/20260404-专项检查通知-v01.docx \
  --font-preset noto-cjk
```

说明：

- `.docx` 默认记录字体名称，不自动嵌入字体二进制
- 如果需要稳定锁定视觉效果，应在已安装目标字体的机器上导出最终 PDF
- 商用字体分发需自行确认授权边界

<a id="compliance"></a>

## 十一、合规与使用声明

以下要求建议逐项理解并执行：

1. **合规优先**：合规是第一要求。宁可留空、待核实，也不得编造；凡无法核实、依据不足、来源不明或口径冲突的内容，均应保守处理，不得为了成稿完整性强行补齐。
2. **项目定位与非保证边界**：本项目仅提供公文模板、结构参考、语言规范化和排版导出辅助，不构成法律意见、政策解释、正式发文授权或任何保证性结论，也不当然代表某一单位最终定稿口径。
3. **用途边界**：本项目仅用于辅助起草、整理、规范化中文公文与正式材料，不得用于伪造公文、冒用机关或单位名义、虚构会议、虚构批示、虚构事实、误导性报送、规避监管或其他违法违规用途。
4. **真实性优先**：涉及政策依据、法律条款、文件号、机构名称、会议结论、领导表态、统计数据、时间地点和新闻事实的内容，均应以可核实来源为准；未经核实的内容，不得写成确定事实。
5. **时效性内容必须复核**：对“当前”“最新”“今日”“近日”等时效性任务，必须同时核对来源、发布日期和事件发生日期；如无法核实，应明确标注“待核实”，而不是用经验补全。
6. **不为润色而补造事实**：无论用户要求“润色、扩写、补全、规范化”，都只能在现有事实边界内展开，不得借机虚构背景、数字、依据、过程、表态或结论。
7. **文种和程序边界**：文种判断应服从真实行文目的，不得把“请示”写成“报告”、把“函”写成“通知”、把内部沟通稿写成可直接对外发布的正式公文；用户或单位模板另有要求时，应以真实办文程序为准。
8. **占位符不是事实**：主送单位、落款、日期、联系人、版记、审核、附件名称、会议元数据等占位符仅用于起草阶段补齐结构，不代表真实信息。正式使用前，必须逐项替换、删除或确认，不得带占位符直接报送、印发或公开。
9. **项目自定义字段不等于通用规范**：本项目中的部分结构属于项目模板或系统样式，例如某些文种的附注联系人、纪要中的 `主送 / 抄送 / 审核` 等。这些字段用于提高起草效率，不当然代表全国统一通行格式，落地时仍须服从本单位模板和制度。
10. **图片、附件与附录的合规责任**：当前版本支持附件图片说明和本地真实图片嵌入 `.docx`，但图片内容、图片来源、截图真实性、拍摄时间、版权授权和对外使用边界，均需由使用者自行确认。不得插入未经授权传播的图片、截图或涉敏感图件。
11. **引用外部材料时要核来源和权限**：引用新闻、报告、统计、网页、截图、公众号、第三方图表、会议材料或其他外部文本时，应核对来源真实性、引用口径和转载授权；如来源不稳、时间不清或版权不明，应避免作为正式依据使用。
12. **敏感信息与保密要求**：不得将国家秘密、工作秘密、商业秘密、个人敏感信息、未公开会议材料、内部台账、受限截图或其他未经授权披露的信息输入本项目或相关模型环境。涉及涉密、涉敏感、涉执法、涉舆情、涉人事、涉隐私内容时，应先做脱敏和权限判断。
13. **对外发布前必须人工审核**：涉及正式发文、对外报送、政策解读、法律敏感、涉密、涉舆情、可能影响单位权责或公众判断的文本，必须经过有权限的人员人工审核后方可使用。模型生成稿只能视为草稿，不应直接等同于正式定稿。
14. **版式导出不等于正式发文**：即使 `.docx` 已完成字体、版式、附注、版记、页码、图片等排版处理，也不代表当然符合某一单位最终发文模板。对外正式红头件、盖章件、签发件、编号件，仍应套用本单位现行 Word 模板并做最后核定。
15. **最终清稿责任在使用者**：正式定稿前，应逐项检查错别字、漏字、多字、病句、标点误用、数字日期、机构名称、称谓、附件序号、图片说明、联系人信息、落款日期、占位符残留和文种是否用对。因使用、修改、发布或报送相关内容产生的责任，由最终使用者承担。
16. **适用场景边界**：当前版本更适合内部草稿、内部流转稿、汇报稿、简报、专报和正式公文正文初稿；对外正式发文、盖章件、红头件和编号件，仍应使用本单位现行模板做最后核定。
17. **复杂版式边界**：当前真实图片嵌入仅支持本地块级图片，不适合复杂宣传册式排版、远程图片混排或高度定制化图文页面。
18. **模板替代边界**：文种默认模板和项目自定义字段是为了提高起草效率，不替代单位正式模板，不当然代表全国统一通行格式。
19. **最终审定边界**：项目输出只能视为结构化草稿和排版辅助结果，不能替代单位内部审签、核稿、套版、编号、盖章和正式发文流程。

<a id="principles"></a>

## 十二、设计原则

- 先判断文种是否正确，再润色语言
- 先核对事实和时间，再整理成稿
- 不把地方或系统样式误写成全国通行必备格式
- Markdown 成稿与 `.docx` 导出分离，先定结构再做版式
- 对图片、附件、附录、版记、附注等扩展要素，默认按“有依据才保留”的原则处理

<a id="license"></a>

## 十三、License

- 仓库中的原创代码与文档采用 [MIT License](./LICENSE)
- 第三方字体和其他二进制资源可能适用各自的许可条款，不因本仓库的 MIT 许可证而自动改变授权边界

<a id="references"></a>

## 十四、公开参考来源

以下来源在项目规则演化过程中被反复用于核对文种边界、结构写法、版式口径和机关样例：

- 沈阳市人民政府：关于进一步规范行政机关公文处理工作的通知
  https://www.shenyang.gov.cn/zwgk/zcwj/zfwj/szfbgtwj1/202112/t20211201_1701386.html
- 辽宁省人民政府：辽宁省人民政府办公厅关于印发《辽宁省行政机关公文格式细则》的通知
  https://www.ln.gov.cn/web/zwgkx/zfwj/szfbgtwj/zfwj2004/7ED90F8968BD491FB190A231069CA87B/index.shtml
- 紫阳县人民政府：关于规范政府机关公文格式的通知
  https://www.zyx.gov.cn/Content-1778525.html
- 安康市人民政府：党政机关公文处理如何走向“统一”
  https://www.ankang.gov.cn/Content-2060366.html
- 平凉市发改委：机关公文处理实施细则
  https://fgw.pingliang.gov.cn/gzzd/art/2022/art_58cb4a2b5abe4509a554bc7951638496.html
