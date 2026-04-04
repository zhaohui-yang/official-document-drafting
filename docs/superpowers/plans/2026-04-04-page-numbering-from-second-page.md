# Page Numbering From Second Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Change exported `.docx` page numbering so the first page has no footer page number and the second page displays page number `2`.

**Architecture:** Keep the current single-footer design, but update section properties so Word treats the first page as a distinct page without a footer. The default footer remains attached to subsequent pages, and the page number field continues to use section page numbering.

**Tech Stack:** Python ZIP-based DOCX XML generation, unittest

---

### Task 1: Add failing tests for first-page suppression

**Files:**
- Modify: `tests/test_generate_docx.py`
- Modify: `scripts/generate_docx.py`

- [ ] **Step 1: Add a test that builds a document with `show_page_number=True` and asserts the section XML contains `w:titlePg`**

- [ ] **Step 2: Run the docx unit tests and verify the new test fails before implementation**

Run: `python3 -m unittest discover -s tests -p 'test_generate_docx.py'`

Expected: FAIL because the generated section XML does not yet include first-page suppression.

### Task 2: Implement minimal DOCX section-property change

**Files:**
- Modify: `scripts/generate_docx.py`

- [ ] **Step 1: Update section properties so `show_page_number=True` adds `w:titlePg` and keeps the default footer for later pages**

- [ ] **Step 2: Explicitly preserve normal page numbering semantics for the section**

- [ ] **Step 3: Re-run the tests**

Run: `python3 -m unittest discover -s tests -p 'test_generate_docx.py'`

Expected: all tests pass.

### Task 3: Rebuild and verify

**Files:**
- Modify: generated artifacts only if needed for smoke checks

- [ ] **Step 1: Re-run build smoke check**

Run: `python3 scripts/build_all.py`

Expected: build succeeds.

- [ ] **Step 2: Re-run final diff hygiene**

Run: `git diff --check`

Expected: no whitespace errors.
