# Heading Numbering and Demo Regeneration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make substantive正文小标题 default to numbered headings with two-character indentation semantics, then regenerate affected demos under the new rule.

**Architecture:** Update shared writing/layout rules first so the repo’s normative source is unambiguous. Then align high-frequency document templates and the Word exporter so Markdown structure and `.docx` rendering produce the same visual convention. Finally regenerate representative demos and re-run structure/export checks.

**Tech Stack:** Markdown prompt sources, Python exporter/tests, git-tracked demo assets

---

### Task 1: Lock the shared rule and affected scope

**Files:**
- Modify: `prompts/core/style.md`
- Modify: `prompts/core/layout.md`
- Modify: `references/style-rules.md`
- Modify: `references/layout-rules.md`

- [ ] **Step 1: Update shared style rule for numbered substantive headings**

Add or tighten wording so substantive正文并列板块 default to `一、二、三、四` and subordinate headings default to `（一）（二）（三）`, while `标题 / 主送单位 / 落款 / 附注 / 版记 / 附件` remain outside the正文编号体系.

- [ ] **Step 2: Update shared layout rule for heading indentation semantics**

Add wording that substantive正文一级标题 in text should reflect “左起空两格”的常见写法, while exported Word should render the same convention through heading paragraph formatting instead of literal spaces where possible.

- [ ] **Step 3: Mirror the same rule in readable references**

Update `references/style-rules.md` and `references/layout-rules.md` so user-facing documentation matches the source rule.

- [ ] **Step 4: Verify rule text is internally consistent**

Run: `rg -n "左起空两格|一、二、三|正文编号体系|主送单位|落款|附注|版记|附件" prompts/core references`

Expected: matching wording appears in shared rules and references without contradictory guidance.

### Task 2: Align high-frequency templates with the shared rule

**Files:**
- Modify: `prompts/doc-types/report-报告/spec.md`
- Modify: `prompts/doc-types/summary-工作总结/spec.md`
- Modify: `prompts/doc-types/presentation-汇报材料/spec.md`
- Modify: `prompts/doc-types/special-report-情况专报/spec.md`
- Modify: `prompts/doc-types/circular-通报/spec.md`
- Modify: `assets/templates/report.md`
- Modify: `assets/templates/summary.md`
- Modify: `assets/templates/presentation.md`
- Modify: `assets/templates/circular.md`

- [ ] **Step 1: Convert bare substantive section headings to numbered headings in prompt specs**

Replace patterns like `## 基本情况` with `## 一、基本情况` where the section is a substantive正文板块 rather than metadata or end matter.

- [ ] **Step 2: Apply the same conversion in compatibility templates**

Update the corresponding files under `assets/templates/` so fallback examples and direct template reads produce the same heading style.

- [ ] **Step 3: Leave exception cases untouched**

Keep `标题 / 主送单位 / 落款 / 附注 / 版记 / 附件` unchanged, and keep纪要的 `会议认为，……` / `会议决定，……` as inline prompt language rather than converting them into identical headings.

- [ ] **Step 4: Verify template heading consistency**

Run: `rg -n "^## (基本情况|工作开展情况|工作进展|存在问题|下一步建议|下一步打算|下一步措施)$|^## [一二三四五六七八九十]+、" prompts/doc-types assets/templates`

Expected: high-frequency substantive sections appear in numbered form; metadata/end-matter headings stay unnumbered.

### Task 3: Update exporter behavior and test it

**Files:**
- Modify: `scripts/generate_docx.py`
- Modify: `tests/test_generate_docx.py`

- [ ] **Step 1: Add a failing/targeted test for numbered substantive heading rendering**

Add or extend a test that renders a simple Markdown document containing:

```markdown
## 一、基本情况

　　正文示例。
```

and asserts the heading is rendered through the heading path with the expected paragraph formatting for numbered正文标题.

- [ ] **Step 2: Implement minimal heading formatting change**

Adjust the exporter so substantive正文 headings preserve the numbering text and apply the new paragraph formatting convention without affecting title,主送单位,落款,附注,版记 handling.

- [ ] **Step 3: Re-run exporter tests**

Run: `python3 -m unittest discover -s tests -p 'test_generate_docx.py'`

Expected: all tests pass.

- [ ] **Step 4: Rebuild generated prompt artifacts if shared rules changed**

Run: `python3 scripts/build_all.py`

Expected: generated artifacts refresh successfully.

### Task 4: Regenerate representative demos under the new rule

**Files:**
- Modify or regenerate files under: `demo/online/`
- Modify or regenerate files under: `demo/offline/` if the new rule affects mirrored samples
- Modify: `demo/README.md`
- Modify: `README.md` only if sample descriptions need wording updates

- [ ] **Step 1: Update sample Markdown headings to the new numbered style**

For representative demos with substantive section headings, change them from bare section titles to numbered section titles.

- [ ] **Step 2: Re-export affected `.docx` files**

Use the existing exporter commands for each affected demo sample so Markdown and Word output stay aligned.

- [ ] **Step 3: Re-run structure validators where available**

Run:

```bash
python3 renderers/validate.py report <report-md>
python3 renderers/validate.py notice <notice-md>
python3 renderers/validate.py request <request-md>
```

Expected: each validator reports `[OK]`.

- [ ] **Step 4: Final verification**

Run:

```bash
git diff --check
git status --short
```

Expected: no whitespace errors; changed files reflect only the intended rule/template/demo regeneration scope.
