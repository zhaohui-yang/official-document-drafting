---
name: official-document-drafting
description: 起草、改写、润色、扩写、压缩、规范并导出中文公文与行政正式文本。Use when the user asks to write, revise, summarize, standardize, or convert 公文、决议、决定、命令、公告、公报、通告、意见、通知、通报、报告、请示、批复、议案、函、纪要，以及总结、简报、新闻简报、信息专报、舆情专报、汇报材料、讲话稿、工作方案、实施方案、回复函等正式机关或单位文稿，尤其适用于需要固定文种结构、正式机关语气、统一口径、规范标题、层级编号、落款日期、模板套用、Word docx 导出，或将当前新闻材料整理为正式公文和正式汇报材料的场景。
metadata: {"openclaw": {"homepage": "https://github.com/zhaohui-yang/official-document-drafting", "requires": {"bins": ["bash", "python3", "curl"]}}}
---

<!-- Generated from prompts/ and adapters/skill/build.py. -->

# 公文写作

## 调用方式

- 先读取共享总规则。
- 判断当前任务最匹配的文种。
- 文种确定后，先应用共享的防编造约束 `prompts/core/doc-type-guardrails.md`，再读取对应文种目录中的 `spec.md`，按其中的“写作规则”“版式要求”“模板”章节处理，并按 `meta.toml` 中的 `font_profile` 和 `layout_profile` 应用字体与版式参数。
- 如存在 `examples.md`，并且用户明确要求更贴近既有样稿或单位写法，再按需参考。
- 用户要求 Word 时，先形成 Markdown 成稿，再调用导出脚本。

## 政策边界

### 基本边界

- 只能基于用户提供的事实、当前 profile、共享总规则和当前文种规则起草或改写。
- 不得编造政策依据、文件号、会议结论、机构名称、统计数据、时间地点、人物表态或新闻事实。
- 信息不完整时，使用 `[主送单位]`、`[发文单位]`、`[日期]`、`[事项名称]`、`[待核实]` 等占位符补齐结构，不要把待核实内容写成既成事实。
- 涉及“当前”“最新”“今日”“近日”等时效信息时，只能使用用户在材料中明确给出的时间和来源；材料没有写清日期或来源时，应明确标注待核实。
- 涉及正式发文、对外报送、政策敏感、法律敏感、涉密、涉隐私或可能产生权利义务影响的文本，必须经过具备相应权限的人员人工审核后方可使用。

### 交付边界

- 默认直接输出最终 Markdown 成稿，不先输出分析过程。
- 用户只要求提纲时输出提纲；未特别说明时优先输出完整成稿。
- 用户要求 Word 时，先产出结构正确的 Markdown 成稿，再调用导出脚本生成 `.docx`。
- 成稿前必须认真校对错别字、病句、标点、数字、日期、称谓和机构名称。
- 材料不足以形成完整成稿时，应输出待补充版或保留占位符，而不是虚构内容。

## 事实核验与防编造

### 强制要求

- 不得编造事实、数据、时间、地点、机构名称、人员身份、会议结论、政策依据、文件号、法律条款或新闻来源。
- 不得把推测、常识补全、经验判断或未核实材料写成确定事实。
- 用户材料没有明确写出的内容，宁可保留占位符、标注“待核实”，也不要擅自补齐。
- 对“当前”“最新”“今日”“近日”等时效性内容，必须以用户明确提供的时间和来源为准；没有来源或日期时，直接标注待核实。
- 如材料之间存在冲突、缺口或歧义，应优先保守表述，并明确提示“以下内容需进一步核实”。

### 输出口径

- 起草任何文种时，都要把“真实性优先于文采完整性”放在第一位。
- 正式成稿中不要出现模型自我说明，但要通过占位符、待核实标记和谨慎措辞体现防幻觉约束。
- 如果用户要求“补全”“润色”“扩写”，也只能在现有事实边界内展开，不得借机虚构背景、数字或依据。

## 处理流程

### 判断流程

1. 先判断是不是法定公文 15 种；不属于法定公文时，再判断是否属于常见正式材料，如工作方案、总结、简报、专报、讲话稿、汇报材料。
2. 判断行文方向：上行、下行、平行或公开发布；避免把“报告”写成“请示”，把“函”写成“通知”。
3. 判断发文主体、主送对象、事项性质、时间要求，以及是否需要请求批准、答复请示、公开告知或形成会议纪要。
4. 目标文种确定后，先应用共享的防编造约束 `prompts/core/doc-type-guardrails.md`，再读取对应文种目录中的 `spec.md`，按其中的“写作规则”“版式要求”“模板”章节处理，并按 `meta.toml` 中的 `font_profile` 读取字体方案、按 `layout_profile` 读取版式参数；如存在 `examples.md`，可按需读取。
5. 如果没有独立文种模板，退回 `prompts/core/fallback-template.md` 的骨架。

### 文种路由规则

- 需要请求上级批准：优先用“请示”
- 需要回复下级请示：优先用“批复”
- 需要部署安排工作：优先用“通知”
- 需要提出原则性指导办法：优先用“意见”
- 需要作出重要处理、奖惩、调整：优先用“决定”
- 需要公开告知重大事项：优先用“公告”或“通告”
- 需要向上级汇报情况：优先用“报告”
- 需要平行沟通商洽或答复：优先用“函”
- 需要形成会议议定事项：优先用“纪要”
- 需要整理新闻动态或专题情况：优先用“简报”或“专报”

### 输出习惯

- 先保证“文种正确”，再追求文风和修辞。
- 法定公文优先使用法定文种名称，不混用、不自造文种。
- 高频文种优先套用独立模板；结构不完整时使用占位符补齐，而不是删掉关键章节。
- 未明确要求“压缩、简写、提纲化、只保留核心部分”时，默认优先采用目标文种较完整的常见结构，尽量保留该文种常见的组成元素、可选板块和执行信息，再由用户后续删减。
- 解读各文种规则时，应区分 `必备`、`常见`、`条件项`、`地方或系统样式`、`项目自定义` 五类口径；`地方或系统样式` 和 `项目自定义` 只能按用户模板或本项目约定使用，不得误写成全国通行必备要素。
- 进入具体文种后，要按对应 `spec.md` 中各板块职责起草，逐段自检“这一部分是否回答了它本来该回答的问题”；不能只保留标题框架而用空泛套话填充。
- 起草完成后，应反向核对各层次是否分工清楚：背景段回答“为什么写”，进展段回答“做到哪里”，问题段回答“卡在哪里”，建议或要求段回答“下一步怎么做、由谁做、何时做”。
- 对目标文种通常应包含的结构项，如主送单位、落款、日期等，若用户已提供对应信息，则据实填入；若用户未提供，则保留对应占位符，不得因信息缺失而省略该结构。
- 对需要设置附注的文稿，如用户已提供联系人、固定电话、手机或公开属性等信息，则在附注处据实写入；未提供时保留对应占位符，不擅自省略或虚构。
- 本项目默认将 `请示、报告、通知、函、回复函、公告、通告` 设为保留附注联系人信息的文种；除非用户明确要求删除，否则起草时默认保留 `（联系人：[联系人] 联系电话：[固定电话]，[手机号]）`。
- 对涉及其他部门、其他地区、其他单位职责的事项，如材料未明确写明已协商一致、联合行文或共同决定，不得直接写成“经研究同意”“联合决定”“共同推进”等确定口径。
- 长篇方案、办法、细则、名单、表格、台账、清单等实体内容，如更适合作为附件承载，应优先在正文中做提要式交代，再通过附件承接，不把附件全文机械重复进正文。
- 需要承载图片、流程图、示意图、截图、现场照片时，普通公文和内部材料默认优先使用 `附件`、`附图` 或 `附表`；只有当前文种明确属于技术说明、操作指南、标准性资料，或用户明确要求时，才使用 `附录` 结构。
- 图片类附件应写清编号、标题和说明文字；如图片来源、拍摄时间、数据截止时点、适用范围或“仅供示意、以正式图件为准”等提示对理解结果有影响，应一并保留。
- 对目标文种通常不设置的结构项，不要机械补齐；是否设置主送单位、落款、日期，应以当前文种 `spec.md` 和模板为准。
- 是否设置附注，应以当前文种 `spec.md` 和模板为准；请示类公文优先保留附注结构。
- 是否设置版记，应以当前文种 `spec.md`、用户模板或系统样式为准；标准公文版记常见要素通常是 `抄送机关、印发机关、印发日期`，`分送`、`主送移入版记` 等做法属于地方或系统样式，`审核` 属本项目内部模板字段。
- 用户要求保存文件但未指定路径时，默认在 `~/official-document-drafting-output/` 下按任务类型建立子目录。
- 用户要求保存文稿但未指定文件名时，默认采用 `YYYYMMDD-标题-vNN` 命名；同一次任务如需同时保存离线提示词、附带说明等辅助生成文件，则在版本号后追加产物类型后缀，如 `YYYYMMDD-标题-v01-提示词.md`、`YYYYMMDD-标题-v01-说明.md`，避免与最终成稿重名。

## 语言与输出

### 语言风格

- 保持正式、准确、简洁、可执行，避免口语化、宣传口号化和空泛套话。
- 优先写明目的、依据、任务、要求，不堆砌空话。
- 多用动作导向表达，例如“开展”“落实”“报送”“组织实施”“严格执行”。
- 少用模糊词，例如“尽快”“适当”“有点”“比较好”。
- 生成的文本原则上少用分号，除非确需用于排比句、长并列结构或同层级事项的集中列举。

### 标题与层级

- 标题通常由发文机关、事由和文种组成；无须重复发文机关时，可直接写事由和文种，但仍应让读者一眼判断文种和事项。
- 标题应直接点明事项和文种，常见格式如“关于 + 事项 + 的通知”。
- 同一标题内避免同时出现多个中心事项。
- 标题较长时可分行，但回行时应保持词意完整、排列对称。
- 标题中除法规、规章、办法、方案、会议名称等确需使用全称的名称外，一般不用标点符号；需要保留完整名称时，优先使用书名号，不额外叠加无关标点。
- 正文层级默认使用 `一、`、`（一）`、`1.`、`（1）`，不要混用成 `一是、（二）、3.` 这类不统一形式。
- 一级标题优先使用汉字序号加顿号，如 `一、二、三、四`。
- 二级标题优先使用带括号的汉字序号，如 `（一）（二）（三）`。
- 三级标题优先使用阿拉伯数字加点号，如 `1. 2. 3.`。
- 四级标题优先使用带括号的阿拉伯数字，如 `（1）（2）（3）`。
- 正文中的并列实质性板块标题，默认使用一级标题编号，不裸写成无编号标题；常见写法如 `一、基本情况`、`二、工作开展情况`、`三、存在问题`、`四、下一步打算`。
- 同一份文稿内，标题层级应逐级展开，不要从一级直接跳到三级，也不要在同一层并列中混用不同编号体系。
- 10 页以内的文稿，统一控制到二级标题，不再展开到三级标题及以下层级。
- 2 至 3 页左右的文稿，通常使用一级和二级标题即可，不必为了形式完整继续下钻层级。
- 除标准层级标题外，可适当使用“一是、二是、三是”等分点衔接句增强机关文风，但不要机械堆砌。
- `一是、二是、三是` 更适合作为段内分点衔接语，不宜与正式层级标题体系混用为同级标题。
- 使用 `一是、二是、三是` 等分点衔接语时，默认应在同一自然段内连续书写，不得将 `一是`、`二是`、`三是` 分别另起自然段。
- 除非用户明确要求逐条分段，或者单一点内容明显过长、确需单独强调，否则不拆分为多个自然段。

### 正文与结尾

- 第一段优先交代背景、目的或依据，再展开具体安排、请示事项或答复意见。
- 正文首次出现非规范简称、项目简称、机构简称或会议简称时，应先写全称，再用括号注明简称；后文再按简称统一使用。
- 引用政策文件、会议决定、来文依据时，宜先写文件标题或会议名称，再写文号、届次、日期等标识信息；日期、届次和会议名称要写完整，不用含混缩写。
- 正文各板块都应承担明确功能，不能只挂标题不写实质内容；写“基本情况”就要交代起因、范围、现状和总体态势，写“工作进展”就要交代已做事项、主要做法和阶段结果，写“存在问题”就要直陈短板、风险和制约因素，写“下一步打算”就要落到后续安排、改进措施和需要协调的事项。
- 同一层级标题之间应各有分工，不要把背景写进“工作要求”，也不要把请批事项混进“报告”或把执行要求埋在“会议认为”里；如果某一板块事实不足，应压缩篇幅，但仍要把该板块要说明的内容说清。
- 对正文中的一级编号标题，默认按“左起空两格”的常见机关写法理解和导出；在 Markdown 结构稿中通过标题层级保留结构，在 `.docx` 中通过标题段落格式体现，不把 `标题、主送单位、落款、附注、版记、附件` 等结构栏混入正文编号体系。
- 涉及其他部门、其他单位职权的事项，只有材料已明确写明协商一致、联合发文或共同决定时，才能写成联合口径；没有明确依据时，不擅自代替其他部门表态。
- 通知重在部署安排；意见重在原则和办法；通报重在事实、评价和要求；报告重在汇报情况，不混入请求批准事项。
- 简报和专报优先做到“先事实、后判断、再建议”。
- 报告、纪要、汇报材料、工作总结、情况专报等综合性材料中，二级标题下通常先用 3 至 5 句话概述本节，再用 `一是、二是、三是` 等段内分点展开；每一点一般写 5 至 7 句话。对责任分工、完成时限、单项结论、单条进展等执行性内容可从简，但不得只写空泛口号，也不得为凑句数编造事实。
- 会议类材料和纪要类材料要准确使用提示语：`会议认为` 主要写总体判断和一致意见，`会议指出` 主要写重要观点、基本情况、成绩、问题或意义，`会议强调` 主要写需要重点重申的要求和定调，`会议要求` 主要写直接可执行的任务、责任、时限和落实安排。
- 通知常用结尾：`特此通知。`
- 请示常用结尾：`妥否，请批示。`
- 报告常用结尾：`特此报告。`
- 函常用结尾：`特此函复。` 或 `特此函达。`

### 落款与日期

- 落款通常包含发文单位和日期。
- 日期建议写成中文年月日形式，例如 `2026年3月15日`。
- 年份应写全，月、日不补前导零。
- 若用户未给出单位名称或日期，保留占位符，不要自行猜测真实主体。

### 主送、附件与版记

- 主送机关宜使用全称、规范化简称或同类型机关统称；能明确写清对象范围时，不用含混的“各有关单位”“有关部门”等模糊称谓。
- 有附件时，正文与附件应分工清楚；方案、名单、清单、表格、细则等内容较长时，优先作为附件承载，不把附件全文重复抄入正文。
- 需要插入图片、流程图、示意图、照片、截图、成果图时，普通公文和内部材料原则上优先放入 `附件`、`附图` 或 `附表`，不直接把图片写进正文主体。
- 只有技术指南、操作手册、规范性附表、标准性说明等更偏技术资料的文本，才默认允许使用 `附录A/附录B` 承载图片说明；普通通知、报告、请示、函、纪要等不默认使用 `附录`。
- 当前导出器已支持在 Markdown 中使用独立图片块语法 `![图1 标题](./本地图片路径.png)` 嵌入真实图片；第一版仅支持本地 `png/jpg/jpeg` 文件，且更适合放在 `附件`、`附图`、`附录` 中单独成块排布。
- 同一文稿如列多个附件，宜按顺序编号，正文中先提“附件”，后列附件名称；未形成正式附件时，不虚构附件名称和数量。
- 图片类附件宜包含图片编号或附件编号、图片标题，以及必要的 `说明`、`注`、`来源`、`截至时间` 等说明字段；图片不能裸放而没有文字说明。
- 版记不是所有文种的默认结构。只有当前文种 `spec.md`、用户模板或系统样式明确要求时才保留版记，不机械给所有文稿追加 `版记` 章节。

## 版式与导出

### 基线版式

- 以下要求是默认基线；如当前文种目录中的 `spec.md` 在“版式要求”章节有更具体要求，以文种专项版式为准。
- 正式公文正文默认采用 A4 版式思路，正文主体尽量接近每面 22 行、每行 28 字的常见排版密度。
- 标题通常用 2 号小标宋体，居中排布；能排成一行时不主动回行，标题较长确需回行时，应保持词意完整、排列对称，优先做到逐行等长；不能完全等长时，宜逐行递减，不应出现后行明显长于前行、长短参差失衡的情况。
- 正文通常用 3 号仿宋体，首行缩进 2 字符；在 Markdown 或纯文本成稿中，正文自然段前默认保留两个全角空格，体现“左起空两格”的常见写法；导出 Word 时仍按首行缩进 2 字符处理，不依赖半角空格堆砌版式。固定行距和段前后距由当前文种绑定的 `layout_profile` 统一约束，正式公文默认正文行距为 `580 twips`（约 `29.00pt`），阅读型内部材料通常为 `600 twips`（`30pt`）。
- 一级标题通常用 3 号黑体，二级标题通常用 3 号楷体，三级标题通常用 3 号仿宋体加粗，四级标题通常用 3 号仿宋体。
- 正文中的一级编号标题，如 `一、基本情况`、`二、主要做法`，通常按“左起空两格”编排；导出 Word 时应通过标题段落缩进体现这一习惯，不把 `标题、主送单位、落款、附注、版记、附件` 等结构栏误作正文编号标题处理。
- 主送单位通常放在标题下空一行，顶格书写，末尾用全角冒号。
- 正文与落款之间通常空 3 行；具体段前距由当前文种绑定的 `layout_profile` 控制。
- 落款通常将发文单位和日期置于文末右侧；日期写中文年月日，年份写全，月日不补前导零，并按右空 4 字编排。
- 如有附件说明，正式公文中通常在正文或结语下空一行左空 2 字编排“附件：”；多个附件时顺序编号列示，附件正文一般另页或另块排布。
- 图片、流程图、示意图等作为附件或附图时，宜先写标题，再写图号、说明、注或来源，不直接把说明文字塞进图片标题里。
- 如有附注，通常编排在成文日期下一行，左空 2 字，并用圆括号标识；联系人和联系电话一般放在附注中填写。
- 如设置版记，标准公文的常见版记要素通常为 `抄送机关、印发机关、印发日期`；`主送移入版记`、`分送`、`报/送/发` 等属于地方或系统样式，`审核` 属项目自定义字段。
- 如设置版记，导出 Word 时宜将版记整体编排在最后一页底部；当前页剩余空间不足时，应将版记整体移至下一页底部，不拆散排布。

### 导出约定

- 当前导出脚本已支持标题、正文、层级标题的字体字号区分，也支持固定行距、正文首行缩进、标题自动断行和页码显示；页码默认自第二页起显示，首页不显示页脚页码。
- 如需导出 Word，优先保证 Markdown 结构正确，再按需要选择 `--font-preset` 或显式传入 `--title-font`、`--body-font` 等参数。
- 如需按文种自动套用字体和精细版式，优先在文种 `meta.toml` 中指定 `font_profile` 与 `layout_profile`；字体由 `prompts/font-profiles/` 和 `assets/fonts/catalog.toml` 统一映射，版式参数由 `prompts/layout-profiles/` 统一维护。
- 对外正式红头件、印章压日期、完整版记和单位专用模板，不在当前自动化范围内，仍应由本单位模板做最后套版。

## 文种目录

### 法定公文

- `announcement` / 公告 / 别名：公告 / 字体方案：`official-standard` / 版式方案：`official-standard` / 向国内外宣布重要事项或者法定事项。 / 字体：`prompts/font-profiles/official-standard.toml` / 版式：`prompts/layout-profiles/official-standard.toml` / 规范：`prompts/doc-types/announcement-公告/spec.md`
- `approval` / 批复 / 别名：批复 / 字体方案：`official-standard` / 版式方案：`official-standard` / 用于答复下级机关请示事项。 / 字体：`prompts/font-profiles/official-standard.toml` / 版式：`prompts/layout-profiles/official-standard.toml` / 规范：`prompts/doc-types/approval-批复/spec.md`
- `circular` / 通报 / 别名：通报 / 字体方案：`official-standard` / 版式方案：`official-standard` / 用于表彰先进、批评错误或传达重要情况。 / 字体：`prompts/font-profiles/official-standard.toml` / 版式：`prompts/layout-profiles/official-standard.toml` / 规范：`prompts/doc-types/circular-通报/spec.md`
- `communique` / 公报 / 别名：公报 / 字体方案：`official-standard` / 版式方案：`official-standard` / 公开发布重要决定、重大事项或重要会议情况。 / 字体：`prompts/font-profiles/official-standard.toml` / 版式：`prompts/layout-profiles/official-standard.toml` / 规范：`prompts/doc-types/communique-公报/spec.md`
- `decision` / 决定 / 别名：决定 / 字体方案：`official-standard` / 版式方案：`official-standard` / 对重要事项作出部署、奖惩、处理或调整。 / 字体：`prompts/font-profiles/official-standard.toml` / 版式：`prompts/layout-profiles/official-standard.toml` / 规范：`prompts/doc-types/decision-决定/spec.md`
- `letter` / 函 / 别名：函 / 字体方案：`official-standard` / 版式方案：`official-standard` / 用于平行机关或不相隶属机关之间商洽、询问、答复。 / 字体：`prompts/font-profiles/official-standard.toml` / 版式：`prompts/layout-profiles/official-standard.toml` / 规范：`prompts/doc-types/letter-函/spec.md`
- `minutes` / 纪要 / 别名：纪要、会议纪要 / 字体方案：`official-standard` / 版式方案：`official-standard` / 用于记载会议主要情况和议定事项。 / 字体：`prompts/font-profiles/official-standard.toml` / 版式：`prompts/layout-profiles/official-standard.toml` / 规范：`prompts/doc-types/minutes-纪要/spec.md`
- `motion` / 议案 / 别名：议案 / 字体方案：`official-standard` / 版式方案：`official-standard` / 具有特定法定主体和程序要求的议案。 / 字体：`prompts/font-profiles/official-standard.toml` / 版式：`prompts/layout-profiles/official-standard.toml` / 规范：`prompts/doc-types/motion-议案/spec.md`
- `notice` / 通知 / 别名：通知 / 字体方案：`official-standard` / 版式方案：`official-standard` / 用于发布、传达、转发事项或安排部署工作。 / 字体：`prompts/font-profiles/official-standard.toml` / 版式：`prompts/layout-profiles/official-standard.toml` / 规范：`prompts/doc-types/notice-通知/spec.md`
- `opinion` / 意见 / 别名：意见 / 字体方案：`official-standard` / 版式方案：`official-standard` / 对重要问题提出见解和处理办法。 / 字体：`prompts/font-profiles/official-standard.toml` / 版式：`prompts/layout-profiles/official-standard.toml` / 规范：`prompts/doc-types/opinion-意见/spec.md`
- `order` / 命令（令） / 别名：命令、令、命令令 / 字体方案：`official-standard` / 版式方案：`official-standard` / 用于公布规章、施行重大强制性措施等。 / 字体：`prompts/font-profiles/official-standard.toml` / 版式：`prompts/layout-profiles/official-standard.toml` / 规范：`prompts/doc-types/order-命令（令）/spec.md`
- `public-notice` / 通告 / 别名：通告 / 字体方案：`official-standard` / 版式方案：`official-standard` / 在一定范围内公布应当遵守或者周知的事项。 / 字体：`prompts/font-profiles/official-standard.toml` / 版式：`prompts/layout-profiles/official-standard.toml` / 规范：`prompts/doc-types/public-notice-通告/spec.md`
- `report` / 报告 / 别名：报告 / 字体方案：`official-standard` / 版式方案：`official-standard` / 用于向上级汇报工作、反映情况、回复询问。 / 字体：`prompts/font-profiles/official-standard.toml` / 版式：`prompts/layout-profiles/official-standard.toml` / 规范：`prompts/doc-types/report-报告/spec.md`
- `request` / 请示 / 别名：请示 / 字体方案：`official-standard` / 版式方案：`official-standard` / 用于向上级请求指示、批准。 / 字体：`prompts/font-profiles/official-standard.toml` / 版式：`prompts/layout-profiles/official-standard.toml` / 规范：`prompts/doc-types/request-请示/spec.md`
- `resolution` / 决议 / 别名：决议 / 字体方案：`official-standard` / 版式方案：`official-standard` / 会议讨论通过的重要决策事项。 / 字体：`prompts/font-profiles/official-standard.toml` / 版式：`prompts/layout-profiles/official-standard.toml` / 规范：`prompts/doc-types/resolution-决议/spec.md`

### 常见正式材料

- `briefing` / 简报 / 别名：简报、信息简报、新闻简报 / 字体方案：`internal-readable` / 版式方案：`internal-readable` / 用于简要报送动态、会议情况、阶段成果和新闻整理。 / 字体：`prompts/font-profiles/internal-readable.toml` / 版式：`prompts/layout-profiles/internal-readable.toml` / 规范：`prompts/doc-types/briefing-简报/spec.md`
- `presentation` / 汇报材料 / 别名：汇报材料、汇报稿 / 字体方案：`internal-readable` / 版式方案：`internal-readable` / 用于向领导、检查组或上级进行阶段性工作汇报。 / 字体：`prompts/font-profiles/internal-readable.toml` / 版式：`prompts/layout-profiles/internal-readable.toml` / 规范：`prompts/doc-types/presentation-汇报材料/spec.md`
- `reply` / 回复函 / 别名：回复函、复函 / 字体方案：`official-standard` / 版式方案：`official-standard` / 用于对来函、来文、咨询事项作出正式回复。 / 字体：`prompts/font-profiles/official-standard.toml` / 版式：`prompts/layout-profiles/official-standard.toml` / 规范：`prompts/doc-types/reply-回复函/spec.md`
- `special-report` / 情况专报 / 别名：情况专报、信息专报、舆情专报、专报 / 字体方案：`internal-readable` / 版式方案：`internal-readable` / 用于向领导或上级报送专题信息、风险情况和舆情态势。 / 字体：`prompts/font-profiles/internal-readable.toml` / 版式：`prompts/layout-profiles/internal-readable.toml` / 规范：`prompts/doc-types/special-report-情况专报/spec.md`
- `speech` / 讲话稿 / 别名：讲话稿、发言稿 / 字体方案：`speech-readable` / 版式方案：`speech-readable` / 用于领导讲话、会议发言、动员部署和总结点评。 / 字体：`prompts/font-profiles/speech-readable.toml` / 版式：`prompts/layout-profiles/speech-readable.toml` / 规范：`prompts/doc-types/speech-讲话稿/spec.md`
- `summary` / 工作总结 / 别名：工作总结、总结、总结材料 / 字体方案：`internal-readable` / 版式方案：`internal-readable` / 用于阶段性复盘、年度总结、专项工作总结。 / 字体：`prompts/font-profiles/internal-readable.toml` / 版式：`prompts/layout-profiles/internal-readable.toml` / 规范：`prompts/doc-types/summary-工作总结/spec.md`
- `work-plan` / 工作方案 / 别名：工作方案、实施方案、方案 / 字体方案：`internal-readable` / 版式方案：`internal-readable` / 用于专项行动、阶段性工作、制度落地和项目推进。 / 字体：`prompts/font-profiles/internal-readable.toml` / 版式：`prompts/layout-profiles/internal-readable.toml` / 规范：`prompts/doc-types/work-plan-工作方案/spec.md`
