import argparse
import base64
import pathlib
import subprocess
import tempfile
import unittest
import zipfile

from scripts.generate_docx import (
    Block,
    DEFAULT_BODY_LINE_SPACING_TWIPS,
    DEFAULT_FONT_SETTINGS,
    DEFAULT_LAYOUT_SETTINGS,
    ImageAsset,
    PRINTABLE_WIDTH_TWIPS,
    PRINTABLE_HEIGHT_TWIPS,
    Section,
    build_document_xml,
    build_footer_xml,
    build_image_assets,
    compute_image_size_emu,
    compute_end_matter_position,
    estimate_image_twips,
    estimate_section_height_twips,
    image_paragraph_xml,
    render_section_content,
    twips_to_emu,
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
    def test_default_body_line_spacing_matches_28_95pt(self) -> None:
        self.assertEqual(DEFAULT_BODY_LINE_SPACING_TWIPS, 579)

    def test_parse_markdown_recognizes_standalone_image_blocks(self) -> None:
        blocks = parse_markdown("# 标题\n\n![图1 现场照片](./样例/sample.png)\n")

        self.assertEqual(len(blocks), 2)
        self.assertEqual(blocks[1].kind, "image")
        self.assertEqual(blocks[1].text, "图1 现场照片")
        self.assertEqual(blocks[1].src, "./样例/sample.png")

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
                    "src/scripts/generate_docx.py",
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

    def test_image_outside_markdown_dir_is_rejected(self) -> None:
        """业务素材同目录（最小授权）：`../` 越级引用图片应被拒绝。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            markdown_path = pathlib.Path(tmpdir) / "doc" / "sample.md"
            blocks = parse_markdown("# 标题\n\n![图1 越级图](../outside.png)\n")
            with self.assertRaises(ValueError) as ctx:
                build_image_assets(blocks, markdown_path, show_page_number=False)
            self.assertIn("跨目录", str(ctx.exception))

    def test_image_in_markdown_subdir_passes_scope_check(self) -> None:
        """同目录/子目录内的图片放行越级校验；不存在则报缺失而非越级错误。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            markdown_path = pathlib.Path(tmpdir) / "sample.md"
            blocks = parse_markdown("# 标题\n\n![图1 子目录图](./img/p.png)\n")
            with self.assertRaises(FileNotFoundError):
                build_image_assets(blocks, markdown_path, show_page_number=False)

    def test_compute_image_size_uses_conservative_width_cap(self) -> None:
        png_bytes = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aD9kAAAAASUVORK5CYII="
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = pathlib.Path(tmpdir) / "sample.png"
            image_path.write_bytes(png_bytes)

            width_emu, height_emu = compute_image_size_emu(image_path)

        expected_width_emu = twips_to_emu(round(PRINTABLE_WIDTH_TWIPS * 0.85))
        self.assertEqual(width_emu, expected_width_emu)
        self.assertEqual(height_emu, expected_width_emu)

    def test_image_paragraph_renders_as_dedicated_paragraph_without_table_wrapper(self) -> None:
        asset = ImageAsset(
            source=pathlib.Path("/tmp/sample.png"),
            rel_id="rId99",
            target_name="image99.png",
            content_type="image/png",
            width_emu=100,
            height_emu=100,
        )

        xml = image_paragraph_xml(asset, alt_text="图1 测试图片", drawing_id=7)

        self.assertIn("<w:p>", xml)
        self.assertNotIn("<w:tbl>", xml)
        self.assertNotIn("<w:cantSplit/>", xml)
        self.assertIn('w:lineRule="atLeast"', xml)
        self.assertIn('w:before="120"', xml)
        self.assertIn('w:after="120"', xml)

    def test_image_height_estimate_includes_spacing_buffer(self) -> None:
        asset = ImageAsset(
            source=pathlib.Path("/tmp/sample.png"),
            rel_id="rId99",
            target_name="image99.png",
            content_type="image/png",
            width_emu=100,
            height_emu=6350,
        )

        estimated = estimate_image_twips(asset, make_args())

        self.assertGreaterEqual(estimated, 10 + 240)

    def test_build_document_inserts_page_break_before_image_section_that_would_overflow(self) -> None:
        args = make_args()
        hidden_sections = {item.strip() for item in args.hide_sections.split(",") if item.strip()}
        attachment_section = Section(
            heading="附件1（可选）",
            blocks=[
                Block(kind="paragraph", text="图1：示意图"),
                Block(kind="image", text="图1 示例图", src="./sample.png"),
                Block(kind="paragraph", text="说明：用于测试图片整块分页。"),
            ],
        )
        image_assets = {
            "./sample.png": ImageAsset(
                source=pathlib.Path("/tmp/sample.png"),
                rel_id="rId99",
                target_name="image99.png",
                content_type="image/png",
                width_emu=4773930,
                height_emu=3182620,
            )
        }
        title_section = Section(heading="标题", blocks=[Block(kind="paragraph", text="示例报告")])
        recipient_section = Section(heading="主送单位", blocks=[Block(kind="paragraph", text="[主送单位]：")])
        attachment_height = estimate_section_height_twips(
            attachment_section,
            args=args,
            hidden_sections=hidden_sections,
            image_assets=image_assets,
        )
        consumed_before_body = (
            estimate_section_height_twips(title_section, args=args, hidden_sections=hidden_sections)
            + estimate_section_height_twips(recipient_section, args=args, hidden_sections=hidden_sections)
        )

        paragraphs: list[Block] = []
        while True:
            body_section = Section(heading="正文", blocks=paragraphs[:])
            consumed = consumed_before_body + estimate_section_height_twips(
                body_section,
                args=args,
                hidden_sections=hidden_sections,
            )
            remaining = PRINTABLE_HEIGHT_TWIPS - (consumed % PRINTABLE_HEIGHT_TWIPS)
            if 0 < remaining < attachment_height:
                break
            paragraphs.append(
                Block(
                    kind="paragraph",
                    text="　　这是用于测试分页行为的正文段落，用于把附件图片区逐步推到页尾附近，以便验证导出器是否会在图片区块前主动分页。",
                )
            )
            self.assertLess(len(paragraphs), 40)

        blocks = [
            Block(kind="heading", level=2, text="标题"),
            Block(kind="paragraph", text="示例报告"),
            Block(kind="heading", level=2, text="主送单位"),
            Block(kind="paragraph", text="[主送单位]："),
            Block(kind="heading", level=2, text="正文"),
            *paragraphs,
            Block(kind="heading", level=2, text="附件1（可选）"),
            Block(kind="paragraph", text="图1：示意图"),
            Block(kind="image", text="图1 示例图", src="./sample.png"),
            Block(kind="paragraph", text="说明：用于测试图片整块分页。"),
        ]

        document_xml = build_document_xml(blocks, args, image_assets=image_assets)

        self.assertRegex(document_xml, r'w:type="page".*?附件1（可选）')

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

    def test_recipient_section_uses_no_extra_after_spacing(self) -> None:
        section = Section(
            heading="主送单位",
            blocks=[Block(kind="paragraph", text="[主送单位]：")],
        )

        xml_parts = render_section_content(section, args=make_args(), hidden_sections=set())

        self.assertEqual(len(xml_parts), 1)
        self.assertIn('w:after="0"', xml_parts[0])

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

    def test_second_level_numbered_heading_uses_two_character_first_line_indent(self) -> None:
        section = Section(
            heading="（一）短视频平台集中出现“我的刀盾”相关表达",
            blocks=[Block(kind="paragraph", text="　　正文示例。")],
        )

        xml_parts = render_section_content(section, args=make_args(), hidden_sections=set())

        self.assertGreaterEqual(len(xml_parts), 2)
        self.assertIn(">（一）短视频平台集中出现“我的刀盾”相关表达<", xml_parts[0])
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
                    "src/scripts/generate_docx.py",
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

    def test_footer_uses_simple_page_field_without_shading_markup(self) -> None:
        args = make_args()
        args.show_page_number = True

        footer_xml = build_footer_xml(args)

        self.assertIn('<w:fldSimple w:instr=" PAGE "', footer_xml)
        self.assertNotIn("<w:fldChar", footer_xml)
        self.assertNotIn("<w:shd", footer_xml)
        self.assertNotIn("<w:highlight", footer_xml)


class GbtConformanceTests(unittest.TestCase):
    """GB/T 9704-2012 对标项：页边距、成文日期两版规则、版头要素、页码。"""

    def _render(self, section: Section, **overrides) -> str:
        args = make_args()
        for key, value in overrides.items():
            setattr(args, key, value)
        return "".join(render_section_content(section, args=args, hidden_sections=set()))

    def test_strict_gbt_margins(self) -> None:
        from scripts.generate_docx import (
            MARGIN_BOTTOM_TWIPS,
            MARGIN_LEFT_TWIPS,
            MARGIN_RIGHT_TWIPS,
            MARGIN_TOP_TWIPS,
        )

        self.assertEqual(
            (MARGIN_TOP_TWIPS, MARGIN_BOTTOM_TWIPS, MARGIN_LEFT_TWIPS, MARGIN_RIGHT_TWIPS),
            (2098, 1984, 1587, 1474),
        )

    def test_sealed_signing_date_is_right_4_chars(self) -> None:
        from scripts.generate_docx import SIGNING_DATE_RIGHT_CHARS

        section = Section(heading="落款", blocks=[Block(kind="paragraph", text="[发文单位]\n2026年6月24日")])
        xml = self._render(section)
        self.assertIn(f'w:rightChars="{SIGNING_DATE_RIGHT_CHARS}"', xml)

    def test_unsealed_signing_date_is_right_2_chars(self) -> None:
        from scripts.generate_docx import MIN_SIGNING_UNIT_RIGHT_CHARS, SIGNING_DATE_RIGHT_CHARS

        section = Section(heading="落款", blocks=[Block(kind="paragraph", text="[发文单位]\n2026年6月24日")])
        xml = self._render(section, unsealed=True)
        self.assertIn(f'w:rightChars="{MIN_SIGNING_UNIT_RIGHT_CHARS}"', xml)
        self.assertNotIn(f'w:rightChars="{SIGNING_DATE_RIGHT_CHARS}"', xml)

    def test_classification_level_uses_heading_font(self) -> None:
        section = Section(heading="密级", blocks=[Block(kind="paragraph", text="机密★1年")])
        xml = self._render(section)
        self.assertIn(DEFAULT_FONT_SETTINGS["heading_font"], xml)  # 黑体
        self.assertIn("机密★1年", xml)

    def test_signer_is_right_aligned_kai(self) -> None:
        section = Section(heading="签发人", blocks=[Block(kind="paragraph", text="签发人：[姓名]")])
        xml = self._render(section)
        self.assertIn(DEFAULT_FONT_SETTINGS["subheading_font"], xml)  # 楷体
        self.assertIn('<w:jc w:val="right"/>', xml)

    def test_page_number_font_and_footer_distance(self) -> None:
        from scripts.generate_docx import PAGE_NUMBER_FONT, PAGE_NUMBER_FOOTER_TWIPS

        footer = build_footer_xml(make_args())
        self.assertIn(PAGE_NUMBER_FONT, footer)  # 宋体
        self.assertEqual(PAGE_NUMBER_FOOTER_TWIPS, 1587)  # ≈版心下 7mm


if __name__ == "__main__":
    unittest.main()
