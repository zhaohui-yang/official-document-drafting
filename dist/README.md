# dist：自动生成的产物（请勿手改）

本目录下所有文件都由 `prompts/` 主源经构建脚本生成，**不要手动编辑**——手改的内容会在下次构建或 `--check` 校验时被覆盖、或报「与主源漂移」。要改内容，请改 `prompts/` 主源后运行 `python3 src/scripts/build_all.py` 重建。

两个子目录：

- `offline/default/`：离线提示词产物。其中 `doc-types/<文种>/prompt.md` 可**直接复制粘贴**到网页版 AI 助手或本地离线模型使用（见根目录 README「快速上手」的模式二 / 模式三）。`system_prompt.md` 是全量规则的离线系统提示词。
- `skill/`：自包含的 references 模式 **skill 包**（`SKILL.md` + `references/` + `agents/`），可整体复制成一个 skill 安装到能装 skill 的工具里（模式一）。
