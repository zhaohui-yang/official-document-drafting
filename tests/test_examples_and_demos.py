from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


class ExamplesAndDemosTests(unittest.TestCase):
    def test_every_doc_type_has_examples_markdown(self) -> None:
        for spec_path in (REPO_ROOT / "prompts" / "doc-types").glob("*/spec.md"):
            examples_path = spec_path.parent / "examples.md"
            self.assertTrue(
                examples_path.exists(),
                f"Missing examples.md for {spec_path.parent.name}",
            )

    def test_online_minutes_demo_uses_wo_de_dao_dun_theme(self) -> None:
        base = REPO_ROOT / "demo" / "online" / "minutes-纪要"
        task = (base / "task.md").read_text(encoding="utf-8")
        materials = (base / "materials.md").read_text(encoding="utf-8")
        readme = (base / "README.md").read_text(encoding="utf-8")

        self.assertIn("我的刀盾", task)
        self.assertIn("我的刀盾", materials)
        self.assertIn("我的刀盾", readme)
        self.assertNotIn("“刀盾”网络传播热度情况", readme)

    def test_offline_demo_has_outline_first_examples(self) -> None:
        offline_root = REPO_ROOT / "demo" / "offline"
        expected = {
            "report-报告": "20260405-关于“我的刀盾”网络传播情况的报告-v02-提纲提示词.md",
            "notice-通知": "20260405-关于开展“我的刀盾”传播素材整理工作的通知-v02-提纲提示词.md",
            "request-请示": "20260405-关于申请开展“我的刀盾”传播案例梳理工作的请示-v02-提纲提示词.md",
            "minutes-纪要": "20260405-关于研究“我的刀盾”网络传播情况的专题会议纪要-v02-提纲提示词.md",
        }

        for folder, filename in expected.items():
            self.assertTrue(
                (offline_root / folder / filename).exists(),
                f"Missing outline-first demo prompt for {folder}",
            )


if __name__ == "__main__":
    unittest.main()
