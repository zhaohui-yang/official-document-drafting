#!/usr/bin/env python3
"""适配层共用的主源读取与渲染辅助模块。

功能说明：
- 统一读取 `prompts/`、`assets/`、`dist/` 等目录下的主源配置。
- 提供 profile、文种、字体方案、版式方案的加载能力。
- 提供 skill 侧和 offline 侧共用的文本渲染、模板导出和路径常量。

适用范围：
- `src/adapters/skill/build.py`
- `src/adapters/offline/build.py`

实现已按职责拆分至 paths.py / profiles.py / doc_types.py / rendering.py，本文件保留为兼容再导出层，新代码请直接从子模块导入。

Author: official-document-drafting maintainers
"""

from __future__ import annotations

from adapters.paths import (
    DIST_DIR,
    DOC_TYPE_GUARDRAILS_PATH,
    DOC_TYPES_DIR,
    FONT_CATALOG_PATH,
    FONT_PROFILES_DIR,
    LAYOUT_PROFILES_DIR,
    PROFILES_DIR,
    PROMPTS_DIR,
    REPO_ROOT,
    ROOT_SKILL_PATH,
    ROOT_TEMPLATES_DIR,
    format_chars,
    format_twips_as_pt,
    load_toml,
    read_text,
    shift_markdown_headings,
    write_text,
)
from adapters.profiles import (
    CoreSection,
    FontFamily,
    FontProfile,
    LayoutProfile,
    Profile,
    build_font_profile_lookup,
    build_layout_profile_lookup,
    format_font_family_files,
    load_font_families,
    load_font_profiles,
    load_layout_profiles,
    load_profile,
    render_font_profile_markdown,
    render_layout_profile_markdown,
    resolve_font_profile,
    resolve_layout_profile,
)
from adapters.doc_types import (
    DocType,
    DocTypeSpec,
    build_doc_type_lookup,
    format_doc_type_catalog,
    load_doc_types,
    normalize_doc_type_key,
    parse_doc_type_spec,
    resolve_doc_type,
    sort_doc_types,
)
from adapters.rendering import (
    SKILL_DEFAULT_FLOW,
    SKILL_DEFAULT_FLOW_REFERENCE,
    SKILL_FILE_INDEX,
    build_skill_references,
    build_template_outputs,
    export_templates,
    render_agent_yaml,
    render_core_sections,
    render_doc_type_guardrails,
    render_doc_type_reference,
    render_offline_system_prompt,
    render_skill_markdown,
    render_skill_markdown_reference_mode,
    render_skill_routing_table,
)


__author__ = "official-document-drafting maintainers"
__maintainer__ = "official-document-drafting maintainers"


__all__ = [
    # paths.py：路径常量与最小 IO/文本工具
    "REPO_ROOT",
    "PROMPTS_DIR",
    "PROFILES_DIR",
    "DOC_TYPES_DIR",
    "FONT_PROFILES_DIR",
    "LAYOUT_PROFILES_DIR",
    "DIST_DIR",
    "ROOT_SKILL_PATH",
    "ROOT_TEMPLATES_DIR",
    "DOC_TYPE_GUARDRAILS_PATH",
    "FONT_CATALOG_PATH",
    "read_text",
    "write_text",
    "load_toml",
    "format_twips_as_pt",
    "format_chars",
    "shift_markdown_headings",
    # profiles.py：profile、字体方案、版式方案
    "CoreSection",
    "Profile",
    "FontFamily",
    "FontProfile",
    "LayoutProfile",
    "load_profile",
    "load_font_families",
    "load_font_profiles",
    "load_layout_profiles",
    "build_font_profile_lookup",
    "resolve_font_profile",
    "build_layout_profile_lookup",
    "resolve_layout_profile",
    "format_font_family_files",
    "render_font_profile_markdown",
    "render_layout_profile_markdown",
    # doc_types.py：文种加载、检索与目录渲染
    "DocTypeSpec",
    "DocType",
    "load_doc_types",
    "sort_doc_types",
    "build_doc_type_lookup",
    "normalize_doc_type_key",
    "resolve_doc_type",
    "parse_doc_type_spec",
    "format_doc_type_catalog",
    # rendering.py：skill/offline 共用渲染与模板导出
    "render_core_sections",
    "render_doc_type_guardrails",
    "SKILL_FILE_INDEX",
    "render_skill_routing_table",
    "SKILL_DEFAULT_FLOW",
    "SKILL_DEFAULT_FLOW_REFERENCE",
    "render_skill_markdown",
    "render_doc_type_reference",
    "build_skill_references",
    "render_skill_markdown_reference_mode",
    "render_agent_yaml",
    "render_offline_system_prompt",
    "build_template_outputs",
    "export_templates",
]
