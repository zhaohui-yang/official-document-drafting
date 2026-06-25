"""skills/ 下薄路由 skill 的防腐测试。

skills/*/SKILL.md 是手写路由（不由 prompts/ 生成），指向仓库里的既有入口脚本和
主源目录。一旦这些入口被移走或改名，路由就会指向不存在的文件而无人发现。本测试
钉住每个 skill 必备的 frontmatter 和它依赖的关键入口路径，保证路由不腐烂。
"""

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / "skills"

# 每个 skill -> 它在 SKILL.md 中承诺存在的关键入口（相对仓库根）。
SKILL_ENTRYPOINTS = {
    "docx-export": [
        "src/scripts/generate_docx.py",
        "src/scripts/install_fonts.sh",
        "prompts/font-profiles",
        "prompts/layout-profiles",
    ],
    "offline-prompt-packager": [
        "src/adapters/offline/build.py",
        "src/adapters/shared.py",
        "prompts/profiles/default.toml",
    ],
    "document-qa": [
        "src/scripts/check_sections.py",
        "docs/references/style-rules.md",
        "prompts/core/doc-type-guardrails.md",
    ],
    "skill-build": [
        "src/adapters/skill/build.py",
        "src/adapters/shared.py",
        "src/scripts/build_all.py",
    ],
    "ministry-news-daily": [
        "prompts/doc-types/report-报告/spec.md",
        "prompts/core/doc-type-guardrails.md",
        "src/scripts/generate_docx.py",
    ],
    "doc-type-routing": [
        "prompts/core/workflow.md",
        "prompts/core/drafting-thinking.md",
        "docs/references/document-types.md",
    ],
    "policy-keyword-tracker": [
        "prompts/doc-types/special-report-情况专报/spec.md",
        "prompts/core/doc-type-guardrails.md",
        "src/scripts/generate_docx.py",
    ],
}


class SkillRouterTests(unittest.TestCase):
    def test_every_declared_skill_has_router(self) -> None:
        for name in SKILL_ENTRYPOINTS:
            self.assertTrue(
                (SKILLS_DIR / name / "SKILL.md").exists(),
                f"缺少 skills/{name}/SKILL.md",
            )

    def test_router_has_frontmatter_name_and_description(self) -> None:
        for name in SKILL_ENTRYPOINTS:
            text = (SKILLS_DIR / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---"), f"{name} 缺少 frontmatter")
            self.assertIn(f"name: {name}", text, f"{name} 的 frontmatter name 与目录不一致")
            self.assertIn("description:", text, f"{name} 缺少 description")

    def test_referenced_entrypoints_exist(self) -> None:
        for name, entries in SKILL_ENTRYPOINTS.items():
            for rel in entries:
                self.assertTrue(
                    (REPO_ROOT / rel).exists(),
                    f"skills/{name} 路由引用了不存在的入口：{rel}",
                )


if __name__ == "__main__":
    unittest.main()
