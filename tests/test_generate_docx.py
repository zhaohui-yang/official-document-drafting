import argparse
import base64
import pathlib
import subprocess
import tempfile
import unittest
import zipfile

from scripts.generate_docx import (
    Block,
    DEFAULT_FONT_SETTINGS,
    DEFAULT_LAYOUT_SETTINGS,
    PRINTABLE_HEIGHT_TWIPS,
    Section,
    build_document_xml,
    compute_end_matter_position,
    render_section_content,
    wrap_title_text,
    parse_markdown,
)


def make_args() -> argparse.Namespace:
    data = {}
    data.update(DEFAULT_FONT_SETTINGS)
    data.update(DEFAULT_LAYOUT_SETTINGS)
    data["show_page_number"] = False
    data["hide_sections"] = "标题,主送单位,正文,落款"
    data["title_wrap"] = "auto"
    data["title_max_chars"] = 20
    return argparse.Namespace(**data)


class GenerateDocxSigningLayoutTests(unittest.TestCase):
    def test_parse_markdown_recognizes_standalone_image_blocks(self) -> None:
        blocks = parse_markdown("# 标题\n\n![图1 现场照片](./demo/sample.png)\n")

        self.assertEqual(len(blocks), 2)
        self.assertEqual(blocks[1].kind, "image")
        self.assertEqual(blocks[1].text, "图1 现场照片")
        self.assertEqual(blocks[1].src, "./demo/sample.png")

    def test_end_to_end_export_embeds_local_image_into_docx(self) -> None:
        png_bytes = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aD9kAAAAASUVORK5CYII="
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = pathlib.Path(tmpdir)
            image_path = tmp_path / "sample.png"
            markdown_path = tmp_path / "sample.md"
            output_path = tmp_path / "sample.docx"

            image_path.write_bytes(png_bytes)
            markdown_path.write_text(
                "# 示例文稿\n\n## 附件\n\n附件1：现场照片\n\n![图1 现场照片](./sample.png)\n\n说明：用于测试图片嵌入。\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    "python3",
                    "scripts/generate_docx.py",
                    str(markdown_path),
                    "-o",
                    str(output_path),
                ],
                cwd="/root/home/Desktop/official-document-drafting",
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertTrue(output_path.exists())

            with zipfile.ZipFile(output_path) as archive:
                names = set(archive.namelist())
                self.assertIn("word/media/image1.png", names)

                document_xml = archive.read("word/document.xml").decode("utf-8")
                relationships_xml = archive.read("word/_rels/document.xml.rels").decode("utf-8")
                content_types_xml = archive.read("[Content_Types].xml").decode("utf-8")

            self.assertIn("w:drawing", document_xml)
            self.assertIn("图1 现场照片", document_xml)
            self.assertIn("relationships/image", relationships_xml)
            self.assertIn('Target="media/image1.png"', relationships_xml)
            self.assertIn('Extension="png"', content_types_xml)

    def test_end_matter_uses_remaining_space_when_it_fits_current_page(self) -> None:
        consumed = PRINTABLE_HEIGHT_TWIPS - 2000
        page_break, before_twips = compute_end_matter_position(consumed, 1000)

        self.assertFalse(page_break)
        self.assertEqual(before_twips, 1000)

    def test_end_matter_moves_to_next_page_when_current_page_cannot_fit(self) -> None:
        consumed = PRINTABLE_HEIGHT_TWIPS - 800
        page_break, before_twips = compute_end_matter_position(consumed, 1000)

        self.assertTrue(page_break)
        self.assertEqual(before_twips, PRINTABLE_HEIGHT_TWIPS - 1000)

    def test_end_matter_rendering_can_insert_page_break_and_bottom_spacing(self) -> None:
        section = Section(
            heading="版记",
            blocks=[
                Block(kind="paragraph", text="主送：[主送单位]"),
                Block(kind="paragraph", text="抄送：[抄送单位]"),
                Block(kind="paragraph", text="审核：[审核人]"),
            ],
        )

        xml_parts = render_section_content(
            section,
            args=make_args(),
            hidden_sections=set(),
            first_paragraph_before_override=1234,
            prepend_page_break=True,
        )

        self.assertEqual(len(xml_parts), 4)
        self.assertIn('w:type="page"', xml_parts[0])
        self.assertIn('w:before="1234"', xml_parts[1])

    def test_date_only_signing_line_uses_four_character_right_indent(self) -> None:
        section = Section(
            heading="落款",
            blocks=[Block(kind="paragraph", text="2026年4月3日")],
        )

        xml_parts = render_section_content(section, args=make_args(), hidden_sections=set())

        self.assertEqual(len(xml_parts), 1)
        self.assertIn('w:rightChars="400"', xml_parts[0])

    def test_signing_date_uses_four_character_right_indent_when_unit_present(self) -> None:
        section = Section(
            heading="落款",
            blocks=[Block(kind="paragraph", text="[发文单位]\n2026年4月3日")],
        )

        xml_parts = render_section_content(section, args=make_args(), hidden_sections=set())

        self.assertEqual(len(xml_parts), 2)
        self.assertIn('w:rightChars="400"', xml_parts[-1])

    def test_annotation_section_renders_with_left_two_character_indent_and_parentheses(self) -> None:
        section = Section(
            heading="附注",
            blocks=[Block(kind="paragraph", text="联系人：张三，联系电话：010-12345678，手机：13800000000")],
        )

        xml_parts = render_section_content(section, args=make_args(), hidden_sections=set())

        self.assertEqual(len(xml_parts), 1)
        self.assertNotIn(">附注<", xml_parts[0])
        self.assertIn('w:leftChars="200"', xml_parts[0])
        self.assertIn("（联系人：张三，联系电话：010-12345678，手机：13800000000）", xml_parts[0])

    def test_numbered_substantive_section_heading_uses_two_character_first_line_indent(self) -> None:
        section = Section(
            heading="一、基本情况",
            blocks=[Block(kind="paragraph", text="　　正文示例。")],
        )

        xml_parts = render_section_content(section, args=make_args(), hidden_sections=set())

        self.assertGreaterEqual(len(xml_parts), 2)
        self.assertIn(">一、基本情况<", xml_parts[0])
        self.assertIn('w:firstLineChars="200"', xml_parts[0])
        self.assertNotIn('w:leftChars="200"', xml_parts[0])

    def test_wrap_title_prefers_single_line_when_it_fits(self) -> None:
        title = "关于开展春季绿化工作的通知"
        self.assertEqual(wrap_title_text(title, max_chars=20, enabled=True), title)

    def test_wrapped_title_lines_should_not_increase_in_length(self) -> None:
        title = "步加服知通设营安实，设好治示强化案有规优全基优产做展治整层层落治好项风步优基通方环开"

        wrapped = wrap_title_text(title, max_chars=12, enabled=True)
        lengths = [len(line) for line in wrapped.split("\n")]

        self.assertGreater(len(lengths), 1)
        self.assertTrue(all(lengths[i] >= lengths[i + 1] for i in range(len(lengths) - 1)), lengths)

    def test_show_page_number_uses_distinct_first_page_without_footer_number(self) -> None:
        args = make_args()
        args.show_page_number = True
        blocks = parse_markdown("# 示例文稿\n\n## 正文\n\n　　正文示例。\n")

        document_xml = build_document_xml(blocks, args)

        self.assertIn('<w:footerReference w:type="default" r:id="rId3"/>', document_xml)
        self.assertIn("<w:titlePg/>", document_xml)

    def test_cli_export_enables_page_number_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = pathlib.Path(tmpdir)
            markdown_path = tmp_path / "sample.md"
            output_path = tmp_path / "sample.docx"

            markdown_path.write_text("# 示例文稿\n\n## 正文\n\n　　正文示例。\n", encoding="utf-8")

            result = subprocess.run(
                [
                    "python3",
                    "scripts/generate_docx.py",
                    str(markdown_path),
                    "-o",
                    str(output_path),
                ],
                cwd="/root/home/Desktop/official-document-drafting",
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertTrue(output_path.exists())

            with zipfile.ZipFile(output_path) as archive:
                names = set(archive.namelist())
                self.assertIn("word/footer1.xml", names)
                document_xml = archive.read("word/document.xml").decode("utf-8")

            self.assertIn('<w:footerReference w:type="default" r:id="rId3"/>', document_xml)
            self.assertIn("<w:titlePg/>", document_xml)


if __name__ == "__main__":
    unittest.main()
