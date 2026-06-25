---
name: docx-export
description: 把中文公文 Markdown 成稿导出为符合机关版式的 .docx。Use when the user wants to export/convert a 公文 Markdown draft to Word/.docx, adjust 字体、字号、页边距、行距、页码、标题断行, embed local images as 附件/附图, or inspect the resolved 字体与版式方案. 不负责起草内容，只负责渲染版式。
---

# 公文 docx 导出

把已成稿的中文公文 Markdown 渲染成符合机关版式的 `.docx`。这是「版式渲染」能力，**不起草内容**——起草走根目录「公文写作」skill，本 skill 只在 Markdown 结构正确后做导出与版式调整。

与「公文写作」共用同一份 `prompts/` 主源（字体方案、版式方案、文种绑定），不复制规则。

## 文件索引

```
src/scripts/generate_docx.py            # 导出器主入口（CLI）
src/scripts/install_fonts.sh            # 安装 assets/fonts/ 下字体到系统
src/scripts/download_fonts.sh           # 拉取开源替代字体
prompts/font-profiles/*.toml        # 字体方案（标题/正文/层级字体字号）
prompts/layout-profiles/*.toml      # 版式方案（固定行距、各段后距、首行缩进）
prompts/doc-types/<id>-<文种>/meta.toml  # 文种 → font_profile / layout_profile 绑定
assets/fonts/catalog.toml           # 字体族 → assets/fonts/ 具体文件映射
docs/references/font-usage.md            # 字体速查、导出已知坑、自检命令（面向读者）
docs/references/layout-rules.md          # 版式规范、已自动化/未自动化清单、页边距
```

## 调用方式

- 先确认 Markdown 结构正确（标题、主送单位、正文、落款、附注、附件等用 `##` 分块）。
- 按文种自动套字体与版式：`--doc-type <文种>`（中文别名或英文 ID 均可），脚本据 `meta.toml` 解析 `font_profile`/`layout_profile`。
- 或手动指定：`--font-preset`、`--title-font`、`--body-font` 等槽位。
- 导出前可用 `--show-font-plan` / `--show-layout-plan` 预览实际落到的字体、字号、版式参数。

```bash
python3 src/scripts/generate_docx.py 成稿.md -o 成稿.docx --doc-type 通知
python3 src/scripts/generate_docx.py --doc-type 报告 --show-font-plan      # 预览不导出
```

## 默认版式（主源）

- 页边距：上、左 3.6cm，下、右 2.7cm（`src/scripts/generate_docx.py` 的 `MARGIN_*_TWIPS`）。
- 行距、各段后距、首行缩进：由文种绑定的 `prompts/layout-profiles/*.toml` 决定，不在文档里重复硬编码数值。
- 标题/正文/层级字体字号：由 `prompts/font-profiles/*.toml` + `assets/fonts/catalog.toml` 决定。
- 调整版式优先改对应 `*.toml` 主源；只在一次性需求时用 CLI 覆盖。

## 已知坑（症状 / 成因 / 对策）

- **换机器字体变样**：脚本只写字体名、不嵌入 `.ttf`；目标机器先 `bash src/scripts/install_fonts.sh`，锁定视觉时导出 PDF。
- **图片没出现**：仅支持本地 `png/jpg/jpeg`，用 `![图1 标题](./本地路径.png)` 独立成块，优先放 `附件/附图/附录`。
- **首页无页脚页码**：预期行为（自第二页起显示）；完全不要页码加 `--hide-page-number`。
- **页脚灰底**：是编辑器“域底纹”显示，非文档底纹。

更完整的字体速查与命令见 `docs/references/font-usage.md`，版式规范见 `docs/references/layout-rules.md`。

## 边界

- 不在自动化范围：机关红头套版、印章压成文日期、完整套红线——仍需用本单位 Word 模板做最后核定。
- 改字体/版式后若涉及 `*.toml` 主源，跑 `python3 src/adapters/skill/build.py --check` 确认产物同步。
