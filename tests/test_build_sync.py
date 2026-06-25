"""产物与 prompts/ 主源的同步守卫测试。

目的：SKILL.md、agent 接口、dist 副本和 assets/templates/ 都是由 prompts/ 主源
生成的产物。改了主源却忘了重新运行 `src/adapters/skill/build.py` 时，这些产物会陈旧、
与主源漂移，而其他测试未必能发现。本测试断言「当前主源渲染结果 == 落盘文件」，
等价于在测试里跑一遍 `build.py --check`，覆盖全部生成目标（含模板）。
"""

import unittest

from adapters.offline.build import DEFAULT_OFFLINE_PROFILES, build_profile_targets
from adapters.skill.build import build_targets
from adapters.shared import (
    build_skill_references,
    load_doc_types,
    load_profile,
    render_skill_markdown_reference_mode,
)


class BuildSyncTests(unittest.TestCase):
    def test_all_generated_artifacts_match_source(self) -> None:
        profile = load_profile("default")
        doc_types = load_doc_types()
        targets = build_targets(profile, doc_types)

        # 至少应覆盖根 SKILL.md、dist 的 SKILL 与 agent 两份，以及每个文种模板 + 兜底提纲。
        self.assertGreaterEqual(len(targets), 3 + len(doc_types) + 1)

        stale: list[str] = []
        for path, expected in targets.items():
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                stale.append(str(path))

        self.assertEqual(
            stale,
            [],
            "以下产物未与 prompts/ 主源同步，请运行 `python3 src/adapters/skill/build.py`：\n"
            + "\n".join(stale),
        )

    def test_skill_references_package_is_self_contained(self) -> None:
        """dist/skill 的 references 模式包：每篇 reference 由主源生成、SKILL.md 自包含指向 references/。"""
        profile = load_profile("default")
        doc_types = load_doc_types()

        refs = build_skill_references(profile, doc_types)
        # 共享规则（core_sections）+ 每个文种各一篇。
        self.assertEqual(len(refs), len(profile.core_sections) + len(doc_types))
        self.assertTrue(all(rel.startswith("references/") for rel in refs))

        skill_ref = render_skill_markdown_reference_mode(profile, doc_types)
        self.assertIn("## References", skill_ref)
        self.assertIn("./references/文种-报告.md", skill_ref)
        self.assertIn("./references/core-政策边界.md", skill_ref)
        # 自包含：正文不得有指向 prompts/ 的链接。
        self.assertNotIn("](prompts/", skill_ref)
        self.assertNotIn("](./prompts/", skill_ref)

    def test_offline_artifacts_match_source(self) -> None:
        """离线 dist/offline/** 也是预渲染快照，须与主源同步（在线侧已有同等守卫）。"""
        stale: list[str] = []
        total = 0
        for profile_name in DEFAULT_OFFLINE_PROFILES:
            for path, expected in build_profile_targets(profile_name).items():
                total += 1
                if not path.exists() or path.read_text(encoding="utf-8") != expected:
                    stale.append(str(path))

        self.assertGreater(total, 0)
        self.assertEqual(
            stale,
            [],
            "以下离线产物未与 prompts/ 主源同步，请运行 `python3 src/scripts/build_all.py`：\n"
            + "\n".join(stale),
        )


if __name__ == "__main__":
    unittest.main()
