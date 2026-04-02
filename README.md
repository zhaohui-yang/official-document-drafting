# 公文写作 Skill

## 合规与使用声明

> **合规是第一要求。宁可留空、待核实，也不得编造。**
>
> **本项目仅提供公文模板、结构参考、语言规范化和排版导出辅助，不构成法律意见、政策解释、正式发文授权或任何保证性结论。**

- 本项目旨在辅助起草、整理、规范化中文公文及正式材料，不得用于伪造公文、冒用机关或单位名义、虚构事实、误导性报送、规避监管或其他违法违规用途。
- 使用本项目时，必须遵守适用的法律法规、保密要求、单位制度、行业规范及信息发布流程。
- 涉及政策依据、法律条款、文件号、机构名称、会议结论、领导表态、统计数据、时间地点和新闻事实的内容，均应由使用者自行核实；未经核实的信息不得作为正式事实使用。
- 对于“当前新闻”“最新动态”“今日情况”等时效性内容，必须先核对来源、发布日期和事件日期，再整理成稿。
- 用户未提供或无法核实的信息，应使用占位符或明确标注“待核实”，不得擅自补齐成既成事实。
- 涉及正式发文、对外报送、政策敏感、法律敏感、涉密、涉隐私或可能产生权利义务影响的文本，必须经过具备相应权限的人员人工审核后方可使用。
- 不得将任何秘密信息、商业秘密、个人敏感信息或其他未经授权披露的信息输入本项目或相关模型环境。
- 本项目不保证输出内容当然合法、真实、完整、准确或符合特定单位版式要求；因使用、修改、发布或报送相关内容产生的责任，由使用者自行承担。

正式定稿前，请务必结合本单位制度、业务要求和人工审核意见进行复核。

这是一个面向 agents 的中文公文与正式材料 skill，覆盖法定公文 15 种以及机关、事业单位、国企等场景中的高频正式材料，支持成稿、改写、规范化和 `.docx` 导出。

当前版本同时支持两种使用方式：

- `agent / skill mode`：在 Codex、agents 等环境中通过生成后的 [SKILL.md](./SKILL.md) 触发
- `standalone / offline mode`：在断网单机的 WebUI + Qwen 场景中，通过 [adapters/webui/build.py](./adapters/webui/build.py) 生成离线提示词

## Quick Start

1. 安装 skill 到 `~/.codex/skills/official-document-drafting`
2. 在 agents 或 Codex 中显式使用 `$official-document-drafting`
3. 直接输入：`总结当前热点新闻并且形成报告`

如需从 GitHub 安装：

```bash
python3 /root/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo zhaohui-yang/official-document-drafting \
  --path . \
  --name official-document-drafting
```

如需从本地复制：

```bash
mkdir -p ~/.codex/skills
cp -R ./official-document-drafting ~/.codex/skills/
```

## 默认样例

唯一推荐样例：

```text
总结当前热点新闻并且形成报告
```

处理约定：

- 先核验“当前热点新闻”的来源、发布日期和事件日期，再整理为正式材料。
- 文种一般优先落在“简报”“专报”或“报告”，并按正式机关材料结构输出。
- 如果用户要求保存文件但未指定路径，默认创建目录并落盘，再在回复中明确提示最终文件路径。

## 默认输出约定

- 新闻报告默认目录：`~/official-document-drafting-output/news-reports/`
- 一般公文草稿默认目录：`~/official-document-drafting-output/drafts/`
- 同名 `Markdown` 与 `Word` 文件默认放在同一目录

默认命名示例：

- Markdown：`~/official-document-drafting-output/news-reports/当前热点新闻报告（YYYY年M月D日）.md`
- Word：`~/official-document-drafting-output/news-reports/当前热点新闻报告（YYYY年M月D日）.docx`

## 运行模式

### Agent / Skill Mode

- 保留当前 [SKILL.md](./SKILL.md) 与 [agents/openai.yaml](./agents/openai.yaml) 的用法
- 适用于 Codex、Claude 类 agent 或支持技能加载的宿主
- 这两个文件由 [prompts/](./prompts) 主源通过 [adapters/skill/build.py](./adapters/skill/build.py) 生成

### Standalone / Offline Mode

- 适用于断网单机的 WebUI + Qwen 场景
- 不依赖宿主自动读取 `SKILL.md`
- 通过 [adapters/webui/build.py](./adapters/webui/build.py) 或兼容包装脚本 [scripts/build_offline_prompt.py](./scripts/build_offline_prompt.py) 使用
- 离线提示词直接读取 [prompts/core](./prompts/core)、[prompts/doc-types](./prompts/doc-types) 和 [prompts/profiles/default.toml](./prompts/profiles/default.toml)
- 当前功能保留不变，只是在原有模板和规则之外新增一层离线提示词工程

## 能力与边界

可以处理：

- 通知、请示、报告、函、纪要、决定、意见等法定公文
- 简报、专报、汇报材料、讲话稿、方案、回复函等常见正式材料
- 当前新闻整理、正式中文成稿、Markdown 结构校验、`.docx` 导出

不能默认保证：

- 未经核验的“最新新闻”真实性和完整性
- 最终对外正式红头件版式
- 未提供依据情况下的真实政策条款、文件号、会议结论和数据

交付前要求：

- 成稿前必须认真仔细校对，重点检查错别字、漏字、多字、病句、语病、标点误用、数字日期错误、称谓和机构名称错误，避免带明显文字差错交付。

以下命令示例默认假设 Markdown 成稿已保存在 `~/official-document-drafting-output/drafts/`。

适用边界：

- 当前版本更适合内部草稿、内部流转稿、汇报稿、简报、专报和正式公文正文初稿。
- 如果要形成可直接对外发出的正式红头文件，仍建议套用本单位现成 Word 模板并做人工复核。
- 正文中如使用“一是、二是、三是”等分点衔接语，默认应在同一自然段内连续书写，不将每一点分别另起自然段；除非用户明确要求逐条分段，或单一点内容明显过长、确需单独强调。关键词宜用黑体或同等强调字体与正文区分。

## 最小验证

结构校验：

```bash
python3 renderers/validate.py notice ~/official-document-drafting-output/drafts/通知示例.md
```

安装字体：

```bash
bash scripts/install_fonts.sh
```

导出 Word：

```bash
python3 renderers/docx.py \
  ~/official-document-drafting-output/drafts/通知示例.md \
  -o ~/official-document-drafting-output/drafts/通知示例.docx
```

红头增强导出：

```bash
python3 renderers/docx.py \
  ~/official-document-drafting-output/drafts/红头通知示例.md \
  -o ~/official-document-drafting-output/drafts/红头通知示例.docx \
  --font-preset noto-cjk \
  --show-page-number \
  --title-wrap auto
```

## 覆盖范围

### 法定公文 15 种

- 决议
- 决定
- 命令（令）
- 公报
- 公告
- 通告
- 意见
- 通知
- 通报
- 报告
- 请示
- 批复
- 议案
- 函
- 纪要

### 常见正式材料

- 工作总结
- 工作方案 / 实施方案
- 讲话稿 / 发言稿
- 汇报材料
- 回复函
- 信息简报 / 新闻简报
- 情况专报 / 信息专报 / 舆情专报

所有文种和材料的适用场景、结构建议和使用提醒，见 [references/document-types.md](./references/document-types.md)。

## 目录说明

- `prompts/core/`：共享总规则，供在线 skill 和离线 prompt 共用。
- `prompts/core/doc-type-guardrails.md`：共享的防编造 / 防幻觉强制约束，会自动作用到每个文种。
- `prompts/doc-types/<英文-中文目录>/`：每个文种自己的规范和元数据；`meta.toml` 维护结构化字段，当前同时包含 `font_profile` 和 `layout_profile`，`spec.md` 统一包含“写作规则 / 版式要求 / 模板”。
- `prompts/font-profiles/`：字体方案主源，定义每种文种可复用的字体槽位和字号。
- `prompts/layout-profiles/`：版式方案主源，定义正文行距、标题后距、主送机关后距、落款前距、正文首行缩进等精细参数。
- `prompts/profiles/default.toml`：profile 配置，定义 skill 元数据、agent 元数据、WebUI 系统提示词前言和共享章节顺序。
- `adapters/skill/build.py`：根据 `prompts/` 主源生成在线 skill 产物。
- `adapters/webui/build.py`：根据 `prompts/` 主源生成离线 WebUI / Qwen 提示词。
- `dist/`：生成产物目录，包含 `dist/skill/` 和 `dist/webui/`。
- `SKILL.md`：由 `prompts/` 主源生成的根目录 skill 入口文件。
- `agents/openai.yaml`：由 `prompts/` 主源生成的根目录 agents 界面元数据。
- `requirements.txt`：Python 依赖入口。当前版本无第三方依赖。
- `references/`：补充性的文种说明和行文规范参考，不是当前构建链路的唯一主源。
- `references/layout-rules.md`：版式、字号、换行、落款和脚本边界说明。
- `references/font-usage.md`：字体与导出行为速查。
- `assets/fonts/`：自备或脚本下载的字体目录。
- `assets/fonts/catalog.toml`：字体族注册表，定义字体名称与 `assets/fonts/` 中具体文件的映射。
- `assets/templates/`：由 `prompts/doc-types/*/spec.md` 中的“模板”章节导出的兼容模板目录。
- `assets/templates/official-types-outline.md`：由 `prompts/core/fallback-template.md` 导出的兜底骨架。
- `renderers/docx.py`：Markdown 转 `.docx` 的语义化入口。
- `renderers/validate.py`：Markdown 章节校验的语义化入口。
- `scripts/build_all.py`：一键生成在线 skill 和离线基础系统提示词。
- `scripts/build_offline_prompt.py`：兼容包装脚本，转发到 `adapters/webui/build.py`。
- `scripts/render_runtime_assets.py`：兼容包装脚本，转发到 `adapters/skill/build.py`。
- `scripts/check_sections.py`：旧的章节校验入口。
- `scripts/download_fonts.sh`：从官方开源来源下载推荐字体到 `assets/fonts/`。
- `scripts/generate_docx.py`：旧的 `.docx` 导出入口。
- `scripts/install_fonts.sh`：将 `assets/fonts/` 中的字体安装到当前用户字体目录。
- `~/official-document-drafting-output/`：默认生成目录；新闻报告默认写入 `news-reports/`，一般公文草稿默认写入 `drafts/`。

## 单一主源维护

推荐维护顺序：

1. 共享总规则：修改 [prompts/core](./prompts/core)
2. 共享的防编造约束：修改 [prompts/core/doc-type-guardrails.md](./prompts/core/doc-type-guardrails.md)
3. 字体族和文件映射：修改 [assets/fonts/catalog.toml](./assets/fonts/catalog.toml)
4. 复用型字体方案：修改 [prompts/font-profiles](./prompts/font-profiles)
5. 复用型版式方案：修改 [prompts/layout-profiles](./prompts/layout-profiles)
6. 单个文种的专项规范和字体/版式方案引用：修改 [prompts/doc-types](./prompts/doc-types) 下对应的 `英文-中文` 目录
7. profile 元数据和系统前言：修改 [prompts/profiles/default.toml](./prompts/profiles/default.toml)
8. 补充性规则说明：按需修改 [references/](./references)

一键构建：

```bash
python3 scripts/build_all.py
```

只构建在线 skill：

```bash
python3 adapters/skill/build.py
```

只生成离线基础系统提示词：

```bash
python3 adapters/webui/build.py --emit-system
```

列出支持的文种：

```bash
python3 adapters/webui/build.py --list-doc-types
```

这个结构的核心思路是：

- 每个文种的专项规则单独维护
- `skill` 负责“判断文种并调用底层规则 + 模板”
- 离线 WebUI / Qwen 也使用同一套底层规则和模板
- `SKILL.md`、`agents/openai.yaml`、`assets/templates/` 和 `dist/` 都是生成产物

兼容性说明：

- [scripts/build_offline_prompt.py](./scripts/build_offline_prompt.py) 仍可用，但推荐优先使用 [adapters/webui/build.py](./adapters/webui/build.py)
- [scripts/render_runtime_assets.py](./scripts/render_runtime_assets.py) 仍可用，但推荐优先使用 [adapters/skill/build.py](./adapters/skill/build.py)
- Word 导出和结构校验仍保留旧脚本入口，但推荐优先使用 [renderers/docx.py](./renderers/docx.py) 与 [renderers/validate.py](./renderers/validate.py)

## 模板清单

### 法定公文 15 种独立模板

- `assets/templates/resolution.md`：决议
- `assets/templates/decision.md`：决定
- `assets/templates/order.md`：命令（令）
- `assets/templates/communique.md`：公报
- `assets/templates/announcement.md`：公告
- `assets/templates/public-notice.md`：通告
- `assets/templates/opinion.md`：意见
- `assets/templates/notice.md`：通知
- `assets/templates/circular.md`：通报
- `assets/templates/report.md`：报告
- `assets/templates/request.md`：请示
- `assets/templates/approval.md`：批复
- `assets/templates/motion.md`：议案
- `assets/templates/letter.md`：函
- `assets/templates/minutes.md`：纪要

### 常见扩展模板

- `assets/templates/reply.md`：复函 / 回复函
- `assets/templates/work-plan.md`：工作方案 / 实施方案
- `assets/templates/summary.md`：工作总结
- `assets/templates/briefing.md`：简报 / 信息简报 / 新闻简报
- `assets/templates/special-report.md`：情况专报 / 信息专报 / 舆情专报
- `assets/templates/speech.md`：讲话稿 / 发言稿
- `assets/templates/presentation.md`：汇报材料
- `assets/templates/official-types-outline.md`：15 种法定公文骨架总表

## 安装依赖

当前版本的脚本只使用 Python 标准库，没有第三方依赖，但仍保留了统一的依赖入口文件 [requirements.txt](./requirements.txt)。

如需按统一流程准备环境，可以执行：

```bash
python3 -m pip install -r requirements.txt
```

这条命令在当前版本不会额外安装任何库；后续如果本 skill 引入 `python-docx` 等第三方包，只需要更新 `requirements.txt`，用户仍然使用同一条命令即可。

## 安装为 Skill

如果你希望让 Codex/agents 自动发现这个 skill，建议安装到 `~/.codex/skills/official-document-drafting`。

可以直接从 GitHub 安装：

```bash
python3 /root/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo zhaohui-yang/official-document-drafting \
  --path . \
  --name official-document-drafting
```

也可以直接从本地复制：

```bash
mkdir -p ~/.codex/skills
cp -R ./official-document-drafting ~/.codex/skills/
```

安装完成后，重启 Codex，使新 skill 被重新扫描并加载。

## 离线 WebUI / Qwen 模式

如果你的内网或单机环境只有 `WebUI + Qwen`，没有会自动加载 `skill` 的 agent，可以直接使用离线提示词模式。

查看当前离线模式支持的文种：

```bash
python3 adapters/webui/build.py --list-doc-types
```

生成一份可直接粘贴到 WebUI 的提示词：

```bash
python3 adapters/webui/build.py \
  --doc-type 通知 \
  --instruction "起草一份关于开展2026年春季安全检查工作的通知，语气正式、结构清晰。" \
  --material-file ./素材.md \
  -o /tmp/offline_prompt.md
```

如果需要少量示例增强文风，可增加：

```bash
python3 adapters/webui/build.py \
  --doc-type 专报 \
  --instruction "根据材料整理一份领导看的情况专报，先事实后研判。" \
  --material-file ./news.md \
  --include-examples \
  -o /tmp/offline_special_report_prompt.md
```

脚本输出包含两部分：

- `# System Prompt`
- `# User Prompt`

如果你的 WebUI 支持独立系统提示词框，就分开粘贴；如果只有一个输入框，整份一起粘贴即可。

兼容旧命令时，也可以继续使用 [scripts/build_offline_prompt.py](./scripts/build_offline_prompt.py)。

## 下载字体

当前仓库默认不提交开源替代字体文件。需要时，推荐执行：

```bash
bash scripts/download_fonts.sh minimal
```

这会下载一套最小可用字体到 [assets/fonts](./assets/fonts)：

- `Noto Serif SC`：作为标题近似替代“小标宋”
- `Noto Sans SC`：作为小标题字体
- `FandolFang`：作为正文近似替代“仿宋”
- `FandolSong`：作为宋体风格备用

推荐放入或下载后的文件名：

- `NotoSerifSC-Bold.otf`
- `NotoSerifSC-Regular.otf`
- `NotoSansSC-Bold.otf`
- `NotoSansSC-Regular.otf`
- `FandolFang-Regular.otf`
- `FandolSong-Regular.otf`

当前仓库的 [assets/fonts](./assets/fonts) 目录中保留了用户自行加入的中文字体文件：

- `方正小标宋简.TTF`
- `仿宋_GB2312.ttf`
- `黑体公文字体.ttf`
- `楷体_GB2312.ttf`

前两个字体文件的来源页备注为：

- https://life.scnu.edu.cn/a/20220309/5508.html

如果通过 ClawHub 发布 skill，当前仓库会通过 `.clawhubignore` 排除字体二进制；源码仓库可以继续保留这些字体文件，但发布到 ClawHub 的 skill 包默认不携带它们，需要在本地单独准备或安装。

下载完成后，再安装到本机：

```bash
bash scripts/install_fonts.sh
```

如果你想一次拉更多字重，可以使用：

```bash
bash scripts/download_fonts.sh all
```

## 字体与字体文件

生成 `.docx` 时，通常不需要把 `.ttf` 或 `.otf` 字体文件直接提交进 repo。

- `.docx` 默认只记录“字体名称”，不会自动嵌入字体二进制
- 打开文档时，Word 会在当前机器上查找对应字体；找不到就会回退
- 如果你只接受“本机已装什么字体就按什么显示”，那就不必额外存字体文件
- 如果你要在固定机器上稳定导出、统一团队显示效果，或者后续还要导出 PDF / 图片 / HTML，就应该准备字体文件

当前仓库推荐的做法是：

1. 把字体放到 [assets/fonts](./assets/fonts)
2. 运行 `bash scripts/install_fonts.sh`
3. 再执行 `renderers/docx.py`

当前脚本的字体槽位：

- `--header-font`：版头
- `--title-font`：标题
- `--heading-font`：一级标题
- `--subheading-font`：二级标题
- `--body-font`：正文

当前推荐的做法不是给每个文种手工写死字体文件，而是：

1. 在 [prompts/doc-types/*/meta.toml](./prompts/doc-types) 中为文种指定 `font_profile`
2. 在 [prompts/font-profiles](./prompts/font-profiles) 中定义字体方案
3. 在 [prompts/layout-profiles](./prompts/layout-profiles) 中定义版式方案
4. 在 [assets/fonts/catalog.toml](./assets/fonts/catalog.toml) 中把字体方案里的字体族指向 `assets/fonts/` 下的具体文件

这样改一处字体映射，所有引用该方案的文种会同步更新。

如果通过 ClawHub 分发 skill，建议保留 `assets/fonts/catalog.toml` 和字体方案定义，但通过 `.clawhubignore` 排除 `.ttf`、`.otf` 字体二进制，仅在源码仓库或本地运行环境中保留实际字体文件。

如果使用 `## 版头（可选）`，脚本会优先调用 `--header-font` 对应字体。

风险边界：

- 商用字体不能默认分发，尤其是类似“方正小标宋”的字体要先确认授权
- 当前脚本只写字体名称，不做字体嵌入
- 如果要完全锁定视觉效果，应该在安装好字体的机器上导出 PDF
- 仓库中如包含用户自行加入的标准字体文件，其来源页和使用背景应在文档中明确备注，但具体授权与分发边界仍需使用者自行确认

## 如何使用

1. 维护主源时，优先修改 [prompts/core](./prompts/core)、[prompts/doc-types](./prompts/doc-types) 和 [prompts/profiles/default.toml](./prompts/profiles/default.toml)。
2. 修改完成后，执行 `python3 scripts/build_all.py`，生成在线 skill 和离线基础系统提示词。
3. 在 agents 或 Codex 环境中，可通过自然语言触发，或显式使用 `$official-document-drafting`。
4. 在离线 WebUI / Qwen 环境中，可运行 `python3 adapters/webui/build.py --doc-type 通知 --instruction "..."` 生成可直接粘贴的提示词。
5. 如需检查 Markdown 结构，可运行 `python3 renderers/validate.py ...`。
   当前校验器除检查必备章节外，也会对标题层级写法给出提醒，例如一级标题是否用 `一、`、二级标题是否用 `（一）`，以及短文是否过度下钻到三级以下标题。
6. 如需导出 Word，可将 Markdown 成稿交给 `python3 renderers/docx.py ...`。
7. 如需简化版头、发文字号、版记，可在 Markdown 中增加 `## 版头（可选）`、`## 发文字号（可选）`、`## 版记（可选）`。
8. 如需页码，在导出时增加 `--show-page-number`。
9. 特别长的标题可以交给脚本自动均衡断行，也可以在 Markdown 中手动换行后再导出。
10. 如果你要使用 repo 中的开源字体，先运行 `bash scripts/download_fonts.sh minimal`，再运行 `bash scripts/install_fonts.sh`。
11. 如果要按文种自动套用字体和版式方案，可直接运行 `python3 renderers/docx.py <稿件>.md --doc-type 通知`。

## 文种判断建议

- 请求上级批准：请示
- 回复下级请示：批复
- 部署安排工作：通知
- 提出原则性办法：意见
- 重要处理、奖惩、调整：决定
- 面向社会公开告知：公告 / 通告 / 公报
- 向上级汇报情况：报告
- 平行沟通商洽：函
- 形成会议议定事项：纪要
- 基于当前新闻或动态形成内部材料：简报 / 专报 / 报告

## 版式依据与当前实现

这次版本已按公开可核的政府系统资料，把正文主体排版调整到更接近 `GB/T 9704-2012` 常见执行口径：

- A4 用纸
- 页边距约为：上 37mm、下 35mm、左 28mm、右 26mm
- 标题默认接近 `2号小标宋`
- 正文默认接近 `3号仿宋`
- 一级标题默认接近 `3号黑体`
- 二级标题默认接近 `3号楷体`
- 结构层级默认采用 `一、`、`（一）`、`1.`、`（1）`
- 一般 10 页以内文稿统一控制到二级标题；其中 2 至 3 页左右的文稿通常使用一级和二级标题即可
- 正文首行缩进 2 字符
- 长标题默认自动均衡断行，避免出现“20 字 + 1 字”这种失衡排版
- 正文固定行距、标题后距、主送机关后距、落款前距跟随文种绑定的 `layout_profile`；正式公文默认正文行距为 `580 twips`（约 `29.00pt`），阅读型内部材料默认正文行距为 `600 twips`（`30pt`），并尽量接近每面 22 行、每行 28 字
- 成文日期使用阿拉伯数字书写 `YYYY年M月D日`
- 可选生成简化版头、发文字号、版记和页脚页码

详细规则和未覆盖边界见 [references/layout-rules.md](./references/layout-rules.md)。当前版本适合草稿、内部流转稿、简报、专报、汇报材料和正式公文正文初稿；如果要直接形成对外正式红头件，仍建议套用本单位现成 Word 模板做最后核定。

## 自动触发与自动排版

这个 skill 的 [agents/openai.yaml](./agents/openai.yaml) 里设置了 `allow_implicit_invocation: true`，表示运行环境支持时，它可以被系统隐式调用。

但这不等于“无条件自动加载”。是否真的自动注入给模型，取决于两件事：

- 这个 skill 是否已经被放进运行环境实际扫描的 skills 目录
- 当前 agents / Codex 宿主是否启用了隐式技能加载

更稳的用法仍然是显式写出 `$official-document-drafting`。

如果你只说“生成一个公文总结当前新闻”，通常会有三层行为：

- 如果 skill 被成功触发，模型会按这个 skill 的公文结构和文风来写，通常会自动做标题、分段、结尾、落款这类排版
- 如果任务本身包含“当前”“最新”“今日”等时效信息，模型需要先拿到新闻内容或联网核验后才能可靠成稿
- 但它不会自动输出 `.docx` 文件，除非你进一步要求“导出 Word”或执行 `renderers/docx.py`

也就是说：

- 自动触发：可能，但不保证
- 自动按公文格式排版文本：大概率会，如果 skill 已触发
- 自动生成 Word 文件：不会，除非显式执行导出步骤

## 导出补充说明

使用样例、默认路径和最小验证见文档顶部。本节只补充字体和导出参数说明。

默认字体：

- 标题：`方正小标宋简体`
- 一级标题：`黑体`
- 二级标题：`楷体_GB2312`
- 正文：`仿宋_GB2312`

默认字号：

- 标题：约 `22pt`，接近 `2号`
- 一级标题 / 二级标题 / 正文：约 `16pt`，接近 `3号`

现在也可以直接按文种调用字体和版式方案：

```bash
python3 renderers/docx.py \
  ~/official-document-drafting-output/drafts/通知示例.md \
  -o ~/official-document-drafting-output/drafts/通知示例.docx \
  --doc-type 通知
```

如需查看某个文种最终会使用哪些字体和对应文件：

```bash
python3 scripts/generate_docx.py --doc-type 通知 --show-font-plan
```

如需列出当前支持的字体方案：

```bash
python3 scripts/generate_docx.py --list-font-profiles
```

也可以在生成时覆盖：

```bash
python3 renderers/docx.py \
  ~/official-document-drafting-output/drafts/通知示例.md \
  -o ~/official-document-drafting-output/drafts/通知示例.docx \
  --title-font "思源宋体" \
  --heading-font "思源黑体" \
  --body-font "思源宋体"
```

如果你已经把开源字体下载到 `assets/fonts/` 并安装到本机，也可以直接用预设：

```bash
bash scripts/download_fonts.sh minimal
bash scripts/install_fonts.sh
python3 renderers/docx.py \
  ~/official-document-drafting-output/drafts/通知示例.md \
  -o ~/official-document-drafting-output/drafts/通知示例.docx \
  --font-preset noto-cjk
```

如果你希望同时启用字体预设、页码和自动断行：

```bash
python3 renderers/docx.py \
  ~/official-document-drafting-output/drafts/红头通知示例.md \
  -o ~/official-document-drafting-output/drafts/红头通知示例.docx \
  --font-preset noto-cjk \
  --show-page-number \
  --title-wrap auto
```

## Word 增强排版

`renderers/docx.py` 现在支持这几类附加控制：

- `## 版头（可选）`：生成简化红色版头文字
- `## 发文字号（可选）`：生成带红色下划线的发文字号行；如果同一行里用制表符 `\t`，右侧内容会贴右排版，可用于 `签发人`
- `## 版记（可选）`：在正文末尾生成简化版记区
- `--show-page-number`：在页脚中居中显示页码
- `--title-wrap auto`：对长标题做均衡断行；若你已手动换行，脚本会保留原样

示例：

```md
## 版头（可选）
XX市教育局文件

## 发文字号（可选）
X教发〔2026〕3号	签发人：张三

## 标题
关于开展2026年春季校园安全和应急能力联合检查工作的通知
```

字体目录约定见 [assets/fonts/README.md](./assets/fonts/README.md)。如需脚本侧速查，可看 [references/font-usage.md](./references/font-usage.md)。

## 设计原则

- 先判断文种是否正确，再润色语言。
- 先核对事实和时间，再整理为正式材料。
- 法定公文优先遵循法定文种边界，常见材料按机关习惯结构处理。
- Markdown 成稿与 `.docx` 导出分离，避免在结构未定稿前直接进入 Word 排版。
- 长标题默认可自动均衡断行，但正式定稿前仍应人工复核是否符合词意完整和对称要求。

## 备注

- 目录名使用英文是为了兼容 skill 的命名规则。
- 文件内容已尽量使用中文。
- 生成 `.docx` 时通常不需要把 `.ttf` 放进 skill；脚本默认只写入字体名称。
- 当前推荐的自动下载来源是 `notofonts/noto-cjk` 与 CTAN `fandol`。
- 文种清单主要参照现行《党政机关公文处理工作条例》常见口径整理，实际落地仍应结合本单位制度和版式规范复核。
- 如果你后续想补“红头文件”“党组材料”“领导讲话提纲”等细分场景，可以继续往 `references/` 和 `assets/templates/` 扩展。

## License

- 仓库中的原创代码与文档采用 [MIT License](./LICENSE)。
- 第三方字体和其他二进制资源可能适用各自的许可条款，不因本仓库的 MIT 许可证而自动变更授权边界。

## 公开参考来源

以下链接已于 `2026-03-16` 重新核验可访问：

- 沈阳市人民政府：关于进一步规范行政机关公文处理工作的通知  
  https://www.shenyang.gov.cn/zwgk/zcwj/zfwj/szfbgtwj1/202112/t20211201_1701386.html
- 辽宁省人民政府：辽宁省人民政府办公厅关于印发《辽宁省行政机关公文格式细则》的通知  
  https://www.ln.gov.cn/web/zwgkx/zfwj/szfbgtwj/zfwj2004/7ED90F8968BD491FB190A231069CA87B/index.shtml
- 紫阳县人民政府：关于规范政府机关公文格式的通知  
  https://www.zyx.gov.cn/Content-1778525.html
- 安康市人民政府：党政机关公文处理如何走向“统一”  
  https://www.ankang.gov.cn/Content-2060366.html
