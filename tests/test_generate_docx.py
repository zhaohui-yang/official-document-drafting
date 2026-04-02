import argparse
import unittest

from scripts.generate_docx import (
    Block,
    DEFAULT_FONT_SETTINGS,
    DEFAULT_LAYOUT_SETTINGS,
    Section,
    render_section_content,
    wrap_title_text,
)


def make_args() -> argparse.Namespace:
    data = {}
    data.update(DEFAULT_FONT_SETTINGS)
    data.update(DEFAULT_LAYOUT_SETTINGS)
    return argparse.Namespace(**data)


class GenerateDocxSigningLayoutTests(unittest.TestCase):
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

    def test_wrap_title_prefers_single_line_when_it_fits(self) -> None:
        title = "关于开展春季绿化工作的通知"
        self.assertEqual(wrap_title_text(title, max_chars=20, enabled=True), title)

    def test_wrapped_title_lines_should_not_increase_in_length(self) -> None:
        title = "步加服知通设营安实，设好治示强化案有规优全基优产做展治整层层落治好项风步优基通方环开"

        wrapped = wrap_title_text(title, max_chars=12, enabled=True)
        lengths = [len(line) for line in wrapped.split("\n")]

        self.assertGreater(len(lengths), 1)
        self.assertTrue(all(lengths[i] >= lengths[i + 1] for i in range(len(lengths) - 1)), lengths)


if __name__ == "__main__":
    unittest.main()
