# 字体速查

- `scripts/generate_docx.py` 生成 `.docx` 时只写入字体名称，不嵌入 `.ttf/.otf`。
- 如果需要稳定显示自定义字体，先把字体放入 `assets/fonts/`，再运行 `bash scripts/install_fonts.sh`。
- 文种级字体要求和版式参数不再手工散落维护，统一由 `prompts/doc-types/*/meta.toml` 中的 `font_profile` 指向 `prompts/font-profiles/*.toml`，`layout_profile` 指向 `prompts/layout-profiles/*.toml`。
- `assets/fonts/catalog.toml` 负责把字体方案中的字体族映射到 `assets/fonts/` 下的具体文件。
- 当前 `assets/fonts/` 目录中除开源替代字体外，还包含用户自行加入的 `方正小标宋简.TTF`、`仿宋_GB2312.ttf`、`黑体公文字体.ttf` 和 `楷体_GB2312.ttf`。
- 当前默认字体方案已改为直接优先使用 repo 内中文字体文件，不再默认首选开源 Noto 系列，也不再依赖系统字体占位。
- 默认字体槽位包括：`--header-font`、`--title-font`、`--heading-font`、`--subheading-font`、`--body-font`。
- 可以直接用 `python3 scripts/generate_docx.py --doc-type 通知 --show-font-plan` 查看当前文种会落到哪些字体、字号、版式参数和文件。
- 如需只看版式参数，可用 `python3 scripts/generate_docx.py --doc-type 通知 --show-layout-plan`。
- `## 版头（可选）` 使用 `--header-font`；标题和正文分别使用各自槽位。
- 使用商用字体前先确认授权，尤其是方正系字体。
- 需要面向最终发布锁定视觉效果时，建议在已安装目标字体的机器上导出 PDF。

用户侧的完整说明、推荐字体文件名和安装流程见仓库根目录 `README.md`。
