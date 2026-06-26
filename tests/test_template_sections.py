"""校验项目自带模板满足 check_sections 的必备章节。

`src/scripts/check_sections.py` 用 `REQUIRED_SECTIONS` 校验成稿章节是否齐全。本测试反向
保证：项目自己生成的 `assets/templates/<id>.md` 始终能通过对应文种的必备章节校验——
任何人改 `spec.md` 模板漏掉必备章节，或改 `REQUIRED_SECTIONS` 与模板脱节时即失败。
"""

from pathlib import Path
import unittest

from scripts.check_sections import (
    ENDING_PHRASES,
    REQUIRED_SECTIONS,
    audit_unsourced_specifics,
    check_ending_phrase,
    check_format_redlines,
    check_heading_structure,
    check_residual_placeholders,
    check_title_punctuation,
    collect_markdown_headings,
    detect_heading_levels,
    match_subtype,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = REPO_ROOT / "assets" / "templates"

# 不计入文种模板的辅助文件：大纲索引而非单一文种成稿。
# 不计入文种成稿模板的辅助文件：大纲索引、统一起草请求模板。
NON_DOC_TEMPLATES = {"official-types-outline", "draft-request"}


class TemplateSectionTests(unittest.TestCase):
    def test_each_covered_template_has_required_sections(self) -> None:
        for doc_type, required in REQUIRED_SECTIONS.items():
            template_path = TEMPLATES_DIR / f"{doc_type}.md"
            self.assertTrue(
                template_path.exists(),
                f"check_sections 覆盖 {doc_type}，但缺少模板 {template_path}",
            )
            headings = collect_markdown_headings(template_path.read_text(encoding="utf-8"))
            missing = [section for section in required if section not in headings]
            self.assertEqual(
                missing,
                [],
                f"模板 {doc_type}.md 缺少 check_sections 要求的章节：{missing}",
            )

    def test_required_sections_cover_every_doc_template(self) -> None:
        templates = {
            path.stem
            for path in TEMPLATES_DIR.glob("*.md")
            if path.stem not in NON_DOC_TEMPLATES
        }
        uncovered = sorted(templates - set(REQUIRED_SECTIONS))
        self.assertEqual(
            uncovered,
            [],
            f"以下文种模板未被 REQUIRED_SECTIONS 覆盖：{uncovered}",
        )

    def test_templates_have_no_false_level_jump_warning(self) -> None:
        # 附件清单 `1. [附件名称]` 等列表序号不应被误判为标题跳级。
        for path in TEMPLATES_DIR.glob("*.md"):
            warnings = check_heading_structure(path.read_text(encoding="utf-8"))
            jumps = [w for w in warnings if "跳级" in w]
            self.assertEqual(
                jumps,
                [],
                f"模板 {path.name} 出现疑似跳级误报：{jumps}",
            )


class HeadingLevelDetectionTests(unittest.TestCase):
    """`detect_heading_levels` 的层级识别须与 prompts/core/style.md 约定一致。"""

    def test_attachment_list_items_are_not_headings(self) -> None:
        content = "## 附件（可选）\n\n1. [附件名称]\n2. [附件名称]\n"
        levels = [lvl for _, lvl, _ in detect_heading_levels(content)]
        self.assertNotIn(3, levels, "附件清单序号被误当成三级标题")

    def test_real_level3_outside_attachment_is_detected(self) -> None:
        # style.md 约定三级标题写作 `1. 内容`；附件区外仍应识别为三级，
        # 以便「10 页以内控制到二级标题」等规则照常生效。
        content = "一、基本情况\n\n（一）总体进展\n\n1. 健全机制\n"
        levels = [lvl for _, lvl, _ in detect_heading_levels(content)]
        self.assertIn(3, levels, "附件区外的三级标题 `1. ` 未被识别")

    def test_level_marker_inside_markdown_heading_counts(self) -> None:
        # `## 二、形势判断` 这类内嵌一级标记应计入层级，避免后文 `（一）` 误判跳级。
        content = "## 二、形势判断\n\n（一）任务一\n"
        warnings = check_heading_structure(content)
        self.assertEqual([w for w in warnings if "跳级" in w], [])


class ContentCheckTests(unittest.TestCase):
    """成稿内容机检：占位符残留与结尾用语↔文种匹配。"""

    def test_residual_placeholder_detected(self) -> None:
        self.assertTrue(check_residual_placeholders("发文单位：[发文单位]，日期待核实"))
        self.assertEqual(check_residual_placeholders("发文单位：某某市人民政府"), [])

    def test_ending_phrase_matches_doc_type(self) -> None:
        self.assertEqual(check_ending_phrase("……特此通知。", "notice"), [])
        self.assertTrue(check_ending_phrase("……请遵照执行。", "notice"))

    def test_ending_phrase_skips_doc_types_without_fixed_ending(self) -> None:
        # 未登记固定结尾用语的文种（如简报）不做该项提示。
        self.assertEqual(check_ending_phrase("任意结尾。", "briefing"), [])

    def test_format_redlines_detect_common_errors(self) -> None:
        self.assertTrue(check_format_redlines("发文字号：国办发〔2026〕第5号"))  # 加「第」
        self.assertTrue(check_format_redlines("发文字号：国办发〔2026〕05号"))  # 补零
        self.assertTrue(check_format_redlines("发文字号：国办发[2026]5号"))  # 方括号
        self.assertTrue(check_format_redlines("成文日期：2026年06月01日"))  # 月日补零
        self.assertTrue(check_format_redlines("主题词：公文 格式"))  # 主题词残留
        self.assertEqual(check_format_redlines("国办发〔2026〕5号，2026年6月1日"), [])

    def test_subtype_signature_matches_real_variants(self) -> None:
        # 制式年报凭「总体情况」标题命中子型；普通报告无签名则不命中。
        self.assertEqual(
            match_subtype("report", "正文", {"标题", "总体情况", "其他需要报告的事项"}),
            "制式/年度报告",
        )
        self.assertIsNone(match_subtype("report", "正文", {"标题", "主送单位"}))
        # 公布式决定凭正文短语「现予公布」命中。
        self.assertEqual(
            match_subtype("decision", "已经常务会议通过，现予公布，自……起施行。", set()),
            "公布式决定",
        )

    def test_audit_flags_concrete_values_but_skips_placeholders(self) -> None:
        # 非占位的具体值应被列出（0 幻觉核对）。
        hits = audit_unsourced_specifics(
            "国办发〔2026〕5号，2026年6月1日，完成率98.6%，投入1200万元，归集300万件。"
        )
        labels = {item.split("：", 1)[0].split(" ")[-1] for item in hits}
        self.assertEqual(labels, {"文号", "日期", "百分比", "金额", "数量"})
        # 占位符写法不应被误报。
        self.assertEqual(
            audit_unsourced_specifics("发文字号 [X发〔YYYY〕X号]，日期 [日期]，完成率 [X]%"),
            [],
        )

    def test_title_punctuation_flags_trailing_period(self) -> None:
        self.assertTrue(check_title_punctuation("# 关于开展某项工作的通知。\n\n正文"))
        self.assertEqual(check_title_punctuation("# 关于开展某项工作的通知\n\n正文"), [])

    def test_ending_phrases_match_drafting_thinking_source(self) -> None:
        # ENDING_PHRASES 与 prompts/core/drafting-thinking.md 的「结尾用语强绑定」清单
        # 必须对应：每个文种的首选结尾用语都应能在主源里找到，防止两处各改其一而漂移。
        drafting = (REPO_ROOT / "prompts" / "core" / "drafting-thinking.md").read_text(encoding="utf-8")
        missing = [
            doc_type
            for doc_type, phrases in ENDING_PHRASES.items()
            if phrases and phrases[0] not in drafting
        ]
        self.assertEqual(
            missing,
            [],
            f"以下文种的首选结尾用语未出现在 drafting-thinking.md 主源：{missing}",
        )


if __name__ == "__main__":
    unittest.main()
