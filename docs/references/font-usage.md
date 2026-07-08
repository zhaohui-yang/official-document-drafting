# 字体速查

> 说明：本文件是面向读者的说明文档，便于人工查阅。操作性规则以 `prompts/core/*.md` 与 `prompts/font-profiles/*.toml`、`assets/fonts/catalog.toml` 为唯一主源；本文件与主源冲突时以主源为准。本文件仅作同步说明。

- `src/scripts/generate_docx.py` 生成 `.docx` 时只写入字体名称，不嵌入 `.ttf/.otf`（实现拆分在 `src/docgen/`，该脚本为兼容入口）。
- 如果需要稳定显示自定义字体，先把字体放入 `assets/fonts/`，再运行 `bash src/scripts/install_fonts.sh`。
- 文种级字体要求和版式参数不再手工散落维护，统一由 `prompts/doc-types/*/meta.toml` 中的 `font_profile` 指向 `prompts/font-profiles/*.toml`，`layout_profile` 指向 `prompts/layout-profiles/*.toml`。
- `assets/fonts/catalog.toml` 负责把字体方案中的字体族映射到 `assets/fonts/` 下的具体文件。
- 当前 `assets/fonts/` 目录中除开源替代字体外，还包含用户自行加入的 `方正小标宋简.TTF`、`仿宋_GB2312.ttf`、`黑体公文字体.ttf` 和 `楷体_GB2312.ttf`。
- 当前默认字体方案已改为直接优先使用 repo 内中文字体文件，不再默认首选开源 Noto 系列，也不再依赖系统字体占位。
- 默认字体槽位包括：`--header-font`、`--title-font`、`--heading-font`、`--subheading-font`、`--body-font`。
- 可以直接用 `python3 src/scripts/generate_docx.py --doc-type 通知 --show-font-plan` 查看当前文种会落到哪些字体、字号、版式参数和文件。
- 如需只看版式参数，可用 `python3 src/scripts/generate_docx.py --doc-type 通知 --show-layout-plan`。
- `## 版头（可选）` 使用 `--header-font`；标题和正文分别使用各自槽位。
- 使用商用字体前先确认授权，尤其是方正系字体。
- 需要面向最终发布锁定视觉效果时，建议在已安装目标字体的机器上导出 PDF。

## 导出已知坑（症状 / 成因 / 对策）

- **症状**：导出的 `.docx` 在别的电脑上字体变了样。
  **成因**：脚本只写字体名称、不嵌入 `.ttf/.otf`，目标机器没装对应中文字体就会回退。
  **对策**：在目标机器先 `bash src/scripts/install_fonts.sh` 安装 `assets/fonts/` 字体；需要锁定最终视觉时在已装字体的机器上导出 PDF。
- **症状**：Markdown 里写了图片却没出现在 `.docx`，或报找不到图片。
  **成因**：当前仅支持本地 `png/jpg/jpeg` 文件，不支持网络图片、`svg/gif/webp` 等格式。
  **对策**：先把图片下载/转换成本地 `png/jpg/jpeg`，用独立图片块 `![图1 标题](./本地路径.png)` 引用，并优先放在 `附件/附图/附录`。
- **症状**：首页页脚没有页码，怀疑导出有问题。
  **成因**：这是预期行为——页码默认自第二页起显示，首页不显示页脚页码。
  **对策**：属正常；如完全不需要页码，导出时加 `--hide-page-number`。
- **症状**：编辑器里页脚页码有灰底，以为文档写入了背景色。
  **成因**：多为 Word/WPS 的“域底纹”显示设置，文档本身未写入底纹或高亮。
  **对策**：关闭编辑器的域底纹显示即可，无需改文档。

## 构建与导出自检命令

```bash
python3 src/adapters/skill/build.py --check                       # 校验 SKILL.md/dist/模板是否与 prompts/ 主源同步
python3 -m pytest -q                                          # 跑全部测试（含主源同步与 references 一致性守卫）
python3 src/scripts/generate_docx.py --doc-type 通知 --show-font-plan    # 查看某文种实际落到的字体、字号、文件
python3 src/scripts/generate_docx.py --doc-type 通知 --show-layout-plan  # 仅查看该文种的版式参数
```

用户侧的完整说明、推荐字体文件名和安装流程见仓库根目录 `README.md`。
