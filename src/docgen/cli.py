"""命令行入口：解析参数并驱动 Markdown → .docx 导出全流程。"""

from __future__ import annotations

import argparse
import pathlib
import sys
import traceback

from docgen.document import build_document_xml
from docgen.images import build_image_assets
from docgen.markdown import extract_title_and_sections, parse_markdown
from docgen.package import resolve_output_path, write_docx_package
from docgen.settings import (
    finalize_export_settings,
    format_font_profile_catalog,
    format_layout_profile_catalog,
    render_current_export_plan,
    render_current_layout_plan,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="将 Markdown 公文稿导出为 .docx。")
    parser.add_argument("input", nargs="?", type=pathlib.Path, help="输入 Markdown 文件")
    parser.add_argument("-o", "--output", type=pathlib.Path, help="输出 docx 文件，默认与输入同名")
    font_source_group = parser.add_mutually_exclusive_group()
    font_source_group.add_argument("--doc-type", help="按文种自动应用在 prompts/doc-types 中配置的字体方案")
    font_source_group.add_argument("--font-profile", help="直接应用 prompts/font-profiles 中定义的字体方案")
    parser.add_argument("--layout-profile", help="直接应用 prompts/layout-profiles 中定义的版式方案")
    parser.add_argument(
        "--font-preset",
        choices=["system-cn", "source-han", "noto-cjk", "fandol"],
        help="字体预设。仅在未被文种/字体方案和手工字体参数覆盖时补齐对应槽位。",
    )
    parser.add_argument("--list-font-profiles", action="store_true", help="列出当前可用字体方案并退出")
    parser.add_argument("--list-layout-profiles", action="store_true", help="列出当前可用版式方案并退出")
    parser.add_argument("--show-font-plan", action="store_true", help="打印当前解析后的字体与版式方案并退出")
    parser.add_argument("--show-layout-plan", action="store_true", help="仅打印当前解析后的版式方案并退出")
    parser.add_argument("--title-font", help="标题字体名称")
    parser.add_argument("--heading-font", help="小标题字体名称")
    parser.add_argument("--subheading-font", help="二级标题字体名称")
    parser.add_argument("--body-font", help="正文字体名称")
    parser.add_argument("--header-font", help="版头字体名称")
    parser.add_argument("--title-size", type=int, help="标题字号，单位 pt，默认接近 2 号")
    parser.add_argument("--heading-size", type=int, help="小标题字号，单位 pt，默认接近 3 号")
    parser.add_argument("--body-size", type=int, help="正文字号，单位 pt，默认接近 3 号")
    parser.add_argument("--header-size", type=int, help="版头字号，单位 pt")
    parser.add_argument("--line-spacing-pt", type=float, help="粗粒度固定行距，单位 pt；未显式指定 twips 时可作为快捷覆盖")
    parser.add_argument("--body-line-spacing-twips", type=int, help="正文固定行距，单位 twips")
    parser.add_argument("--title-line-spacing-twips", type=int, help="标题行距，单位 twips")
    parser.add_argument("--header-after-twips", type=int, help="版头段后间距，单位 twips")
    parser.add_argument("--doc-number-after-twips", type=int, help="发文字号段后间距，单位 twips")
    parser.add_argument("--title-after-twips", type=int, help="标题段后间距，单位 twips")
    parser.add_argument("--recipient-after-twips", type=int, help="主送机关段后间距，单位 twips")
    parser.add_argument("--signing-before-twips", type=int, help="落款前段距，单位 twips")
    parser.add_argument("--body-first-line-chars", type=int, help="正文首行缩进，单位为百分之一字符，默认 200")
    parser.set_defaults(show_page_number=True)
    parser.add_argument(
        "--show-page-number",
        dest="show_page_number",
        action="store_true",
        help="在页脚中显示页码（默认开启）",
    )
    parser.add_argument(
        "--hide-page-number",
        dest="show_page_number",
        action="store_false",
        help="隐藏页脚页码",
    )
    parser.add_argument(
        "--unsealed",
        action="store_true",
        help="不加盖印章版（电子版）：发文机关署名与成文日期均右空 2 字，而非默认加章版的右空 4 字",
    )
    parser.add_argument("--title-wrap", choices=["auto", "off"], default="auto", help="长标题是否自动断行")
    parser.add_argument("--title-max-chars", type=int, default=20, help="长标题自动断行时每行目标字符数")
    parser.add_argument(
        "--hide-sections",
        default="标题,主送单位,正文,落款",
        help="这些二级标题只作为结构标记，不直接写入文档，使用逗号分隔",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.list_font_profiles:
        print(format_font_profile_catalog())
        return 0
    if args.list_layout_profiles:
        print(format_layout_profile_catalog())
        return 0

    stage = "解析字体与版式方案"
    output_path: pathlib.Path | None = None
    try:
        selected_font_profile, selected_layout_profile = finalize_export_settings(args)

        if args.show_font_plan:
            print(render_current_export_plan(args, selected_font_profile, selected_layout_profile))
            return 0
        if args.show_layout_plan:
            print(render_current_layout_plan(args, selected_layout_profile))
            return 0

        if args.input is None:
            raise SystemExit("缺少输入 Markdown 文件。")

        stage = "读取输入 Markdown"
        markdown = args.input.read_text(encoding="utf-8")
        stage = "解析 Markdown 结构"
        blocks = parse_markdown(markdown)
        if not blocks:
            raise SystemExit("输入文件为空，无法生成 docx。")

        stage = "构建 docx 内容"
        image_assets = build_image_assets(blocks, args.input, show_page_number=args.show_page_number)
        document_xml = build_document_xml(blocks, args, image_assets=image_assets)
        top_title, sections = extract_title_and_sections(blocks)
        if sections:
            title = next(
                (
                    block.text
                    for section in sections
                    if section.heading == "标题"
                    for block in section.blocks
                    if block.kind == "paragraph" and block.text
                ),
                top_title or "公文稿件",
            )
        else:
            title = top_title or "公文稿件"

        stage = "写出 docx 文件"
        output_path = resolve_output_path(args.input, args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        write_docx_package(
            output_path,
            args=args,
            title=title,
            document_xml=document_xml,
            image_assets=image_assets,
        )
    except (OSError, ValueError) as exc:
        # IOError 是 OSError 的别名，一并覆盖；先输出完整堆栈便于诊断，不吞栈。
        traceback.print_exc()
        involved = f"输入 {args.input}" if args.input is not None else "（未提供输入文件）"
        if output_path is not None:
            involved += f"，输出 {output_path}"
        print(f"[ERROR] 导出 docx 失败（阶段：{stage}；{involved}）：{exc}", file=sys.stderr)
        return 1

    print(f"[OK] 已生成 {output_path}")
    return 0
