# 公文写作 Skill

<a id="toc"></a>

## 目录

- [合规与使用声明](#compliance)
- [项目概览](#overview)
- [当前能力](#capabilities)
- [规则体系](#rules)
- [Quick Start](#quick-start)
- [默认样例](#default-example)
- [默认输出约定](#default-output)
- [文种覆盖范围](#coverage)
- [Word 导出与版式](#word-export)
- [图片、附件与附录](#images-attachments-appendices)
- [联系人与附注](#contact-note)
- [结构校验](#validation)
- [构建与维护](#build-and-maintain)
- [目录说明](#repo-layout)
- [字体与依赖](#fonts-and-deps)
- [如何使用这个仓库](#how-to-use)
- [设计原则](#principles)
- [边界提醒](#boundaries)
- [License](#license)
- [公开参考来源](#references)

<a id="compliance"></a>

## 合规与使用声明

> **合规是第一要求。宁可留空、待核实，也不得编造。**
>
> **本项目仅提供公文模板、结构参考、语言规范化和排版导出辅助，不构成法律意见、政策解释、正式发文授权或任何保证性结论。**

- 本项目用于辅助起草、整理、规范化中文公文与正式材料，不得用于伪造公文、冒用机关或单位名义、虚构事实、误导性报送、规避监管或其他违法违规用途。
- 涉及政策依据、法律条款、文件号、机构名称、会议结论、统计数据、领导表态、时间地点和新闻事实的内容，均应由使用者自行核实。
- 对“当前新闻”“最新动态”“今日情况”等时效性内容，必须先核对来源、发布日期和事件日期，再整理成稿。
- 用户未提供或无法核实的信息，应保留占位符或标注“待核实”，不得擅自补齐成既成事实。
- 涉及正式发文、对外报送、涉密、涉敏感、涉隐私或可能产生权利义务影响的内容，必须由有权限的人员人工审核后方可使用。

<a id="overview"></a>

## 项目概览

这是一个面向 agents、Codex 和离线 WebUI/Qwen 场景的中文公文与正式材料 skill。它以 `prompts/` 为单一主源，统一生成：

- 在线 skill 入口 [SKILL.md](./SKILL.md)
- agents 元数据 [agents/openai.yaml](./agents/openai.yaml)
- 离线系统提示词 [dist/webui/default/system_prompt.md](./dist/webui/default/system_prompt.md)
- 各文种兼容模板 [assets/templates/](./assets/templates)

当前版本覆盖 `22` 类文体：

- 法定公文 `15` 种：决议、决定、命令（令）、公报、公告、通告、意见、通知、通报、报告、请示、批复、议案、函、纪要
- 常见正式材料 `7` 种：工作总结、工作方案、讲话稿、汇报材料、回复函、简报、情况专报

<a id="capabilities"></a>

## 当前能力

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

<a id="rules"></a>

## 规则体系

### 共享规则

共享规则位于 [prompts/core/](./prompts/core)，主要负责：

- 文种判断流程
- 防编造与防幻觉约束
- 通用语言风格
- 标题与层级编号
- 通用版式与导出边界
- 附件、附注、版记、图片等共性要求

关键文件：

- [workflow.md](./prompts/core/workflow.md)
- [style.md](./prompts/core/style.md)
- [layout.md](./prompts/core/layout.md)
- [doc-type-guardrails.md](./prompts/core/doc-type-guardrails.md)

### 单文种规则

每个文种目录都包含：

- `meta.toml`：绑定 `font_profile` 与 `layout_profile`
- `spec.md`：写作规则、版式要求、模板
- `examples.md`：按需提供示例

例如：

- [prompts/doc-types/notice-通知/](./prompts/doc-types/notice-通知)
- [prompts/doc-types/report-报告/](./prompts/doc-types/report-报告)
- [prompts/doc-types/request-请示/](./prompts/doc-types/request-请示)
- [prompts/doc-types/minutes-纪要/](./prompts/doc-types/minutes-纪要)

### 要素分层

当前版本不再把所有“可能出现的元素”都视为默认项，而是按文种分层解释：

- `必备`：相对稳定、默认保留
- `常见`：公开样例中高频出现，默认优先保留
- `条件项`：只在特定场景出现，例如会议通知里的联系人、技术资料里的附录
- `地方或系统样式`：属于地方、系统或单位模板习惯，不上升为全国通行必备项
- `项目自定义`：本项目为了目标模板定制的口径，不冒充通用规范

例如 `纪要` 中的 `主送 / 抄送 / 审核`，当前被明确标注为项目自定义内部模板字段，而不是所有纪要的通用国标版记。

<a id="quick-start"></a>

## Quick Start

### 作为 Skill 使用

安装到 `~/.codex/skills/official-document-drafting`：

```bash
mkdir -p ~/.codex/skills
cp -R ./official-document-drafting ~/.codex/skills/
```

或从 GitHub 安装：

```bash
python3 /root/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo zhaohui-yang/official-document-drafting \
  --path . \
  --name official-document-drafting
```

在 Codex / agents 中使用：

```text
$official-document-drafting
请根据材料起草一份情况专报
```

### 作为离线提示词工程使用

列出支持的文种：

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

如需附带当前文种示例：

```bash
python3 adapters/webui/build.py \
  --doc-type 专报 \
  --instruction "根据材料整理一份领导看的情况专报，先事实后研判。" \
  --material-file ./news.md \
  --include-examples \
  -o /tmp/offline_special_report_prompt.md
```

<a id="default-example"></a>

## 默认样例

推荐从这类任务开始验证：

```text
总结当前热点新闻并形成正式报告
```

处理约定：

- 先核验新闻来源、发布日期和事件日期
- 文种一般优先落在“简报”“专报”或“报告”
- 如用户要求保存文件但未指定路径，默认落盘到输出目录并返回最终路径

<a id="default-output"></a>

## 默认输出约定

- 新闻报告默认目录：`~/official-document-drafting-output/news-reports/`
- 一般公文草稿默认目录：`~/official-document-drafting-output/drafts/`
- 同名 `Markdown` 与 `Word` 文件默认放在同一目录

命名示例：

- Markdown：`~/official-document-drafting-output/news-reports/当前热点新闻报告（YYYY年M月D日）.md`
- Word：`~/official-document-drafting-output/news-reports/当前热点新闻报告（YYYY年M月D日）.docx`

<a id="coverage"></a>

## 文种覆盖范围

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

### 常见正式材料 7 种

- 工作总结
- 工作方案 / 实施方案
- 讲话稿 / 发言稿
- 汇报材料
- 回复函
- 简报 / 信息简报 / 新闻简报
- 情况专报 / 信息专报 / 舆情专报

所有文种的适用场景和差异边界见 [references/document-types.md](./references/document-types.md)。

<a id="word-export"></a>

## Word 导出与版式

### 导出入口

- 语义化入口：[renderers/docx.py](./renderers/docx.py)
- 核心实现：[scripts/generate_docx.py](./scripts/generate_docx.py)

最小导出：

```bash
python3 renderers/docx.py \
  ~/official-document-drafting-output/drafts/通知示例.md \
  -o ~/official-document-drafting-output/drafts/通知示例.docx
```

按文种自动套用字体和版式：

```bash
python3 renderers/docx.py \
  ~/official-document-drafting-output/drafts/通知示例.md \
  -o ~/official-document-drafting-output/drafts/通知示例.docx \
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

### 当前排版行为

当前 `.docx` 导出已支持：

- A4 页面
- 按文种套用字体与版式方案
- 标题、一级标题、二级标题、正文分字体字号
- 正文首行缩进 2 字符
- 标题自动均衡断行
- 页脚页码
- 主送单位段后距、落款前距、成文日期右空 4 字
- 正文与落款之间默认空 3 行
- 附注默认位于成文日期下一行左空 2 字
- 如存在版记，版记整体压到最后一页底部，空间不足时整块移页

当前基线版式和边界说明见 [references/layout-rules.md](./references/layout-rules.md)。

### 版头、发文字号、版记

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

<a id="images-attachments-appendices"></a>

## 图片、附件与附录

### 当前支持的图片方式

当前版本已经支持在 Markdown 中用独立图片块把本地图片真实嵌入 `.docx`：

```md
![图1 现场照片](./demo/sample.png)
```

支持范围：

- 本地文件
- `png / jpg / jpeg`
- 独立图片块
- 路径相对当前 Markdown 文件解析

当前限制：

- 不支持远程 URL
- 不支持正文行内图片
- 不支持 `webp`
- 不支持复杂环绕排版

### 推荐放置位置

普通公文和内部材料中，图片默认更适合放在：

- `附件`
- `附图`
- `附表`

只有技术指南、操作手册、标准性说明、规范附表等更偏技术资料的文本，才默认允许使用：

- `附录A`
- `附录B`

### 图片说明建议

图片不要裸放，至少应包含：

- 图片编号
- 图片标题
- 说明文字

按需要再补：

- `注`
- `来源`
- `截至时间`
- `仅供示意，以正式图件为准`

示例：

```md
## 附件1（可选）

图1：现场宣传海报

![图1 现场宣传海报](./demo/poster.png)

说明：活动现场设置的主题宣传海报。
来源：项目组现场拍摄。
截至时间：2026年4月。
```

<a id="contact-note"></a>

## 联系人与附注

当前项目默认将以下文种设置为保留附注联系人信息：

- 请示
- 报告
- 通知
- 函
- 回复函
- 公告
- 通告

默认格式：

```text
（联系人：[联系人] 联系电话：[固定电话]，[手机号]）
```

说明：

- 这是本项目的默认起草口径，不等于所有公开样例都统一默认带联系人
- 如用户明确要求删除，可在生成后手动删减
- 是否最终保留，仍以具体文种规则、用户模板和单位制度为准

<a id="validation"></a>

## 结构校验

校验入口：

- 语义化入口：[renderers/validate.py](./renderers/validate.py)
- 核心实现：[scripts/check_sections.py](./scripts/check_sections.py)

最小校验：

```bash
python3 renderers/validate.py notice ~/official-document-drafting-output/drafts/通知示例.md
```

当前校验器会检查：

- 必备章节是否缺失
- 标题层级是否混乱
- 一级 / 二级 / 三级标题写法是否明显异常
- 是否存在常见结构漏项

<a id="build-and-maintain"></a>

## 构建与维护

### 单一主源维护顺序

推荐维护顺序：

1. 共享总规则：修改 [prompts/core](./prompts/core)
2. 共享防编造约束：修改 [prompts/core/doc-type-guardrails.md](./prompts/core/doc-type-guardrails.md)
3. 字体族和文件映射：修改 [assets/fonts/catalog.toml](./assets/fonts/catalog.toml)
4. 复用型字体方案：修改 [prompts/font-profiles](./prompts/font-profiles)
5. 复用型版式方案：修改 [prompts/layout-profiles](./prompts/layout-profiles)
6. 单个文种规则：修改 [prompts/doc-types](./prompts/doc-types) 下对应目录
7. profile 元数据和系统前言：修改 [prompts/profiles/default.toml](./prompts/profiles/default.toml)
8. 补充说明：按需修改 [references/](./references)

### 构建命令

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
python3 adapters/webui/build.py --emit-system
```

<a id="repo-layout"></a>

## 目录说明

- `prompts/core/`：共享规则主源
- `prompts/doc-types/<英文-中文目录>/`：单文种规则主源
- `prompts/font-profiles/`：字体方案主源
- `prompts/layout-profiles/`：版式方案主源
- `prompts/profiles/default.toml`：构建 profile 和系统前言
- `assets/fonts/`：本地字体目录
- `assets/fonts/catalog.toml`：字体名称到字体文件的映射
- `assets/templates/`：由各文种模板导出的兼容模板
- `adapters/skill/build.py`：生成 `SKILL.md`、`agents/openai.yaml` 等在线产物
- `adapters/webui/build.py`：生成离线 WebUI / Qwen 提示词
- `renderers/docx.py`：Word 导出入口
- `renderers/validate.py`：结构校验入口
- `scripts/generate_docx.py`：Word 导出核心实现
- `scripts/check_sections.py`：章节校验核心实现
- `scripts/build_all.py`：一键构建在线与离线产物
- `dist/`：构建产物目录
- `demo/`：示例文稿和导出样稿

<a id="fonts-and-deps"></a>

## 字体与依赖

### Python 依赖

当前版本的脚本只使用 Python 标准库，[requirements.txt](./requirements.txt) 仍保留为统一依赖入口。

如需按统一流程准备环境：

```bash
python3 -m pip install -r requirements.txt
```

### 字体安装

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
  ~/official-document-drafting-output/drafts/通知示例.md \
  -o ~/official-document-drafting-output/drafts/通知示例.docx \
  --font-preset noto-cjk
```

说明：

- `.docx` 默认记录字体名称，不自动嵌入字体二进制
- 如果需要稳定锁定视觉效果，应在已安装目标字体的机器上导出最终 PDF
- 商用字体分发需自行确认授权边界

<a id="how-to-use"></a>

## 如何使用这个仓库

1. 优先修改 [prompts/core](./prompts/core)、[prompts/doc-types](./prompts/doc-types)、[prompts/profiles/default.toml](./prompts/profiles/default.toml)
2. 执行 `python3 scripts/build_all.py`
3. 如需校验，执行 `python3 renderers/validate.py ...`
4. 如需导出 Word，执行 `python3 renderers/docx.py ...`
5. 如需检查字体与版式解析结果，执行 `--show-font-plan` 或 `--show-layout-plan`

<a id="principles"></a>

## 设计原则

- 先判断文种是否正确，再润色语言
- 先核对事实和时间，再整理成稿
- 不把地方或系统样式误写成全国通行必备格式
- Markdown 成稿与 `.docx` 导出分离，先定结构再做版式
- 对图片、附件、附录、版记、附注等扩展要素，默认按“有依据才保留”的原则处理

<a id="boundaries"></a>

## 边界提醒

- 当前更适合内部草稿、内部流转稿、汇报稿、简报、专报和正式公文正文初稿
- 如需形成可直接对外发出的正式红头件，仍建议套用本单位现成 Word 模板
- 当前真实图片嵌入仅支持本地块级图片，不适合复杂宣传册式排版
- 文种默认模板和项目自定义字段，是为了提高起草效率，不替代单位正式模板

<a id="license"></a>

## License

- 仓库中的原创代码与文档采用 [MIT License](./LICENSE)
- 第三方字体和其他二进制资源可能适用各自的许可条款，不因本仓库的 MIT 许可证而自动改变授权边界

<a id="references"></a>

## 公开参考来源

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
