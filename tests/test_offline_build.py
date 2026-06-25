import unittest

from adapters.offline.build import build_doc_type_prompt_bundle, parse_args
from adapters.shared import (
    load_doc_types,
    load_profile,
    render_offline_system_prompt,
    resolve_doc_type,
    sort_doc_types,
)


class OfflineBuildTests(unittest.TestCase):
    def test_parse_args_defaults_to_full_offline_build_when_no_task_inputs(self) -> None:
        args = parse_args([])

        self.assertTrue(args.emit_system)
        self.assertTrue(args.emit_doc_type_prompts)
        self.assertIsNone(args.doc_type)
        self.assertTrue(args.all_profiles)

    def test_parse_args_with_explicit_profile_only_targets_that_profile(self) -> None:
        args = parse_args(["--profile", "small-local"])

        self.assertTrue(args.emit_system)
        self.assertTrue(args.emit_doc_type_prompts)
        self.assertEqual(args.profile, "small-local")
        self.assertFalse(args.all_profiles)

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

    def test_small_local_profile_can_load(self) -> None:
        profile = load_profile("small-local")

        self.assertEqual(profile.name, "small-local")
        self.assertIn("只输出最终 Markdown", profile.offline_system_preamble)
        self.assertGreaterEqual(len(profile.core_sections), 4)

    def test_small_local_prompt_uses_lite_shared_rules(self) -> None:
        profile = load_profile("small-local")
        doc_types = sort_doc_types(load_doc_types(), profile.category_order)
        doc_type = resolve_doc_type("通知", doc_types)

        system_prompt = render_offline_system_prompt(profile, doc_types, doc_type, include_examples=False)

        self.assertIn("你只处理当前提示词中明确给出的内容", system_prompt)
        self.assertIn("不得自行判断其他文种", system_prompt)
        self.assertIn("只输出最终 Markdown 成稿", system_prompt)
        self.assertIn("- 文种：通知", system_prompt)

    def test_small_local_bundle_is_available_for_all_doc_types(self) -> None:
        profile = load_profile("small-local")
        doc_types = sort_doc_types(load_doc_types(), profile.category_order)

        for doc_type in doc_types:
            bundle = build_doc_type_prompt_bundle(profile, doc_types, doc_type)
            self.assertEqual(set(bundle), {"system_prompt.md", "user_prompt_template.md", "prompt.md"})

    def test_both_profiles_carry_redlines_in_every_doc_type_prompt(self) -> None:
        # 网页版（离线）prompt 必须带行文与格式红线：每个文种的单文种 prompt 都应包含
        # 共享核心里的硬约束（如发文字号写法），防止某次精简误删后弱模型版静默丢失。
        markers = ["发文字号", "主题词"]
        for profile_name in ("default", "small-local"):
            profile = load_profile(profile_name)
            doc_types = sort_doc_types(load_doc_types(), profile.category_order)
            for doc_type in doc_types:
                bundle = build_doc_type_prompt_bundle(profile, doc_types, doc_type)
                for marker in markers:
                    self.assertIn(
                        marker,
                        bundle["prompt.md"],
                        f"{profile_name}/{doc_type.id} 的网页版 prompt 缺少红线标记「{marker}」",
                    )


if __name__ == "__main__":
    unittest.main()
