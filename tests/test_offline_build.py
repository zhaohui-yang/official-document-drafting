import unittest

from adapters.offline.build import build_doc_type_prompt_bundle, parse_args
from adapters.shared import load_doc_types, load_profile, resolve_doc_type, sort_doc_types


class OfflineBuildTests(unittest.TestCase):
    def test_parse_args_defaults_to_full_offline_build_when_no_task_inputs(self) -> None:
        args = parse_args([])

        self.assertTrue(args.emit_system)
        self.assertTrue(args.emit_doc_type_prompts)
        self.assertIsNone(args.doc_type)

    def test_build_doc_type_prompt_bundle_contains_three_artifacts(self) -> None:
        profile = load_profile("default")
        doc_types = sort_doc_types(load_doc_types(), profile.category_order)
        doc_type = resolve_doc_type("报告", doc_types)

        bundle = build_doc_type_prompt_bundle(profile, doc_types, doc_type)

        self.assertEqual(set(bundle), {"system_prompt.md", "user_prompt_template.md", "prompt.md"})
        self.assertIn("## 当前文种", bundle["system_prompt.md"])
        self.assertIn("文种：报告", bundle["system_prompt.md"])
        self.assertIn("[在这里填写当前任务说明", bundle["user_prompt_template.md"])
        self.assertIn("# System Prompt", bundle["prompt.md"])
        self.assertIn("# User Prompt", bundle["prompt.md"])
        self.assertIn("目标文种：报告（report）", bundle["prompt.md"])


if __name__ == "__main__":
    unittest.main()
