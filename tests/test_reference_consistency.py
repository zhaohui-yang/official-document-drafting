"""references/ 与 prompts/ 主源的一致性守卫测试。

目的：references/ 下的说明文档是手工维护的面向读者文档，容易与 prompts/core
主源漂移。本测试钉住几个关键口径（主源声明、正文固定行距、标题字体表述），
一旦 references 与主源出现已知类型的漂移即失败。
"""

from pathlib import Path
import unittest

from adapters.shared import load_doc_types, load_layout_profiles


REPO_ROOT = Path(__file__).resolve().parents[1]


class ReferenceConsistencyTests(unittest.TestCase):
    def test_references_declare_prompts_core_as_source(self) -> None:
        for name in ("style-rules.md", "layout-rules.md", "font-usage.md", "document-types.md"):
            text = (REPO_ROOT / "references" / name).read_text(encoding="utf-8")
            self.assertIn("prompts/", text, f"{name} 未声明 prompts/ 主源")
            self.assertIn("以主源为准", text, f"{name} 未声明冲突时以主源为准")

    def test_core_layout_does_not_hardcode_line_spacing_value(self) -> None:
        # 行距数值只应存在于 layout-profiles/*.toml 主源；core/layout.md 改为指向主源，
        # 不再硬编码 twips，避免与 toml 脱节。
        core = (REPO_ROOT / "prompts" / "core" / "layout.md").read_text(encoding="utf-8")
        self.assertNotIn("579 twips", core)
        self.assertNotIn("600 twips", core)
        self.assertIn("layout_profile", core)

    def test_official_standard_body_line_spacing_is_single_sourced(self) -> None:
        layout = load_layout_profiles()["official-standard"]
        self.assertEqual(layout.body_line_spacing_twips, 579)
        # 面向读者的版式文档可列出具体数值，但必须与 toml 主源一致。
        self.assertIn(
            "579",
            (REPO_ROOT / "references" / "layout-rules.md").read_text(encoding="utf-8"),
            "references/layout-rules.md 未与 official-standard 行距主源（579 twips）保持一致",
        )

    def test_title_font_wording_does_not_drift(self) -> None:
        core = (REPO_ROOT / "prompts" / "core" / "layout.md").read_text(encoding="utf-8")
        self.assertIn("2 号小标宋体", core)
        for name in ("layout-rules.md", "style-rules.md"):
            text = (REPO_ROOT / "references" / name).read_text(encoding="utf-8")
            self.assertIn("2 号小标宋体", text, f"{name} 标题字体表述与主源不一致")
            self.assertNotIn("接近 2 号字", text, f"{name} 出现已修复的模糊漂移表述")

    def test_document_types_lists_every_legal_doc_type(self) -> None:
        # document-types.md 保留人工编排的 prose，但法定公文清单不能与 meta.toml 主源漂移：
        # 任一法定文种被新增/改名后，本测试要求同步到说明文档。
        text = (REPO_ROOT / "references" / "document-types.md").read_text(encoding="utf-8")
        legal = [dt for dt in load_doc_types() if dt.category == "法定公文"]
        self.assertEqual(len(legal), 15, "法定公文数量应为 15，meta.toml 可能漂移")
        for dt in legal:
            self.assertIn(
                dt.display_name,
                text,
                f"document-types.md 缺少法定文种 {dt.display_name}，请同步说明文档",
            )


if __name__ == "__main__":
    unittest.main()
